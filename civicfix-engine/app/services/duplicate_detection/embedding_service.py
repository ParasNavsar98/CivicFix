"""
Embedding Service for Dense Vector Generation.
Source: duplicate-detection/app/services/embedding.py
"""
import logging
from typing import List, Optional
import numpy as np
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """Base exception for embedding service failures."""
    pass


class InvalidEmbeddingInputError(EmbeddingError):
    """Raised when input text is invalid or empty."""
    pass


class EmbeddingModelError(EmbeddingError):
    """Raised when SentenceTransformer encounters a runtime model failure."""
    pass


class EmbeddingService:
    """Manages dense vector generation using BAAI/bge-small-en-v1.5."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = None

    def load_model(self):
        """Loads the SentenceTransformer model on demand or startup."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading embedding model: %s", self.model_name)
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.error("Failed to load embedding model '%s': %s", self.model_name, e)
                raise EmbeddingModelError(f"Failed to load model '{self.model_name}': {e}") from e
        return self._model

    def embed(self, text: str) -> np.ndarray:
        """Generates a 384-dimensional L2-normalized numpy float vector."""
        if not text or not text.strip():
            raise InvalidEmbeddingInputError("Input text for embedding cannot be empty.")

        model = self.load_model()
        try:
            vector = model.encode(text.strip(), normalize_embeddings=True)
            return np.array(vector, dtype=np.float32)
        except Exception as e:
            logger.error("Error encoding text for embedding: %s", e)
            raise EmbeddingModelError(f"Error encoding embedding: {e}") from e

    def embed_many(self, texts: List[str]) -> List[np.ndarray]:
        """Encodes multiple text strings in a single batch pass."""
        if not texts:
            return []

        model = self.load_model()
        try:
            cleaned_texts = [t.strip() if t and t.strip() else " " for t in texts]
            vectors = model.encode(cleaned_texts, normalize_embeddings=True)
            return [np.array(v, dtype=np.float32) for v in vectors]
        except Exception as e:
            logger.error("Error encoding batch embeddings: %s", e)
            raise EmbeddingModelError(f"Error in batch embedding: {e}") from e
