from pydantic import BaseModel


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
    developmentStage: str  # e.g. IDEA | PROTOTYPE | PILOT | DEPLOYED
    supportNeeded: list[str] = []
    partnerType: list[str] = []
    visibility: str = "PUBLIC"
    status: str = "PUBLISHED"
