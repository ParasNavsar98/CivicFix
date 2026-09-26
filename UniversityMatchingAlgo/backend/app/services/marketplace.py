"""
Industry Marketplace — filtering only. NO scoring, NO ranking, NO AI.
Only PUBLISHED + PUBLIC solutions are ever visible here.
"""

ARRAY_FIELDS = {"supportNeeded", "partnerType"}


def build_solution_filter(
    domain: str | None = None,
    subcategory: str | None = None,
    state: str | None = None,
    district: str | None = None,
    development_stage: str | None = None,
    support_needed: list[str] | None = None,
    partner_type: list[str] | None = None,
) -> dict:
    query: dict = {"status": "PUBLISHED", "visibility": "PUBLIC"}

    if domain:
        query["domain"] = domain
    if subcategory:
        query["subcategory"] = subcategory
    if state:
        query["location.state"] = state
    if district:
        query["location.district"] = district
    if development_stage:
        query["developmentStage"] = development_stage
    if support_needed:
        # solution matches if it needs AT LEAST ONE of the requested support types
        query["supportNeeded"] = {"$in": support_needed}
    if partner_type:
        query["partnerType"] = {"$in": partner_type}

    return query


def search_solutions(db, **filters) -> list[dict]:
    query = build_solution_filter(**filters)
    return list(db.solutions.find(query, {"_id": 0}))


def get_solution(db, solution_id: str) -> dict | None:
    return db.solutions.find_one(
        {"solutionId": solution_id, "status": "PUBLISHED", "visibility": "PUBLIC"},
        {"_id": 0},
    )
