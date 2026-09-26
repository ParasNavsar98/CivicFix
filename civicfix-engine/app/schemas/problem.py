"""
Canonical Problem Model Schema for civicfix-engine.
Source: backend/app/models/problem.py
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import ProblemLocation


class Problem(BaseModel):
    problemId: str = Field(..., description="Unique problem identifier")
    submitterId: str = Field("citizen_dev", description="User ID of citizen submitter")
    title: str = Field(..., description="Problem title")
    description: str = Field(..., description="Detailed problem description")

    location: Optional[ProblemLocation] = Field(None, description="Geographic location")
    primaryDomain: Optional[str] = Field(None, description="Primary domain from taxonomy")
    secondaryDomains: List[str] = Field(default_factory=list, description="Secondary domains list")
    subcategory: Optional[str] = Field(None, description="Subcategory from taxonomy")

    status: str = Field("SUBMITTED", description="Workflow status: SUBMITTED, CLASSIFIED, IN_REVIEW, ROUTED, ASSIGNED, RESOLVED, REJECTED")
    severity: Optional[str] = Field(None, description="Severity: LOW, MEDIUM, HIGH, CRITICAL")
    urgency: Optional[str] = Field(None, description="Urgency: LOW, MEDIUM, HIGH, CRITICAL")

    mediaRefs: List[str] = Field(default_factory=list)
    governmentCaseRef: Optional[str] = None
    universityMatches: List[Dict[str, Any]] = Field(default_factory=list)
    projectRef: Optional[str] = None

    publicSummary: Optional[str] = None
    privacyClass: str = Field("PUBLIC")

    # Workflow & Integration Metadata
    processingState: str = Field("pending", description="AI processing status: pending, processing, completed, failed")
    classificationState: str = Field("pending", description="Classification state: pending, completed, review_required, failed")
    duplicateDetectionState: str = Field("pending", description="Duplicate detection state: pending, completed, failed")

    reviewRequired: bool = Field(False)
    reviewReasons: List[str] = Field(default_factory=list)

    masterProblemId: Optional[str] = None
    duplicateStatus: Optional[str] = Field(None, description="Duplicate status: none, potential_duplicate, merged")

    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
