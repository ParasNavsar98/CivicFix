"""
Phase 5 — Candidate Retriever
Implementation Decision (not mandated by SRS):
Provides lightweight local in-memory vector index for retrieving top-K semantic candidate problems.
Abstracted interface allows future integration with vector databases (e.g. MongoDB Atlas Vector Search, FAISS).
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np


class CandidateRetrieverError(Exception):
    """Base exception for candidate retriever operations."""
    pass


class CandidateRetriever:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._index: List[Dict[str, Any]] = []

    def clear(self) -> None:
        """Clears all stored candidate embeddings."""
        self._index.clear()

    def add_candidate(
        self, problem_id: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Adds a candidate problem with its precomputed embedding vector and optional metadata.

        :param problem_id: Unique string identifier for the problem.
        :param embedding: 384-dimensional normalized float vector.
        :param metadata: Dict containing structured problem fields (title, description, location, domain, etc.).
        """
        if not problem_id or not isinstance(problem_id, str):
            raise CandidateRetrieverError("problem_id must be a non-empty string.")
        if not embedding or not isinstance(embedding, list) or len(embedding) != self.dimension:
            raise CandidateRetrieverError(
                f"Embedding vector must be a list of length {self.dimension}, got length {len(embedding) if embedding else 0}."
            )

        vec_arr = np.asarray(embedding, dtype=np.float32)
        norm = np.linalg.norm(vec_arr)
        if norm > 0:
            vec_arr = vec_arr / norm  # Ensure normalization

        self._index.append({
            "problem_id": problem_id,
            "embedding": vec_arr,
            "metadata": metadata or {}
        })

    def search(
        self, query_embedding: List[float], top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieves Top-K candidate problems ordered by cosine similarity to the query embedding.

        :param query_embedding: 384-dimensional normalized query vector.
        :param top_k: Maximum number of candidates to return.
        :return: List of candidate records sorted by semantic similarity descending.
                 Each item: {"problem_id": str, "semantic_similarity": float, "metadata": dict}
        """
        if not query_embedding or not isinstance(query_embedding, list) or len(query_embedding) != self.dimension:
            raise CandidateRetrieverError(
                f"Query vector must be a list of length {self.dimension}, got length {len(query_embedding) if query_embedding else 0}."
            )

        if not self._index:
            return []

        q_vec = np.asarray(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        results = []
        for cand in self._index:
            c_vec = cand["embedding"]
            sim = float(np.dot(q_vec, c_vec))
            sim = float(np.clip(sim, -1.0, 1.0))
            results.append({
                "problem_id": cand["problem_id"],
                "semantic_similarity": round(sim, 6),
                "metadata": cand["metadata"],
            })

        # Sort descending by semantic similarity
        results.sort(key=lambda x: x["semantic_similarity"], reverse=True)
        return results[:top_k]
