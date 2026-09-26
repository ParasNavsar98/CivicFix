from types import SimpleNamespace
from app.services.scoring.geography import score_geography


def test_same_district(sample_university):
    loc = SimpleNamespace(district="Ranchi", state="Jharkhand")
    result = score_geography(loc, sample_university)
    assert result["score"] == 1.0


def test_same_state_different_district(sample_university):
    loc = SimpleNamespace(district="Dhanbad", state="Jharkhand")
    result = score_geography(loc, sample_university)
    assert result["score"] == 0.6


def test_different_state(sample_university):
    loc = SimpleNamespace(district="Kolkata", state="West Bengal")
    result = score_geography(loc, sample_university)
    assert result["score"] == 0.2
