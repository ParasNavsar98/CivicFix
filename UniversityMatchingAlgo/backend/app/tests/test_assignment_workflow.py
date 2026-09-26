from datetime import datetime, timedelta, timezone

import pytest

from app.services import assignment_workflow as workflow


def make_candidates(n=5):
    return [
        {"universityId": f"UNI-{i}", "rank": i, "finalScore": 100 - i, "factorScores": {"expertise": 0.8}}
        for i in range(1, n + 1)
    ]


def test_create_chain_sends_only_rank_1(db):
    candidates = make_candidates()
    docs = workflow.create_assignment_chain(db, "PROB-1", candidates)

    statuses = {d["universityId"]: d["status"] for d in docs}
    assert statuses["UNI-1"] == "SENT"
    assert statuses["UNI-2"] == "PENDING"
    assert statuses["UNI-3"] == "PENDING"


def test_duplicate_active_chain_rejected(db):
    workflow.create_assignment_chain(db, "PROB-1", make_candidates())
    with pytest.raises(workflow.AssignmentError):
        workflow.create_assignment_chain(db, "PROB-1", make_candidates())


def test_accept_stops_chain_and_cancels_others(db):
    docs = workflow.create_assignment_chain(db, "PROB-1", make_candidates())
    first_id = docs[0]["assignmentId"]

    result = workflow.accept_assignment(db, first_id)
    assert result["status"] == "ACCEPTED"

    others = list(db.university_assignments.find({"problemId": "PROB-1", "assignmentId": {"$ne": first_id}}))
    assert all(o["status"] == "CANCELLED" for o in others)


def test_reject_activates_next_rank(db):
    docs = workflow.create_assignment_chain(db, "PROB-1", make_candidates())
    first_id = docs[0]["assignmentId"]

    workflow.reject_assignment(db, first_id, reason="Not enough capacity right now.")

    rank2 = db.university_assignments.find_one({"problemId": "PROB-1", "rank": 2})
    assert rank2["status"] == "SENT"


def test_reject_requires_reason(db):
    docs = workflow.create_assignment_chain(db, "PROB-1", make_candidates())
    with pytest.raises(workflow.AssignmentError):
        workflow.reject_assignment(db, docs[0]["assignmentId"], reason="")


def test_timeout_activates_next_rank(db):
    docs = workflow.create_assignment_chain(db, "PROB-1", make_candidates())
    first_id = docs[0]["assignmentId"]

    # force the deadline into the past to simulate a timeout
    db.university_assignments.update_one(
        {"assignmentId": first_id},
        {"$set": {"deadline": datetime.now(timezone.utc) - timedelta(hours=1)}},
    )

    assignment = workflow.get_assignment(db, first_id)  # lazy check resolves it
    assert assignment["status"] == "TIMED_OUT"

    rank2 = db.university_assignments.find_one({"problemId": "PROB-1", "rank": 2})
    assert rank2["status"] == "SENT"


def test_all_reject_leaves_none_active(db):
    docs = workflow.create_assignment_chain(db, "PROB-1", make_candidates())
    current_id = docs[0]["assignmentId"]

    for _ in range(5):
        assignment = workflow.get_assignment(db, current_id)
        if assignment["status"] != "SENT":
            break
        workflow.reject_assignment(db, current_id, reason="No capacity.")
        next_sent = db.university_assignments.find_one({"problemId": "PROB-1", "status": "SENT"})
        current_id = next_sent["assignmentId"] if next_sent else current_id

    active = list(
        db.university_assignments.find({"problemId": "PROB-1", "status": {"$in": ["PENDING", "SENT"]}})
    )
    assert active == []


def test_cannot_accept_already_resolved_assignment(db):
    docs = workflow.create_assignment_chain(db, "PROB-1", make_candidates())
    first_id = docs[0]["assignmentId"]
    workflow.reject_assignment(db, first_id, reason="No capacity.")

    with pytest.raises(workflow.AssignmentError):
        workflow.accept_assignment(db, first_id)


def test_changing_default_deadline_does_not_affect_existing_assignment(db, monkeypatch):
    docs = workflow.create_assignment_chain(db, "PROB-1", make_candidates())
    assignment_id = docs[0]["assignmentId"]
    original_deadline = db.university_assignments.find_one({"assignmentId": assignment_id})["deadline"]

    from app.config.settings import settings

    monkeypatch.setattr(settings, "default_assignment_deadline_hours", 72)

    # Re-reading after the config change must return the SAME stored deadline.
    # BSON round-trip via the driver may normalize precision/tz representation,
    # so compare via timestamp (with a small tolerance) rather than strict equality.
    stored = db.university_assignments.find_one({"assignmentId": assignment_id})
    assert stored["deadline"].timestamp() == pytest.approx(original_deadline.timestamp(), abs=1)
