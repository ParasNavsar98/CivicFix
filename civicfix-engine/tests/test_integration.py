"""
Integration tests for the civicfix-engine unified pipeline.
Tests the Problem -> Classification -> Duplicate Detection -> University Matching flow
using internal service objects (no HTTP calls).
"""
import pytest

from app.services.duplicate_detection.similarity_service import SimilarityService
from app.services.duplicate_detection.location_service import LocationService
from app.services.duplicate_detection.fingerprint_service import ProblemFingerprintService
from app.services.university_matching.matching_engine import score_university
from app.services.university_matching.matching_config import DEFAULT_WEIGHTS
from app.services.university_matching.ranking import top_n
from app.services.university_matching.assignment_workflow import (
    create_assignment_chain,
    accept_assignment,
    AssignmentError,
)
from app.database.categorization_adapter import (
    adapt_classification_output,
    should_attempt_university_matching,
    CategorizationAdapterError,
)
from app.services.university_matching.problem_input import ProblemInput, ProblemLocation


# ── Integration: Duplicate Detection Signal Correctness ──────────────────────

class TestDuplicateDetectionIntegration:
    def test_similarity_and_location_combined(self):
        """Two semantically similar problems at same location should trigger strong candidate."""
        sim_service = SimilarityService()
        loc_service = LocationService()

        # Same area — Ranchi
        dist = loc_service.haversine_distance(23.3441, 85.3096, 23.3460, 85.3110)
        assert dist is not None and dist < 2.0

        loc_score = loc_service.calculate_location_score(dist, max_radius_km=5.0)
        assert loc_score > 0.5

        # Identical vectors -> perfect semantic match
        v = [1.0, 0.0, 0.0]
        sim = sim_service.cosine_similarity(v, v)
        assert sim == 1.0

    def test_fingerprint_contradiction_detection(self):
        """Problems at same entity but different resources should be contradictory."""
        fp_service = ProblemFingerprintService()

        fp_a = fp_service.extract_fingerprint(
            "Hospital medicine shortage",
            "The hospital lacks medicines and drugs for patients."
        )
        fp_b = fp_service.extract_fingerprint(
            "Hospital electricity outage",
            "The hospital has a complete electricity blackout and power failure."
        )

        assert fp_a["state"] == "AVAILABLE"
        assert fp_b["state"] == "AVAILABLE"
        assert fp_a["affectedEntity"] == "hospital"
        assert fp_b["affectedEntity"] == "hospital"

        state, is_contradictory, reason = fp_service.compare_fingerprints(fp_a, fp_b)
        assert is_contradictory is True
        assert reason is not None

    def test_fingerprint_same_problem_not_contradictory(self):
        """Two descriptions of the same problem should not be contradictory."""
        fp_service = ProblemFingerprintService()

        fp_a = fp_service.extract_fingerprint(
            "Road pothole damage",
            "The road surface has deep potholes that are damaged."
        )
        fp_b = fp_service.extract_fingerprint(
            "Dangerous pothole on road",
            "There are cracked and damaged potholes on the road."
        )

        state, is_contradictory, reason = fp_service.compare_fingerprints(fp_a, fp_b)
        assert is_contradictory is False


# ── Integration: Categorization Adapter -> Matching Pipeline ─────────────────

class TestPipelineIntegration:
    def test_full_classify_to_match_pipeline(self, db, sample_university):
        """Full pipeline: classification output -> adapter -> matching -> assignment."""
        db.universities.insert_one(sample_university)

        # Simulate classification engine output
        classification_json = {
            "primaryDomain": "Environment",
            "subcategory": "Pollution",
            "secondaryDomains": ["Healthcare"],
            "requiredExpertise": ["Environmental Management", "Public Health"],
            "requiredResources": ["Waste collection", "Waste disposal infrastructure"],
            "researchRequired": True,
            "governmentActionPossible": True,
        }
        location = {"district": "Ranchi", "state": "Jharkhand"}

        # Adapter: classification JSON -> ProblemInput
        problem = adapt_classification_output("TEST-PIPE-001", classification_json, location)
        assert problem.problem_id == "TEST-PIPE-001"
        assert problem.primary_domain == "Environment"
        assert problem.location.district == "Ranchi"

        # Gate check
        should_run, reason = should_attempt_university_matching(problem)
        assert should_run is True

        # Score
        result = score_university(problem, sample_university, DEFAULT_WEIGHTS)
        assert result["finalScore"] > 0
        assert result["universityId"] == "UNI-TEST-001"

        # Assignment chain
        ranked = [result]
        ranked[0]["rank"] = 1
        docs = create_assignment_chain(db, "TEST-PIPE-001", ranked)
        assert len(docs) == 1
        assert docs[0]["status"] == "SENT"

    def test_adapter_validates_missing_fields(self):
        """Adapter must reject classification JSON missing required fields."""
        with pytest.raises(CategorizationAdapterError):
            adapt_classification_output(
                "TEST-ERR-001",
                {"primaryDomain": "Environment"},  # missing subcategory, requiredExpertise, requiredResources
                {"district": "Ranchi", "state": "Jharkhand"},
            )

    def test_adapter_validates_missing_location(self):
        """Adapter must reject location missing district or state."""
        with pytest.raises(CategorizationAdapterError):
            adapt_classification_output(
                "TEST-ERR-002",
                {
                    "primaryDomain": "Environment",
                    "subcategory": "Pollution",
                    "requiredExpertise": [],
                    "requiredResources": [],
                },
                {"latitude": 23.3},  # missing district and state
            )

    def test_matching_gate_blocks_no_expertise_problems(self):
        """Problems with no expertise/resources and no research flag should not be matched."""
        problem = ProblemInput(
            problem_id="TEST-GATE-001",
            primary_domain="Other",
            subcategory="Unclassified",
            required_expertise=[],
            required_resources=[],
            location=ProblemLocation(district="X", state="Y"),
            government_action_possible=False,
            research_required=False,
        )
        should_run, reason = should_attempt_university_matching(problem)
        assert should_run is False


# ── Integration: Assignment Chain Lifecycle ───────────────────────────────────

class TestAssignmentChainIntegration:
    def test_accept_cancels_siblings(self, db):
        """Accepting rank 1 must cancel ranks 2-5."""
        candidates = [
            {"universityId": f"UNI-{i}", "rank": i, "finalScore": 90 - i, "factorScores": {"expertise": 0.8}}
            for i in range(1, 6)
        ]
        docs = create_assignment_chain(db, "INT-PROB-001", candidates)
        first_id = docs[0]["assignmentId"]

        result = accept_assignment(db, first_id)
        assert result["status"] == "ACCEPTED"

        siblings = list(db.university_assignments.find(
            {"problemId": "INT-PROB-001", "assignmentId": {"$ne": first_id}}
        ))
        assert all(s["status"] == "CANCELLED" for s in siblings)

    def test_duplicate_chain_prevented(self, db):
        """Cannot create a second chain while one is active."""
        candidates = [
            {"universityId": "UNI-1", "rank": 1, "finalScore": 90, "factorScores": {"expertise": 0.8}}
        ]
        create_assignment_chain(db, "INT-PROB-002", candidates)
        with pytest.raises(AssignmentError):
            create_assignment_chain(db, "INT-PROB-002", candidates)
