import json
import pytest
from fastapi.testclient import TestClient

from app.main import app, classifier_service
from app.ai.provider import LLMUnavailableException
from tests.test_classifier import MockLLMProvider


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """Verify /health returns 200 healthy regardless of LLM provider availability."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_classify_endpoint_success(client):
    mock_json = json.dumps({
        "problemSummary": "Garbage burning near school",
        "primaryDomain": "Environment",
        "secondaryDomains": ["Sanitation"],
        "subcategory": "Pollution",
        "severity": "HIGH",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": ["Waste Management"],
        "requiredResources": ["Waste collection"],
        "confidence": 0.91,
        "reasoning": "Outdoor garbage burning near a school."
    })
    
    # Inject mock provider into classifier service
    classifier_service.llm_provider = MockLLMProvider(response_text=mock_json)

    payload = {
        "problemId": "P1001",
        "title": "Garbage burning near school",
        "description": "People dump garbage near our school and burn it every evening.",
        "location": {
            "district": "Ranchi",
            "state": "Jharkhand"
        }
    }

    response = client.post("/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["problemId"] == "P1001"
    assert data["status"] == "classified"
    assert data["classification"]["primaryDomain"] == "Environment"


def test_classify_endpoint_invalid_input(client):
    payload = {
        "problemId": "",  # Invalid empty problemId
        "title": "Broken road",
        "description": "Road is damaged",
        "location": {
            "district": "Ranchi",
            "state": "Jharkhand"
        }
    }

    response = client.post("/classify", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "failed"
    assert data["errorCode"] == "INVALID_INPUT"


def test_classify_endpoint_provider_failure(client):
    classifier_service.llm_provider = MockLLMProvider(
        exception_to_raise=LLMUnavailableException("Unable to connect to Ollama.")
    )

    payload = {
        "problemId": "P1002",
        "title": "Garbage burning near school",
        "description": "People dump garbage near school.",
        "location": {
            "district": "Ranchi",
            "state": "Jharkhand"
        }
    }

    response = client.post("/classify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error"]["errorCode"] == "AI_PROVIDER_UNAVAILABLE"
