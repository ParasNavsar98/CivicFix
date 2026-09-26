"""
Classification API route — POST /api/v1/classify
"""
import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.classification import ClassificationResponse, ProblemClassificationInput
from app.services.classification.classifier_service import ClassifierService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Classification"])

# Singleton service instance
_classifier_service: ClassifierService | None = None


def get_classifier_service() -> ClassifierService:
    global _classifier_service
    if _classifier_service is None:
        _classifier_service = ClassifierService()
    return _classifier_service


@router.post(
    "/classify",
    response_model=ClassificationResponse,
    summary="Classify a citizen-reported societal problem",
)
async def classify_problem(input_data: ProblemClassificationInput):
    """Classify a problem using the AI classification engine (Gemma 3 4B via Ollama)."""
    logger.info("Received /api/v1/classify request for problemId: %s", input_data.problemId)
    service = get_classifier_service()
    return await service.classify_problem(input_data)
