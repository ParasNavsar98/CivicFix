"""
Phase 2 — Embedding Service
Implementation Decision (not mandated by SRS):
Uses BAAI/bge-small-en-v1.5 via sentence-transformers yielding 384-dimensional normalized vectors.
"""

from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingError(Exception):
    """Base exception for embedding service operations."""
    pass


class InvalidEmbeddingInputError(EmbeddingError):
    """Raised when input text for embedding is empty, whitespace, or invalid."""
    pass


class EmbeddingModelError(EmbeddingError):
    """Raised when model loading or encoding fails."""
    pass


class EmbeddingService:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model: Optional[SentenceTransformer] = None
        self._dimension: int = 384

    def load_model(self) -> None:
        """Loads the SentenceTransformer model once if not already loaded."""
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name)
                # Verify dimension
                if hasattr(self._model, "get_embedding_dimension"):
                    self._dimension = self._model.get_embedding_dimension()
                elif hasattr(self._model, "get_sentence_embedding_dimension"):
                    self._dimension = self._model.get_sentence_embedding_dimension()
            except Exception as e:
                raise EmbeddingModelError(f"Failed to load embedding model '{self.model_name}': {str(e)}") from e

    @property
    def embedding_dimension(self) -> int:
        """Returns the vector dimension (384 for BGE-small)."""
        return self._dimension

    def embed(self, text: str) -> List[float]:
        """
        Generates a 384-dimensional normalized embedding vector for a single text.

        :param text: Non-empty string text to embed.
        :return: Normalized float vector of length 384.
        """
        if not text or not isinstance(text, str) or not text.strip():
            raise InvalidEmbeddingInputError("Embedding input text cannot be empty or whitespace-only.")

        self.load_model()
        try:
            vector = self._model.encode(text.strip(), normalize_embeddings=True)
            if isinstance(vector, np.ndarray):
                vector = vector.tolist()
            if len(vector) != self._dimension:
                raise EmbeddingError(f"Generated embedding dimension {len(vector)} does not match expected {self._dimension}.")
            return vector
        except Exception as e:
            if isinstance(e, (InvalidEmbeddingInputError, EmbeddingError)):
                raise
            raise EmbeddingModelError(f"Error generating embedding: {str(e)}") from e

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        """
        Generates 384-dimensional normalized embedding vectors for a list of texts efficiently in batch.

        :param texts: List of non-empty string texts.
        :return: List of normalized float vectors, each of length 384.
        """
        if not texts or not isinstance(texts, list):
            raise InvalidEmbeddingInputError("Batch embedding input must be a non-empty list of strings.")

        cleaned_texts = []
        for i, text in enumerate(texts):
            if not text or not isinstance(text, str) or not text.strip():
                raise InvalidEmbeddingInputError(f"Text at index {i} is empty or invalid.")
            cleaned_texts.append(text.strip())

        self.load_model()
        try:
            vectors = self._model.encode(cleaned_texts, normalize_embeddings=True)
            if isinstance(vectors, np.ndarray):
                vectors = vectors.tolist()
            for i, vec in enumerate(vectors):
                if len(vec) != self._dimension:
                    raise EmbeddingError(f"Vector at index {i} dimension {len(vec)} does not match expected {self._dimension}.")
            return vectors
        except Exception as e:
            if isinstance(e, (InvalidEmbeddingInputError, EmbeddingError)):
                raise
            raise EmbeddingModelError(f"Error generating batch embeddings: {str(e)}") from e
