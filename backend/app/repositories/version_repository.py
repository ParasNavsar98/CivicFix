"""
Problem Version Repository Abstraction.
Preserves historical AI and reviewer problem versions.
"""

from typing import Dict, List, Optional
from app.models.version import ProblemVersion


class VersionRepository:
    def __init__(self, db_client=None):
        self.db_client = db_client
        self._memory_store: Dict[str, ProblemVersion] = {}

    async def save_version(self, version: ProblemVersion) -> ProblemVersion:
        """Saves an immutable problem version snapshot."""
        self._memory_store[version.versionId] = version
        if self.db_client:
            try:
                doc = version.model_dump()
                await self.db_client.civicfix.problem_versions.replace_one(
                    {"versionId": version.versionId}, doc, upsert=True
                )
            except Exception as e:
                print(f"MongoDB version write notice: {e}")
        return version

    async def get_version(self, version_id: str) -> Optional[ProblemVersion]:
        """Gets a version snapshot by ID."""
        if self.db_client:
            try:
                doc = await self.db_client.civicfix.problem_versions.find_one({"versionId": version_id})
                if doc:
                    doc.pop("_id", None)
                    return ProblemVersion(**doc)
            except Exception as e:
                print(f"MongoDB version read notice: {e}")
        return self._memory_store.get(version_id)

    async def list_versions_for_problem(self, problem_id: str) -> List[ProblemVersion]:
        """Lists all historical versions for a given problem ordered by creation."""
        all_versions = list(self._memory_store.values())
        matching = [v for v in all_versions if v.problemId == problem_id]
        matching.sort(key=lambda x: x.createdAt)
        return matching

    async def clear(self) -> None:
        """Clears memory storage (for testing)."""
        self._memory_store.clear()
