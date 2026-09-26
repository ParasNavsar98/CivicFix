"""
Pydantic Schemas for Duplicate Candidate Detection Engine.
Source: duplicate-detection/app/schemas/input.py and duplicate.py
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import LocationInput


class ProblemInput(BaseModel):
    problemId: Optional[str] = Field(None, max_length=100)
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., min_length=1, max_length=5000)
    location: Optional[LocationInput] = None
    primaryDomain: Optional[str] = Field(None, max_length=100)
    secondaryDomains: List[str] = Field(default_factory=list)
    subcategory: Optional[str] = Field(None, max_length=100)


class DuplicateCheckRequest(BaseModel):
    problem: ProblemInput
    candidates: List[ProblemInput] = Field(default_factory=list)
    topK: Optional[int] = Field(10, ge=1, le=100)


class CandidateStatusEnum(str, Enum):
    STRONG_CANDIDATE = "strong_candidate"
    POTENTIAL_DUPLICATE = "potential_duplicate"
    WEAK_CANDIDATE = "weak_candidate"
    NO_CANDIDATE = "no_candidate"


class OverallDuplicateStatusEnum(str, Enum):
    CANDIDATE_FOUND = "candidate_found"
    NO_CANDIDATE = "no_candidate"


class CandidateMatch(BaseModel):
    candidateProblemId: str
    duplicateScore: float = Field(..., ge=0.0, le=1.0)
    semanticSimilarity: float = Field(..., ge=-1.0, le=1.0)
    primaryDomainMatch: bool
    subcategoryMatch: bool
    secondaryDomainOverlap: float = Field(..., ge=0.0, le=1.0)
    locationDistanceKm: Optional[float] = None
    locationScore: float = Field(..., ge=0.0, le=1.0)
    candidateStatus: CandidateStatusEnum
    signalStates: Optional[Dict[str, str]] = None
    scoreBreakdown: Optional[Dict[str, Any]] = None
    availableWeight: Optional[float] = None
    normalizedCompositeScore: Optional[float] = None
    reasons: List[str] = Field(default_factory=list)


class DuplicateCheckResponse(BaseModel):
    problemId: str
    status: OverallDuplicateStatusEnum
    duplicateCandidates: List[CandidateMatch] = Field(default_factory=list)
    scoringVersion: str = "duplicate-v2"
