from fastapi import APIRouter, Depends, HTTPException

from app.config.database import get_db
from app.schemas.university import UniversityCreate, UniversityUpdate
from app.core.auth import get_current_user, CurrentUser

router = APIRouter(prefix="/api/universities", tags=["universities"])


@router.get("")
def list_universities(status: str | None = None):
    db = get_db()
    query = {"status": status} if status else {}
    return list(db.universities.find(query, {"_id": 0}))


@router.get("/{university_id}")
def get_university(university_id: str):
    db = get_db()
    uni = db.universities.find_one({"universityId": university_id}, {"_id": 0})
    if not uni:
        raise HTTPException(status_code=404, detail="University not found.")
    return uni


@router.post("", status_code=201)
def create_university(payload: UniversityCreate, user: CurrentUser = Depends(get_current_user)):
    db = get_db()
    if db.universities.find_one({"universityId": payload.universityId}):
        raise HTTPException(status_code=409, detail="universityId already exists.")
    doc = payload.model_dump()
    db.universities.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


@router.put("/{university_id}")
def update_university(
    university_id: str, payload: UniversityUpdate, user: CurrentUser = Depends(get_current_user)
):
    db = get_db()
    existing = db.universities.find_one({"universityId": university_id})
    if not existing:
        raise HTTPException(status_code=404, detail="University not found.")

    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if updates:
        db.universities.update_one({"universityId": university_id}, {"$set": updates})
    return db.universities.find_one({"universityId": university_id}, {"_id": 0})
