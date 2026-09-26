"""
Geographic Relevance — 10% weight. Deterministic table, no distance math:
  same district      -> 1.0
  same state, diff district -> 0.6
  different state     -> 0.2
"""


def score_geography(problem_location, university: dict) -> dict:
    uni_location = university.get("institution", {}).get("location", {})
    uni_district = (uni_location.get("district") or "").strip().lower()
    uni_state = (uni_location.get("state") or "").strip().lower()

    problem_district = (problem_location.district or "").strip().lower()
    problem_state = (problem_location.state or "").strip().lower()

    if problem_district and problem_district == uni_district and problem_state == uni_state:
        return {
            "score": 1.0,
            "reason": f"Same district ({university.get('institution', {}).get('location', {}).get('district')}).",
        }
    if problem_state and problem_state == uni_state:
        return {
            "score": 0.6,
            "reason": f"Same state ({university.get('institution', {}).get('location', {}).get('state')}), different district.",
        }
    return {
        "score": 0.2,
        "reason": "Different state from the problem location.",
    }
