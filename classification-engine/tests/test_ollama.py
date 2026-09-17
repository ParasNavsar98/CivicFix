import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.ai.ollama import OllamaProvider
from app.ai.provider import LLMTimeoutException, LLMUnavailableException, LLMProviderException
from app.schemas.input import ProblemClassificationInput, ProblemLocation
from app.schemas.classification import StatusEnum, ClassificationResult
from app.services.classifier import ClassifierService


@pytest.mark.asyncio
async def test_ollama_successful_request():
    mock_payload = {
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
        "reasoning": "Garbage burning causes pollution."
    }
    mock_response_data = {"response": json.dumps(mock_payload)}

    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = mock_response_data

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_http_response
        provider = OllamaProvider(max_retries=1)

        result = await provider.classify("Test prompt", response_schema=ClassificationResult.model_json_schema())
        
        assert result == json.dumps(mock_payload)
        assert mock_post.call_count == 1
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["model"] == "gemma3:4b"
        assert call_kwargs["json"]["stream"] is False
        assert "format" in call_kwargs["json"]


@pytest.mark.asyncio
async def test_ollama_timeout():
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Timeout error")):
        provider = OllamaProvider(max_retries=1)
        with pytest.raises(LLMTimeoutException) as exc_info:
            await provider.classify("Test prompt")
        assert exc_info.value.error_code == "AI_PROVIDER_TIMEOUT"


@pytest.mark.asyncio
async def test_ollama_connection_failure():
    request_mock = MagicMock(spec=httpx.Request)
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused", request=request_mock)):
        provider = OllamaProvider(max_retries=1)
        with pytest.raises(LLMUnavailableException) as exc_info:
            await provider.classify("Test prompt")
        assert exc_info.value.error_code == "AI_PROVIDER_UNAVAILABLE"
        assert "http://localhost:11434" in str(exc_info.value)


@pytest.mark.asyncio
async def test_ollama_transient_retry_and_success():
    mock_error_resp = MagicMock(spec=httpx.Response)
    mock_error_resp.status_code = 503
    mock_error_resp.text = "Service Unavailable"

    mock_ok_resp = MagicMock(spec=httpx.Response)
    mock_ok_resp.status_code = 200
    mock_ok_resp.json.return_value = {"response": '{"test": "ok"}'}

    with patch("httpx.AsyncClient.post", side_effect=[mock_error_resp, mock_ok_resp]) as mock_post:
        with patch("asyncio.sleep", new_callable=AsyncMock):
            provider = OllamaProvider(max_retries=2)
            result = await provider.classify("Test prompt")
            assert result == '{"test": "ok"}'
            assert mock_post.call_count == 2


@pytest.mark.asyncio
async def test_ollama_retry_exhaustion():
    mock_error_resp = MagicMock(spec=httpx.Response)
    mock_error_resp.status_code = 500
    mock_error_resp.text = "Internal Server Error"

    with patch("httpx.AsyncClient.post", return_value=mock_error_resp) as mock_post:
        with patch("asyncio.sleep", new_callable=AsyncMock):
            provider = OllamaProvider(max_retries=2)
            with pytest.raises(LLMUnavailableException) as exc_info:
                await provider.classify("Test prompt")
            assert exc_info.value.error_code == "AI_PROVIDER_UNAVAILABLE"
            assert mock_post.call_count == 3


@pytest.mark.asyncio
async def test_ollama_model_missing_404():
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 404
    mock_resp.text = "Model not found"

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        provider = OllamaProvider(max_retries=1)
        with pytest.raises(LLMProviderException) as exc_info:
            await provider.classify("Test prompt")
        assert exc_info.value.error_code == "AI_MODEL_NOT_FOUND"
        assert "gemma3:4b" in str(exc_info.value)
        assert "ollama pull gemma3:4b" in str(exc_info.value)


@pytest.mark.asyncio
async def test_ollama_pipeline_integration_success():
    mock_data = {
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
    }
    mock_http_resp = MagicMock(spec=httpx.Response)
    mock_http_resp.status_code = 200
    mock_http_resp.json.return_value = {"response": json.dumps(mock_data)}

    with patch("httpx.AsyncClient.post", return_value=mock_http_resp):
        provider = OllamaProvider(max_retries=0)
        service = ClassifierService(llm_provider=provider)

        inp = ProblemClassificationInput(
            problemId="P1001",
            title="Garbage burning near school",
            description="People dump garbage near our school and burn it every evening.",
            location=ProblemLocation(district="Ranchi", state="Jharkhand"),
        )

        response = await service.classify_problem(inp)
        assert response.status == StatusEnum.CLASSIFIED
        assert response.classification.primaryDomain == "Environment"
        assert response.classification.subcategory == "Pollution"


@pytest.mark.asyncio
async def test_ollama_pipeline_enum_titlecase_normalization():
    mock_data = {
        "problemSummary": "Garbage burning near school",
        "primaryDomain": "Environment",
        "secondaryDomains": [],
        "subcategory": "Pollution",
        "severity": "Medium",  # TitleCase returned by LLM
        "urgency": "High",     # TitleCase returned by LLM
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": [],
        "requiredResources": [],
        "confidence": 0.90,
        "reasoning": "Outdoor garbage burning."
    }
    mock_http_resp = MagicMock(spec=httpx.Response)
    mock_http_resp.status_code = 200
    mock_http_resp.json.return_value = {"response": json.dumps(mock_data)}

    with patch("httpx.AsyncClient.post", return_value=mock_http_resp):
        provider = OllamaProvider(max_retries=0)
        service = ClassifierService(llm_provider=provider)

        inp = ProblemClassificationInput(
            problemId="P1001",
            title="Garbage burning near school",
            description="People dump garbage near our school and burn it every evening.",
            location=ProblemLocation(district="Ranchi", state="Jharkhand"),
        )

        response = await service.classify_problem(inp)
        assert response.status == StatusEnum.CLASSIFIED
        assert response.classification.severity == "MEDIUM"
        assert response.classification.urgency == "HIGH"


@pytest.mark.asyncio
async def test_ollama_pipeline_extra_fields_rejection():
    mock_data = {
        "problemSummary": "Garbage burning near school",
        "primaryDomain": "Environment",
        "secondaryDomains": [],
        "subcategory": "Pollution",
        "severity": "HIGH",
        "urgency": "HIGH",
        "researchRequired": False,
        "governmentActionPossible": True,
        "requiredExpertise": [],
        "requiredResources": [],
        "confidence": 0.90,
        "reasoning": "Outdoor garbage burning.",
        "additionalNotes": "Extra field that should be forbidden"
    }
    mock_http_resp = MagicMock(spec=httpx.Response)
    mock_http_resp.status_code = 200
    mock_http_resp.json.return_value = {"response": json.dumps(mock_data)}

    with patch("httpx.AsyncClient.post", return_value=mock_http_resp):
        provider = OllamaProvider(max_retries=0)
        service = ClassifierService(llm_provider=provider)

        inp = ProblemClassificationInput(
            problemId="P1001",
            title="Garbage burning near school",
            description="People dump garbage near school.",
            location=ProblemLocation(district="Ranchi", state="Jharkhand"),
        )

        response = await service.classify_problem(inp)
        assert response.status == StatusEnum.FAILED
        assert response.error.errorCode == "AI_VALIDATION_ERROR"
