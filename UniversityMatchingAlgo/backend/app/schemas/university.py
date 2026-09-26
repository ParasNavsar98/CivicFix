from pydantic import BaseModel, Field


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
    contact: Contact = Field(default_factory=Contact)


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
    availability: str = "AVAILABLE"  # AVAILABLE | LIMITED | UNAVAILABLE


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
    capacity: Capacity = Field(default_factory=Capacity)
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
