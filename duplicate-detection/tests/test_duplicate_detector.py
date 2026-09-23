"""
Unit tests for DuplicateDetector (Phase 7)
"""

import pytest
from app.services.duplicate_detector import DuplicateDetector


@pytest.fixture(scope="module")
def detector():
    return DuplicateDetector()


def test_obvious_duplicate(detector):
    prob_a = {
        "problemId": "P2001",
        "title": "Garbage is being burned near a school",
        "description": "Garbage is being burned near a school, producing harmful smoke.",
        "location": {"lat": 23.3441, "long": 85.3096},
        "primaryDomain": "Environment",
        "subcategory": "Air Pollution",
    }
    prob_b = {
        "problemId": "P1001",
        "title": "Unprocessed waste burning near school",
        "description": "Unprocessed waste is being burned close to the school and causing air pollution.",
        "location": {"lat": 23.3445, "long": 85.3098},
        "primaryDomain": "Environment",
        "subcategory": "Air Pollution",
    }

    result = detector.detect_duplicates(prob_a, [prob_b])
    assert result["problemId"] == "P2001"
    assert result["status"] == "candidate_found"
    assert len(result["duplicateCandidates"]) == 1

    cand = result["duplicateCandidates"][0]
    assert cand["candidateProblemId"] == "P1001"
    assert cand["duplicateScore"] >= 0.78
    assert cand["semanticSimilarity"] > 0.80
    assert cand["primaryDomainMatch"] is True
    assert cand["subcategoryMatch"] is True
    assert cand["locationDistanceKm"] < 0.1
    assert len(cand["reasons"]) > 0


def test_obvious_non_duplicate(detector):
    prob_a = {
        "problemId": "P2002",
        "title": "Garbage is being burned near a school",
        "description": "Garbage is being burned near a school, producing harmful smoke.",
        "location": {"lat": 23.3441, "long": 85.3096},
        "primaryDomain": "Environment",
        "subcategory": "Air Pollution",
    }
    prob_b = {
        "problemId": "P1002",
        "title": "Computer science teacher shortage in high school",
        "description": "High school lacks qualified computer science teachers and functioning computers.",
        "location": {"lat": 23.3441, "long": 85.3096},
        "primaryDomain": "Education",
        "subcategory": "Teacher Staffing",
    }

    result = detector.detect_duplicates(prob_a, [prob_b])
    assert len(result["duplicateCandidates"]) == 1
    cand = result["duplicateCandidates"][0]
    assert cand["candidateStatus"] == "no_candidate"
    assert cand["duplicateScore"] < 0.60


def test_nearby_vs_distant_candidate(detector):
    prob_a = {
        "problemId": "P2003",
        "title": "Broken water pipeline in Sector 4",
        "description": "Drinking water pipeline broken near Sector 4 community hall.",
        "location": {"lat": 23.3700, "long": 85.3400},
        "primaryDomain": "Water & Sanitation",
        "subcategory": "Pipe Leakage",
    }
    cand_nearby = {
        "problemId": "P_NEARBY",
        "title": "Water pipe leak near Sector 4 hall",
        "description": "Water supply pipe has burst in front of Sector 4 community center.",
        "location": {"lat": 23.3705, "long": 85.3405},
        "primaryDomain": "Water & Sanitation",
        "subcategory": "Pipe Leakage",
    }
    cand_distant = {
        "problemId": "P_DISTANT",
        "title": "Water pipe leak near Sector 4 hall",
        "description": "Water supply pipe has burst in front of Sector 4 community center.",
        "location": {"lat": 28.6139, "long": 77.2090},  # Delhi coordinates (~1000 km away)
        "primaryDomain": "Water & Sanitation",
        "subcategory": "Pipe Leakage",
    }

    result = detector.detect_duplicates(prob_a, [cand_nearby, cand_distant])
    candidates = result["duplicateCandidates"]
    assert len(candidates) == 2
    # Nearby candidate should score higher than distant candidate
    assert candidates[0]["candidateProblemId"] == "P_NEARBY"
    assert candidates[0]["duplicateScore"] > candidates[1]["duplicateScore"]


def test_empty_candidates(detector):
    prob_a = {
        "problemId": "P2004",
        "title": "Pothole on Main Street",
        "description": "Pothole on Main Street causing traffic accidents.",
    }
    result = detector.detect_duplicates(prob_a, [])
    assert result["status"] == "no_candidate"
    assert result["duplicateCandidates"] == []
