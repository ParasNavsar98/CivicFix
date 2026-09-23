"""
Duplicate Candidate Repository Abstraction.
Stores surfaced duplicate candidates, individual signals, and confirmation status.
"""

from typing import Dict, List, Optional
from app.models.duplicate_candidate import DuplicateCandidateRecord


class DuplicateRepository:
    def __init__(self, db_client=None):
        self.db_client = db_client
        self._memory_store: Dict[str, DuplicateCandidateRecord] = {}

    async def save_candidate(self, record: DuplicateCandidateRecord) -> DuplicateCandidateRecord:
        """Saves or updates a duplicate candidate record."""
        self._memory_store[record.recordId] = record
        if self.db_client:
            try:
                doc = record.model_dump()
                await self.db_client.civicfix.duplicate_candidates.replace_one(
                    {"recordId": record.recordId}, doc, upsert=True
                )
            except Exception as e:
                print(f"MongoDB duplicate write notice: {e}")
        return record

    async def list_candidates_for_problem(self, problem_id: str) -> List[DuplicateCandidateRecord]:
        """Lists surfaced candidate records for a target problem."""
        all_records = list(self._memory_store.values())
        matching = [r for r in all_records if r.problemId == problem_id]
        matching.sort(key=lambda x: x.duplicateScore, reverse=True)
        return matching

    async def clear(self) -> None:
        """Clears memory storage (for testing)."""
        self._memory_store.clear()
