"""
Categorization Adapter
=======================
This is the single translation boundary between the categorization system's
output (see their README — classification JSON with severityAssessment,
peopleAffected, duplicate-detection, etc.) and OUR internal ProblemInput.

Rules enforced here, deliberately, per project scope:
  - severity, severityAssessment, urgency, confidence, peopleAffected,
    reasoning, severityEvidence are read (if useful for logging) but are
    NEVER forwarded into anything that reaches the scoring engine.
  - researchRequired / governmentActionPossible are passed through ONLY as
    gates on whether matching should run at all — never as score inputs.
  - location does NOT come from the classification JSON (it doesn't contain
    any). It comes from the original problem record (citizen submission).
    Callers must supply it separately.

If the real categorization system's schema changes, this is the ONLY file
that needs to change — the rest of the matching engine is unaffected.
"""
from app.models.problem_input import ProblemInput, ProblemLocation


class CategorizationAdapterError(ValueError):
    pass


REQUIRED_CLASSIFICATION_FIELDS = [
    "primaryDomain",
    "subcategory",
    "requiredExpertise",
    "requiredResources",
]


def adapt_classification_output(
    problem_id: str,
    classification_json: dict,
    location: dict,
) -> ProblemInput:
    """
    classification_json: the exact JSON documented in the categorization
        system's README (their `Classification Engine` output).
    location: {"district": str, "state": str, "latitude": float|None,
               "longitude": float|None} — sourced from the original problem
        record, NOT from classification_json.
    """
    missing = [f for f in REQUIRED_CLASSIFICATION_FIELDS if f not in classification_json]
    if missing:
        raise CategorizationAdapterError(
            f"classification_json is missing required fields: {missing}"
        )

    if "district" not in location or "state" not in location:
        raise CategorizationAdapterError(
            "location must include at least 'district' and 'state'"
        )

    return ProblemInput(
        problem_id=problem_id,
        primary_domain=classification_json["primaryDomain"],
        subcategory=classification_json["subcategory"],
        secondary_domains=classification_json.get("secondaryDomains", []) or [],
        required_expertise=classification_json.get("requiredExpertise", []) or [],
        required_resources=classification_json.get("requiredResources", []) or [],
        location=ProblemLocation(
            district=location["district"],
            state=location["state"],
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
        ),
        research_required=bool(classification_json.get("researchRequired", False)),
        government_action_possible=bool(
            classification_json.get("governmentActionPossible", True)
        ),
    )


def should_attempt_university_matching(problem_input: ProblemInput) -> tuple[bool, str]:
    """
    Gate check — decides WHETHER matching should run, never HOW WELL a
    university scores. Returns (should_run, reason).

    Current rule (adjust as the real workflow is clarified with your team):
    if the classifier says government action isn't reasonably applicable,
    routing to a university may still be valid (research angle), so we only
    block matching if there's neither a government route NOR a research
    angle — i.e. genuinely nothing actionable was identified upstream.
    """
    if not problem_input.government_action_possible and not problem_input.research_required:
        return False, "Neither government action nor research was flagged as applicable."
    if not problem_input.required_expertise and not problem_input.required_resources:
        return False, "No required expertise or resources were identified for this problem."
    return True, "OK"
