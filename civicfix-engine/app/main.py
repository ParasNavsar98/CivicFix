"""
CivicFix Integrated AI Engine & Capability Portal
===================================================
Unified FastAPI application integrating three features:
  1. AI Classification Engine  (POST /api/v1/classify)
  2. Duplicate Detection Engine (POST /api/v1/duplicate-detection/check)
  3. University Matching & Marketplace (POST /api/v1/matching/{problem_id}, etc.)
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.connection import ensure_indexes
from app.api.v1 import classification, duplicate_detection, university_matching, health

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("civicfix-engine")


# ─── Lifespan ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CivicFix Engine — creating MongoDB indexes...")
    try:
        ensure_indexes()
        logger.info("MongoDB indexes ready.")
    except Exception as e:
        logger.warning("Could not ensure MongoDB indexes (DB may not be running): %s", e)
    yield
    logger.info("Shutting down CivicFix Engine.")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=(
        "Unified CivicFix AI Engine: classifies citizen-reported societal problems, "
        "detects duplicates, matches universities to problems, and provides an "
        "industry marketplace for solutions."
    ),
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Exception Handlers ───────────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_msg = "; ".join(
        [f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()]
    )
    logger.warning("Input validation error on %s: %s", request.url.path, error_msg)
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
    logger.exception("Unhandled exception on %s: %s", request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "failed",
            "errorCode": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred.",
        },
    )


# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(classification.router)
app.include_router(duplicate_detection.router)
app.include_router(university_matching.router)


# ─── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "service": "CivicFix Integrated Engine",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "features": [
            "AI Classification Engine → POST /api/v1/classify",
            "Duplicate Detection → POST /api/v1/duplicate-detection/check",
            "University Matching → POST /api/v1/matching/{problem_id}",
            "Marketplace → GET /api/v1/marketplace/solutions",
        ],
    }
