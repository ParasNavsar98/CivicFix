"""
Unit tests for SimilarityService (Phase 3)
"""

import pytest
from app.services.similarity import (
    SimilarityService,
    InvalidSimilarityInputError,
    VectorDimensionMismatchError,
)


@pytest.fixture
def similarity_service():
    return SimilarityService()


def test_identical_vectors(similarity_service):
    v = [1.0, 2.0, 3.0, 4.0]
    score = similarity_service.cosine_similarity(v, v)
    assert pytest.approx(score, abs=1e-5) == 1.0


def test_orthogonal_vectors(similarity_service):
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    score = similarity_service.cosine_similarity(v1, v2)
    assert pytest.approx(score, abs=1e-5) == 0.0


def test_opposite_vectors(similarity_service):
    v1 = [1.0, 2.0, 3.0]
    v2 = [-1.0, -2.0, -3.0]
    score = similarity_service.cosine_similarity(v1, v2)
    assert pytest.approx(score, abs=1e-5) == -1.0


def test_zero_vector_handling(similarity_service):
    v1 = [1.0, 2.0, 3.0]
    v_zero = [0.0, 0.0, 0.0]
    score = similarity_service.cosine_similarity(v1, v_zero)
    assert score == 0.0


def test_dimension_mismatch(similarity_service):
    v1 = [1.0, 2.0, 3.0]
    v2 = [1.0, 2.0]
    with pytest.raises(VectorDimensionMismatchError):
        similarity_service.cosine_similarity(v1, v2)


def test_invalid_vector_inputs(similarity_service):
    with pytest.raises(InvalidSimilarityInputError):
        similarity_service.cosine_similarity(None, [1.0, 2.0])

    with pytest.raises(InvalidSimilarityInputError):
        similarity_service.cosine_similarity([], [1.0, 2.0])

    with pytest.raises(InvalidSimilarityInputError):
        similarity_service.cosine_similarity([[1.0]], [1.0])


def test_compare_one_to_many(similarity_service):
    query = [1.0, 0.0, 0.0]
    candidates = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.5, 0.5, 0.0],
    ]
    scores = similarity_service.compare_one_to_many(query, candidates)
    assert len(scores) == 3
    assert pytest.approx(scores[0], abs=1e-4) == 1.0
    assert pytest.approx(scores[1], abs=1e-4) == 0.0
    assert scores[2] > 0.0


def test_compare_one_to_many_empty(similarity_service):
    query = [1.0, 0.0, 0.0]
    assert similarity_service.compare_one_to_many(query, []) == []
