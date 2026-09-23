"""
Async HTTP Client Adapter for Classification Engine microservice.
Queries classification-engine microservice (FastAPI + Gemma 3 4B) cleanly without duplicating internal logic.
"""

from typing import Any, Dict, Optional
import httpx


class ClassificationClientError(Exception):
    """Raised when classification service request fails or times out."""
    pass


class ClassificationClient:
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def classify_problem(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends problem details to Classification Engine and returns structured classification result.

        :param problem_data: Dict with problemId, title, description, location (district, state, lat, long).
        :return: Dict response from classification engine.
        """
        url = f"{self.base_url}/classify"

        # Format input expected by Classification Engine
        loc = problem_data.get("location") or {}
        payload = {
            "problemId": problem_data.get("problemId") or "P000",
            "title": problem_data.get("title", ""),
            "description": problem_data.get("description", ""),
            "location": {
                "district": loc.get("district") or loc.get("address") or "General District",
                "state": loc.get("state") or "General State",
                "latitude": loc.get("lat") or loc.get("latitude"),
                "longitude": loc.get("long") or loc.get("longitude"),
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise ClassificationClientError(
                        f"Classification service returned status {response.status_code}: {response.text}"
                    )
        except httpx.RequestError as e:
            raise ClassificationClientError(f"Classification service connection failed: {str(e)}") from e
