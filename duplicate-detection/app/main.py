"""
FastAPI application for CivicFix Duplicate Candidate Detection module.

SRS REQUIREMENT COMPLIANCE:
- AI layer identifies, calculates similarity, and ranks duplicate candidate problems.
- AI layer surfaces explainable evidence/reasons for reviewer inspection.
- AI layer DOES NOT automatically merge, delete, or replace problem records.
- Human reviewer retains 100% authority over final merge decisions.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas.duplicate import DuplicateCheckResponse, ErrorDetails, ErrorResponse
from app.schemas.input import DuplicateCheckRequest
from app.services.duplicate_detector import DuplicateDetector
from app.services.embedding import (
    EmbeddingError,
    EmbeddingModelError,
    EmbeddingService,
    InvalidEmbeddingInputError,
)
from app.services.location import LocationError
from app.services.similarity import SimilarityError, VectorDimensionMismatchError

# Singleton embedding service instance for efficient lifespan loading
embedding_service = EmbeddingService(model_name=settings.EMBEDDING_MODEL)
detector = DuplicateDetector(embedding_service=embedding_service)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Preloads the BGE-small embedding model on startup."""
    try:
        embedding_service.load_model()
    except Exception as e:
        print(f"Warning: Startup embedding model load encountered issue: {e}")
    yield


app = FastAPI(
    title="CivicFix Duplicate Candidate Detection Engine",
    description=(
        "FastAPI service for semantic embedding-based duplicate candidate detection, "
        "incorporating taxonomy signals and geographic location proximity. "
        "Provides human-in-the-loop candidate recommendations."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_error_response(status_code: int, error_code: str, message: str) -> JSONResponse:
    """Helper to build standardized JSON error responses."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"errorCode": error_code, "message": message}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Centralized handler for Pydantic v2 input validation errors."""
    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="INVALID_INPUT",
        message=f"Request validation failed: {str(exc)}",
    )


@app.exception_handler(InvalidEmbeddingInputError)
async def invalid_embedding_handler(request: Request, exc: InvalidEmbeddingInputError):
    return build_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="INVALID_EMBEDDING",
        message=str(exc),
    )


@app.exception_handler(EmbeddingModelError)
async def embedding_model_handler(request: Request, exc: EmbeddingModelError):
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="EMBEDDING_MODEL_ERROR",
        message=str(exc),
    )


@app.exception_handler(VectorDimensionMismatchError)
async def dimension_mismatch_handler(request: Request, exc: VectorDimensionMismatchError):
    return build_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="VECTOR_DIMENSION_MISMATCH",
        message=str(exc),
    )


@app.exception_handler(LocationError)
async def location_error_handler(request: Request, exc: LocationError):
    return build_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="INVALID_LOCATION",
        message=str(exc),
    )


@app.exception_handler(SimilarityError)
async def similarity_error_handler(request: Request, exc: SimilarityError):
    return build_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="SIMILARITY_CALCULATION_ERROR",
        message=str(exc),
    )


@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint exposing engine status and model information."""
    return {
        "status": "ok",
        "service": "CivicFix Duplicate Candidate Detection Engine",
        "embeddingModel": settings.EMBEDDING_MODEL,
        "embeddingDimension": settings.EMBEDDING_DIMENSION,
        "duplicateThreshold": settings.DUPLICATE_SIMILARITY_THRESHOLD,
        "scoringVersion": getattr(settings, "SCORING_VERSION", "duplicate-v2"),
    }


@app.post(
    "/duplicate-check",
    response_model=DuplicateCheckResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def check_duplicates(payload: DuplicateCheckRequest):
    """
    Evaluates a new problem against candidate existing problems.
    Generates semantic embeddings, calculates structured taxonomy matches and location distance,
    and returns ranked duplicate candidate recommendations with explainable reasons.

    NOTE: Does NOT perform automatic merges.
    """
    try:
        problem_dict = payload.problem.model_dump()
        candidates_dict = [c.model_dump() for c in payload.candidates]

        result = detector.detect_duplicates(
            problem=problem_dict,
            candidates=candidates_dict,
            top_k=payload.topK or settings.VECTOR_TOP_K,
        )
        return result
    except Exception as e:
        if isinstance(e, (EmbeddingError, LocationError, SimilarityError)):
            raise
        return build_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DUPLICATE_DETECTION_ERROR",
            message=f"An error occurred during duplicate detection: {str(e)}",
        )
