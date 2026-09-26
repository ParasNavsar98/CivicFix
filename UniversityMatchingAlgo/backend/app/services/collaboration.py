"""
Industry Express Interest -> Accept/Reject -> Collaboration.
No automatic partnership: acceptance is always an explicit action by the
solution's owning university/project owner.
"""
import uuid
from datetime import datetime, timezone


class CollaborationError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc)


def express_interest(
    db,
    solution_id: str,
    partner_id: str,
    support_offered: list[str],
    contribution: dict,
    message: str,
) -> dict:
    solution = db.solutions.find_one({"solutionId": solution_id, "status": "PUBLISHED"})
    if not solution:
        raise CollaborationError(f"Solution {solution_id} not found or not published.")

    duplicate = db.industry_interests.find_one(
        {"solutionId": solution_id, "partnerId": partner_id, "status": "PENDING"}
    )
    if duplicate:
        raise CollaborationError(
            f"Partner {partner_id} already has a pending interest in {solution_id}."
        )

    doc = {
        "interestId": f"INT-{uuid.uuid4().hex[:10].upper()}",
        "solutionId": solution_id,
        "partnerId": partner_id,
        "supportOffered": support_offered,
        "contribution": contribution,
        "message": message,
        "status": "PENDING",
        "createdAt": _now(),
        "respondedAt": None,
        "rejectionReason": None,
    }
    db.industry_interests.insert_one(doc)
    return doc


def get_interests_for_solution(db, solution_id: str) -> list[dict]:
    return list(db.industry_interests.find({"solutionId": solution_id}, {"_id": 0}))


def _authorize_owner(db, solution_id: str, acting_user_id: str) -> dict:
    solution = db.solutions.find_one({"solutionId": solution_id})
    if not solution:
        raise CollaborationError(f"Solution {solution_id} not found.")
    # MVP authorization: acting user must be tied to the owning university.
    # `owner_check` is intentionally simple/pluggable — swap in real auth once
    # the main platform's user/university linkage is available.
    if solution.get("universityId") != acting_user_id and acting_user_id != "ADMIN":
        raise CollaborationError(
            "Not authorized: only the owning university/project owner may respond to this interest."
        )
    return solution


def accept_interest(db, interest_id: str, acting_user_id: str) -> dict:
    interest = db.industry_interests.find_one({"interestId": interest_id})
    if not interest:
        raise CollaborationError(f"Interest {interest_id} not found.")
    if interest["status"] != "PENDING":
        raise CollaborationError(f"Interest {interest_id} is not PENDING (status={interest['status']}).")

    _authorize_owner(db, interest["solutionId"], acting_user_id)

    now = _now()
    db.industry_interests.update_one(
        {"interestId": interest_id},
        {"$set": {"status": "ACCEPTED", "respondedAt": now}},
    )

    collaboration = {
        "collaborationId": f"COL-{uuid.uuid4().hex[:10].upper()}",
        "solutionId": interest["solutionId"],
        "partnerId": interest["partnerId"],
        "acceptedBy": acting_user_id,
        "supportDetails": {
            "supportOffered": interest["supportOffered"],
            "contribution": interest["contribution"],
        },
        "status": "ACTIVE",
        "createdAt": now,
        "updatedAt": now,
    }
    db.collaborations.insert_one(collaboration)
    return collaboration


def reject_interest(db, interest_id: str, acting_user_id: str, reason: str) -> dict:
    if not reason or not reason.strip():
        raise CollaborationError("A rejection reason is required.")

    interest = db.industry_interests.find_one({"interestId": interest_id})
    if not interest:
        raise CollaborationError(f"Interest {interest_id} not found.")
    if interest["status"] != "PENDING":
        raise CollaborationError(f"Interest {interest_id} is not PENDING (status={interest['status']}).")

    _authorize_owner(db, interest["solutionId"], acting_user_id)

    now = _now()
    db.industry_interests.update_one(
        {"interestId": interest_id},
        {"$set": {"status": "REJECTED", "respondedAt": now, "rejectionReason": reason}},
    )
    return db.industry_interests.find_one({"interestId": interest_id}, {"_id": 0})
