"""
Reviewer Queue & Action API Endpoints.
SRS COMPLIANCE:
Enforces RBAC authorization — only authorized reviewers can view queue and execute actions.
"""

import uuid
from typing import Any
from fastapi import APIRouter, Header, HTTPException, Request, status
from app.schemas.common import StandardApiResponse
from app.schemas.reviewer import ReviewerActionRequest, ReviewerQueueResponse
from app.services.reviewer_service import ReviewerService

router = APIRouter(prefix="/api/reviewer", tags=["Reviewer"])


def get_reviewer_service(request: Request) -> ReviewerService:
    return request.app.state.reviewer_service


@router.get("/queue", response_model=StandardApiResponse)
async def get_reviewer_queue(
    request: Request,
    x_user_role: str = Header("reviewer", alias="X-User-Role"),
):
    """Retrieves pending problems in reviewer queue."""
    if x_user_role.lower() not in ("reviewer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only authorized reviewers can view the queue.",
        )

    reviewer_service = get_reviewer_service(request)
    queue = await reviewer_service.get_reviewer_queue()

    return StandardApiResponse(
        success=True,
        data={"count": len(queue), "queue": queue},
        requestId=f"REQ-{uuid.uuid4().hex[:8].upper()}",
    )


@router.post("/{problem_id}/action", response_model=StandardApiResponse)
async def execute_reviewer_action(
    problem_id: str,
    payload: ReviewerActionRequest,
    request: Request,
    x_user_id: str = Header("reviewer_001", alias="X-User-ID"),
    x_user_role: str = Header("reviewer", alias="X-User-Role"),
):
    """
    Executes a human reviewer action on a problem.
    Supported actions: ACCEPT, CORRECT, REQUEST_CLARIFICATION, MERGE_DUPLICATE, REJECT_INVALID, REQUEST_VERIFICATION, REDIRECT, ESCALATE.
    """
    if x_user_role.lower() not in ("reviewer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only authorized reviewers can execute actions.",
        )

    reviewer_service = get_reviewer_service(request)
    try:
        result = await reviewer_service.process_action(
            problem_id=problem_id,
            reviewer_id=x_user_id,
            action=payload.action,
            reason=payload.reason,
            master_problem_id=payload.masterProblemId,
            payload=payload.payload,
        )

        return StandardApiResponse(
            success=True,
            data=result,
            requestId=f"REQ-{uuid.uuid4().hex[:8].upper()}",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reviewer action execution error: {str(e)}",
        )
