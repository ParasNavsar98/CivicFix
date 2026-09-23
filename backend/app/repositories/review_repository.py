"""
Review Action Repository Abstraction.
Stores all human reviewer decisions, actions, and payload details.
"""

from typing import Dict, List, Optional
from app.models.review import ReviewActionRecord


class ReviewRepository:
    def __init__(self, db_client=None):
        self.db_client = db_client
        self._memory_store: Dict[str, ReviewActionRecord] = {}

    async def save_review(self, record: ReviewActionRecord) -> ReviewActionRecord:
        """Saves a reviewer action record."""
        self._memory_store[record.reviewId] = record
        if self.db_client:
            try:
                doc = record.model_dump()
                await self.db_client.civicfix.reviews.replace_one(
                    {"reviewId": record.reviewId}, doc, upsert=True
                )
            except Exception as e:
                print(f"MongoDB review write notice: {e}")
        return record

    async def list_reviews_for_problem(self, problem_id: str) -> List[ReviewActionRecord]:
        """Lists review actions for a problem ordered chronologically."""
        all_reviews = list(self._memory_store.values())
        matching = [r for r in all_reviews if r.problemId == problem_id]
        matching.sort(key=lambda x: x.createdAt)
        return matching

    async def clear(self) -> None:
        """Clears memory storage (for testing)."""
        self._memory_store.clear()
