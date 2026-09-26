"""
Pydantic Schemas for University Capability Matching & Assignments.
Source: UniversityMatchingAlgo/backend/app/schemas/
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    problem_id: str
    primary_domain: str
    subcategory: str
    secondary_domains: List[str] = Field(default_factory=list)
    required_expertise: List[str] = Field(default_factory=list)
    required_resources: List[str] = Field(default_factory=list)
    location: Dict[str, Any]  # {"district": str, "state": str, ...}
    limit: int = Field(default=5, ge=1, le=20)


class FactorBreakdown(BaseModel):
    raw: float
    weight: float
    weighted: float
    reason: str


class ScoreBreakdownSchema(BaseModel):
    expertise: FactorBreakdown
    faculty: FactorBreakdown
    capacity: FactorBreakdown
    past_projects: FactorBreakdown
    infrastructure: FactorBreakdown
    industry_ecosystem: FactorBreakdown
    geography: FactorBreakdown


class RankedUniversityMatch(BaseModel):
    rank: int
    university_id: str
    name: str
    tier: str
    score: float
    score_breakdown: ScoreBreakdownSchema
    summary: str


class MatchResponse(BaseModel):
    problem_id: str
    eligible: bool = True
    gate_reason: str = "OK"
    matches: List[RankedUniversityMatch] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AssignmentStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class CreateAssignmentRequest(BaseModel):
    problem_id: str
    chain_limit: int = 5


class AssignmentResponse(BaseModel):
    assignment_id: str
    problem_id: str
    university_id: str
    university_name: str
    chain_position: int
    status: AssignmentStatus
    sent_at: Optional[str] = None
    deadline: str
    rejection_reason: Optional[str] = None
    created_at: str


class AssignmentResponseAction(BaseModel):
    action: str = Field(..., description="ACCEPTED or REJECTED")
    rejection_reason: Optional[str] = None
