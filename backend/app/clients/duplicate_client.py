"""
Async HTTP Client Adapter for Duplicate Candidate Detection Engine microservice.
Queries duplicate-detection microservice (FastAPI + Sentence Transformers BGE-small) cleanly.
"""

from typing import Any, Dict, List, Optional
import httpx


class DuplicateClientError(Exception):
    """Raised when duplicate detection service request fails or times out."""
    pass


class DuplicateClient:
    def __init__(self, base_url: str = "http://localhost:8001", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def check_duplicates(
        self, problem_data: Dict[str, Any], candidates: List[Dict[str, Any]], top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Sends problem details and candidate pool to Duplicate Detection Engine.

        :param problem_data: Target problem dict.
        :param candidates: Candidate problems list.
        :param top_k: Top K results limit.
        :return: Dict response from duplicate detection engine.
        """
        url = f"{self.base_url}/duplicate-check"

        payload = {
            "problem": problem_data,
            "candidates": candidates,
            "topK": top_k
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise DuplicateClientError(
                        f"Duplicate detection service returned status {response.status_code}: {response.text}"
                    )
        except httpx.RequestError as e:
            raise DuplicateClientError(f"Duplicate detection service connection failed: {str(e)}") from e
