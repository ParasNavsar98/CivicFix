"""
Shape of a `matching_configuration` document, plus the default used when
none exists in the DB yet (seeded on first run).
"""

DEFAULT_WEIGHTS = {
    "expertise": 0.35,
    "faculty": 0.20,
    "infrastructure": 0.15,
    "pastProjects": 0.10,
    "geography": 0.10,
    "capacity": 0.05,
    "industry": 0.05,
}

DEFAULT_CONFIG = {
    "configId": "default",
    "version": 1,
    "weights": DEFAULT_WEIGHTS,
    "pastProjectsDivisor": 2,
}


def get_active_config(db) -> dict:
    config = db.matching_configuration.find_one({"configId": "default"})
    if config:
        return config
    db.matching_configuration.insert_one(dict(DEFAULT_CONFIG))
    return dict(DEFAULT_CONFIG)
