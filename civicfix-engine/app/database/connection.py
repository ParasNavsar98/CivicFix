"""
MongoDB connection for civicfix-engine (unified database: civicfix).
Consolidates all three features into a single MongoDB database.

Swapping to MongoDB Atlas is a ONE-LINE change: update MONGO_URI in .env.
For tests, set_db_for_testing() injects a mongomock database.
"""
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database

from app.config import settings

_client: MongoClient | None = None
_db: Database | None = None
_test_db: Database | None = None  # set by tests, takes priority when present


def get_db() -> Database:
    global _client, _db
    if _test_db is not None:
        return _test_db
    if _db is None:
        _client = MongoClient(settings.MONGO_URI)
        _db = _client[settings.MONGO_DB_NAME]
    return _db


def set_db_for_testing(db: Database) -> None:
    """Used by pytest fixtures to inject a mongomock database."""
    global _test_db
    _test_db = db


def clear_test_db() -> None:
    global _test_db
    _test_db = None


def ensure_indexes() -> None:
    """Create all indexes across unified civicfix database. Safe to call repeatedly (idempotent)."""
    db = get_db()

    # --- University Matching indexes ---
    db.universities.create_index([("universityId", ASCENDING)], unique=True)
    db.universities.create_index([("institution.location.district", ASCENDING)])
    db.universities.create_index([("institution.location.state", ASCENDING)])
    db.universities.create_index([("expertise", ASCENDING)])
    db.universities.create_index([("status", ASCENDING)])

    db.solutions.create_index([("domain", ASCENDING)])
    db.solutions.create_index([("subcategory", ASCENDING)])
    db.solutions.create_index([("location.state", ASCENDING)])
    db.solutions.create_index([("location.district", ASCENDING)])
    db.solutions.create_index([("developmentStage", ASCENDING)])
    db.solutions.create_index([("supportNeeded", ASCENDING)])
    db.solutions.create_index([("partnerType", ASCENDING)])
    db.solutions.create_index([("status", ASCENDING)])
    db.solutions.create_index([("visibility", ASCENDING)])

    db.university_assignments.create_index([("problemId", ASCENDING)])
    db.university_assignments.create_index([("status", ASCENDING)])
    db.university_assignments.create_index([("assignmentId", ASCENDING)], unique=True)

    db.industry_interests.create_index([("solutionId", ASCENDING)])
    db.industry_interests.create_index([("status", ASCENDING)])

    db.matching_results.create_index([("problemId", ASCENDING)])
    db.matching_configuration.create_index([("configId", ASCENDING)], unique=True)
