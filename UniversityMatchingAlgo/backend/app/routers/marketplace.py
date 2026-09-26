from fastapi import APIRouter, HTTPException, Query

from app.config.database import get_db
from app.schemas.solution import SolutionCreate
from app.services import marketplace

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


@router.post("/solutions", status_code=201)
def publish_solution(payload: SolutionCreate):
    """Minimal create endpoint so the module is self-contained for demo/testing.
    The richer solution-authoring UI belongs to the main frontend."""
    db = get_db()
    if db.solutions.find_one({"solutionId": payload.solutionId}):
        raise HTTPException(status_code=409, detail="solutionId already exists.")
    doc = payload.model_dump()
    db.solutions.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


@router.get("/solutions")
def list_solutions(
    domain: str | None = None,
    subcategory: str | None = None,
    state: str | None = None,
    district: str | None = None,
    developmentStage: str | None = None,
    supportNeeded: list[str] | None = Query(default=None),
    partnerType: list[str] | None = Query(default=None),
):
    db = get_db()
    return marketplace.search_solutions(
        db,
        domain=domain,
        subcategory=subcategory,
        state=state,
        district=district,
        development_stage=developmentStage,
        support_needed=supportNeeded,
        partner_type=partnerType,
    )


@router.get("/solutions/{solution_id}")
def get_solution(solution_id: str):
    db = get_db()
    solution = marketplace.get_solution(db, solution_id)
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found.")
    return solution
