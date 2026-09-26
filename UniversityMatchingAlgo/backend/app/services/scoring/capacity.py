"""
Current Capacity — 5% weight.

Explicit, deterministic handling of every edge case called out in the spec:
  - availability == UNAVAILABLE           -> 0.0
  - maximumProjects == 0                  -> 0.0 (can't divide, and means no slots exist)
  - activeProjects >= maximumProjects     -> 0.0 (no free slots, even if labelled AVAILABLE)
  - availability == LIMITED               -> free ratio capped at 50% of its raw value
  - availability == AVAILABLE             -> free ratio used directly
  - negative/missing numbers              -> treated as 0 (defensive default)
"""

VALID_AVAILABILITY = {"AVAILABLE", "LIMITED", "UNAVAILABLE"}


def score_capacity(university: dict) -> dict:
    capacity = university.get("capacity") or {}
    availability = capacity.get("availability", "UNKNOWN")
    active = capacity.get("activeProjects", 0) or 0
    maximum = capacity.get("maximumProjects", 0) or 0

    active = max(active, 0)
    maximum = max(maximum, 0)

    if availability not in VALID_AVAILABILITY:
        return {
            "score": 0.0,
            "explanation": f"Unrecognized/missing availability status ('{availability}') — treated as unavailable.",
        }

    if availability == "UNAVAILABLE":
        return {"score": 0.0, "explanation": "University marked UNAVAILABLE."}

    if maximum == 0:
        return {
            "score": 0.0,
            "explanation": "University has no project capacity configured (maximumProjects=0).",
        }

    if active >= maximum:
        return {
            "score": 0.0,
            "explanation": f"No free slots ({active}/{maximum} active projects).",
        }

    free_ratio = (maximum - active) / maximum

    if availability == "LIMITED":
        free_ratio *= 0.5
        note = "capacity is LIMITED, so free-slot ratio is discounted by half"
    else:  # AVAILABLE
        note = "capacity is AVAILABLE, free-slot ratio used directly"

    score = min(free_ratio, 1.0)

    return {
        "score": round(score, 4),
        "explanation": (
            f"{maximum - active} free slot(s) out of {maximum} ({note})."
        ),
    }
