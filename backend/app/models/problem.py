"""
Canonical Problem Model for CivicFix Main Backend.
SRS COMPLIANCE:
Main backend owns operational problem records, workflow states, and relationship references.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProblemLocation(BaseModel):
    lat: Optional[float] = Field(None, description="Latitude (-90 to 90)")
    long: Optional[float] = Field(None, description="Longitude (-180 to 180)")
    address: Optional[str] = Field(None, description="Human readable address description")


class Problem(BaseModel):
    problemId: str = Field(..., description="Unique problem identifier")
    submitterId: str = Field(..., description="User ID of citizen submitter")
    title: str = Field(..., description="Problem title")
    description: str = Field(..., description="Detailed problem description")

    location: Optional[ProblemLocation] = Field(None, description="Problem geographic location")
    primaryDomain: Optional[str] = Field(None, description="Primary domain from taxonomy")
    secondaryDomains: List[str] = Field(default_factory=list, description="Secondary domains list")
    subcategory: Optional[str] = Field(None, description="Subcategory from taxonomy")

    status: str = Field("SUBMITTED", description="Workflow state machine status")
    severity: Optional[str] = Field(None, description="Severity level: LOW, MEDIUM, HIGH, CRITICAL")
    urgency: Optional[str] = Field(None, description="Urgency level: LOW, MEDIUM, HIGH, CRITICAL")

    mediaRefs: List[str] = Field(default_factory=list, description="Associated media references")
    governmentCaseRef: Optional[str] = Field(None, description="External government case reference")
    universityMatches: List[Dict[str, Any]] = Field(default_factory=list, description="Matched university capabilities")
    projectRef: Optional[str] = Field(None, description="Associated execution project ID")

    publicSummary: Optional[str] = Field(None, description="Anonymized/sanitized summary for public view")
    privacyClass: str = Field("PUBLIC", description="Privacy classification: PUBLIC, INTERNAL, RESTRICTED, CONFIDENTIAL")

    # Workflow & Integration Metadata
    processingState: str = Field("pending", description="AI processing status: pending, processing, completed, failed")
    classificationState: str = Field("pending", description="Classification state: pending, completed, review_required, failed")
    duplicateDetectionState: str = Field("pending", description="Duplicate detection state: pending, completed, failed")

    reviewRequired: bool = Field(False, description="Whether human reviewer intervention is required")
    reviewReasons: List[str] = Field(default_factory=list, description="Reasons for routing to reviewer queue")

    masterProblemId: Optional[str] = Field(None, description="ID of master problem if merged as duplicate")
    duplicateStatus: Optional[str] = Field(None, description="Duplicate status: none, potential_duplicate, merged")
    currentProblemVersionId: Optional[str] = Field(None, description="Active problem version ID")

    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
