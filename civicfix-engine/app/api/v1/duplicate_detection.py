"""
Duplicate Detection API route — POST /api/v1/duplicate-detection/check
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.duplicate_detection.duplicate_service import DuplicateDetector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/duplicate-detection", tags=["Duplicate Detection"])

# Singleton service instance
_detector: DuplicateDetector | None = None


def get_detector() -> DuplicateDetector:
    global _detector
    if _detector is None:
        _detector = DuplicateDetector()
    return _detector


class DuplicateCheckRequest(BaseModel):
    problem: Dict[str, Any]
    candidates: List[Dict[str, Any]]
    top_k: int = 10


class DuplicatePairRequest(BaseModel):
    problem: Dict[str, Any]
    candidate: Dict[str, Any]


@router.post(
    "/check",
    summary="Detect duplicate candidates for a new problem",
)
def check_duplicates(payload: DuplicateCheckRequest):
    """
    Run available-signal normalized composite scoring against a list of candidate problems.
    Returns ranked duplicate candidates with full score breakdown and explainability.
    """
    logger.info(
        "Received duplicate check for problemId: %s against %d candidates",
        payload.problem.get("problemId", "UNKNOWN"),
        len(payload.candidates),
    )
    detector = get_detector()
    return detector.detect_duplicates(
        problem=payload.problem,
        candidates=payload.candidates,
        top_k=payload.top_k,
    )


@router.post(
    "/analyze-pair",
    summary="Analyze a single problem-candidate pair",
)
def analyze_pair(payload: DuplicatePairRequest):
    """
    Analyze one problem vs one candidate problem across all signals.
    Returns full score breakdown, signal states, and contradiction detection.
    """
    detector = get_detector()
    return detector.analyze_candidate_pair(
        problem=payload.problem,
        candidate=payload.candidate,
    )
