"""
Categorization Adapter — translates classification output into ProblemInput.
Source: UniversityMatchingAlgo/backend/app/integrations/categorization_adapter.py

Import paths updated to use civicfix-engine's internal service paths.
"""
from app.services.university_matching.problem_input import ProblemInput, ProblemLocation


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
    classification_json: the classification engine's output JSON.
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
    """
    if not problem_input.government_action_possible and not problem_input.research_required:
        return False, "Neither government action nor research was flagged as applicable."
    if not problem_input.required_expertise and not problem_input.required_resources:
        return False, "No required expertise or resources were identified for this problem."
    return True, "OK"
