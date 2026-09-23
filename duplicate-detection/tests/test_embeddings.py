"""
Unit tests for EmbeddingService (Phase 2)
"""

import math
import pytest
from app.services.embedding import EmbeddingService, InvalidEmbeddingInputError


@pytest.fixture(scope="module")
def embedding_service():
    service = EmbeddingService(model_name="BAAI/bge-small-en-v1.5")
    service.load_model()
    return service


def test_model_loads_and_dimension(embedding_service):
    assert embedding_service.embedding_dimension == 384
    assert embedding_service._model is not None


def test_single_embedding_dimension_and_normalization(embedding_service):
    text = "Garbage burning near school"
    vector = embedding_service.embed(text)
    assert isinstance(vector, list)
    assert len(vector) == 384

    # Verify L2 normalization (sum of squares ≈ 1.0)
    l2_norm = math.sqrt(sum(v ** 2 for v in vector))
    assert math.isclose(l2_norm, 1.0, abs_tol=1e-4)


def test_deterministic_embedding(embedding_service):
    text = "Water pipeline leak in Sector 4"
    v1 = embedding_service.embed(text)
    v2 = embedding_service.embed(text)
    assert v1 == v2


def test_batch_embedding(embedding_service):
    texts = [
        "Pothole on main road causing accidents",
        "Streetlight failure in residential block",
        "Hospital medicine shortage reported"
    ]
    vectors = embedding_service.embed_many(texts)
    assert isinstance(vectors, list)
    assert len(vectors) == 3
    for vec in vectors:
        assert len(vec) == 384
        l2_norm = math.sqrt(sum(v ** 2 for v in vec))
        assert math.isclose(l2_norm, 1.0, abs_tol=1e-4)


def test_invalid_input_handling(embedding_service):
    with pytest.raises(InvalidEmbeddingInputError):
        embedding_service.embed("")

    with pytest.raises(InvalidEmbeddingInputError):
        embedding_service.embed("   ")

    with pytest.raises(InvalidEmbeddingInputError):
        embedding_service.embed(None)

    with pytest.raises(InvalidEmbeddingInputError):
        embedding_service.embed_many([])

    with pytest.raises(InvalidEmbeddingInputError):
        embedding_service.embed_many(["Valid text", "   ", "Another valid"])
