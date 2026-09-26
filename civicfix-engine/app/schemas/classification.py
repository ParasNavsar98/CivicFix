"""
Pydantic Schemas for AI Classification Engine.
Source: classification-engine/app/schemas/classification.py
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import ProblemLocation, ErrorDetails


class StatusEnum(str, Enum):
    CLASSIFIED = "classified"
    REVIEW_REQUIRED = "review_required"
    FAILED = "failed"


class SeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SeverityImpactEnum(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class ExposureScopeEnum(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    LOCAL = "LOCAL"
    COMMUNITY = "COMMUNITY"
    LARGE_AREA = "LARGE_AREA"
    WIDESPREAD = "WIDESPREAD"
    UNKNOWN = "UNKNOWN"


class VulnerablePopulationEnum(str, Enum):
    NONE_IDENTIFIED = "NONE_IDENTIFIED"
    POSSIBLE = "POSSIBLE"
    CLEAR = "CLEAR"
    UNKNOWN = "UNKNOWN"


class GeographicExtentEnum(str, Enum):
    SINGLE_LOCATION = "SINGLE_LOCATION"
    LOCAL_AREA = "LOCAL_AREA"
    MULTIPLE_LOCATIONS = "MULTIPLE_LOCATIONS"
    WIDE_AREA = "WIDE_AREA"
    UNKNOWN = "UNKNOWN"


class DurationEnum(str, Enum):
    SHORT_TERM = "SHORT_TERM"
    ONGOING = "ONGOING"
    LONG_TERM = "LONG_TERM"
    PERSISTENT = "PERSISTENT"
    UNKNOWN = "UNKNOWN"


class ReversibilityEnum(str, Enum):
    EASILY_REVERSIBLE = "EASILY_REVERSIBLE"
    RECOVERABLE = "RECOVERABLE"
    DIFFICULT_TO_RECOVER = "DIFFICULT_TO_RECOVER"
    POTENTIALLY_IRREVERSIBLE = "POTENTIALLY_IRREVERSIBLE"
    UNKNOWN = "UNKNOWN"


class PeopleAffectedSourceEnum(str, Enum):
    NOT_PROVIDED = "NOT_PROVIDED"
    CITIZEN_REPORTED = "CITIZEN_REPORTED"


class ProblemClassificationInput(BaseModel):
    problemId: str = Field(..., max_length=100)
    title: str = Field(..., max_length=300)
    description: str = Field(..., max_length=5000)
    location: ProblemLocation


class SeverityAssessment(BaseModel):
    healthSafetyImpact: SeverityImpactEnum = SeverityImpactEnum.UNKNOWN
    exposureScope: ExposureScopeEnum = ExposureScopeEnum.UNKNOWN
    vulnerablePopulationExposure: VulnerablePopulationEnum = VulnerablePopulationEnum.UNKNOWN
    geographicExtent: GeographicExtentEnum = GeographicExtentEnum.UNKNOWN
    duration: DurationEnum = DurationEnum.UNKNOWN
    infrastructureImpact: SeverityImpactEnum = SeverityImpactEnum.UNKNOWN
    environmentalImpact: SeverityImpactEnum = SeverityImpactEnum.UNKNOWN
    socialEconomicImpact: SeverityImpactEnum = SeverityImpactEnum.UNKNOWN
    reversibility: ReversibilityEnum = ReversibilityEnum.UNKNOWN


class PeopleAffected(BaseModel):
    value: Optional[int] = Field(None, ge=1)
    unit: Optional[str] = Field(None, max_length=50)
    source: PeopleAffectedSourceEnum = PeopleAffectedSourceEnum.NOT_PROVIDED


class ClassificationResult(BaseModel):
    problemSummary: str = Field(...)
    primaryDomain: str = Field(...)
    secondaryDomains: List[str] = Field(default_factory=list)
    subcategory: str = Field(...)
    severity: SeverityEnum = Field(...)
    severityAssessment: SeverityAssessment = Field(default_factory=SeverityAssessment)
    severityEvidence: List[str] = Field(default_factory=list)
    peopleAffected: PeopleAffected = Field(default_factory=PeopleAffected)
    urgency: SeverityEnum = Field(...)
    researchRequired: bool = Field(default=False)
    governmentActionPossible: bool = Field(default=True)
    requiredExpertise: List[str] = Field(default_factory=list)
    requiredResources: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(...)


class ClassificationResponse(BaseModel):
    problemId: str
    status: StatusEnum
    classification: Optional[ClassificationResult] = None
    error: Optional[ErrorDetails] = None
