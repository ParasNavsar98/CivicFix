from app.config import settings
from app.schemas.classification import StatusEnum


def evaluate_confidence(
    confidence: float,
    evidence_sufficient: bool = True,
    ambiguity_detected: bool = False,
) -> StatusEnum:
    """Evaluate classification confidence against thresholds and safeguards.
    
    Returns 'classified' ONLY IF:
    1. Confidence score >= AI_HIGH_CONFIDENCE_THRESHOLD (default 0.85)
    2. Evidence is sufficient for classification
    3. No significant ambiguity is detected
    
    Otherwise returns 'review_required'.
    """
    if (
        confidence >= settings.AI_HIGH_CONFIDENCE_THRESHOLD
        and evidence_sufficient
        and not ambiguity_detected
    ):
        return StatusEnum.CLASSIFIED
    return StatusEnum.REVIEW_REQUIRED
