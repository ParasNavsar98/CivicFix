"""
University Matching API routes — matching, assignment, marketplace, collaboration.
Consolidated from UniversityMatchingAlgo/backend/app/routers/*.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.database.connection import get_db
from app.database.categorization_adapter import (
    adapt_classification_output,
    should_attempt_university_matching,
    CategorizationAdapterError,
)
from app.services.university_matching.matching_engine import run_matching_for_problem
from app.services.university_matching.ranking import top_n, get_latest_matching_result
from app.services.university_matching.assignment_workflow import (
    AssignmentError,
    create_assignment_chain,
    get_assignment,
    get_assignments_for_problem,
    accept_assignment,
    reject_assignment,
    build_handoff_payload,
)
from app.services.university_matching.marketplace import search_solutions, get_solution
from app.services.university_matching.collaboration import (
    express_interest,
    get_interests_for_solution,
    accept_interest,
    reject_interest,
    CollaborationError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["University Matching"])


# ======== Request Schemas ========

class LocationInput(BaseModel):
    district: str
    state: str
    latitude: float | None = None
    longitude: float | None = None


class MatchingRequest(BaseModel):
    classification: dict
    location: LocationInput


class RejectAssignmentRequest(BaseModel):
    reason: str


class ExpressInterestRequest(BaseModel):
    partnerId: str
    supportOffered: list[str] = []
    contribution: dict = {}
    message: str = ""


class RejectInterestRequest(BaseModel):
    reason: str


class SolutionLocation(BaseModel):
    state: str
    district: str


class SolutionCreate(BaseModel):
    solutionId: str
    problemId: str
    projectId: str
    universityId: str
    title: str
    domain: str
    subcategory: str
    location: SolutionLocation
    developmentStage: str
    supportNeeded: list[str] = []
    partnerType: list[str] = []
    visibility: str = "PUBLIC"
    status: str = "PUBLISHED"


# ======== University CRUD ========

class Location(BaseModel):
    district: str
    state: str
    latitude: float | None = None
    longitude: float | None = None


class Contact(BaseModel):
    email: str | None = None
    phone: str | None = None


class Institution(BaseModel):
    name: str
    type: str = "University"
    location: Location
    contact: Contact = Contact()


class FacultyEntry(BaseModel):
    facultyId: str
    name: str
    department: str
    expertise: list[str] = []
    researchAreas: list[str] = []
    availableForProjects: bool = True


class PastProject(BaseModel):
    title: str
    domains: list[str] = []
    expertise: list[str] = []
    description: str = ""


class Capacity(BaseModel):
    activeProjects: int = 0
    maximumProjects: int = 0
    availableTeams: int = 0
    availability: str = "AVAILABLE"


class UniversityCreate(BaseModel):
    universityId: str
    institution: Institution
    departments: list[str] = []
    expertise: list[str] = []
    researchAreas: list[str] = []
    faculty: list[FacultyEntry] = []
    infrastructure: list[str] = []
    technologyCapabilities: list[str] = []
    pastProjects: list[PastProject] = []
    industryRelationships: list[str] = []
    capacity: Capacity = Capacity()
    status: str = "ACTIVE"


class UniversityUpdate(BaseModel):
    institution: Institution | None = None
    departments: list[str] | None = None
    expertise: list[str] | None = None
    researchAreas: list[str] | None = None
    faculty: list[FacultyEntry] | None = None
    infrastructure: list[str] | None = None
    technologyCapabilities: list[str] | None = None
    pastProjects: list[PastProject] | None = None
    industryRelationships: list[str] | None = None
    capacity: Capacity | None = None
    status: str | None = None


def _clean(doc):
    if doc:
        doc.pop("_id", None)
    return doc


# ======== University Routes ========

@router.get("/universities", summary="List universities")
def list_universities(status: str | None = None):
    db = get_db()
    query = {"status": status} if status else {}
    return list(db.universities.find(query, {"_id": 0}))


@router.get("/universities/{university_id}", summary="Get university by ID")
def get_university(university_id: str):
    db = get_db()
    uni = db.universities.find_one({"universityId": university_id}, {"_id": 0})
    if not uni:
        raise HTTPException(status_code=404, detail="University not found.")
    return uni


@router.post("/universities", status_code=201, summary="Register a university")
def create_university(payload: UniversityCreate):
    db = get_db()
    if db.universities.find_one({"universityId": payload.universityId}):
        raise HTTPException(status_code=409, detail="universityId already exists.")
    doc = payload.model_dump()
    db.universities.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


@router.put("/universities/{university_id}", summary="Update a university")
def update_university(university_id: str, payload: UniversityUpdate):
    db = get_db()
    existing = db.universities.find_one({"universityId": university_id})
    if not existing:
        raise HTTPException(status_code=404, detail="University not found.")
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if updates:
        db.universities.update_one({"universityId": university_id}, {"$set": updates})
    return db.universities.find_one({"universityId": university_id}, {"_id": 0})


# ======== Matching Routes ========

@router.post("/matching/{problem_id}", summary="Run university matching for a problem")
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
        return {"problemId": problem_id, "topUniversities": top5, "assignmentWarning": str(exc)}

    return {"problemId": problem_id, "topUniversities": top5}


@router.get("/matching/{problem_id}", summary="Get latest matching result for a problem")
def get_matching_result(problem_id: str):
    db = get_db()
    result = get_latest_matching_result(db, problem_id)
    if not result:
        raise HTTPException(status_code=404, detail="No matching result found for this problem.")
    result.pop("_id", None)
    return result


@router.get("/universities/matches/{problem_id}", summary="Get top-5 university matches for a problem")
def get_top_matches(problem_id: str):
    db = get_db()
    result = get_latest_matching_result(db, problem_id)
    if not result:
        raise HTTPException(status_code=404, detail="No matching result found for this problem.")
    return {"problemId": problem_id, "topUniversities": top_n(result["results"], 5)}


# ======== Assignment Routes ========

@router.get("/assignments/by-problem/{problem_id}", summary="List assignments for a problem")
def list_assignments_for_problem(problem_id: str):
    db = get_db()
    assignments = get_assignments_for_problem(db, problem_id)
    return [_clean(a) for a in assignments]


@router.get("/assignments/{assignment_id}", summary="Get assignment detail")
def get_assignment_detail(assignment_id: str):
    db = get_db()
    assignment = get_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")
    return _clean(assignment)


@router.post("/assignments/{assignment_id}/accept", summary="Accept a university assignment")
def accept(assignment_id: str):
    db = get_db()
    try:
        assignment = accept_assignment(db, assignment_id)
    except AssignmentError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    handoff = build_handoff_payload(assignment)
    return {"assignment": _clean(assignment), "handoff": handoff}


@router.post("/assignments/{assignment_id}/reject", summary="Reject a university assignment")
def reject(assignment_id: str, payload: RejectAssignmentRequest):
    db = get_db()
    try:
        assignment = reject_assignment(db, assignment_id, payload.reason)
    except AssignmentError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return _clean(assignment)


# ======== Marketplace Routes ========

@router.post("/marketplace/solutions", status_code=201, summary="Publish a marketplace solution")
def publish_solution(payload: SolutionCreate):
    db = get_db()
    if db.solutions.find_one({"solutionId": payload.solutionId}):
        raise HTTPException(status_code=409, detail="solutionId already exists.")
    doc = payload.model_dump()
    db.solutions.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


@router.get("/marketplace/solutions", summary="List marketplace solutions")
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
    return search_solutions(
        db,
        domain=domain,
        subcategory=subcategory,
        state=state,
        district=district,
        development_stage=developmentStage,
        support_needed=supportNeeded,
        partner_type=partnerType,
    )


@router.get("/marketplace/solutions/{solution_id}", summary="Get a marketplace solution")
def get_solution_by_id(solution_id: str):
    db = get_db()
    solution = get_solution(db, solution_id)
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found.")
    return solution


# ======== Collaboration/Interest Routes ========

@router.post("/marketplace/{solution_id}/interest", status_code=201, summary="Express interest in a solution")
def express_interest_endpoint(solution_id: str, payload: ExpressInterestRequest):
    db = get_db()
    try:
        interest = express_interest(
            db,
            solution_id=solution_id,
            partner_id=payload.partnerId,
            support_offered=payload.supportOffered,
            contribution=payload.contribution,
            message=payload.message,
        )
    except CollaborationError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    interest.pop("_id", None)
    return interest


@router.get("/solutions/{solution_id}/interests", summary="List interests for a solution")
def list_interests(solution_id: str):
    db = get_db()
    return get_interests_for_solution(db, solution_id)


@router.post("/interests/{interest_id}/accept", summary="Accept a collaboration interest")
def accept_interest_endpoint(interest_id: str, acting_user_id: str = "ADMIN"):
    db = get_db()
    try:
        collaboration = accept_interest(db, interest_id, acting_user_id)
    except CollaborationError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    collaboration.pop("_id", None)
    return collaboration


@router.post("/interests/{interest_id}/reject", summary="Reject a collaboration interest")
def reject_interest_endpoint(interest_id: str, payload: RejectInterestRequest, acting_user_id: str = "ADMIN"):
    db = get_db()
    try:
        interest = reject_interest(db, interest_id, acting_user_id, payload.reason)
    except CollaborationError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return interest


# ======== Collaborations Routes ========

@router.get("/collaborations", summary="List collaborations")
def list_collaborations(solutionId: str | None = None, partnerId: str | None = None):
    db = get_db()
    query = {}
    if solutionId:
        query["solutionId"] = solutionId
    if partnerId:
        query["partnerId"] = partnerId
    return list(db.collaborations.find(query, {"_id": 0}))


@router.get("/collaborations/{collaboration_id}", summary="Get collaboration by ID")
def get_collaboration(collaboration_id: str):
    db = get_db()
    doc = db.collaborations.find_one({"collaborationId": collaboration_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Collaboration not found.")
    return doc
