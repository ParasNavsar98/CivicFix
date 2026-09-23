"""
Duplicate Candidate Record Model for CivicFix Main Backend.
SRS COMPLIANCE:
AI identifies duplicate candidates and supporting signals.
Reviewer explicitly confirms merge. AI NEVER merges automatically.
"""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field


class DuplicateCandidateRecord(BaseModel):
    recordId: str = Field(..., description="Unique record identifier")
    problemId: str = Field(..., description="Target problem ID checked for duplicates")
    candidateProblemId: str = Field(..., description="surfaced candidate problem ID")

    duplicateScore: float = Field(..., description="Composite duplicate score (0.0 to 1.0)")
    semanticSimilarity: float = Field(..., description="Text embedding similarity (0.0 to 1.0)")
    primaryDomainMatch: bool = Field(False, description="Primary domain match boolean")
    subcategoryMatch: bool = Field(False, description="Subcategory match boolean")
    secondaryDomainOverlap: float = Field(0.0, description="Secondary domain Jaccard overlap")

    locationDistanceKm: Optional[float] = Field(None, description="Geographic distance in km")
    locationScore: float = Field(0.0, description="Location proximity score")

    thresholdUsed: float = Field(0.75, description="Duplicate threshold active during check")
    status: str = Field("candidate", description="Status: candidate, confirmed_duplicate, dismissed")
    reasons: List[str] = Field(default_factory=list, description="Human readable explainability reasons list")

    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
