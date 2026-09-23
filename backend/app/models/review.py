"""
Reviewer Action Record Model for CivicFix Main Backend.
SRS COMPLIANCE:
Tracks human reviewer decisions, actions, justification reasons, and timestamps.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ReviewerActionEnum(str, Enum):
    ACCEPT = "ACCEPT"
    CORRECT = "CORRECT"
    REQUEST_CLARIFICATION = "REQUEST_CLARIFICATION"
    MERGE_DUPLICATE = "MERGE_DUPLICATE"
    REJECT_INVALID = "REJECT_INVALID"
    REQUEST_VERIFICATION = "REQUEST_VERIFICATION"
    REDIRECT = "REDIRECT"
    ESCALATE = "ESCALATE"


class ReviewActionRecord(BaseModel):
    reviewId: str = Field(..., description="Unique review action ID")
    problemId: str = Field(..., description="Target problem ID")
    reviewerId: str = Field(..., description="User ID of authorized reviewer")

    action: ReviewerActionEnum = Field(..., description="Reviewer action type")
    reason: Optional[str] = Field(None, description="Human reviewer explanation / justification")

    masterProblemId: Optional[str] = Field(None, description="Master problem ID if action is MERGE_DUPLICATE")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Additional action parameters / modifications")

    previousState: str = Field(..., description="Problem state before action")
    newState: str = Field(..., description="Problem state after action")

    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
