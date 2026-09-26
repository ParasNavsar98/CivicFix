"""
Pydantic v2 output and response schemas for Duplicate Candidate Detection API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SignalScoreDetail(BaseModel):
    rawValue: Optional[float] = Field(None, description="Raw value of signal (0.0 to 1.0 or None)")
    state: str = Field(..., description="Signal evaluation state: MATCH, MISMATCH, UNKNOWN, AVAILABLE, UNAVAILABLE")
    weight: float = Field(..., description="Configured weight for this signal")
    contribution: Optional[float] = Field(None, description="Weighted contribution to composite score or None")
    used: bool = Field(..., description="Whether this signal was available and included in the score calculation")


class ScoreBreakdown(BaseModel):
    semantic: SignalScoreDetail
    primaryDomain: SignalScoreDetail
    subcategory: SignalScoreDetail
    secondaryDomains: SignalScoreDetail
    location: SignalScoreDetail


class CandidateMatch(BaseModel):
    candidateProblemId: str = Field(..., description="Unique ID of candidate problem")
    duplicateScore: float = Field(..., description="Multi-factor normalized composite duplicate score (0.0 to 1.0)")
    semanticSimilarity: float = Field(..., description="Cosine similarity score of text embeddings (0.0 to 1.0)")
    primaryDomainMatch: bool = Field(..., description="Whether primary domains match (True only for explicit MATCH)")
    subcategoryMatch: bool = Field(..., description="Whether subcategories match (True only for explicit MATCH)")
    secondaryDomainOverlap: float = Field(..., description="Jaccard overlap fraction of secondary domains")
    locationDistanceKm: Optional[float] = Field(None, description="Distance between problems in kilometers")
    locationScore: float = Field(..., description="Location proximity score (0.0 to 1.0 or 0.0 if unavailable)")
    candidateStatus: str = Field(
        ..., description="Candidate recommendation status: strong_candidate, potential_duplicate, no_candidate"
    )
    reasons: List[str] = Field(default_factory=list, description="Human-readable explainability evidence list")

    # Transparent score breakdown and signal states
    signalStates: Dict[str, str] = Field(
        default_factory=dict,
        description="State of each signal: MATCH, MISMATCH, UNKNOWN for taxonomy; AVAILABLE, UNAVAILABLE for location",
    )
    scoreBreakdown: Optional[Dict[str, Any]] = Field(
        None, description="Detailed score breakdown per signal including weight, contribution, and usage"
    )
    weights: Dict[str, float] = Field(
        default_factory=dict, description="Configured base weights for all signals"
    )
    weightedContributions: Dict[str, Optional[float]] = Field(
        default_factory=dict, description="Actual calculated contribution of each signal"
    )
    availableWeight: float = Field(
        1.0, description="Sum of weights of available signals used as score denominator"
    )
    normalizedCompositeScore: float = Field(
        0.0, description="Final composite score normalized by available weights"
    )
    decisionEvidence: Dict[str, Any] = Field(
        default_factory=dict, description="Diagnostic evidence rules evaluated for decision"
    )
    fingerprint: Optional[Dict[str, Any]] = Field(
        None, description="Problem fingerprint feature comparison result"
    )
    scoringVersion: str = Field("duplicate-v2", description="Scoring engine version identifier")


class DuplicateCheckResponse(BaseModel):
    problemId: str = Field(..., description="Unique ID of the query problem checked")
    status: str = Field(..., description="Overall check result status: candidate_found or no_candidate")
    duplicateCandidates: List[CandidateMatch] = Field(
        default_factory=list, description="Ranked candidate recommendations for human review"
    )
    scoringVersion: str = Field("duplicate-v2", description="Scoring engine version identifier")


class ErrorDetails(BaseModel):
    errorCode: str = Field(..., description="Stable machine-readable error code")
    message: str = Field(..., description="Human-readable error explanation")


class ErrorResponse(BaseModel):
    error: ErrorDetails = Field(..., description="Error details payload")
