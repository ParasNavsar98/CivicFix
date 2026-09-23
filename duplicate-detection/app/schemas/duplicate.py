"""
Pydantic v2 output and response schemas for Duplicate Candidate Detection API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CandidateMatch(BaseModel):
    candidateProblemId: str = Field(..., description="Unique ID of candidate problem")
    duplicateScore: float = Field(..., description="Multi-factor composite duplicate score (0.0 to 1.0)")
    semanticSimilarity: float = Field(..., description="Cosine similarity score of text embeddings (0.0 to 1.0)")
    primaryDomainMatch: bool = Field(..., description="Whether primary domains match")
    subcategoryMatch: bool = Field(..., description="Whether subcategories match")
    secondaryDomainOverlap: float = Field(..., description="Jaccard overlap fraction of secondary domains")
    locationDistanceKm: Optional[float] = Field(None, description="Distance between problems in kilometers")
    locationScore: float = Field(..., description="Location proximity score (0.0 to 1.0)")
    candidateStatus: str = Field(..., description="Candidate recommendation status: strong_candidate, potential_duplicate, no_candidate")
    reasons: List[str] = Field(default_factory=list, description="Human-readable explainability evidence list")


class DuplicateCheckResponse(BaseModel):
    problemId: str = Field(..., description="Unique ID of the query problem checked")
    status: str = Field(..., description="Overall check result status: candidate_found or no_candidate")
    duplicateCandidates: List[CandidateMatch] = Field(
        default_factory=list, description="Ranked candidate recommendations for human review"
    )


class ErrorDetails(BaseModel):
    errorCode: str = Field(..., description="Stable machine-readable error code")
    message: str = Field(..., description="Human-readable error explanation")


class ErrorResponse(BaseModel):
    error: ErrorDetails = Field(..., description="Error details payload")
