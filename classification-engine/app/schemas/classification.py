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


class ClassificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problemSummary: str = Field(..., description="Concise summary of the reported problem")
    primaryDomain: str = Field(..., description="Primary domain from controlled taxonomy")
    secondaryDomains: List[str] = Field(default_factory=list, description="Secondary relevant domains")
    subcategory: str = Field(..., description="Subcategory belonging to primary domain")
    severity: SeverityEnum = Field(..., description="Severity level")
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
