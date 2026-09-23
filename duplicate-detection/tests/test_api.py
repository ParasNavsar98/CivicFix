"""
API tests for FastAPI Duplicate Candidate Detection endpoint (Phase 10)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["embeddingModel"] == "BAAI/bge-small-en-v1.5"
    assert data["embeddingDimension"] == 384


def test_duplicate_check_success(client):
    payload = {
        "problem": {
            "problemId": "P2001",
            "title": "Garbage is being burned near a school",
            "description": "Garbage is being burned near a school, producing harmful smoke.",
            "location": {"lat": 23.3441, "long": 85.3096},
            "primaryDomain": "Environment",
            "secondaryDomains": ["Public Health"],
            "subcategory": "Air Pollution",
        },
        "candidates": [
            {
                "problemId": "P1001",
                "title": "Unprocessed waste burning near school",
                "description": "Unprocessed waste is being burned close to the school and causing air pollution.",
                "location": {"lat": 23.3445, "long": 85.3098},
                "primaryDomain": "Environment",
                "secondaryDomains": ["Public Health"],
                "subcategory": "Air Pollution",
            }
        ],
        "topK": 10,
    }

    response = client.post("/duplicate-check", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["problemId"] == "P2001"
    assert data["status"] == "candidate_found"
    assert len(data["duplicateCandidates"]) == 1

    cand = data["duplicateCandidates"][0]
    assert cand["candidateProblemId"] == "P1001"
    assert cand["duplicateScore"] >= 0.75
    assert cand["semanticSimilarity"] > 0.80
    assert cand["primaryDomainMatch"] is True
    assert cand["subcategoryMatch"] is True
    assert isinstance(cand["reasons"], list)
    assert len(cand["reasons"]) > 0


def test_duplicate_check_empty_candidates(client):
    payload = {
        "problem": {
            "problemId": "P2002",
            "title": "Pothole on Main Street",
            "description": "Pothole on Main Street causing traffic accidents.",
        },
        "candidates": [],
    }

    response = client.post("/duplicate-check", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["problemId"] == "P2002"
    assert data["status"] == "no_candidate"
    assert data["duplicateCandidates"] == []


def test_duplicate_check_invalid_input(client):
    payload = {
        "problem": {
            "problemId": "P2003",
            "title": "",  # Empty title invalid
            "description": "Some description",
        },
        "candidates": [],
    }

    response = client.post("/duplicate-check", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["errorCode"] == "INVALID_INPUT"


def test_duplicate_check_malformed_location(client):
    payload = {
        "problem": {
            "problemId": "P2004",
            "title": "Valid title",
            "description": "Valid description",
            "location": {"lat": 150.0, "long": 85.0},  # Invalid lat > 90
        },
        "candidates": [],
    }

    response = client.post("/duplicate-check", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["errorCode"] == "INVALID_INPUT"
