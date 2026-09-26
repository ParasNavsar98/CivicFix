from app.services.scoring.infrastructure import score_infrastructure


def test_full_match(sample_university):
    result = score_infrastructure(["Environmental Laboratory", "IoT Monitoring"], sample_university)
    assert result["score"] == 1.0


def test_partial_match(sample_university):
    result = score_infrastructure(["Environmental Laboratory", "Waste collection"], sample_university)
    assert result["score"] == 0.5


def test_no_match(sample_university):
    result = score_infrastructure(["Waste collection", "Waste disposal infrastructure"], sample_university)
    assert result["score"] == 0.0


def test_no_required_resources_scores_full(sample_university):
    result = score_infrastructure([], sample_university)
    assert result["score"] == 1.0
