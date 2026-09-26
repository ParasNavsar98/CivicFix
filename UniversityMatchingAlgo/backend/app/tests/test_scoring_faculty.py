from app.services.scoring.faculty import score_faculty


def test_matching_faculty(sample_university):
    result = score_faculty(["Environmental Management", "Public Health"], sample_university)
    assert result["score"] == 0.5
    assert result["matched_faculty"] == ["FAC-001"]
    assert "Public Health" in result["uncovered_expertise"]


def test_no_available_faculty(sample_university):
    sample_university["faculty"][0]["availableForProjects"] = False
    result = score_faculty(["Environmental Management"], sample_university)
    assert result["score"] == 0.0
    assert result["matched_faculty"] == []


def test_no_required_expertise_scores_full(sample_university):
    result = score_faculty([], sample_university)
    assert result["score"] == 1.0
