"""
Audit Trail Service for CivicFix Main Backend.
SRS COMPLIANCE:
Creates append-only audit events for all critical system and human state-changing operations.
"""

import uuid
from typing import Any, Dict, List, Optional
from app.models.audit import AuditEvent
from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, audit_repository: AuditRepository):
        self.repo = audit_repository

    async def log_event(
        self,
        entity_type: str,
        entity_id: str,
        actor_id: str,
        actor_role: str,
        action: str,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Appends a new audit event."""
        event_id = f"AUD-{uuid.uuid4().hex[:10].upper()}"
        event = AuditEvent(
            eventId=event_id,
            entityType=entity_type,
            entityId=entity_id,
            actorId=actor_id,
            actorRole=actor_role,
            action=action,
            previousState=previous_state,
            newState=new_state,
            metadata=metadata or {},
        )
        return await self.repo.log_event(event)

    async def get_trail(self, entity_id: str) -> List[AuditEvent]:
        """Retrieves chronological audit trail for an entity."""
        return await self.repo.list_events_for_entity(entity_id)
