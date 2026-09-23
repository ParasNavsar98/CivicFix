"""
Common API schemas and response contracts.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorDetails(BaseModel):
    code: str = Field(..., description="Stable machine-readable error code")
    message: str = Field(..., description="Human readable explanation")


class StandardApiResponse(BaseModel):
    success: bool = Field(True, description="Indicates request success status")
    data: Optional[Any] = Field(None, description="Response payload data")
    error: Optional[ErrorDetails] = Field(None, description="Error details if success is False")
    requestId: Optional[str] = Field(None, description="Unique request tracing ID")
