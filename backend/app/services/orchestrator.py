"""
Problem Intake Orchestrator for CivicFix Main Backend.
SRS COMPLIANCE:
Coordinates Problem Storage -> Classification Engine -> Duplicate Detection Engine -> Workflow Evaluation -> Audit Trail.

RESILIENCE GUARANTEE:
Problem is persisted FIRST before AI invocation.
AI microservice failures (timeout/error) NEVER delete or lose the citizen problem submission.
AI services are recommendations engines; workflow state machine evaluates review queues.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.clients.classification_client import ClassificationClient, ClassificationClientError
from app.clients.duplicate_client import DuplicateClient, DuplicateClientError
from app.models.ai_analysis import AIAnalysisRecord
from app.models.duplicate_candidate import DuplicateCandidateRecord
from app.models.problem import Problem, ProblemLocation
from app.models.version import ProblemVersion
from app.repositories.audit_repository import AuditRepository
from app.repositories.duplicate_repository import DuplicateRepository
from app.repositories.problem_repository import ProblemRepository
from app.repositories.version_repository import VersionRepository
from app.services.audit_service import AuditService
from app.services.routing_service import RoutingService
from app.services.workflow import WorkflowService


class ProblemIntakeOrchestrator:
    def __init__(
        self,
        problem_repo: ProblemRepository,
        version_repo: VersionRepository,
        duplicate_repo: DuplicateRepository,
        audit_service: AuditService,
        classification_client: Optional[ClassificationClient] = None,
        duplicate_client: Optional[DuplicateClient] = None,
    ):
        self.problem_repo = problem_repo
        self.version_repo = version_repo
        self.duplicate_repo = duplicate_repo
        self.audit_service = audit_service
        self.classification_client = classification_client or ClassificationClient()
        self.duplicate_client = duplicate_client or DuplicateClient()

    async def submit_problem(self, problem_data: Dict[str, Any], submitter_id: str = "citizen_001") -> Problem:
        """
        1. Validates and stores Problem FIRST in database before AI processing.
        2. Creates initial Version snapshot.
        3. Logs PROBLEM_CREATED audit event.
        """
        prob_id = problem_data.get("problemId") or f"P-{uuid.uuid4().hex[:8].upper()}"

        loc_data = problem_data.get("location") or {}
        location_obj = ProblemLocation(
            lat=loc_data.get("lat") or loc_data.get("latitude"),
            long=loc_data.get("long") or loc_data.get("longitude"),
            address=loc_data.get("address") or loc_data.get("district"),
        )

        problem = Problem(
            problemId=prob_id,
            submitterId=submitter_id,
            title=problem_data.get("title", "").strip(),
            description=problem_data.get("description", "").strip(),
            location=location_obj,
            status=WorkflowService.SUBMITTED,
            processingState="pending",
            classificationState="pending",
            duplicateDetectionState="pending",
            privacyClass=problem_data.get("privacyClass", "PUBLIC"),
        )

        # Store Problem FIRST
        saved_problem = await self.problem_repo.save(problem)

        # Create System Initial Version
        ver_id = f"VER-{uuid.uuid4().hex[:8].upper()}"
        initial_version = ProblemVersion(
            versionId=ver_id,
            problemId=prob_id,
            source="system",
            title=saved_problem.title,
            description=saved_problem.description,
            createdBy=submitter_id,
            changeReason="Initial citizen submission",
        )
        await self.version_repo.save_version(initial_version)
        saved_problem.currentProblemVersionId = ver_id
        await self.problem_repo.save(saved_problem)

        # Log Audit Event
        await self.audit_service.log_event(
            entity_type="problem",
            entity_id=prob_id,
            actor_id=submitter_id,
            actor_role="citizen",
            action="PROBLEM_CREATED",
            previous_state=None,
            new_state=WorkflowService.SUBMITTED,
        )

        return saved_problem

    async def process_problem(self, problem_id: str) -> Problem:
        """
        Executes AI Processing Pipeline:
        Classification Engine -> AI Version -> Duplicate Engine -> Workflow Evaluation.
        """
        problem = await self.problem_repo.get_by_id(problem_id)
        if not problem:
            raise ValueError(f"Problem {problem_id} not found.")

        # Transition to AI_PROCESSING
        prev_state = problem.status
        if prev_state == WorkflowService.SUBMITTED:
            WorkflowService.validate_transition(prev_state, WorkflowService.AI_PROCESSING)
            problem.status = WorkflowService.AI_PROCESSING

        problem.processingState = "processing"
        await self.problem_repo.save(problem)

        await self.audit_service.log_event(
            entity_type="problem",
            entity_id=problem_id,
            actor_id="system",
            actor_role="system",
            action="AI_PROCESSING_STARTED",
            previous_state=prev_state,
            new_state=problem.status,
        )

        # STEP A: Classification Engine Execution
        classification_result = None
        try:
            raw_cls = await self.classification_client.classify_problem(problem.model_dump())
            if raw_cls and raw_cls.get("status") in ("classified", "review_required"):
                cls_data = raw_cls.get("classification") or {}
                classification_result = cls_data

                problem.primaryDomain = cls_data.get("primaryDomain")
                problem.secondaryDomains = cls_data.get("secondaryDomains", [])
                problem.subcategory = cls_data.get("subcategory")
                problem.severity = cls_data.get("severity")
                problem.urgency = cls_data.get("urgency")
                problem.publicSummary = cls_data.get("problemSummary")
                problem.classificationState = "completed"

                confidence = float(cls_data.get("confidence", 0.0))

                # Check Confidence Threshold Safeguard (e.g. < 0.85 requires review)
                if confidence < 0.85 or raw_cls.get("status") == "review_required":
                    problem.reviewRequired = True
                    problem.reviewReasons.append(f"Low AI classification confidence ({confidence:.2f} < 0.85)")

                # Create AI Problem Version
                ver_id = f"VER-AI-{uuid.uuid4().hex[:8].upper()}"
                ai_version = ProblemVersion(
                    versionId=ver_id,
                    problemId=problem_id,
                    source="ai",
                    title=problem.title,
                    description=problem.description,
                    primaryDomain=problem.primaryDomain,
                    secondaryDomains=problem.secondaryDomains,
                    subcategory=problem.subcategory,
                    severity=problem.severity,
                    urgency=problem.urgency,
                    researchRequired=cls_data.get("researchRequired"),
                    governmentActionPossible=cls_data.get("governmentActionPossible"),
                    requiredExpertise=cls_data.get("requiredExpertise", []),
                    requiredResources=cls_data.get("requiredResources", []),
                    publicSummary=problem.publicSummary,
                    reasoning=cls_data.get("reasoning"),
                    createdBy="classification-engine",
                    changeReason="AI Classification Analysis",
                )
                await self.version_repo.save_version(ai_version)
                problem.currentProblemVersionId = ver_id

                await self.audit_service.log_event(
                    entity_type="problem",
                    entity_id=problem_id,
                    actor_id="classification-engine",
                    actor_role="system",
                    action="AI_CLASSIFICATION_COMPLETED",
                    metadata={"confidence": confidence, "status": raw_cls.get("status")},
                )
            else:
                problem.classificationState = "failed"
                problem.reviewRequired = True
                problem.reviewReasons.append("Classification Engine returned failed outcome.")
        except Exception as e:
            # Classification Service Failure Safeguard — DO NOT DELETE PROBLEM
            problem.classificationState = "failed"
            problem.reviewRequired = True
            problem.reviewReasons.append(f"Classification Engine service error: {str(e)}")
            await self.audit_service.log_event(
                entity_type="problem",
                entity_id=problem_id,
                actor_id="classification-engine",
                actor_role="system",
                action="AI_CLASSIFICATION_FAILED",
                metadata={"error": str(e)},
            )

        # STEP B: Duplicate Detection Engine Execution
        try:
            existing_candidates = await self.problem_repo.list_all(limit=50)
            candidate_pool = [
                p.model_dump() for p in existing_candidates if p.problemId != problem_id
            ]

            raw_dup = await self.duplicate_client.check_duplicates(
                problem_data=problem.model_dump(),
                candidates=candidate_pool,
                top_k=10
            )

            if raw_dup and raw_dup.get("status") == "candidate_found":
                candidates_list = raw_dup.get("duplicateCandidates", [])
                has_duplicate_risk = False

                for cand in candidates_list:
                    rec_id = f"DUP-{uuid.uuid4().hex[:8].upper()}"
                    rec = DuplicateCandidateRecord(
                        recordId=rec_id,
                        problemId=problem_id,
                        candidateProblemId=cand["candidateProblemId"],
                        duplicateScore=cand["duplicateScore"],
                        semanticSimilarity=cand["semanticSimilarity"],
                        primaryDomainMatch=cand["primaryDomainMatch"],
                        subcategoryMatch=cand["subcategoryMatch"],
                        secondaryDomainOverlap=cand["secondaryDomainOverlap"],
                        locationDistanceKm=cand.get("locationDistanceKm"),
                        locationScore=cand.get("locationScore", 0.0),
                        status="candidate",
                        reasons=cand.get("reasons", []),
                    )
                    await self.duplicate_repo.save_candidate(rec)

                    if cand.get("candidateStatus") in ("strong_candidate", "potential_duplicate"):
                        has_duplicate_risk = True

                if has_duplicate_risk:
                    problem.reviewRequired = True
                    problem.duplicateStatus = "potential_duplicate"
                    problem.reviewReasons.append("Potential duplicate candidate(s) discovered")

                problem.duplicateDetectionState = "completed"

                await self.audit_service.log_event(
                    entity_type="problem",
                    entity_id=problem_id,
                    actor_id="duplicate-detection",
                    actor_role="system",
                    action="DUPLICATE_ANALYSIS_COMPLETED",
                    metadata={"candidatesFound": len(candidates_list)},
                )
            else:
                problem.duplicateDetectionState = "completed"
        except Exception as e:
            # Duplicate Service Failure Safeguard — DO NOT DELETE PROBLEM
            problem.duplicateDetectionState = "failed"
            problem.reviewRequired = True
            problem.reviewReasons.append(f"Duplicate Detection service error: {str(e)}")
            await self.audit_service.log_event(
                entity_type="problem",
                entity_id=problem_id,
                actor_id="duplicate-detection",
                actor_role="system",
                action="DUPLICATE_ANALYSIS_FAILED",
                metadata={"error": str(e)},
            )

        # STEP C: Final Workflow State Evaluation
        prev_state = problem.status
        if problem.reviewRequired:
            target_state = WorkflowService.REVIEW_REQUIRED
        else:
            target_state = WorkflowService.VALIDATED

        WorkflowService.validate_transition(prev_state, target_state)
        problem.status = target_state
        problem.processingState = "completed"

        # Automatic Routing Recommendation Evaluation if Validated
        if problem.status == WorkflowService.VALIDATED and classification_result:
            route_dest = RoutingService.get_routing_recommendation(
                government_action_possible=classification_result.get("governmentActionPossible"),
                research_required=classification_result.get("researchRequired"),
            )
            if route_dest == "BOTH":
                problem.status = WorkflowService.PENDING_MATCH
            elif route_dest == "RESEARCH":
                problem.status = WorkflowService.PENDING_MATCH
            else:
                problem.status = WorkflowService.ROUTED_GOVERNMENT

        saved_problem = await self.problem_repo.save(problem)

        await self.audit_service.log_event(
            entity_type="problem",
            entity_id=problem_id,
            actor_id="system",
            actor_role="system",
            action="AI_PROCESSING_COMPLETED",
            previous_state=prev_state,
            new_state=saved_problem.status,
        )

        return saved_problem
