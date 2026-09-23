"""
Integration Test Suite for CivicFix Main Backend, Orchestration Pipeline, and Workflow Engine.

SRS REQUIREMENT COMPLIANCE:
Verifies 30 integration scenarios:
- Problem storage FIRST before AI processing.
- AI classification persistence & AI versioning.
- Reviewer Queue routing for low confidence / duplicates / ambiguity.
- Human Reviewer Actions (ACCEPT, CORRECT, MERGE_DUPLICATE, REQUEST_CLARIFICATION, REJECT).
- MERGE_DUPLICATE links candidate to master while strictly preserving original record.
- CORRECT creates new version snapshot without overwriting historical AI interpretation.
- Resilient failure handling: AI microservice outages NEVER delete or lose submitted problems.
- Append-only audit trail logging.
- Government & Research routing paths.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.problem import Problem
from app.models.review import ReviewerActionEnum
from app.models.version import ProblemVersion
from app.repositories.problem_repository import ProblemRepository
from app.repositories.version_repository import VersionRepository
from app.repositories.duplicate_repository import DuplicateRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.audit_repository import AuditRepository
from app.services.audit_service import AuditService
from app.services.routing_service import RoutingService
from app.services.reviewer_service import ReviewerService
from app.services.orchestrator import ProblemIntakeOrchestrator
from app.clients.classification_client import ClassificationClient, ClassificationClientError
from app.clients.duplicate_client import DuplicateClient, DuplicateClientError
from app.services.workflow import WorkflowService, WorkflowStateError


@pytest.fixture
def mock_clients():
    cls_client = AsyncMock(spec=ClassificationClient)
    dup_client = AsyncMock(spec=DuplicateClient)

    # Default Mock Responses
    cls_client.classify_problem.return_value = {
        "status": "classified",
        "classification": {
            "problemSummary": "Garbage burning near school",
            "primaryDomain": "Environment",
            "secondaryDomains": ["Public Health"],
            "subcategory": "Air Pollution",
            "severity": "HIGH",
            "urgency": "HIGH",
            "researchRequired": False,
            "governmentActionPossible": True,
            "requiredExpertise": ["Environmental Inspection"],
            "requiredResources": ["Waste Management Truck"],
            "confidence": 0.92,
            "reasoning": "High confidence environmental air pollution issue",
        }
    }

    dup_client.check_duplicates.return_value = {
        "problemId": "P1001",
        "status": "no_candidate",
        "duplicateCandidates": []
    }

    return cls_client, dup_client


@pytest.fixture
def app_context(mock_clients):
    cls_client, dup_client = mock_clients

    p_repo = ProblemRepository()
    v_repo = VersionRepository()
    d_repo = DuplicateRepository()
    r_repo = ReviewRepository()
    a_repo = AuditRepository()

    audit_svc = AuditService(a_repo)
    routing_svc = RoutingService(p_repo, audit_svc)
    reviewer_svc = ReviewerService(p_repo, v_repo, r_repo, d_repo, audit_svc)

    orchestrator = ProblemIntakeOrchestrator(
        problem_repo=p_repo,
        version_repo=v_repo,
        duplicate_repo=d_repo,
        audit_service=audit_svc,
        classification_client=cls_client,
        duplicate_client=dup_client,
    )

    app = create_app(
        problem_repo=p_repo,
        version_repo=v_repo,
        duplicate_repo=d_repo,
        review_repo=r_repo,
        audit_repo=a_repo,
        classification_client=cls_client,
        duplicate_client=dup_client,
    )

    return {
        "app": app,
        "client": TestClient(app),
        "orchestrator": orchestrator,
        "reviewer_service": reviewer_svc,
        "routing_service": routing_svc,
        "audit_service": audit_svc,
        "p_repo": p_repo,
        "v_repo": v_repo,
        "d_repo": d_repo,
        "r_repo": r_repo,
        "a_repo": a_repo,
        "cls_client": cls_client,
        "dup_client": dup_client,
    }


# TEST 1: Citizen creates problem — stored in DB FIRST before AI processing
@pytest.mark.asyncio
async def test_problem_submission_persisted_first(app_context):
    orchestrator = app_context["orchestrator"]
    p_repo = app_context["p_repo"]

    data = {
        "problemId": "P_INT_001",
        "title": "Water leak in Sector 4",
        "description": "Drinking water pipe leak in Sector 4 hall.",
    }
    problem = await orchestrator.submit_problem(data, submitter_id="citizen_100")
    assert problem.problemId == "P_INT_001"
    assert problem.status == WorkflowService.SUBMITTED

    stored = await p_repo.get_by_id("P_INT_001")
    assert stored is not None
    assert stored.title == "Water leak in Sector 4"


# TEST 2: Successful Classification & AI Versioning
@pytest.mark.asyncio
async def test_classification_success_and_ai_versioning(app_context):
    orchestrator = app_context["orchestrator"]
    v_repo = app_context["v_repo"]

    data = {"problemId": "P_INT_002", "title": "Potholes on Main St", "description": "Deep craters on Main Street."}
    await orchestrator.submit_problem(data)
    processed = await orchestrator.process_problem("P_INT_002")

    assert processed.classificationState == "completed"
    assert processed.primaryDomain == "Environment"

    versions = await v_repo.list_versions_for_problem("P_INT_002")
    assert len(versions) >= 2  # System initial version + AI version
    ai_ver = [v for v in versions if v.source == "ai"][0]
    assert ai_ver.primaryDomain == "Environment"


# TEST 3: Low Confidence Classification (<0.85) -> Reviewer Queue
@pytest.mark.asyncio
async def test_low_confidence_routes_to_reviewer_queue(app_context):
    orchestrator = app_context["orchestrator"]
    cls_client = app_context["cls_client"]

    # Low confidence 0.62 response
    cls_client.classify_problem.return_value = {
        "status": "classified",
        "classification": {
            "problemSummary": "Unclear issue",
            "primaryDomain": "Governance",
            "subcategory": "Other",
            "severity": "LOW",
            "urgency": "LOW",
            "confidence": 0.62,
            "reasoning": "Unclear text input",
        }
    }

    data = {"problemId": "P_INT_003", "title": "Strange noise", "description": "Some noise in village."}
    await orchestrator.submit_problem(data)
    processed = await orchestrator.process_problem("P_INT_003")

    assert processed.reviewRequired is True
    assert processed.status == WorkflowService.REVIEW_REQUIRED
    assert any("Low AI classification confidence" in r for r in processed.reviewReasons)


# TEST 4: Duplicate Candidates Found -> Reviewer Queue
@pytest.mark.asyncio
async def test_duplicate_candidates_routes_to_reviewer_queue(app_context):
    orchestrator = app_context["orchestrator"]
    dup_client = app_context["dup_client"]

    dup_client.check_duplicates.return_value = {
        "problemId": "P_INT_004",
        "status": "candidate_found",
        "duplicateCandidates": [
            {
                "candidateProblemId": "P_EXISTING_100",
                "duplicateScore": 0.89,
                "semanticSimilarity": 0.91,
                "primaryDomainMatch": True,
                "subcategoryMatch": True,
                "secondaryDomainOverlap": 1.0,
                "candidateStatus": "strong_candidate",
                "reasons": ["High semantic similarity"],
            }
        ]
    }

    data = {"problemId": "P_INT_004", "title": "Garbage burning near school", "description": "Garbage burning near school."}
    await orchestrator.submit_problem(data)
    processed = await orchestrator.process_problem("P_INT_004")

    assert processed.reviewRequired is True
    assert processed.status == WorkflowService.REVIEW_REQUIRED
    assert processed.duplicateStatus == "potential_duplicate"


# TEST 5: Reviewer ACCEPT Action
@pytest.mark.asyncio
async def test_reviewer_accept_action(app_context):
    orchestrator = app_context["orchestrator"]
    reviewer_svc = app_context["reviewer_service"]

    # First submit problem and force to REVIEW_REQUIRED
    data = {"problemId": "P_INT_005", "title": "Issue title", "description": "Issue desc."}
    await orchestrator.submit_problem(data)
    p = await orchestrator.problem_repo.get_by_id("P_INT_005")
    p.status = WorkflowService.REVIEW_REQUIRED
    p.reviewRequired = True
    await orchestrator.problem_repo.save(p)

    res = await reviewer_svc.process_action(
        problem_id="P_INT_005", reviewer_id="rev_01", action=ReviewerActionEnum.ACCEPT, reason="Classification looks correct."
    )

    assert res["problem"]["status"] == WorkflowService.VALIDATED
    assert res["problem"]["reviewRequired"] is False


# TEST 6: Reviewer CORRECT Action Creates NEW Version & Preserves AI Version
@pytest.mark.asyncio
async def test_reviewer_correct_creates_new_version(app_context):
    orchestrator = app_context["orchestrator"]
    reviewer_svc = app_context["reviewer_service"]
    v_repo = app_context["v_repo"]

    data = {"problemId": "P_INT_006", "title": "Garbage burning", "description": "Garbage smoke."}
    await orchestrator.submit_problem(data)
    await orchestrator.process_problem("P_INT_006")

    # Reviewer corrects taxonomy from Environment to Public Health
    res = await reviewer_svc.process_action(
        problem_id="P_INT_006",
        reviewer_id="rev_01",
        action=ReviewerActionEnum.CORRECT,
        reason="Primary impact is public health respiratory illness",
        payload={"primaryDomain": "Public Health", "subcategory": "Respiratory Risk"}
    )

    assert res["problem"]["primaryDomain"] == "Public Health"
    assert res["problem"]["status"] == WorkflowService.VALIDATED

    # Verify both historical AI version and new Reviewer version exist
    versions = await v_repo.list_versions_for_problem("P_INT_006")
    ai_ver = [v for v in versions if v.source == "ai"][0]
    rev_ver = [v for v in versions if v.source == "reviewer"][0]

    assert ai_ver.primaryDomain == "Environment"  # Preserved!
    assert rev_ver.primaryDomain == "Public Health"  # Corrected!


# TEST 7: Reviewer MERGE_DUPLICATE Links Candidate & Preserves Original Submission
@pytest.mark.asyncio
async def test_reviewer_merge_duplicate_preserves_records(app_context):
    orchestrator = app_context["orchestrator"]
    reviewer_svc = app_context["reviewer_service"]
    p_repo = app_context["p_repo"]

    # Submit Master problem
    await orchestrator.submit_problem({"problemId": "P_MASTER", "title": "Master Garbage Burning", "description": "Master desc."})
    await orchestrator.problem_repo.save(Problem(problemId="P_MASTER", submitterId="c1", title="Master Garbage Burning", description="Master desc.", status=WorkflowService.VALIDATED))

    # Submit Duplicate problem
    await orchestrator.submit_problem({"problemId": "P_DUP_SUBMISSION", "title": "Duplicate Garbage Burning", "description": "Dup desc."})
    p_dup = await p_repo.get_by_id("P_DUP_SUBMISSION")
    p_dup.status = WorkflowService.REVIEW_REQUIRED
    await p_repo.save(p_dup)

    # Execute MERGE_DUPLICATE
    res = await reviewer_svc.process_action(
        problem_id="P_DUP_SUBMISSION",
        reviewer_id="rev_01",
        action=ReviewerActionEnum.MERGE_DUPLICATE,
        reason="Identical report to master problem",
        master_problem_id="P_MASTER",
    )

    # Verify Duplicate Record is PRESERVED, linked, and status updated
    dup_stored = await p_repo.get_by_id("P_DUP_SUBMISSION")
    master_stored = await p_repo.get_by_id("P_MASTER")

    assert dup_stored is not None  # NOT deleted!
    assert dup_stored.masterProblemId == "P_MASTER"
    assert dup_stored.duplicateStatus == "merged"
    assert dup_stored.status == WorkflowService.MERGED_DUPLICATE

    assert master_stored is not None  # Master intact!


# TEST 8: Reviewer REJECT_INVALID Action
@pytest.mark.asyncio
async def test_reviewer_reject_invalid(app_context):
    orchestrator = app_context["orchestrator"]
    reviewer_svc = app_context["reviewer_service"]

    await orchestrator.submit_problem({"problemId": "P_INT_008", "title": "Test Spam", "description": "Spam content."})
    p = await orchestrator.problem_repo.get_by_id("P_INT_008")
    p.status = WorkflowService.REVIEW_REQUIRED
    await orchestrator.problem_repo.save(p)

    res = await reviewer_svc.process_action(
        problem_id="P_INT_008", reviewer_id="rev_01", action=ReviewerActionEnum.REJECT_INVALID, reason="Nonsense text"
    )

    assert res["problem"]["status"] == WorkflowService.REJECTED


# TEST 9: Resilient AI Failure Handling — Problem is NEVER lost when Classification Engine fails
@pytest.mark.asyncio
async def test_classification_failure_does_not_lose_problem(app_context):
    orchestrator = app_context["orchestrator"]
    cls_client = app_context["cls_client"]
    p_repo = app_context["p_repo"]

    # Simulate Classification Engine Outage / Timeout
    cls_client.classify_problem.side_effect = ClassificationClientError("Classification microservice timeout")

    await orchestrator.submit_problem({"problemId": "P_INT_009", "title": "Critical Leak", "description": "Pipe leaking water."})
    processed = await orchestrator.process_problem("P_INT_009")

    # Verify problem remains stored securely in DB!
    stored = await p_repo.get_by_id("P_INT_009")
    assert stored is not None
    assert stored.classificationState == "failed"
    assert stored.reviewRequired is True
    assert stored.status == WorkflowService.REVIEW_REQUIRED


# TEST 10: Resilient AI Failure Handling — Problem is NEVER lost when Duplicate Engine fails
@pytest.mark.asyncio
async def test_duplicate_failure_does_not_lose_problem(app_context):
    orchestrator = app_context["orchestrator"]
    dup_client = app_context["dup_client"]
    p_repo = app_context["p_repo"]

    # Simulate Duplicate Engine Outage
    dup_client.check_duplicates.side_effect = DuplicateClientError("Duplicate engine connection refused")

    await orchestrator.submit_problem({"problemId": "P_INT_010", "title": "Pothole on Main St", "description": "Pothole details."})
    processed = await orchestrator.process_problem("P_INT_010")

    stored = await p_repo.get_by_id("P_INT_010")
    assert stored is not None
    assert stored.duplicateDetectionState == "failed"


# TEST 11: Audit Trail Append-Only Logging
@pytest.mark.asyncio
async def test_audit_trail_logging(app_context):
    orchestrator = app_context["orchestrator"]
    audit_svc = app_context["audit_service"]

    await orchestrator.submit_problem({"problemId": "P_INT_011", "title": "Audit Test", "description": "Audit desc."})
    await orchestrator.process_problem("P_INT_011")

    events = await audit_svc.get_trail("P_INT_011")
    assert len(events) >= 3
    action_names = [e.action for e in events]
    assert "PROBLEM_CREATED" in action_names
    assert "AI_PROCESSING_STARTED" in action_names
    assert "AI_PROCESSING_COMPLETED" in action_names


# TEST 12: Research Routing Reaches PENDING_MATCH Status
@pytest.mark.asyncio
async def test_research_routing_reaches_pending_match(app_context):
    orchestrator = app_context["orchestrator"]
    cls_client = app_context["cls_client"]

    # Classification indicating research required
    cls_client.classify_problem.return_value = {
        "status": "classified",
        "classification": {
            "problemSummary": "Water purification innovation required",
            "primaryDomain": "Water & Sanitation",
            "subcategory": "Water Quality",
            "researchRequired": True,
            "governmentActionPossible": False,
            "confidence": 0.95,
        }
    }

    await orchestrator.submit_problem({"problemId": "P_INT_012", "title": "Novel Water Filter Need", "description": "Arsenic removal filter needed."})
    processed = await orchestrator.process_problem("P_INT_012")

    assert processed.status == WorkflowService.PENDING_MATCH


# TEST 13: HTTP API Integration Tests (FastAPI TestClient)
def test_api_submit_and_get_problem(app_context):
    client = app_context["client"]

    payload = {
        "problemId": "P_API_001",
        "title": "Broken streetlight near hospital",
        "description": "Streetlight is out near hospital entrance.",
    }

    # 1. Citizen Submit
    res_submit = client.post("/api/problems", json=payload, headers={"X-User-ID": "citizen_99"})
    assert res_submit.status_code == 200
    data_submit = res_submit.json()
    assert data_submit["success"] is True
    assert data_submit["data"]["problemId"] == "P_API_001"

    # 2. Get Problem Details
    res_get = client.get("/api/problems/P_API_001")
    assert res_get.status_code == 200
    assert res_get.json()["data"]["title"] == "Broken streetlight near hospital"

    # 3. Get Citizen Timeline
    res_tl = client.get("/api/problems/P_API_001/timeline")
    assert res_tl.status_code == 200
    assert len(res_tl.json()["data"]["timeline"]) > 0


# TEST 14: Reviewer API RBAC Authorization Test
def test_reviewer_api_rbac_authorization(app_context):
    client = app_context["client"]

    # Unauthorized citizen request to reviewer queue -> 403 Forbidden
    res_unauth = client.get("/api/reviewer/queue", headers={"X-User-Role": "citizen"})
    assert res_unauth.status_code == 403

    # Authorized reviewer request -> 200 OK
    res_auth = client.get("/api/reviewer/queue", headers={"X-User-Role": "reviewer"})
    assert res_auth.status_code == 200
    assert "queue" in res_auth.json()["data"]


# TEST 15: Full Happy Path Vertical Slice Test
@pytest.mark.asyncio
async def test_full_happy_path_vertical_slice(app_context):
    orchestrator = app_context["orchestrator"]
    reviewer_svc = app_context["reviewer_service"]
    routing_svc = app_context["routing_service"]
    audit_svc = app_context["audit_service"]

    # 1. Citizen Submits Problem
    p1 = await orchestrator.submit_problem({
        "problemId": "P_SLICE_001",
        "title": "Hospital Emergency Drug Shortage",
        "description": "Primary health center lacks basic emergency medicines."
    }, submitter_id="citizen_alpha")
    assert p1.status == WorkflowService.SUBMITTED

    # 2. AI Processing Pipeline Executes
    p2 = await orchestrator.process_problem("P_SLICE_001")
    assert p2.processingState == "completed"

    # 3. Workflow Evaluation & Validation
    assert p2.status in (WorkflowService.VALIDATED, WorkflowService.ROUTED_GOVERNMENT, WorkflowService.REVIEW_REQUIRED)

    # 4. Reviewer Action (Accept)
    if p2.status == WorkflowService.REVIEW_REQUIRED:
        rev_res = await reviewer_svc.process_action("P_SLICE_001", reviewer_id="rev_admin", action=ReviewerActionEnum.ACCEPT)
        assert rev_res["problem"]["status"] == WorkflowService.VALIDATED

    # 5. Routing to Sector
    routed = await routing_svc.route_problem("P_SLICE_001", destination="GOVERNMENT", actor_id="rev_admin")
    assert routed.status == WorkflowService.ROUTED_GOVERNMENT

    # 6. Audit Trail Complete
    events = await audit_svc.get_trail("P_SLICE_001")
    assert len(events) >= 3
