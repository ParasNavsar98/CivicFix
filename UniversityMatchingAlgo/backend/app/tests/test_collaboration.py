import pytest

from app.services import collaboration as collab


def seed_solution(db, university_id="UNI-1"):
    db.solutions.insert_one(
        {
            "solutionId": "SOL-1", "universityId": university_id,
            "status": "PUBLISHED", "visibility": "PUBLIC",
        }
    )


def test_express_interest_creates_pending_record(db):
    seed_solution(db)
    interest = collab.express_interest(
        db, solution_id="SOL-1", partner_id="IND-1",
        support_offered=["Hardware"], contribution={"hardware": ["10 sensors"]},
        message="We can help.",
    )
    assert interest["status"] == "PENDING"


def test_duplicate_pending_interest_rejected(db):
    seed_solution(db)
    collab.express_interest(db, "SOL-1", "IND-1", ["Hardware"], {}, "msg")
    with pytest.raises(collab.CollaborationError):
        collab.express_interest(db, "SOL-1", "IND-1", ["Hardware"], {}, "msg again")


def test_interest_on_unpublished_solution_rejected(db):
    db.solutions.insert_one({"solutionId": "SOL-2", "status": "DRAFT"})
    with pytest.raises(collab.CollaborationError):
        collab.express_interest(db, "SOL-2", "IND-1", [], {}, "")


def test_accept_creates_collaboration(db):
    seed_solution(db, university_id="UNI-1")
    interest = collab.express_interest(db, "SOL-1", "IND-1", ["Hardware"], {}, "msg")

    collaboration = collab.accept_interest(db, interest["interestId"], acting_user_id="UNI-1")

    assert collaboration["status"] == "ACTIVE"
    assert collaboration["solutionId"] == "SOL-1"
    updated_interest = db.industry_interests.find_one({"interestId": interest["interestId"]})
    assert updated_interest["status"] == "ACCEPTED"


def test_reject_requires_reason(db):
    seed_solution(db, university_id="UNI-1")
    interest = collab.express_interest(db, "SOL-1", "IND-1", ["Hardware"], {}, "msg")
    with pytest.raises(collab.CollaborationError):
        collab.reject_interest(db, interest["interestId"], acting_user_id="UNI-1", reason="")


def test_reject_stores_reason(db):
    seed_solution(db, university_id="UNI-1")
    interest = collab.express_interest(db, "SOL-1", "IND-1", ["Hardware"], {}, "msg")
    result = collab.reject_interest(db, interest["interestId"], acting_user_id="UNI-1", reason="Not a fit.")
    assert result["status"] == "REJECTED"
    assert result["rejectionReason"] == "Not a fit."


def test_unauthorized_user_cannot_accept(db):
    seed_solution(db, university_id="UNI-1")
    interest = collab.express_interest(db, "SOL-1", "IND-1", ["Hardware"], {}, "msg")
    with pytest.raises(collab.CollaborationError):
        collab.accept_interest(db, interest["interestId"], acting_user_id="UNI-DIFFERENT")


def test_cannot_accept_already_resolved_interest(db):
    seed_solution(db, university_id="UNI-1")
    interest = collab.express_interest(db, "SOL-1", "IND-1", ["Hardware"], {}, "msg")
    collab.accept_interest(db, interest["interestId"], acting_user_id="UNI-1")
    with pytest.raises(collab.CollaborationError):
        collab.accept_interest(db, interest["interestId"], acting_user_id="UNI-1")
