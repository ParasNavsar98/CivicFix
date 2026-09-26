"""
Shared Common Pydantic Schemas.
"""
from typing import Optional
from pydantic import BaseModel, Field


class ProblemLocation(BaseModel):
    district: str = Field(..., description="District name", max_length=100)
    state: str = Field(..., description="State name", max_length=100)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Longitude coordinate")


class LocationInput(BaseModel):
    lat: Optional[float] = Field(None, ge=-90.0, le=90.0)
    long: Optional[float] = Field(None, ge=-180.0, le=180.0)
    address: Optional[str] = Field(None, max_length=300)


class ErrorDetails(BaseModel):
    errorCode: str = Field(..., description="Error classification code")
    message: str = Field(..., description="Human-readable error description")


class ErrorResponse(BaseModel):
    error: ErrorDetails
