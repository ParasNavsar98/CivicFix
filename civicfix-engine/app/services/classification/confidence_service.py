"""
Confidence Evaluation Engine.
Source: classification-engine/app/services/confidence.py
"""
from app.config import settings
from app.schemas.classification import StatusEnum


def evaluate_confidence(
    confidence: float,
    evidence_sufficient: bool = True,
    ambiguity_detected: bool = False,
) -> StatusEnum:
    """Evaluate confidence and ambiguity safeguards to return classification status."""

    # Rule 1: Insufficient actionable detail forces human review
    if not evidence_sufficient:
        return StatusEnum.REVIEW_REQUIRED

    # Rule 2: Ambiguity flag forces human review
    if ambiguity_detected:
        return StatusEnum.REVIEW_REQUIRED

    # Rule 3: High confidence threshold
    if confidence >= settings.AI_HIGH_CONFIDENCE_THRESHOLD:
        return StatusEnum.CLASSIFIED

    # Rule 4: Lower confidence falls back to review required
    return StatusEnum.REVIEW_REQUIRED
