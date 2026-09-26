from fastapi import APIRouter, Depends, HTTPException

from app.config.database import get_db
from app.schemas.interest import ExpressInterestRequest, RejectInterestRequest
from app.services import collaboration as collab
from app.core.auth import get_current_user, CurrentUser

router = APIRouter(tags=["interests"])


@router.post("/api/marketplace/{solution_id}/interest", status_code=201)
def express_interest(solution_id: str, payload: ExpressInterestRequest):
    db = get_db()
    try:
        interest = collab.express_interest(
            db,
            solution_id=solution_id,
            partner_id=payload.partnerId,
            support_offered=payload.supportOffered,
            contribution=payload.contribution,
            message=payload.message,
        )
    except collab.CollaborationError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    interest.pop("_id", None)
    return interest


@router.get("/api/solutions/{solution_id}/interests")
def list_interests(solution_id: str):
    db = get_db()
    return collab.get_interests_for_solution(db, solution_id)


@router.post("/api/interests/{interest_id}/accept")
def accept_interest(interest_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_db()
    try:
        collaboration = collab.accept_interest(db, interest_id, user.user_id)
    except collab.CollaborationError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    collaboration.pop("_id", None)
    return collaboration


@router.post("/api/interests/{interest_id}/reject")
def reject_interest(
    interest_id: str, payload: RejectInterestRequest, user: CurrentUser = Depends(get_current_user)
):
    db = get_db()
    try:
        interest = collab.reject_interest(db, interest_id, user.user_id, payload.reason)
    except collab.CollaborationError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return interest
