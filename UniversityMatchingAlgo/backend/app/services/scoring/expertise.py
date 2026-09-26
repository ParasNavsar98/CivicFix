"""
Expertise Match — 35% weight.

score = |matched required-expertise terms| / |required-expertise terms|
"""
from app.core.normalization import match_terms


def score_expertise(required_expertise: list[str], university: dict) -> dict:
    if not required_expertise:
        return {
            "score": 1.0,
            "matched": [],
            "unmatched": [],
            "explanation": "No specific expertise was required for this problem.",
        }

    available = (university.get("expertise") or []) + (university.get("researchAreas") or [])
    matched, unmatched = match_terms(required_expertise, available)

    score = len(matched) / len(required_expertise)
    score = min(score, 1.0)

    if matched and not unmatched:
        explanation = f"All required expertise matched: {', '.join(sorted(matched))}."
    elif matched:
        explanation = (
            f"Matched {len(matched)}/{len(required_expertise)} required expertise areas: "
            f"{', '.join(sorted(matched))}. Missing: {', '.join(sorted(unmatched))}."
        )
    else:
        explanation = "None of the required expertise areas were found at this university."

    return {
        "score": round(score, 4),
        "matched": sorted(matched),
        "unmatched": sorted(unmatched),
        "explanation": explanation,
    }
