"""
Faculty Expertise — 20% weight.

For each required expertise term, check whether at least one AVAILABLE
faculty member (availableForProjects == True) covers it (via expertise or
researchAreas). score = |required terms covered by >=1 faculty| / |required|
"""
from app.core.normalization import build_synonym_lookup, match_terms


def score_faculty(required_expertise: list[str], university: dict) -> dict:
    if not required_expertise:
        return {
            "score": 1.0,
            "matched_faculty": [],
            "covered_expertise": [],
            "uncovered_expertise": [],
            "explanation": "No specific expertise was required for this problem.",
        }

    faculty_list = university.get("faculty") or []
    available_faculty = [f for f in faculty_list if f.get("availableForProjects", False)]

    lookup = build_synonym_lookup()
    covered_expertise: set[str] = set()
    matched_faculty_ids: set[str] = set()

    for faculty in available_faculty:
        faculty_terms = (faculty.get("expertise") or []) + (faculty.get("researchAreas") or [])
        matched, _ = match_terms(required_expertise, faculty_terms, lookup)
        if matched:
            covered_expertise |= matched
            matched_faculty_ids.add(faculty.get("facultyId", faculty.get("name", "unknown")))

    uncovered = set(required_expertise) - covered_expertise
    score = len(covered_expertise) / len(required_expertise)
    score = min(score, 1.0)

    if not available_faculty:
        explanation = "No faculty are currently marked as available for projects."
    elif covered_expertise and not uncovered:
        explanation = (
            f"All required expertise covered by available faculty: "
            f"{', '.join(sorted(matched_faculty_ids))}."
        )
    elif covered_expertise:
        explanation = (
            f"{len(covered_expertise)}/{len(required_expertise)} required expertise areas "
            f"covered by faculty {', '.join(sorted(matched_faculty_ids))}; "
            f"not covered: {', '.join(sorted(uncovered))}."
        )
    else:
        explanation = "No available faculty cover the required expertise."

    return {
        "score": round(score, 4),
        "matched_faculty": sorted(matched_faculty_ids),
        "covered_expertise": sorted(covered_expertise),
        "uncovered_expertise": sorted(uncovered),
        "explanation": explanation,
    }
