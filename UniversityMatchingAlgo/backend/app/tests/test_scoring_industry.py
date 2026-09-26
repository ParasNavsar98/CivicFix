from app.services.scoring.industry_ecosystem import score_industry_ecosystem


def test_relevant_relationship_scores_full(sample_university):
    result = score_industry_ecosystem("Environment", sample_university)
    assert result["score"] == 1.0
    assert result["matched_relationships"] == ["Environmental Technology Companies"]


def test_no_relationships_scores_zero(sample_university):
    sample_university["industryRelationships"] = []
    result = score_industry_ecosystem("Environment", sample_university)
    assert result["score"] == 0.0


def test_unrelated_relationships_scores_baseline():
    university = {"industryRelationships": ["Some Random Corp"]}
    result = score_industry_ecosystem("Environment", university)
    assert result["score"] == 0.3
