from app.services import marketplace


def seed_solutions(db):
    db.solutions.insert_many(
        [
            {
                "solutionId": "SOL-1", "domain": "Agriculture", "subcategory": "Pest Management",
                "location": {"state": "Jharkhand", "district": "Ranchi"},
                "developmentStage": "PROTOTYPE", "supportNeeded": ["Hardware"], "partnerType": ["Startup"],
                "status": "PUBLISHED", "visibility": "PUBLIC",
            },
            {
                "solutionId": "SOL-2", "domain": "Agriculture", "subcategory": "Crop Management",
                "location": {"state": "West Bengal", "district": "Kolkata"},
                "developmentStage": "PILOT", "supportNeeded": ["Funding"], "partnerType": ["Industry"],
                "status": "PUBLISHED", "visibility": "PUBLIC",
            },
            {
                "solutionId": "SOL-3", "domain": "Environment", "subcategory": "Pollution",
                "location": {"state": "Jharkhand", "district": "Ranchi"},
                "developmentStage": "PROTOTYPE", "supportNeeded": ["Hardware", "Testing"], "partnerType": ["Industry"],
                "status": "PUBLISHED", "visibility": "PUBLIC",
            },
            {
                "solutionId": "SOL-4", "domain": "Environment", "subcategory": "Pollution",
                "location": {"state": "Jharkhand", "district": "Ranchi"},
                "developmentStage": "PROTOTYPE", "supportNeeded": ["Hardware"], "partnerType": ["Industry"],
                "status": "DRAFT", "visibility": "PUBLIC",  # not published -> must never appear
            },
        ]
    )


def test_domain_only_filter(db):
    seed_solutions(db)
    results = marketplace.search_solutions(db, domain="Agriculture")
    ids = {r["solutionId"] for r in results}
    assert ids == {"SOL-1", "SOL-2"}


def test_domain_and_state_filter(db):
    seed_solutions(db)
    results = marketplace.search_solutions(db, domain="Agriculture", state="Jharkhand")
    ids = {r["solutionId"] for r in results}
    assert ids == {"SOL-1"}


def test_domain_and_stage_filter(db):
    seed_solutions(db)
    results = marketplace.search_solutions(db, domain="Environment", development_stage="PROTOTYPE")
    ids = {r["solutionId"] for r in results}
    assert ids == {"SOL-3"}  # SOL-4 excluded: not PUBLISHED


def test_multiple_combined_filters(db):
    seed_solutions(db)
    results = marketplace.search_solutions(
        db, domain="Environment", state="Jharkhand", support_needed=["Testing"]
    )
    ids = {r["solutionId"] for r in results}
    assert ids == {"SOL-3"}


def test_no_results(db):
    seed_solutions(db)
    results = marketplace.search_solutions(db, domain="Healthcare")
    assert results == []


def test_unpublished_never_returned(db):
    seed_solutions(db)
    results = marketplace.search_solutions(db)
    ids = {r["solutionId"] for r in results}
    assert "SOL-4" not in ids
