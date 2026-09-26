from fastapi import APIRouter, HTTPException

from app.config.database import get_db
from app.schemas.assignment import RejectAssignmentRequest
from app.services import assignment_workflow as workflow

router = APIRouter(prefix="/api/assignments", tags=["assignments"])


def _clean(doc):
    if doc:
        doc.pop("_id", None)
    return doc


# NOTE: registered before /{assignment_id} to avoid FastAPI route collision
# (both are single path segments). Spec-wise this is GET /api/assignments/{problemId}.
@router.get("/by-problem/{problem_id}")
def list_assignments_for_problem(problem_id: str):
    db = get_db()
    assignments = workflow.get_assignments_for_problem(db, problem_id)
    return [_clean(a) for a in assignments]


@router.get("/{assignment_id}")
def get_assignment_detail(assignment_id: str):
    db = get_db()
    assignment = workflow.get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    return _clean(assignment)


@router.post("/{assignment_id}/accept")
def accept(assignment_id: str):
    db = get_db()
    try:
        assignment = workflow.accept_assignment(db, assignment_id)
    except workflow.AssignmentError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    handoff = workflow.build_handoff_payload(assignment)
    return {"assignment": _clean(assignment), "handoff": handoff}


@router.post("/{assignment_id}/reject")
def reject(assignment_id: str, payload: RejectAssignmentRequest):
    db = get_db()
    try:
        assignment = workflow.reject_assignment(db, assignment_id, payload.reason)
    except workflow.AssignmentError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return _clean(assignment)
