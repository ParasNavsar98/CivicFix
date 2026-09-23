"""
Unit tests for CandidateRetriever (Phase 5)
"""

import pytest
from app.services.candidate_retriever import CandidateRetriever, CandidateRetrieverError


@pytest.fixture
def retriever():
    return CandidateRetriever(dimension=4)  # Small dimension for fast testing


def test_add_and_search(retriever):
    retriever.add_candidate("P101", [1.0, 0.0, 0.0, 0.0], {"title": "Pothole"})
    retriever.add_candidate("P102", [0.0, 1.0, 0.0, 0.0], {"title": "Garbage"})
    retriever.add_candidate("P103", [0.707, 0.707, 0.0, 0.0], {"title": "Road waste"})

    query = [1.0, 0.0, 0.0, 0.0]
    results = retriever.search(query, top_k=2)

    assert len(results) == 2
    assert results[0]["problem_id"] == "P101"
    assert results[0]["semantic_similarity"] == 1.0
    assert results[1]["problem_id"] == "P103"
    assert results[1]["semantic_similarity"] > 0.6


def test_empty_retriever_returns_empty_list(retriever):
    assert retriever.search([1.0, 0.0, 0.0, 0.0]) == []


def test_invalid_dimension_raises_error(retriever):
    with pytest.raises(CandidateRetrieverError):
        retriever.add_candidate("P101", [1.0, 0.0])

    with pytest.raises(CandidateRetrieverError):
        retriever.search([1.0, 0.0])


def test_clear_index(retriever):
    retriever.add_candidate("P101", [1.0, 0.0, 0.0, 0.0])
    assert len(retriever.search([1.0, 0.0, 0.0, 0.0])) == 1
    retriever.clear()
    assert len(retriever.search([1.0, 0.0, 0.0, 0.0])) == 0
