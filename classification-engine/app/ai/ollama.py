import asyncio
import logging
from typing import Dict, Any, Optional
import httpx

from app.ai.provider import (
    LLMProvider,
    LLMProviderException,
    LLMTimeoutException,
    LLMUnavailableException,
)
from app.config import settings

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Local Ollama API provider implementation using httpx.AsyncClient."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS
        self.max_retries = max_retries if max_retries is not None else settings.LLM_MAX_RETRIES

    async def classify(
        self,
        prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Call Ollama /api/generate endpoint with structured JSON requirement and exponential backoff retries."""
        url = f"{self.base_url}/api/generate"

        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
            },
        }

        if response_schema:
            payload["format"] = response_schema
        else:
            payload["format"] = "json"

        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.info(
                    "Calling Ollama API (model: %s, attempt: %d/%d) at %s",
                    self.model,
                    attempt + 1,
                    self.max_retries + 1,
                    url,
                )
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response", "")
                    if not response_text:
                        raise LLMProviderException(
                            "Ollama returned empty response content.",
                            error_code="AI_EMPTY_RESPONSE",
                        )
                    return response_text

                elif response.status_code == 404:
                    logger.error("Ollama HTTP 404: Model '%s' not found.", self.model)
                    raise LLMProviderException(
                        f"Ollama model '{self.model}' not found. Please install it using 'ollama pull {self.model}'.",
                        error_code="AI_MODEL_NOT_FOUND",
                    )

                elif response.status_code in (429, 500, 502, 503, 504):
                    logger.warning(
                        "Ollama transient HTTP status %d: %s",
                        response.status_code,
                        response.text,
                    )
                    last_exception = LLMUnavailableException(
                        f"Ollama service returned transient error (HTTP {response.status_code})."
                    )

                else:
                    logger.error("Ollama error HTTP %d: %s", response.status_code, response.text)
                    raise LLMProviderException(
                        f"Ollama API returned HTTP status {response.status_code}.",
                        error_code="AI_PROVIDER_ERROR",
                    )

            except httpx.TimeoutException as exc:
                logger.warning("Timeout connecting to Ollama API on attempt %d: %s", attempt + 1, str(exc))
                last_exception = LLMTimeoutException("Classification request to Ollama timed out.")

            except (httpx.ConnectError, httpx.RequestError) as exc:
                logger.warning("Connection error with Ollama on attempt %d: %s", attempt + 1, str(exc))
                last_exception = LLMUnavailableException(
                    f"Unable to connect to Ollama. Make sure Ollama is running at {self.base_url}."
                )

            if attempt < self.max_retries:
                backoff = 1.0 * (2 ** attempt)
                await asyncio.sleep(backoff)

        if last_exception:
            raise last_exception
        raise LLMProviderException("Classification failed after retries.", error_code="AI_PROVIDER_ERROR")
