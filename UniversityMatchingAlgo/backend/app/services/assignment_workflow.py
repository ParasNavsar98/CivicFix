"""
Sequential University Assignment Workflow
==========================================
Only ONE university is ever actively "SENT" a request at a time per problem.
Ranks 2-5 sit as PENDING until the university ahead of them rejects or
times out.

Timeout strategy: LAZY evaluation. We don't run a background scheduler
(no infra needed for the MVP/hackathon scope) — instead, every time an
assignment is read or acted on, we first check `now >= deadline` and, if
so, resolve the timeout before returning/acting. This keeps the whole
workflow correct without needing a running cron/queue process.
"""
import uuid
from datetime import datetime, timedelta, timezone

from app.models.assignment import ACTIVE_STATUSES
from app.config.settings import settings


class AssignmentError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc)


def create_assignment_chain(db, problem_id: str, ranked_top5: list[dict]) -> list[dict]:
    """Creates the full chain (rank 1 SENT, ranks 2-5 PENDING). Rejects if an
    active chain already exists for this problem (prevents duplicates)."""
    existing_active = db.university_assignments.find_one(
        {"problemId": problem_id, "status": {"$in": list(ACTIVE_STATUSES)}}
    )
    if existing_active:
        raise AssignmentError(
            f"An active assignment chain already exists for problem {problem_id}."
        )

    if not ranked_top5:
        raise AssignmentError("Cannot create an assignment chain with zero candidates.")

    now = _now()
    deadline = now + timedelta(hours=settings.default_assignment_deadline_hours)

    docs = []
    for i, candidate in enumerate(ranked_top5):
        is_first = i == 0
        doc = {
            "assignmentId": f"ASN-{uuid.uuid4().hex[:10].upper()}",
            "problemId": problem_id,
            "universityId": candidate["universityId"],
            "rank": candidate.get("rank", i + 1),
            "status": "SENT" if is_first else "PENDING",
            "score": candidate["finalScore"],
            "scoreSnapshot": dict(candidate["factorScores"]),
            "explanation": candidate.get("explanation", ""),
            "sentAt": now if is_first else None,
            "deadline": deadline if is_first else None,
            "reminderSent": False,
            "respondedAt": None,
            "response": None,
            "rejectionReason": None,
        }
        docs.append(doc)

    db.university_assignments.insert_many(docs)
    return docs


def _resolve_timeout_if_needed(db, assignment: dict) -> dict:
    """If a SENT assignment is past its deadline, mark it TIMED_OUT and
    activate the next rank. Returns the (possibly updated) assignment."""
    if assignment["status"] != "SENT":
        return assignment

    deadline = assignment.get("deadline")
    if deadline is None:
        return assignment

    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)

    if _now() >= deadline:
        db.university_assignments.update_one(
            {"assignmentId": assignment["assignmentId"]},
            {"$set": {"status": "TIMED_OUT", "respondedAt": _now()}},
        )
        assignment = db.university_assignments.find_one(
            {"assignmentId": assignment["assignmentId"]}
        )
        _activate_next_rank(db, assignment["problemId"])
        assignment = db.university_assignments.find_one(
            {"assignmentId": assignment["assignmentId"]}
        )
    return assignment


def _activate_next_rank(db, problem_id: str) -> dict | None:
    next_assignment = db.university_assignments.find_one(
        {"problemId": problem_id, "status": "PENDING"},
        sort=[("rank", 1)],
    )
    if not next_assignment:
        return None

    now = _now()
    deadline = now + timedelta(hours=settings.default_assignment_deadline_hours)
    db.university_assignments.update_one(
        {"assignmentId": next_assignment["assignmentId"]},
        {"$set": {"status": "SENT", "sentAt": now, "deadline": deadline}},
    )
    return db.university_assignments.find_one(
        {"assignmentId": next_assignment["assignmentId"]}
    )


def get_assignment(db, assignment_id: str) -> dict | None:
    """Read path — resolves timeout lazily before returning."""
    assignment = db.university_assignments.find_one({"assignmentId": assignment_id})
    if not assignment:
        return None
    return _resolve_timeout_if_needed(db, assignment)


def get_assignments_for_problem(db, problem_id: str) -> list[dict]:
    assignments = list(db.university_assignments.find({"problemId": problem_id}).sort("rank", 1))
    # resolve timeout on the currently-SENT one, if any
    for a in assignments:
        if a["status"] == "SENT":
            _resolve_timeout_if_needed(db, a)
    return list(db.university_assignments.find({"problemId": problem_id}).sort("rank", 1))


def accept_assignment(db, assignment_id: str) -> dict:
    assignment = get_assignment(db, assignment_id)  # resolves timeout first
    if not assignment:
        raise AssignmentError(f"Assignment {assignment_id} not found.")
    if assignment["status"] != "SENT":
        raise AssignmentError(
            f"Assignment {assignment_id} cannot be accepted from status {assignment['status']}."
        )

    now = _now()
    db.university_assignments.update_one(
        {"assignmentId": assignment_id},
        {"$set": {"status": "ACCEPTED", "respondedAt": now, "response": "ACCEPTED"}},
    )

    # cancel every sibling assignment for this problem
    db.university_assignments.update_many(
        {
            "problemId": assignment["problemId"],
            "assignmentId": {"$ne": assignment_id},
            "status": {"$in": ["PENDING", "SENT"]},
        },
        {"$set": {"status": "CANCELLED"}},
    )

    return db.university_assignments.find_one({"assignmentId": assignment_id})


def reject_assignment(db, assignment_id: str, reason: str) -> dict:
    if not reason or not reason.strip():
        raise AssignmentError("A rejection reason is required.")

    assignment = get_assignment(db, assignment_id)  # resolves timeout first
    if not assignment:
        raise AssignmentError(f"Assignment {assignment_id} not found.")
    if assignment["status"] != "SENT":
        raise AssignmentError(
            f"Assignment {assignment_id} cannot be rejected from status {assignment['status']}."
        )

    now = _now()
    db.university_assignments.update_one(
        {"assignmentId": assignment_id},
        {
            "$set": {
                "status": "REJECTED",
                "respondedAt": now,
                "response": "REJECTED",
                "rejectionReason": reason,
            }
        },
    )
    _activate_next_rank(db, assignment["problemId"])
    return db.university_assignments.find_one({"assignmentId": assignment_id})


def build_handoff_payload(assignment: dict) -> dict:
    """The clean boundary object emitted after acceptance. The real project-
    management system (out of our scope) consumes this shape."""
    return {
        "problemId": assignment["problemId"],
        "universityId": assignment["universityId"],
        "assignmentId": assignment["assignmentId"],
        "scoreSnapshot": assignment["scoreSnapshot"],
        "acceptedAt": assignment["respondedAt"],
    }
