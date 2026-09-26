import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import mongomock
import pytest

from app.config import database as db_module
from app.models.problem_input import ProblemInput, ProblemLocation


@pytest.fixture()
def db():
    client = mongomock.MongoClient()
    test_db = client["test_db"]
    db_module.set_db_for_testing(test_db)
    yield test_db
    db_module.clear_test_db()


@pytest.fixture()
def sample_problem():
    return ProblemInput(
        problem_id="TEST-001",
        primary_domain="Environment",
        subcategory="Pollution",
        secondary_domains=["Healthcare"],
        required_expertise=["Environmental Management", "Public Health"],
        required_resources=["Waste collection", "Waste disposal infrastructure"],
        location=ProblemLocation(district="Ranchi", state="Jharkhand"),
    )


@pytest.fixture()
def sample_university():
    return {
        "universityId": "UNI-TEST-001",
        "institution": {
            "name": "Test University",
            "location": {"district": "Ranchi", "state": "Jharkhand"},
        },
        "expertise": ["Environmental Management", "Waste Management", "Pollution Control"],
        "researchAreas": ["Environmental Pollution", "Sustainable Development"],
        "faculty": [
            {
                "facultyId": "FAC-001",
                "name": "Faculty Member",
                "department": "Environmental Science",
                "expertise": ["Environmental Management", "Pollution Control"],
                "researchAreas": ["Environmental Pollution"],
                "availableForProjects": True,
            }
        ],
        "infrastructure": ["Environmental Laboratory", "Pollution Monitoring Equipment", "Water Quality Laboratory"],
        "technologyCapabilities": ["Environmental Monitoring", "IoT Monitoring", "Data Analysis"],
        "pastProjects": [
            {
                "title": "Community Waste Management Study",
                "domains": ["Environment", "Sanitation"],
                "expertise": ["Waste Management", "Pollution Control"],
            }
        ],
        "industryRelationships": ["Environmental Technology Companies", "IoT Companies"],
        "capacity": {"activeProjects": 6, "maximumProjects": 10, "availableTeams": 2, "availability": "AVAILABLE"},
        "status": "ACTIVE",
    }
