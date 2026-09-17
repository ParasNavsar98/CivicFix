from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ProblemLocation(BaseModel):
    district: str = Field(..., description="District name", max_length=100)
    state: str = Field(..., description="State name", max_length=100)
    latitude: Optional[float] = Field(None, description="Geographic latitude (-90 to 90)")
    longitude: Optional[float] = Field(None, description="Geographic longitude (-180 to 180)")

    @field_validator("district", "state", mode="before")
    @classmethod
    def trim_and_validate_non_empty(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Location fields cannot be empty or whitespace only.")
        return value

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not (-90.0 <= value <= 90.0):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not (-180.0 <= value <= 180.0):
            raise ValueError("Longitude must be between -180 and 180 degrees.")
        return value


class ProblemClassificationInput(BaseModel):
    problemId: str = Field(..., description="Unique problem identifier", max_length=100)
    title: str = Field(..., description="Short title describing the problem", max_length=300)
    description: str = Field(..., description="Detailed description of the reported problem", max_length=5000)
    location: ProblemLocation = Field(..., description="Location of the reported problem")

    @field_validator("problemId", "title", "description", mode="before")
    @classmethod
    def trim_and_validate_string(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty or whitespace only.")
        return value
