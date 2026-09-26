"""
Matching Engine
===============
Runs all 7 deterministic scoring factors for a single (problem, university)
pair and combines them into one explainable, weighted final score.

This file does NOT touch the database directly for scoring logic (easier to
unit test) — it's given a university dict and a config dict, and returns a
plain dict result. The `run_matching_for_problem` function at the bottom is
the DB-aware entry point used by the API layer.
"""
from app.models.problem_input import ProblemInput
from app.models.matching_config import get_active_config, DEFAULT_WEIGHTS
from app.services.scoring.expertise import score_expertise
from app.services.scoring.faculty import score_faculty
from app.services.scoring.infrastructure import score_infrastructure
from app.services.scoring.past_projects import score_past_projects, DEFAULT_DIVISOR
from app.services.scoring.geography import score_geography
from app.services.scoring.capacity import score_capacity
from app.services.scoring.industry_ecosystem import score_industry_ecosystem


def score_university(
    problem: ProblemInput, university: dict, weights: dict | None = None, past_projects_divisor: int = DEFAULT_DIVISOR
) -> dict:
    """Pure function: score one university against one problem. No DB access."""
    w = weights or DEFAULT_WEIGHTS

    expertise = score_expertise(problem.required_expertise, university)
    faculty = score_faculty(problem.required_expertise, university)
    infrastructure = score_infrastructure(problem.required_resources, university)
    past_projects = score_past_projects(
        problem.primary_domain,
        problem.secondary_domains,
        problem.subcategory,
        problem.required_expertise,
        university,
        divisor=past_projects_divisor,
    )
    geography = score_geography(problem.location, university)
    capacity = score_capacity(university)
    industry = score_industry_ecosystem(problem.primary_domain, university)

    factor_scores = {
        "expertise": expertise["score"],
        "faculty": faculty["score"],
        "infrastructure": infrastructure["score"],
        "pastProjects": past_projects["score"],
        "geography": geography["score"],
        "capacity": capacity["score"],
        "industry": industry["score"],
    }

    final_score = round(
        sum(factor_scores[factor] * w[factor] for factor in factor_scores) * 100,
        2,
    )

    explanation_parts = [
        f"Expertise {expertise['score']:.2f}×{int(w['expertise']*100)}%",
        f"Faculty {faculty['score']:.2f}×{int(w['faculty']*100)}%",
        f"Infrastructure {infrastructure['score']:.2f}×{int(w['infrastructure']*100)}%",
        f"Past Projects {past_projects['score']:.2f}×{int(w['pastProjects']*100)}%",
        f"Geography {geography['score']:.2f}×{int(w['geography']*100)}%",
        f"Capacity {capacity['score']:.2f}×{int(w['capacity']*100)}%",
        f"Industry {industry['score']:.2f}×{int(w['industry']*100)}%",
    ]

    return {
        "universityId": university.get("universityId"),
        "universityName": university.get("institution", {}).get("name"),
        "finalScore": final_score,
        "factorScores": factor_scores,
        "matchedExpertise": expertise["matched"],
        "unmatchedExpertise": expertise["unmatched"],
        "matchedFaculty": faculty["matched_faculty"],
        "matchedInfrastructure": infrastructure["matched"],
        "relevantPastProjects": [p["title"] for p in past_projects["matched_projects"]],
        "geographyReason": geography["reason"],
        "capacityReason": capacity["explanation"],
        "industryReason": industry["explanation"],
        "explanation": "; ".join(explanation_parts) + f" => {final_score}/100.",
        "weightsUsed": dict(w),
    }


def run_matching_for_problem(db, problem: ProblemInput) -> list[dict]:
    """
    DB-aware entry point:
      1. loads active weights config
      2. fetches all ACTIVE universities
      3. scores every one
      4. sorts descending, deterministic tie-break
      5. persists the full ranked result to matching_results
      6. returns the ranked list (rank 1..N added)
    """
    config = get_active_config(db)
    weights = config["weights"]
    divisor = config.get("pastProjectsDivisor", DEFAULT_DIVISOR)

    universities = list(db.universities.find({"status": "ACTIVE"}))

    results = [score_university(problem, u, weights, divisor) for u in universities]

    # Deterministic sort: finalScore desc, then expertise factor desc, then universityId asc
    results.sort(
        key=lambda r: (
            -r["finalScore"],
            -r["factorScores"]["expertise"],
            r["universityId"] or "",
        )
    )

    for i, r in enumerate(results, start=1):
        r["rank"] = i

    db.matching_results.insert_one(
        {
            "problemId": problem.problem_id,
            "configVersion": config.get("version", 1),
            "results": results,
        }
    )

    return results
