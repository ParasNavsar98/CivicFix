"""
Relevant Past Projects — 10% weight.

A past project "counts" as relevant if it shares >=1 domain (primary or
secondary, or subcategory) OR >=1 expertise term with the problem.

score = min(matchedProjectCount / divisor, 1.0)
`divisor` is configurable (default 2 -> two or more relevant past projects
gives full score) rather than a magic number buried in logic.
"""
from app.core.normalization import normalize_terms, build_synonym_lookup

DEFAULT_DIVISOR = 2


def score_past_projects(
    primary_domain: str,
    secondary_domains: list[str],
    subcategory: str,
    required_expertise: list[str],
    university: dict,
    divisor: int = DEFAULT_DIVISOR,
) -> dict:
    past_projects = university.get("pastProjects") or []
    if not past_projects:
        return {
            "score": 0.0,
            "matched_projects": [],
            "explanation": "University has no recorded past projects.",
        }

    lookup = build_synonym_lookup()
    problem_domains = normalize_terms([primary_domain, subcategory, *secondary_domains], lookup)
    problem_expertise = normalize_terms(required_expertise, lookup)

    matched_projects = []
    for project in past_projects:
        project_domains = normalize_terms(project.get("domains") or [], lookup)
        project_expertise = normalize_terms(project.get("expertise") or [], lookup)

        domain_overlap = problem_domains & project_domains
        expertise_overlap = problem_expertise & project_expertise

        if domain_overlap or expertise_overlap:
            matched_projects.append(
                {
                    "title": project.get("title", "Untitled project"),
                    "matchedDomains": sorted(domain_overlap),
                    "matchedExpertise": sorted(expertise_overlap),
                }
            )

    score = min(len(matched_projects) / divisor, 1.0) if divisor > 0 else 0.0

    if matched_projects:
        titles = ", ".join(p["title"] for p in matched_projects)
        explanation = f"{len(matched_projects)} relevant past project(s) found: {titles}."
    else:
        explanation = "No past projects overlap with this problem's domain or expertise."

    return {
        "score": round(score, 4),
        "matched_projects": matched_projects,
        "explanation": explanation,
    }
