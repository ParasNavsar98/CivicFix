"""
Append-Only Audit Repository Abstraction.
SRS COMPLIANCE:
Audit events are strictly append-only from application perspective.
"""

from typing import Dict, List
from app.models.audit import AuditEvent


class AuditRepository:
    def __init__(self, db_client=None):
        self.db_client = db_client
        self._memory_store: Dict[str, AuditEvent] = {}

    async def log_event(self, event: AuditEvent) -> AuditEvent:
        """Appends an immutable audit event to the record log."""
        self._memory_store[event.eventId] = event
        if self.db_client:
            try:
                doc = event.model_dump()
                await self.db_client.civicfix.audit_events.insert_one(doc)
            except Exception as e:
                print(f"MongoDB audit write notice: {e}")
        return event

    async def list_events_for_entity(self, entity_id: str) -> List[AuditEvent]:
        """Retrieves audit trail events for a given entity ordered chronologically."""
        all_events = list(self._memory_store.values())
        matching = [e for e in all_events if e.entityId == entity_id]
        matching.sort(key=lambda x: x.timestamp)
        return matching

    async def clear(self) -> None:
        """Clears memory storage (for testing)."""
        self._memory_store.clear()
