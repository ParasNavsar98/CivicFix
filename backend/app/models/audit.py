"""
Audit Event Model for CivicFix Main Backend.
SRS COMPLIANCE:
Append-only audit trail capturing all critical system and human state-changing operations.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    eventId: str = Field(..., description="Unique audit event ID")
    entityType: str = Field(..., description="Entity type: problem, version, review, duplicate, routing")
    entityId: str = Field(..., description="Target entity ID")

    actorId: str = Field(..., description="ID of user or system service performing action")
    actorRole: str = Field(..., description="Role: citizen, reviewer, government_official, system, admin")
    action: str = Field(..., description="Standardized action event name")

    previousState: Optional[str] = Field(None, description="Previous state if applicable")
    newState: Optional[str] = Field(None, description="New state after action")

    metadata: Dict[str, Any] = Field(default_factory=dict, description="Contextual payload details")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
