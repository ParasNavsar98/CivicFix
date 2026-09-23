"""
Citizen Problem Submission and Status API Endpoints.
"""

import uuid
from typing import Any, Dict
from fastapi import APIRouter, Header, HTTPException, Request, status
from app.schemas.common import StandardApiResponse
from app.schemas.problem import ProblemCreateRequest, ProblemTimelineResponse, ProblemTimelineStep
from app.services.orchestrator import ProblemIntakeOrchestrator
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/problems", tags=["Problems"])


def get_orchestrator(request: Request) -> ProblemIntakeOrchestrator:
    return request.app.state.orchestrator


def get_audit_service(request: Request) -> AuditService:
    return request.app.state.audit_service


@router.post("", response_model=StandardApiResponse)
async def create_problem(
    payload: ProblemCreateRequest,
    request: Request,
    x_user_id: str = Header("citizen_001", alias="X-User-ID"),
    x_user_role: str = Header("citizen", alias="X-User-Role"),
):
    """
    Submits a new citizen problem.
    Stores problem FIRST in database, then executes AI Classification and Duplicate Detection.
    """
    try:
        orchestrator = get_orchestrator(request)
        prob_dict = payload.model_dump()
        problem = await orchestrator.submit_problem(prob_dict, submitter_id=x_user_id)

        # Trigger processing pipeline
        processed_problem = await orchestrator.process_problem(problem.problemId)

        return StandardApiResponse(
            success=True,
            data=processed_problem.model_dump(),
            requestId=f"REQ-{uuid.uuid4().hex[:8].upper()}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Problem submission error: {str(e)}",
        )


@router.get("/{problem_id}", response_model=StandardApiResponse)
async def get_problem(problem_id: str, request: Request):
    """Retrieves problem details by ID."""
    orchestrator = get_orchestrator(request)
    problem = await orchestrator.problem_repo.get_by_id(problem_id)
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Problem {problem_id} not found.")

    return StandardApiResponse(
        success=True,
        data=problem.model_dump(),
        requestId=f"REQ-{uuid.uuid4().hex[:8].upper()}",
    )


@router.get("/{problem_id}/timeline", response_model=StandardApiResponse)
async def get_problem_timeline(problem_id: str, request: Request):
    """
    Returns citizen status timeline for a problem.
    Suppresses private reviewer notes and raw internal prompts.
    """
    orchestrator = get_orchestrator(request)
    audit_service = get_audit_service(request)

    problem = await orchestrator.problem_repo.get_by_id(problem_id)
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Problem {problem_id} not found.")

    audit_events = await audit_service.get_trail(problem_id)

    timeline_steps = []
    for ev in audit_events:
        summary_text = f"Action: {ev.action}"
        if ev.action == "PROBLEM_CREATED":
            summary_text = "Your problem submission was received and stored."
        elif ev.action == "AI_PROCESSING_STARTED":
            summary_text = "AI automated analysis in progress."
        elif ev.action == "AI_CLASSIFICATION_COMPLETED":
            summary_text = "AI domain classification analysis completed."
        elif ev.action == "DUPLICATE_ANALYSIS_COMPLETED":
            summary_text = "Duplicate check completed."
        elif ev.action == "CLASSIFICATION_ACCEPTED":
            summary_text = "Problem review completed and validated by team."
        elif ev.action == "ROUTING_CHANGED":
            summary_text = f"Problem routed to target sector ({ev.metadata.get('destination', 'Government')})."

        timeline_steps.append(
            ProblemTimelineStep(
                step=ev.action,
                status=ev.newState or problem.status,
                timestamp=ev.timestamp,
                summary=summary_text,
            ).model_dump()
        )

    return StandardApiResponse(
        success=True,
        data={
            "problemId": problem.problemId,
            "title": problem.title,
            "currentStatus": problem.status,
            "timeline": timeline_steps,
        },
        requestId=f"REQ-{uuid.uuid4().hex[:8].upper()}",
    )
