"""
Pydantic v2 schemas for Reviewer API endpoints.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.review import ReviewerActionEnum


class ReviewerActionRequest(BaseModel):
    action: ReviewerActionEnum = Field(..., description="Reviewer action to perform")
    reason: Optional[str] = Field(None, description="Human explanation / justification for action")
    masterProblemId: Optional[str] = Field(None, description="Target master problem ID if action is MERGE_DUPLICATE")
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Modification payload for CORRECT or REDIRECT")


class ReviewerQueueResponse(BaseModel):
    success: bool = True
    count: int
    queue: List[Dict[str, Any]]
