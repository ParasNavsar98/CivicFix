"""
Health and Readiness API Endpoint for CivicFix Main Backend.
"""

from typing import Any, Dict
import httpx
from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Returns status of main backend service."""
    return {
        "status": "ok",
        "service": "CivicFix Main Backend Orchestrator",
        "version": "1.0.0",
        "database": "MongoDB / MemoryStore Active",
    }


@router.get("/health/dependencies", response_model=Dict[str, Any])
async def dependency_health_check():
    """
    Checks connection readiness of classification-engine and duplicate-detection microservices.
    Degraded service state does NOT crash main backend.
    """
    classification_status = "unavailable"
    duplicate_status = "unavailable"

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.CLASSIFICATION_SERVICE_URL}/health")
            if resp.status_code == 200:
                classification_status = "healthy"
    except Exception:
        classification_status = "unreachable"

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.DUPLICATE_DETECTION_SERVICE_URL}/health")
            if resp.status_code == 200:
                duplicate_status = "healthy"
    except Exception:
        duplicate_status = "unreachable"

    overall = "healthy" if (classification_status == "healthy" and duplicate_status == "healthy") else "degraded"

    return {
        "status": overall,
        "dependencies": {
            "classificationEngine": classification_status,
            "duplicateDetectionEngine": duplicate_status,
        }
    }
