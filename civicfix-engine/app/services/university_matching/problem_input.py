"""
ProblemInput is the internal, stable representation of a problem used by
every university scoring factor and the matching engine.
Source: UniversityMatchingAlgo/backend/app/models/problem_input.py
"""
from dataclasses import dataclass, field


@dataclass
class ProblemLocation:
    district: str
    state: str
    latitude: float | None = None
    longitude: float | None = None


@dataclass
class ProblemInput:
    problem_id: str
    primary_domain: str
    subcategory: str
    required_expertise: list[str]
    required_resources: list[str]
    location: ProblemLocation
    secondary_domains: list[str] = field(default_factory=list)

    # Gating flags only — NEVER used inside the scoring formula itself.
    research_required: bool = False
    government_action_possible: bool = True
