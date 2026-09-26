"""
Scoring sub-package for University Matching.
All 7 deterministic scoring factors.
"""
from app.services.university_matching.scoring.expertise import score_expertise
from app.services.university_matching.scoring.faculty import score_faculty
from app.services.university_matching.scoring.capacity import score_capacity
from app.services.university_matching.scoring.past_projects import score_past_projects, DEFAULT_DIVISOR
from app.services.university_matching.scoring.infrastructure import score_infrastructure
from app.services.university_matching.scoring.industry_ecosystem import score_industry_ecosystem
from app.services.university_matching.scoring.geography import score_geography

__all__ = [
    "score_expertise",
    "score_faculty",
    "score_capacity",
    "score_past_projects",
    "DEFAULT_DIVISOR",
    "score_infrastructure",
    "score_industry_ecosystem",
    "score_geography",
]
