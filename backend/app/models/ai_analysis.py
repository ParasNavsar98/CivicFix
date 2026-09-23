"""
AI Analysis Record Model for CivicFix Main Backend.
Stores raw AI classification execution outcomes and confidence metadata.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AIAnalysisRecord(BaseModel):
    analysisId: str = Field(..., description="Unique AI analysis execution ID")
    problemId: str = Field(..., description="Associated problem ID")
    provider: str = Field("ollama_gemma3_4b", description="AI provider name")
    model: str = Field("gemma3:4b", description="AI model name")

    confidence: float = Field(0.0, description="Overall AI classification confidence score (0.0 to 1.0)")
    structuredOutput: Dict[str, Any] = Field(default_factory=dict, description="Structured classification JSON output")
    status: str = Field("completed", description="Analysis status: completed, failed, review_required")

    errorCode: Optional[str] = Field(None, description="Machine readable error code if execution failed")
    errorMessage: Optional[str] = Field(None, description="Human readable error message if execution failed")

    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
