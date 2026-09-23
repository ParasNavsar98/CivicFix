"""
Centralized Workflow State Machine for CivicFix.
SRS COMPLIANCE:
Enforces valid status state transitions and prevents arbitrary status assignments across controllers.
"""

class WorkflowStateError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class WorkflowService:
    # Defined State Constants
    SUBMITTED = "SUBMITTED"
    AI_PROCESSING = "AI_PROCESSING"
    AI_PENDING = "AI_PENDING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    PENDING_CLARIFICATION = "PENDING_CLARIFICATION"
    VALIDATED = "VALIDATED"
    ROUTED_GOVERNMENT = "ROUTED_GOVERNMENT"
    ROUTED_RESEARCH = "ROUTED_RESEARCH"
    ROUTED_BOTH = "ROUTED_BOTH"
    PENDING_MATCH = "PENDING_MATCH"
    REJECTED = "REJECTED"
    MERGED_DUPLICATE = "MERGED_DUPLICATE"

    # Allowed Transitions Mapping
    _ALLOWED_TRANSITIONS = {
        SUBMITTED: {AI_PROCESSING, AI_PENDING, REJECTED},
        AI_PROCESSING: {REVIEW_REQUIRED, VALIDATED, AI_PENDING, REJECTED},
        AI_PENDING: {AI_PROCESSING, REVIEW_REQUIRED, VALIDATED, REJECTED},
        REVIEW_REQUIRED: {VALIDATED, PENDING_CLARIFICATION, MERGED_DUPLICATE, REJECTED, ROUTED_GOVERNMENT, ROUTED_RESEARCH, ROUTED_BOTH},
        PENDING_CLARIFICATION: {AI_PROCESSING, REVIEW_REQUIRED, VALIDATED, REJECTED},
        VALIDATED: {ROUTED_GOVERNMENT, ROUTED_RESEARCH, ROUTED_BOTH, PENDING_MATCH, MERGED_DUPLICATE, REJECTED},
        ROUTED_GOVERNMENT: {VALIDATED, REJECTED},
        ROUTED_RESEARCH: {PENDING_MATCH, VALIDATED, REJECTED},
        ROUTED_BOTH: {PENDING_MATCH, VALIDATED, REJECTED},
        PENDING_MATCH: {VALIDATED, ROUTED_RESEARCH},
        REJECTED: set(),  # Terminal state
        MERGED_DUPLICATE: set(),  # Terminal state
    }

    @classmethod
    def validate_transition(cls, current_state: str, next_state: str) -> None:
        """
        Validates whether transitioning from current_state to next_state is permitted.
        Raises WorkflowStateError if transition is illegal.
        """
        if current_state == next_state:
            return  # Idempotent re-entry permitted

        allowed = cls._ALLOWED_TRANSITIONS.get(current_state, set())
        if next_state not in allowed:
            raise WorkflowStateError(
                f"Invalid workflow transition from '{current_state}' to '{next_state}'. Allowed target states: {sorted(list(allowed))}"
            )
