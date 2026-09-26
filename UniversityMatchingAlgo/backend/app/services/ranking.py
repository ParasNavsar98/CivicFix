"""
Thin helper around a full ranked results list (already sorted/ranked by
matching_engine.run_matching_for_problem) — just slices top 5.
Kept separate from the engine because "who is suitable" (scoring) and
"who gets contacted" (assignment) are different concerns.
"""


def top_n(ranked_results: list[dict], n: int = 5) -> list[dict]:
    return ranked_results[:n]


def get_latest_matching_result(db, problem_id: str) -> dict | None:
    return db.matching_results.find_one(
        {"problemId": problem_id}, sort=[("_id", -1)]
    )
