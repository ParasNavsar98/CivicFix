"""
Loads demo data (all tagged "_demo": true) into an empty database.
Called automatically on app startup if SEED_ON_STARTUP=true and the
`universities` collection is empty. Can also be run standalone:

    python -m seed.seed_db
"""
import json
import os

SEED_DIR = os.path.dirname(__file__)


def _load(filename):
    with open(os.path.join(SEED_DIR, filename)) as f:
        return json.load(f)


def run_seed(db):
    universities = _load("universities.json")
    solutions = _load("solutions.json")
    industry_partners = _load("industry_partners.json")

    if universities:
        db.universities.delete_many({"_demo": True})
        db.universities.insert_many(universities)
    if solutions:
        db.solutions.delete_many({"_demo": True})
        db.solutions.insert_many(solutions)
    if industry_partners:
        db.industry_partners.delete_many({"_demo": True})
        db.industry_partners.insert_many(industry_partners)

    print(
        f"Seeded {len(universities)} universities, {len(solutions)} solutions, "
        f"{len(industry_partners)} industry partners."
    )


if __name__ == "__main__":
    from app.config.database import get_db, ensure_indexes

    database = get_db()
    ensure_indexes()
    run_seed(database)
