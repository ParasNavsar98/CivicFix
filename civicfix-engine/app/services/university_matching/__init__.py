"""
University Matching Services package.
"""
from app.services.university_matching.matching_engine import score_university, run_matching_for_problem
from app.services.university_matching.ranking import top_n, get_latest_matching_result
from app.services.university_matching.assignment_workflow import (
    create_assignment_chain,
    get_assignment,
    get_assignments_for_problem,
    accept_assignment,
    reject_assignment,
    build_handoff_payload,
    AssignmentError,
)
from app.services.university_matching.marketplace import (
    build_solution_filter,
    search_solutions,
    get_solution,
)
from app.services.university_matching.collaboration import (
    express_interest,
    get_interests_for_solution,
    accept_interest,
    reject_interest,
    CollaborationError,
)

__all__ = [
    "score_university",
    "run_matching_for_problem",
    "top_n",
    "get_latest_matching_result",
    "create_assignment_chain",
    "get_assignment",
    "get_assignments_for_problem",
    "accept_assignment",
    "reject_assignment",
    "build_handoff_payload",
    "AssignmentError",
    "build_solution_filter",
    "search_solutions",
    "get_solution",
    "express_interest",
    "get_interests_for_solution",
    "accept_interest",
    "reject_interest",
    "CollaborationError",
]
