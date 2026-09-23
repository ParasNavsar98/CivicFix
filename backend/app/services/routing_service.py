"""
Government & Research Routing Service.
SRS COMPLIANCE:
Translates validated classification flags into operational government/research routing.
Consequential routing decisions are backed by workflow state transitions and audit events.
"""

from typing import Any, Dict, Optional
from app.models.problem import Problem
from app.repositories.problem_repository import ProblemRepository
from app.services.audit_service import AuditService
from app.services.workflow import WorkflowService


class RoutingService:
    def __init__(self, problem_repository: ProblemRepository, audit_service: AuditService):
        self.problem_repo = problem_repository
        self.audit_service = audit_service

    @staticmethod
    def get_routing_recommendation(
        government_action_possible: Optional[bool], research_required: Optional[bool]
    ) -> str:
        """Determines AI-recommended routing destination based on classification flags."""
        govt = bool(government_action_possible)
        res = bool(research_required)

        if govt and res:
            return "BOTH"
        elif res:
            return "RESEARCH"
        else:
            return "GOVERNMENT"

    async def route_problem(
        self, problem_id: str, destination: str, actor_id: str, actor_role: str = "reviewer"
    ) -> Problem:
        """
        Executes routing transition for a validated problem to GOVERNMENT, RESEARCH, or BOTH.
        """
        problem = await self.problem_repo.get_by_id(problem_id)
        if not problem:
            raise ValueError(f"Problem with ID {problem_id} not found.")

        destination = destination.upper().strip()
        if destination == "GOVERNMENT":
            target_state = WorkflowService.ROUTED_GOVERNMENT
        elif destination == "RESEARCH":
            target_state = WorkflowService.ROUTED_RESEARCH
        elif destination == "BOTH":
            target_state = WorkflowService.ROUTED_BOTH
        else:
            raise ValueError(f"Invalid routing destination '{destination}'. Expected GOVERNMENT, RESEARCH, or BOTH.")

        prev_state = problem.status
        WorkflowService.validate_transition(prev_state, target_state)

        problem.status = target_state
        if destination in ("RESEARCH", "BOTH"):
            # Set secondary workflow status for university matching
            problem.status = WorkflowService.PENDING_MATCH

        saved_problem = await self.problem_repo.save(problem)

        await self.audit_service.log_event(
            entity_type="problem",
            entity_id=problem_id,
            actor_id=actor_id,
            actor_role=actor_role,
            action="ROUTING_CHANGED",
            previous_state=prev_state,
            new_state=saved_problem.status,
            metadata={"destination": destination},
        )

        return saved_problem
