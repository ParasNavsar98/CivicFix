"""
Problem Repository Abstraction supporting MongoDB and Isolated Storage.
SRS COMPLIANCE:
Main backend owns problem operational data and version references.
"""

from typing import Dict, List, Optional
from app.models.problem import Problem


class ProblemRepository:
    def __init__(self, db_client=None):
        self.db_client = db_client
        self._memory_store: Dict[str, Problem] = {}

    async def save(self, problem: Problem) -> Problem:
        """Saves or updates a canonical problem record."""
        self._memory_store[problem.problemId] = problem
        if self.db_client:
            try:
                doc = problem.model_dump()
                await self.db_client.civicfix.problems.replace_one(
                    {"problemId": problem.problemId}, doc, upsert=True
                )
            except Exception as e:
                print(f"MongoDB write notice: {e}")
        return problem

    async def get_by_id(self, problem_id: str) -> Optional[Problem]:
        """Retrieves a problem by ID."""
        if self.db_client:
            try:
                doc = await self.db_client.civicfix.problems.find_one({"problemId": problem_id})
                if doc:
                    doc.pop("_id", None)
                    return Problem(**doc)
            except Exception as e:
                print(f"MongoDB read notice: {e}")
        return self._memory_store.get(problem_id)

    async def list_all(self, limit: int = 100) -> List[Problem]:
        """Lists all stored problems."""
        if self.db_client:
            try:
                cursor = self.db_client.civicfix.problems.find({}, {"_id": 0}).limit(limit)
                docs = await cursor.to_list(length=limit)
                return [Problem(**doc) for doc in docs]
            except Exception as e:
                print(f"MongoDB query notice: {e}")
        return list(self._memory_store.values())[:limit]

    async def list_by_status(self, status: str, limit: int = 100) -> List[Problem]:
        """Lists problems matching a specific workflow status."""
        all_problems = await self.list_all(limit=limit * 2)
        return [p for p in all_problems if p.status == status][:limit]

    async def list_reviewer_queue(self, limit: int = 100) -> List[Problem]:
        """Surfaces problems flagged for human reviewer attention."""
        all_problems = await self.list_all(limit=limit * 2)
        return [
            p for p in all_problems
            if p.reviewRequired or p.status in ("REVIEW_REQUIRED", "AI_PENDING")
        ][:limit]

    async def clear(self) -> None:
        """Clears memory storage (for testing)."""
        self._memory_store.clear()
