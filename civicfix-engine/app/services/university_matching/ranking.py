"""
Ranking helper — slices top-N from a pre-scored and sorted results list.
Source: UniversityMatchingAlgo/backend/app/services/ranking.py
"""


def top_n(ranked_results: list[dict], n: int = 5) -> list[dict]:
    return ranked_results[:n]


def get_latest_matching_result(db, problem_id: str) -> dict | None:
    return db.matching_results.find_one(
        {"problemId": problem_id}, sort=[("_id", -1)]
    )
