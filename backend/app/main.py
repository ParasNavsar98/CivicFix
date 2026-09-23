"""
CivicFix Main Backend Orchestrator Application.

SRS COMPLIANCE:
- Modular Monolith backend application owning canonical problem data, workflow states, versioning, review queues, and append-only audit trails.
- Coordinates external Classification Engine (port 8000) and Duplicate Detection Engine (port 8001).
- Enforces Human-in-the-Loop decision boundaries.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.repositories.problem_repository import ProblemRepository
from app.repositories.version_repository import VersionRepository
from app.repositories.duplicate_repository import DuplicateRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.audit_repository import AuditRepository
from app.services.audit_service import AuditService
from app.services.routing_service import RoutingService
from app.services.reviewer_service import ReviewerService
from app.services.orchestrator import ProblemIntakeOrchestrator
from app.clients.classification_client import ClassificationClient
from app.clients.duplicate_client import DuplicateClient

from app.api.problems import router as problems_router
from app.api.reviewer import router as reviewer_router
from app.api.routing import router as routing_router
from app.api.health import router as health_router


def create_app(
    problem_repo: ProblemRepository = None,
    version_repo: VersionRepository = None,
    duplicate_repo: DuplicateRepository = None,
    review_repo: ReviewRepository = None,
    audit_repo: AuditRepository = None,
    classification_client: ClassificationClient = None,
    duplicate_client: DuplicateClient = None,
) -> FastAPI:
    """Factory function for creating CivicFix FastAPI main backend application."""
    
    # Initialize Repositories
    p_repo = problem_repo or ProblemRepository()
    v_repo = version_repo or VersionRepository()
    d_repo = duplicate_repo or DuplicateRepository()
    r_repo = review_repo or ReviewRepository()
    a_repo = audit_repo or AuditRepository()

    # Initialize Services
    audit_svc = AuditService(a_repo)
    routing_svc = RoutingService(p_repo, audit_svc)
    reviewer_svc = ReviewerService(p_repo, v_repo, r_repo, d_repo, audit_svc)

    cls_client = classification_client or ClassificationClient(
        base_url=settings.CLASSIFICATION_SERVICE_URL,
        timeout=settings.CLASSIFICATION_SERVICE_TIMEOUT,
    )
    dup_client = duplicate_client or DuplicateClient(
        base_url=settings.DUPLICATE_DETECTION_SERVICE_URL,
        timeout=settings.DUPLICATE_DETECTION_SERVICE_TIMEOUT,
    )

    orchestrator = ProblemIntakeOrchestrator(
        problem_repo=p_repo,
        version_repo=v_repo,
        duplicate_repo=d_repo,
        audit_service=audit_svc,
        classification_client=cls_client,
        duplicate_client=dup_client,
    )

    app = FastAPI(
        title="CivicFix Main Backend Orchestrator API",
        description=(
            "Central backend service managing CivicFix societal innovation problem workflows, "
            "AI microservice integration, human reviewer queues, audit trails, and government/research routing."
        ),
        version="1.0.0",
    )

    # Attach State Dependencies
    app.state.problem_repo = p_repo
    app.state.version_repo = v_repo
    app.state.duplicate_repo = d_repo
    app.state.review_repo = r_repo
    app.state.audit_repo = a_repo
    app.state.audit_service = audit_svc
    app.state.routing_service = routing_svc
    app.state.reviewer_service = reviewer_svc
    app.state.orchestrator = orchestrator

    # Include Routers
    app.include_router(problems_router)
    app.include_router(reviewer_router)
    app.include_router(routing_router)
    app.include_router(health_router)

    return app


app = create_app()
