"""
Pydantic v2 schemas for Problem submission and retrieval APIs.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class LocationSchema(BaseModel):
    lat: Optional[float] = Field(None, ge=-90.0, le=90.0)
    long: Optional[float] = Field(None, ge=-180.0, le=180.0)
    address: Optional[str] = Field(None, max_length=300)


class ProblemCreateRequest(BaseModel):
    problemId: Optional[str] = Field(None, description="Optional custom problem ID", max_length=100)
    title: str = Field(..., description="Problem title", min_length=3, max_length=300)
    description: str = Field(..., description="Detailed problem description", min_length=5, max_length=5000)
    location: Optional[LocationSchema] = Field(None, description="Geographic location details")
    privacyClass: Optional[str] = Field("PUBLIC", description="Privacy class: PUBLIC, INTERNAL, RESTRICTED, CONFIDENTIAL")

    @field_validator("title", "description", mode="before")
    @classmethod
    def trim_strings(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty or whitespace only.")
        return value


class ProblemResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]
    requestId: Optional[str] = None


class ProblemTimelineStep(BaseModel):
    step: str
    status: str
    timestamp: str
    summary: str


class ProblemTimelineResponse(BaseModel):
    problemId: str
    title: str
    currentStatus: str
    timeline: List[ProblemTimelineStep]
