from app.services.scoring.past_projects import score_past_projects


def test_domain_overlap_counts_as_relevant(sample_university):
    result = score_past_projects(
        "Environment", ["Healthcare"], "Pollution",
        ["Environmental Management", "Public Health"], sample_university,
    )
    assert result["score"] == 0.5  # 1 matched project / divisor 2
    assert len(result["matched_projects"]) == 1


def test_no_past_projects_scores_zero(sample_university):
    sample_university["pastProjects"] = []
    result = score_past_projects("Environment", [], "Pollution", [], sample_university)
    assert result["score"] == 0.0


def test_two_or_more_matches_caps_at_one(sample_university):
    sample_university["pastProjects"].append(
        {"title": "Second Project", "domains": ["Environment"], "expertise": []}
    )
    result = score_past_projects(
        "Environment", [], "Pollution", [], sample_university,
    )
    assert result["score"] == 1.0
