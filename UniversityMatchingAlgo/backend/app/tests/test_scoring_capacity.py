from app.services.scoring.capacity import score_capacity


def make_university(active, maximum, availability):
    return {"capacity": {"activeProjects": active, "maximumProjects": maximum, "availability": availability}}


def test_available_partial_free_slots():
    result = score_capacity(make_university(6, 10, "AVAILABLE"))
    assert result["score"] == 0.4


def test_limited_halves_free_ratio():
    result = score_capacity(make_university(9, 10, "LIMITED"))
    assert result["score"] == 0.05


def test_unavailable_scores_zero():
    result = score_capacity(make_university(2, 10, "UNAVAILABLE"))
    assert result["score"] == 0.0


def test_zero_maximum_scores_zero():
    result = score_capacity(make_university(0, 0, "AVAILABLE"))
    assert result["score"] == 0.0


def test_active_exceeds_maximum_scores_zero():
    result = score_capacity(make_university(12, 10, "AVAILABLE"))
    assert result["score"] == 0.0


def test_invalid_availability_scores_zero():
    result = score_capacity(make_university(2, 10, "FOO"))
    assert result["score"] == 0.0


def test_full_availability_no_active_projects():
    result = score_capacity(make_university(0, 10, "AVAILABLE"))
    assert result["score"] == 1.0
