from fastapi import APIRouter, HTTPException

from app.config.database import get_db
from app.schemas.matching import MatchingRequest
from app.integrations.categorization_adapter import (
    adapt_classification_output,
    should_attempt_university_matching,
    CategorizationAdapterError,
)
from app.services.matching_engine import run_matching_for_problem
from app.services.ranking import top_n, get_latest_matching_result
from app.services.assignment_workflow import create_assignment_chain, AssignmentError

router = APIRouter(prefix="/api", tags=["matching"])


@router.post("/matching/{problem_id}")
def run_matching(problem_id: str, payload: MatchingRequest):
    db = get_db()
    try:
        problem = adapt_classification_output(
            problem_id=problem_id,
            classification_json=payload.classification,
            location=payload.location.model_dump(),
        )
    except CategorizationAdapterError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    should_run, reason = should_attempt_university_matching(problem)
    if not should_run:
        raise HTTPException(status_code=422, detail=f"Matching not applicable: {reason}")

    results = run_matching_for_problem(db, problem)
    top5 = top_n(results, 5)

    try:
        create_assignment_chain(db, problem_id, top5)
    except AssignmentError as exc:
        # matching ran and was stored; assignment chain just wasn't (re)created
        return {"problemId": problem_id, "topUniversities": top5, "assignmentWarning": str(exc)}

    return {"problemId": problem_id, "topUniversities": top5}


@router.get("/matching/{problem_id}")
def get_matching_result(problem_id: str):
    db = get_db()
    result = get_latest_matching_result(db, problem_id)
    if not result:
        raise HTTPException(status_code=404, detail="No matching result found for this problem.")
    result.pop("_id", None)
    return result


@router.get("/universities/matches/{problem_id}")
def get_top_matches(problem_id: str):
    db = get_db()
    result = get_latest_matching_result(db, problem_id)
    if not result:
        raise HTTPException(status_code=404, detail="No matching result found for this problem.")
    return {"problemId": problem_id, "topUniversities": top_n(result["results"], 5)}
