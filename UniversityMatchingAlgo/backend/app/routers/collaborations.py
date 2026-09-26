from fastapi import APIRouter, HTTPException

from app.config.database import get_db

router = APIRouter(prefix="/api/collaborations", tags=["collaborations"])


@router.get("")
def list_collaborations(solutionId: str | None = None, partnerId: str | None = None):
    db = get_db()
    query = {}
    if solutionId:
        query["solutionId"] = solutionId
    if partnerId:
        query["partnerId"] = partnerId
    return list(db.collaborations.find(query, {"_id": 0}))


@router.get("/{collaboration_id}")
def get_collaboration(collaboration_id: str):
    db = get_db()
    doc = db.collaborations.find_one({"collaborationId": collaboration_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Collaboration not found.")
    return doc
