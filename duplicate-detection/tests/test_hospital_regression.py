"""
Phase 13 — Hospital Medicine Shortage Regression Test
Verifies that strong semantic duplicates with missing taxonomy metadata are correctly surfaced as candidates,
and that missing metadata is treated as UNKNOWN rather than MISMATCH.
"""

import pytest
from app.services.duplicate_detector import DuplicateDetector
from app.services.embedding import EmbeddingService


@pytest.fixture(scope="module")
def detector():
    emb = EmbeddingService()
    emb.load_model()
    return DuplicateDetector(embedding_service=emb)


def test_hospital_medicine_shortage_regression(detector: DuplicateDetector):
    """
    Hospital Medicine Shortage case:
    Both problems lack taxonomy metadata (primaryDomain=None, subcategory=None).
    Both have identical lat/long (28.7041, 77.1025).
    """
    prob_a = {
        "problemId": "P-MASTER-601",
        "title": "Hospital medicine shortage",
        "description": "Primary health center lacks basic emergency medicines.",
        "location": {"lat": 28.7041, "long": 77.1025, "address": "PHC Center"},
        "primaryDomain": None,
        "subcategory": None,
        "secondaryDomains": [],
    }

    prob_b = {
        "problemId": "P-CANDIDATE-602",
        "title": "Shortage of Medicines in a nearby hospital",
        "description": "Hospitals lack medicines.",
        "location": {"lat": 28.7041, "long": 77.1025, "address": "PHC Center"},
        "primaryDomain": None,
        "subcategory": None,
        "secondaryDomains": [],
    }

    analysis = detector.analyze_candidate_pair(prob_a, prob_b)

    # 1. Semantic similarity must be high
    assert analysis["semanticSimilarity"] >= 0.80, f"Expected high semantic similarity, got {analysis['semanticSimilarity']}"

    # 2. Distance should be 0.0 km
    assert analysis["locationDistanceKm"] == 0.0

    # 3. Missing taxonomy must be UNKNOWN, NOT MISMATCH
    signal_states = analysis["signalStates"]
    assert signal_states["primaryDomain"] == "UNKNOWN"
    assert signal_states["subcategory"] == "UNKNOWN"
    assert signal_states["secondaryDomains"] == "UNKNOWN"

    # Backward compatibility boolean match fields should be False (not MATCH) but state is UNKNOWN
    assert analysis["primaryDomainMatch"] is False
    assert analysis["subcategoryMatch"] is False

    # 4. Normalized composite score must NOT drop to ~53% (must be high >= 0.80)
    assert analysis["duplicateScore"] >= 0.80, f"Composite score suppressed artificially: {analysis['duplicateScore']}"

    # 5. Candidate MUST be surfaced as candidate
    assert analysis["candidateStatus"] in ("strong_candidate", "potential_duplicate")

    # 6. Reasons must explain missing domain as unavailable, not mismatch
    reasons_str = " ".join(analysis["reasons"]).lower()
    assert "not provided" in reasons_str or "unavailable" in reasons_str
    assert "different primary domain" not in reasons_str

    # 7. Engine check endpoint must surface candidate, no auto-merge
    resp = detector.detect_duplicates(prob_a, [prob_b])
    assert resp["status"] == "candidate_found"
    assert len(resp["duplicateCandidates"]) == 1
    assert resp["duplicateCandidates"][0]["candidateProblemId"] == "P-CANDIDATE-602"
