"""
Infrastructure Match — 15% weight.

score = |matched required-resource terms| / |required-resource terms|
Compared against infrastructure + technologyCapabilities.
"""
from app.core.normalization import match_terms


def score_infrastructure(required_resources: list[str], university: dict) -> dict:
    if not required_resources:
        return {
            "score": 1.0,
            "matched": [],
            "unmatched": [],
            "explanation": "No specific resources/infrastructure were required for this problem.",
        }

    available = (university.get("infrastructure") or []) + (
        university.get("technologyCapabilities") or []
    )
    matched, unmatched = match_terms(required_resources, available)

    score = len(matched) / len(required_resources)
    score = min(score, 1.0)

    if matched and not unmatched:
        explanation = f"All required resources available: {', '.join(sorted(matched))}."
    elif matched:
        explanation = (
            f"Matched {len(matched)}/{len(required_resources)} required resources: "
            f"{', '.join(sorted(matched))}. Missing: {', '.join(sorted(unmatched))}."
        )
    else:
        explanation = "None of the required resources/infrastructure were found."

    return {
        "score": round(score, 4),
        "matched": sorted(matched),
        "unmatched": sorted(unmatched),
        "explanation": explanation,
    }
