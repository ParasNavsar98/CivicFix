"""
Health check API route.
"""
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health check")
def health():
    return {"status": "healthy", "service": "civicfix-engine"}


@router.get("/api/v1/health", summary="Health check (versioned)")
def health_v1():
    return {"status": "healthy", "service": "civicfix-engine", "version": "1.0.0"}
