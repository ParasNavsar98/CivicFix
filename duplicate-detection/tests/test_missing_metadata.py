"""
Phase 14 — Comprehensive Missing Metadata & Negative Candidate Tests
Tests signal states, score breakdowns, fingerprint contradictions, and candidate ranking.
"""

import pytest
from app.services.duplicate_detector import DuplicateDetector
from app.services.embedding import EmbeddingService


@pytest.fixture(scope="module")
def detector():
    emb = EmbeddingService()
    emb.load_model()
    return DuplicateDetector(embedding_service=emb)


def test_missing_location_handled_as_unavailable(detector: DuplicateDetector):
    prob_a = {
        "problemId": "P1",
        "title": "Water leakage in Sector 4",
        "description": "Drinking water pipeline burst leaking water on street.",
        "location": None,
        "primaryDomain": "Water & Sanitation",
        "subcategory": "Water Leakage",
        "secondaryDomains": ["Infrastructure"],
    }
    prob_b = {
        "problemId": "P2",
        "title": "Water pipe leak in Sector 4",
        "description": "Pipe leaking water near community hall.",
        "location": {"lat": 23.37, "long": 85.34},
        "primaryDomain": "Water & Sanitation",
        "subcategory": "Water Leakage",
        "secondaryDomains": ["Infrastructure"],
    }

    analysis = detector.analyze_candidate_pair(prob_a, prob_b)
    assert analysis["signalStates"]["location"] == "UNAVAILABLE"
    assert analysis["locationDistanceKm"] is None
    # Location weight (0.10) is excluded from denominator, so available weight = 0.90
    assert analysis["availableWeight"] == 0.90
    assert analysis["duplicateScore"] >= 0.85
    assert analysis["candidateStatus"] in ("strong_candidate", "potential_duplicate")


def test_same_location_different_problem_not_duplicate(detector: DuplicateDetector):
    prob_a = {
        "problemId": "P1",
        "title": "Noise pollution from late night speakers",
        "description": "Loud music played past midnight near residential complex.",
        "location": {"lat": 18.5204, "long": 73.8567},
        "primaryDomain": "Environment",
        "subcategory": "Noise Pollution",
    }
    prob_b = {
        "problemId": "P2",
        "title": "Drainage pipe blockage overflowing on street",
        "description": "Sewage water flowing on road due to blocked drainage pipe.",
        "location": {"lat": 18.5204, "long": 73.8567},
        "primaryDomain": "Water & Sanitation",
        "subcategory": "Drainage Blockage",
    }

    analysis = detector.analyze_candidate_pair(prob_a, prob_b)
    assert analysis["signalStates"]["primaryDomain"] == "MISMATCH"
    assert analysis["signalStates"]["subcategory"] == "MISMATCH"
    assert analysis["candidateStatus"] == "no_candidate"


def test_same_hospital_different_issue_contradiction(detector: DuplicateDetector):
    prob_a = {
        "problemId": "P1",
        "title": "Hospital medicine shortage",
        "description": "Primary health center lacks basic emergency medicines.",
        "location": {"lat": 28.7041, "long": 77.1025},
    }
    prob_b = {
        "problemId": "P2",
        "title": "Hospital electricity outage",
        "description": "Primary health center electricity power cut past 6 hours.",
        "location": {"lat": 28.7041, "long": 77.1025},
    }

    analysis = detector.analyze_candidate_pair(prob_a, prob_b)
    # Fingerprint contradiction must be flagged
    assert analysis["fingerprint"]["isContradictory"] is True
    assert analysis["candidateStatus"] == "no_candidate"


def test_all_taxonomy_and_location_missing(detector: DuplicateDetector):
    prob_a = {
        "problemId": "P1",
        "title": "Deep road pothole on main avenue",
        "description": "Dangerous pothole damaging cars.",
    }
    prob_b = {
        "problemId": "P2",
        "title": "Large crater on main avenue road",
        "description": "Huge road pothole causing vehicle damage.",
    }

    analysis = detector.analyze_candidate_pair(prob_a, prob_b)
    assert analysis["signalStates"]["primaryDomain"] == "UNKNOWN"
    assert analysis["signalStates"]["subcategory"] == "UNKNOWN"
    assert analysis["signalStates"]["location"] == "UNAVAILABLE"
    # Only semantic weight (0.50) is available
    assert analysis["availableWeight"] == 0.50
    assert abs(analysis["duplicateScore"] - round(analysis["semanticSimilarity"], 4)) < 1e-4
    assert analysis["candidateStatus"] in ("strong_candidate", "potential_duplicate")


def test_multiple_candidates_sorted_by_score(detector: DuplicateDetector):
    query = {
        "problemId": "Q1",
        "title": "Potholes on Main Street market",
        "description": "Potholes on Main Street near central market causing heavy traffic.",
        "location": {"lat": 23.36, "long": 85.33},
        "primaryDomain": "Infrastructure",
        "subcategory": "Road Maintenance",
    }
    cand_strong = {
        "problemId": "C1",
        "title": "Deep craters on Main St",
        "description": "Deep road craters near central market creating traffic jams.",
        "location": {"lat": 23.3605, "long": 85.3305},
        "primaryDomain": "Infrastructure",
        "subcategory": "Road Maintenance",
    }
    cand_weak = {
        "problemId": "C2",
        "title": "Streetlight failure on Main St",
        "description": "Dark streetlights near market.",
        "location": {"lat": 23.36, "long": 85.33},
        "primaryDomain": "Infrastructure",
        "subcategory": "Lighting",
    }

    resp = detector.detect_duplicates(query, [cand_weak, cand_strong])
    assert resp["status"] == "candidate_found"
    assert len(resp["duplicateCandidates"]) == 2
    # First candidate must be cand_strong
    assert resp["duplicateCandidates"][0]["candidateProblemId"] == "C1"
    assert resp["duplicateCandidates"][0]["duplicateScore"] > resp["duplicateCandidates"][1]["duplicateScore"]
