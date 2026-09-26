"""
University scoring unit tests (migrated from UniversityMatchingAlgo).
All import paths updated to civicfix-engine's internal paths.
"""
import pytest
from types import SimpleNamespace

from app.services.university_matching.scoring.expertise import score_expertise
from app.services.university_matching.scoring.faculty import score_faculty
from app.services.university_matching.scoring.capacity import score_capacity
from app.services.university_matching.scoring.geography import score_geography
from app.services.university_matching.scoring.infrastructure import score_infrastructure
from app.services.university_matching.scoring.industry_ecosystem import score_industry_ecosystem
from app.services.university_matching.scoring.past_projects import score_past_projects


# ── Expertise ─────────────────────────────────────────────────────────────────

def test_expertise_full_match(sample_university):
    result = score_expertise(["Environmental Management"], sample_university)
    assert result["score"] == 1.0
    assert result["matched"] == ["Environmental Management"]


def test_expertise_partial_match(sample_university):
    result = score_expertise(["Environmental Management", "Public Health"], sample_university)
    assert result["score"] == 0.5
    assert result["matched"] == ["Environmental Management"]
    assert result["unmatched"] == ["Public Health"]


def test_expertise_no_match(sample_university):
    result = score_expertise(["Underwater Basket Weaving"], sample_university)
    assert result["score"] == 0.0
    assert result["matched"] == []


def test_expertise_no_required_expertise_scores_full(sample_university):
    result = score_expertise([], sample_university)
    assert result["score"] == 1.0


# ── Capacity ──────────────────────────────────────────────────────────────────

def make_university(active, maximum, availability):
    return {"capacity": {"activeProjects": active, "maximumProjects": maximum, "availability": availability}}


def test_capacity_available_partial_free_slots():
    result = score_capacity(make_university(6, 10, "AVAILABLE"))
    assert result["score"] == 0.4


def test_capacity_limited_halves_free_ratio():
    result = score_capacity(make_university(9, 10, "LIMITED"))
    assert result["score"] == 0.05


def test_capacity_unavailable_scores_zero():
    result = score_capacity(make_university(2, 10, "UNAVAILABLE"))
    assert result["score"] == 0.0


def test_capacity_zero_maximum_scores_zero():
    result = score_capacity(make_university(0, 0, "AVAILABLE"))
    assert result["score"] == 0.0


def test_capacity_active_exceeds_maximum_scores_zero():
    result = score_capacity(make_university(12, 10, "AVAILABLE"))
    assert result["score"] == 0.0


def test_capacity_invalid_availability_scores_zero():
    result = score_capacity(make_university(2, 10, "FOO"))
    assert result["score"] == 0.0


def test_capacity_full_no_active_projects():
    result = score_capacity(make_university(0, 10, "AVAILABLE"))
    assert result["score"] == 1.0


# ── Geography ─────────────────────────────────────────────────────────────────

def test_geography_same_district(sample_university):
    loc = SimpleNamespace(district="Ranchi", state="Jharkhand")
    result = score_geography(loc, sample_university)
    assert result["score"] == 1.0


def test_geography_same_state_different_district(sample_university):
    loc = SimpleNamespace(district="Dhanbad", state="Jharkhand")
    result = score_geography(loc, sample_university)
    assert result["score"] == 0.6


def test_geography_different_state(sample_university):
    loc = SimpleNamespace(district="Kolkata", state="West Bengal")
    result = score_geography(loc, sample_university)
    assert result["score"] == 0.2


# ── Infrastructure ────────────────────────────────────────────────────────────

def test_infrastructure_no_required_scores_full(sample_university):
    result = score_infrastructure([], sample_university)
    assert result["score"] == 1.0


def test_infrastructure_no_match(sample_university):
    result = score_infrastructure(["Quantum Lab"], sample_university)
    assert result["score"] == 0.0


# ── Industry Ecosystem ────────────────────────────────────────────────────────

def test_industry_ecosystem_match(sample_university):
    result = score_industry_ecosystem("environment", sample_university)
    assert result["score"] == 1.0


def test_industry_ecosystem_no_relationships():
    uni = dict(industryRelationships=[])
    result = score_industry_ecosystem("environment", uni)
    assert result["score"] == 0.0


# ── Past Projects ─────────────────────────────────────────────────────────────

def test_past_projects_relevant_match(sample_university, sample_problem):
    result = score_past_projects(
        sample_problem.primary_domain,
        sample_problem.secondary_domains,
        sample_problem.subcategory,
        sample_problem.required_expertise,
        sample_university,
    )
    assert result["score"] > 0.0
    assert len(result["matched_projects"]) >= 1


def test_past_projects_no_projects():
    uni = {"pastProjects": []}
    result = score_past_projects("Environment", [], "Pollution", ["Env Mgmt"], uni)
    assert result["score"] == 0.0
