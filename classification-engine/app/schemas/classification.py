from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UrgencyEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class StatusEnum(str, Enum):
    CLASSIFIED = "classified"
    REVIEW_REQUIRED = "review_required"
    FAILED = "failed"


# --- Severity Assessment Framework Enums ---

class HealthSafetyImpactEnum(str, Enum):
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


class VulnerablePopulationExposureEnum(str, Enum):
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


class InfrastructureImpactEnum(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class EnvironmentalImpactEnum(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class SocialEconomicImpactEnum(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
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


# --- Severity Assessment & People Models ---

class SeverityAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    healthSafetyImpact: HealthSafetyImpactEnum = Field(
        default=HealthSafetyImpactEnum.UNKNOWN, description="Health and safety impact"
    )
    exposureScope: ExposureScopeEnum = Field(
        default=ExposureScopeEnum.UNKNOWN, description="Qualitative scope of exposed population"
    )
    vulnerablePopulationExposure: VulnerablePopulationExposureEnum = Field(
        default=VulnerablePopulationExposureEnum.UNKNOWN, description="Exposure of vulnerable population"
    )
    geographicExtent: GeographicExtentEnum = Field(
        default=GeographicExtentEnum.UNKNOWN, description="Geographic extent of problem"
    )
    duration: DurationEnum = Field(
        default=DurationEnum.UNKNOWN, description="Duration or persistence of problem"
    )
    infrastructureImpact: InfrastructureImpactEnum = Field(
        default=InfrastructureImpactEnum.UNKNOWN, description="Essential infrastructure/service impact"
    )
    environmentalImpact: EnvironmentalImpactEnum = Field(
        default=EnvironmentalImpactEnum.UNKNOWN, description="Environmental impact"
    )
    socialEconomicImpact: SocialEconomicImpactEnum = Field(
        default=SocialEconomicImpactEnum.UNKNOWN, description="Social or economic impact"
    )
    reversibility: ReversibilityEnum = Field(
        default=ReversibilityEnum.UNKNOWN, description="Reversibility of consequences"
    )

    @field_validator(
        "healthSafetyImpact",
        "exposureScope",
        "vulnerablePopulationExposure",
        "geographicExtent",
        "duration",
        "infrastructureImpact",
        "environmentalImpact",
        "socialEconomicImpact",
        "reversibility",
        mode="before",
    )
    @classmethod
    def normalize_enum_case(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.upper()
        return value


class PeopleAffected(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: Optional[int] = Field(default=None, description="Explicit count if reported by citizen")
    unit: Optional[str] = Field(default=None, description="Unit of count e.g. people, families, students")
    source: PeopleAffectedSourceEnum = Field(
        default=PeopleAffectedSourceEnum.NOT_PROVIDED, description="Source of population data"
    )

    @field_validator("source", mode="before")
    @classmethod
    def normalize_source_case(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.upper()
        return value


class ClassificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problemSummary: str = Field(..., description="Concise summary of the reported problem")
    primaryDomain: str = Field(..., description="Primary domain from controlled taxonomy")
    secondaryDomains: List[str] = Field(default_factory=list, description="Secondary relevant domains")
    subcategory: str = Field(..., description="Subcategory belonging to primary domain")
    severity: SeverityEnum = Field(..., description="Severity level")
    severityAssessment: SeverityAssessment = Field(
        default_factory=SeverityAssessment, description="Structured severity factor assessment"
    )
    severityEvidence: List[str] = Field(
        default_factory=list, description="Evidence statements supporting severity assessment"
    )
    peopleAffected: PeopleAffected = Field(
        default_factory=PeopleAffected, description="Explicit citizen-reported population info"
    )
    urgency: UrgencyEnum = Field(..., description="Urgency level")
    researchRequired: bool = Field(..., description="Whether research or innovation is required")
    governmentActionPossible: bool = Field(..., description="Whether government/authority action is relevant")
    requiredExpertise: List[str] = Field(default_factory=list, description="Expertise needed")
    requiredResources: List[str] = Field(default_factory=list, description="Resources needed")
    confidence: float = Field(..., description="Confidence score between 0 and 1")
    reasoning: str = Field(..., description="Concise explanation for the classification")

    @field_validator("severity", "urgency", mode="before")
    @classmethod
    def normalize_enum_case(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.upper()
        return value

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: float) -> float:
        if not (0.0 <= value <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0 inclusive.")
        return round(value, 4)


class ErrorDetails(BaseModel):
    errorCode: str = Field(..., description="Standardized error code")
    message: str = Field(..., description="User-friendly error message")


class ClassificationResponse(BaseModel):
    problemId: str = Field(..., description="Unique problem identifier")
    status: StatusEnum = Field(..., description="Classification outcome status")
    classification: Optional[ClassificationResult] = Field(None, description="Classification result if successful")
    error: Optional[ErrorDetails] = Field(None, description="Error details if classification failed")

