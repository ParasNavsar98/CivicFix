from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMProviderException(Exception):
    """Base exception for LLM provider errors."""
    def __init__(self, message: str, error_code: str = "AI_PROVIDER_ERROR"):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class LLMTimeoutException(LLMProviderException):
    """Exception raised when LLM provider call times out."""
    def __init__(self, message: str = "LLM provider call timed out."):
        super().__init__(message, error_code="AI_PROVIDER_TIMEOUT")


class LLMUnavailableException(LLMProviderException):
    """Exception raised when LLM provider is unavailable or rate limited."""
    def __init__(self, message: str = "LLM provider is unavailable."):
        super().__init__(message, error_code="AI_PROVIDER_UNAVAILABLE")


class LLMProvider(ABC):
    """Abstract interface for LLM classification providers."""

    @abstractmethod
    async def classify(
        self,
        prompt: str,
        response_schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Asynchronously send prompt to the LLM and return raw string response (structured JSON expected)."""
        pass
