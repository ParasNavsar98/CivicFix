import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.input import ProblemClassificationInput
from app.schemas.classification import ClassificationResponse, StatusEnum, ErrorDetails
from app.services.classifier import ClassifierService

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("classification_engine")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Classification Engine Service...")
    yield
    logger.info("Shutting down AI Classification Engine Service...")


app = FastAPI(
    title="Societal Innovation Portal - AI Classification Engine",
    description="Standalone microservice for classifying citizen-reported societal problems.",
    version="1.0.0",
    lifespan=lifespan,
)

# Global classifier service instance
classifier_service = ClassifierService()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format input validation errors cleanly without exposing internal tracebacks."""
    error_msg = "; ".join([f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()])
    logger.warning("Input validation error on request to %s: %s", request.url.path, error_msg)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "failed",
            "errorCode": "INVALID_INPUT",
            "message": f"Validation failed: {error_msg}",
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler to avoid exposing raw stack traces."""
    logger.exception("Unhandled exception processing request to %s: %s", request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "failed",
            "errorCode": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred.",
        },
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.post(
    "/classify",
    response_model=ClassificationResponse,
    tags=["Classification"],
    summary="Classify citizen reported societal problem",
)
async def classify_problem_endpoint(input_data: ProblemClassificationInput):
    """API endpoint to receive structured problem submission and return AI classification."""
    logger.info("Received /classify request for problemId: %s", input_data.problemId)
    response = await classifier_service.classify_problem(input_data)
    return response
