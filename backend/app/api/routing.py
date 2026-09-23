"""
Routing & Audit Trail API Endpoints.
"""

import uuid
from typing import Any
from fastapi import APIRouter, Header, HTTPException, Request, status
from app.schemas.common import StandardApiResponse
from app.services.routing_service import RoutingService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api", tags=["Routing & Audit"])


def get_routing_service(request: Request) -> RoutingService:
    return request.app.state.routing_service


def get_audit_service(request: Request) -> AuditService:
    return request.app.state.audit_service


@router.post("/government/{problem_id}/route", response_model=StandardApiResponse)
async def route_problem(
    problem_id: str,
    request: Request,
    destination: str = "GOVERNMENT",
    x_user_id: str = Header("reviewer_001", alias="X-User-ID"),
    x_user_role: str = Header("reviewer", alias="X-User-Role"),
):
    """Routes a validated problem to GOVERNMENT, RESEARCH, or BOTH."""
    if x_user_role.lower() not in ("reviewer", "admin", "government_official"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only authorized roles can execute routing.",
        )

    routing_service = get_routing_service(request)
    try:
        updated = await routing_service.route_problem(
            problem_id=problem_id,
            destination=destination,
            actor_id=x_user_id,
            actor_role=x_user_role,
        )

        return StandardApiResponse(
            success=True,
            data=updated.model_dump(),
            requestId=f"REQ-{uuid.uuid4().hex[:8].upper()}",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/audit/{entity_id}", response_model=StandardApiResponse)
async def get_audit_trail(entity_id: str, request: Request):
    """Retrieves append-only audit trail events for an entity."""
    audit_service = get_audit_service(request)
    events = await audit_service.get_trail(entity_id)

    return StandardApiResponse(
        success=True,
        data={"entityId": entity_id, "count": len(events), "events": [e.model_dump() for e in events]},
        requestId=f"REQ-{uuid.uuid4().hex[:8].upper()}",
    )
