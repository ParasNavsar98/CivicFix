"""
Pydantic v2 input schemas for Duplicate Candidate Detection API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class LocationInput(BaseModel):
    lat: Optional[float] = Field(None, description="Geographic latitude (-90 to 90)", ge=-90.0, le=90.0)
    long: Optional[float] = Field(None, description="Geographic longitude (-180 to 180)", ge=-180.0, le=180.0)
    address: Optional[str] = Field(None, description="Street or area address description", max_length=300)


class ProblemInput(BaseModel):
    problemId: Optional[str] = Field(None, description="Unique problem identifier", max_length=100)
    title: str = Field(..., description="Problem title", min_length=1, max_length=300)
    description: str = Field(..., description="Problem detailed description", min_length=1, max_length=5000)
    location: Optional[LocationInput] = Field(None, description="Geographic location details")
    primaryDomain: Optional[str] = Field(None, description="Primary domain from taxonomy", max_length=100)
    secondaryDomains: List[str] = Field(default_factory=list, description="Secondary domains list")
    subcategory: Optional[str] = Field(None, description="Subcategory from taxonomy", max_length=100)

    @field_validator("title", "description", mode="before")
    @classmethod
    def trim_and_validate_non_empty(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Title and description cannot be empty or whitespace only.")
        return value


class DuplicateCheckRequest(BaseModel):
    problem: ProblemInput = Field(..., description="The new problem to check for potential duplicates")
    candidates: List[ProblemInput] = Field(
        default_factory=list, description="Optional explicit candidate problems to compare against"
    )
    topK: Optional[int] = Field(10, description="Maximum number of top candidate recommendations to return", ge=1, le=100)
