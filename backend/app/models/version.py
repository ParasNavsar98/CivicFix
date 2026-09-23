"""
Problem Version Model for CivicFix Main Backend.
SRS COMPLIANCE:
All AI-generated and human-corrected interpretations are versioned.
Reviewer corrections create new versions without overwriting historical AI interpretations.
"""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field


class ProblemVersion(BaseModel):
    versionId: str = Field(..., description="Unique version identifier")
    problemId: str = Field(..., description="Associated problem ID")
    source: str = Field(..., description="Interpretation origin: ai, reviewer, system")

    title: str = Field(..., description="Problem title snapshot")
    description: str = Field(..., description="Problem description snapshot")

    primaryDomain: Optional[str] = Field(None, description="Primary domain snapshot")
    secondaryDomains: List[str] = Field(default_factory=list, description="Secondary domains list snapshot")
    subcategory: Optional[str] = Field(None, description="Subcategory snapshot")

    severity: Optional[str] = Field(None, description="Severity level snapshot")
    urgency: Optional[str] = Field(None, description="Urgency level snapshot")

    researchRequired: Optional[bool] = Field(None, description="Whether research or innovation is required")
    governmentActionPossible: Optional[bool] = Field(None, description="Whether government action is possible")

    requiredExpertise: List[str] = Field(default_factory=list, description="Expertise requirements snapshot")
    requiredResources: List[str] = Field(default_factory=list, description="Resource requirements snapshot")

    publicSummary: Optional[str] = Field(None, description="Public summary snapshot")
    reasoning: Optional[str] = Field(None, description="Reasoning or justification for this version")

    createdBy: str = Field(..., description="User ID or Service Name creating this version")
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    changeReason: Optional[str] = Field(None, description="Explanation for version change")
