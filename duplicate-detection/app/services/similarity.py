"""
Phase 3 — Similarity Service
Implementation Decision (not mandated by SRS):
Calculates cosine similarity between 384-dimensional normalized vectors.
"""

from typing import List, Union
import numpy as np


class SimilarityError(Exception):
    """Base exception for similarity operations."""
    pass


class InvalidSimilarityInputError(SimilarityError):
    """Raised when input vectors are empty, None, or improperly formatted."""
    pass


class VectorDimensionMismatchError(SimilarityError):
    """Raised when comparing vectors of unequal dimensions."""
    pass


class SimilarityService:
    @staticmethod
    def _to_numpy(vector: Union[List[float], np.ndarray], name: str = "Vector") -> np.ndarray:
        if vector is None:
            raise InvalidSimilarityInputError(f"{name} cannot be None.")
        arr = np.asarray(vector, dtype=np.float32)
        if arr.ndim != 1 or arr.size == 0:
            raise InvalidSimilarityInputError(f"{name} must be a non-empty 1D array of float values.")
        return arr

    def cosine_similarity(self, vec_a: Union[List[float], np.ndarray], vec_b: Union[List[float], np.ndarray]) -> float:
        """
        Computes cosine similarity between two 1D float vectors.

        :param vec_a: First vector.
        :param vec_b: Second vector.
        :return: Cosine similarity score bounded in [-1.0, 1.0], rounded to 6 decimal places.
        """
        arr_a = self._to_numpy(vec_a, "vec_a")
        arr_b = self._to_numpy(vec_b, "vec_b")

        if arr_a.shape != arr_b.shape:
            raise VectorDimensionMismatchError(
                f"Dimension mismatch between vec_a ({arr_a.shape[0]}) and vec_b ({arr_b.shape[0]})."
            )

        norm_a = float(np.linalg.norm(arr_a))
        norm_b = float(np.linalg.norm(arr_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        dot_product = float(np.dot(arr_a, arr_b))
        sim = dot_product / (norm_a * norm_b)
        # Clip to ensure numerical stability within [-1.0, 1.0]
        sim = float(np.clip(sim, -1.0, 1.0))
        return round(sim, 6)

    def compare_one_to_many(
        self, query: Union[List[float], np.ndarray], candidates: List[Union[List[float], np.ndarray]]
    ) -> List[float]:
        """
        Computes cosine similarity between a single query vector and a list of candidate vectors.

        :param query: Query vector.
        :param candidates: List of candidate vectors.
        :return: List of similarity scores.
        """
        if candidates is None or not isinstance(candidates, list):
            raise InvalidSimilarityInputError("Candidates must be a list of vectors.")
        if len(candidates) == 0:
            return []

        arr_query = self._to_numpy(query, "query")
        scores = []
        for i, cand in enumerate(candidates):
            try:
                score = self.cosine_similarity(arr_query, cand)
                scores.append(score)
            except VectorDimensionMismatchError as e:
                raise VectorDimensionMismatchError(
                    f"Candidate vector at index {i} dimension mismatch: {str(e)}"
                ) from e
            except Exception as e:
                if isinstance(e, SimilarityError):
                    raise
                raise SimilarityError(f"Error computing similarity for candidate at index {i}: {str(e)}") from e

        return scores
