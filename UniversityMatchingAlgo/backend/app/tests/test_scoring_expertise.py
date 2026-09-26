from app.services.scoring.expertise import score_expertise


def test_full_match(sample_university):
    result = score_expertise(["Environmental Management"], sample_university)
    assert result["score"] == 1.0
    assert result["matched"] == ["Environmental Management"]


def test_partial_match(sample_university):
    result = score_expertise(["Environmental Management", "Public Health"], sample_university)
    assert result["score"] == 0.5
    assert result["matched"] == ["Environmental Management"]
    assert result["unmatched"] == ["Public Health"]


def test_no_match(sample_university):
    result = score_expertise(["Underwater Basket Weaving"], sample_university)
    assert result["score"] == 0.0
    assert result["matched"] == []


def test_no_required_expertise_scores_full(sample_university):
    result = score_expertise([], sample_university)
    assert result["score"] == 1.0
