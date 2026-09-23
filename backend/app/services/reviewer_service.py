"""
Reviewer Service for CivicFix Main Backend.
SRS COMPLIANCE:
Implements human reviewer action queue operations.
AI assists and structures; human reviewers own all consequential decisions.
MERGE_DUPLICATE links candidate to master while strictly preserving original submission.
CORRECT creates a new problem version without overwriting historical AI interpretation.
"""

import uuid
from typing import Any, Dict, List, Optional
from app.models.problem import Problem
from app.models.review import ReviewActionRecord, ReviewerActionEnum
from app.models.version import ProblemVersion
from app.models.duplicate_candidate import DuplicateCandidateRecord
from app.repositories.problem_repository import ProblemRepository
from app.repositories.version_repository import VersionRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.duplicate_repository import DuplicateRepository
from app.services.audit_service import AuditService
from app.services.workflow import WorkflowService


class ReviewerService:
    def __init__(
        self,
        problem_repo: ProblemRepository,
        version_repo: VersionRepository,
        review_repo: ReviewRepository,
        duplicate_repo: DuplicateRepository,
        audit_service: AuditService,
    ):
        self.problem_repo = problem_repo
        self.version_repo = version_repo
        self.review_repo = review_repo
        self.duplicate_repo = duplicate_repo
        self.audit_service = audit_service

    async def get_reviewer_queue(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves pending problems in reviewer queue enriched with classification summary,
        duplicate candidates, and explainable reasons.
        """
        problems = await self.problem_repo.list_reviewer_queue(limit=limit)
        enriched_queue = []

        for p in problems:
            versions = await self.version_repo.list_versions_for_problem(p.problemId)
            duplicates = await self.duplicate_repo.list_candidates_for_problem(p.problemId)

            active_ver = versions[-1] if versions else None
            enriched_queue.append({
                "problem": p.model_dump(),
                "activeVersion": active_ver.model_dump() if active_ver else None,
                "duplicateCandidates": [d.model_dump() for d in duplicates],
                "versionHistoryCount": len(versions),
            })

        return enriched_queue

    async def process_action(
        self,
        problem_id: str,
        reviewer_id: str,
        action: ReviewerActionEnum,
        reason: Optional[str] = None,
        master_problem_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executes an authorized human reviewer action on a problem record.
        """
        problem = await self.problem_repo.get_by_id(problem_id)
        if not problem:
            raise ValueError(f"Problem with ID {problem_id} not found.")

        payload = payload or {}
        prev_state = problem.status

        # Execute Action Specific Logic
        if action == ReviewerActionEnum.ACCEPT:
            target_state = WorkflowService.VALIDATED
            WorkflowService.validate_transition(prev_state, target_state)
            problem.status = target_state
            problem.reviewRequired = False

        elif action == ReviewerActionEnum.CORRECT:
            target_state = WorkflowService.VALIDATED
            WorkflowService.validate_transition(prev_state, target_state)
            problem.status = target_state
            problem.reviewRequired = False

            # Update problem fields from payload if supplied
            if "primaryDomain" in payload:
                problem.primaryDomain = payload["primaryDomain"]
            if "subcategory" in payload:
                problem.subcategory = payload["subcategory"]
            if "secondaryDomains" in payload:
                problem.secondaryDomains = payload["secondaryDomains"]
            if "severity" in payload:
                problem.severity = payload["severity"]
            if "urgency" in payload:
                problem.urgency = payload["urgency"]
            if "title" in payload:
                problem.title = payload["title"]
            if "description" in payload:
                problem.description = payload["description"]

            # Create NEW Reviewer Version snapshot (preserving historical AI version)
            ver_id = f"VER-{uuid.uuid4().hex[:8].upper()}"
            new_version = ProblemVersion(
                versionId=ver_id,
                problemId=problem.problemId,
                source="reviewer",
                title=problem.title,
                description=problem.description,
                primaryDomain=problem.primaryDomain,
                secondaryDomains=problem.secondaryDomains,
                subcategory=problem.subcategory,
                severity=problem.severity,
                urgency=problem.urgency,
                publicSummary=problem.publicSummary,
                reasoning=reason or "Human reviewer correction",
                createdBy=reviewer_id,
                changeReason=reason or "Reviewer taxonomy correction",
            )
            await self.version_repo.save_version(new_version)
            problem.currentProblemVersionId = ver_id

        elif action == ReviewerActionEnum.REQUEST_CLARIFICATION:
            target_state = WorkflowService.PENDING_CLARIFICATION
            WorkflowService.validate_transition(prev_state, target_state)
            problem.status = target_state
            problem.reviewRequired = True
            if reason:
                problem.reviewReasons.append(f"Clarification requested: {reason}")

        elif action == ReviewerActionEnum.MERGE_DUPLICATE:
            if not master_problem_id:
                raise ValueError("masterProblemId is required to perform MERGE_DUPLICATE action.")

            master = await self.problem_repo.get_by_id(master_problem_id)
            if not master:
                raise ValueError(f"Master problem with ID {master_problem_id} not found.")

            target_state = WorkflowService.MERGED_DUPLICATE
            WorkflowService.validate_transition(prev_state, target_state)

            # Preserve duplicate submission record — DO NOT DELETE
            problem.status = target_state
            problem.masterProblemId = master_problem_id
            problem.duplicateStatus = "merged"
            problem.reviewRequired = False

            # Update duplicate candidate records for this problem
            cands = await self.duplicate_repo.list_candidates_for_problem(problem_id)
            for c in cands:
                if c.candidateProblemId == master_problem_id:
                    c.status = "confirmed_duplicate"
                    await self.duplicate_repo.save_candidate(c)

        elif action == ReviewerActionEnum.REJECT_INVALID:
            if not reason:
                raise ValueError("A reason is required to perform REJECT_INVALID action.")

            target_state = WorkflowService.REJECTED
            WorkflowService.validate_transition(prev_state, target_state)
            problem.status = target_state
            problem.reviewRequired = False

        elif action in (ReviewerActionEnum.REQUEST_VERIFICATION, ReviewerActionEnum.REDIRECT, ReviewerActionEnum.ESCALATE):
            target_state = WorkflowService.VALIDATED
            if prev_state in (WorkflowService.REVIEW_REQUIRED, WorkflowService.AI_PROCESSING):
                WorkflowService.validate_transition(prev_state, target_state)
                problem.status = target_state
                problem.reviewRequired = False

        else:
            raise ValueError(f"Unsupported action {action}")

        # Save Updated Problem
        saved_problem = await self.problem_repo.save(problem)

        # Log Review Action Record
        rev_id = f"REV-{uuid.uuid4().hex[:8].upper()}"
        review_record = ReviewActionRecord(
            reviewId=rev_id,
            problemId=problem_id,
            reviewerId=reviewer_id,
            action=action,
            reason=reason,
            masterProblemId=master_problem_id,
            payload=payload,
            previousState=prev_state,
            newState=saved_problem.status,
        )
        await self.review_repo.save_review(review_record)

        # Log Audit Event
        await self.audit_service.log_event(
            entity_type="problem",
            entity_id=problem_id,
            actor_id=reviewer_id,
            actor_role="reviewer",
            action=f"CLASSIFICATION_{action.value}",
            previous_state=prev_state,
            new_state=saved_problem.status,
            metadata={"reason": reason, "masterProblemId": master_problem_id},
        )

        return {
            "problem": saved_problem.model_dump(),
            "reviewRecord": review_record.model_dump(),
        }
