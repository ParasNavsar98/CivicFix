from pydantic import BaseModel


class LocationInput(BaseModel):
    district: str
    state: str
    latitude: float | None = None
    longitude: float | None = None


class MatchingRequest(BaseModel):
    """
    Body for POST /api/matching/{problemId}.

    `classification` is passed through EXACTLY as the categorization system's
    README documents it (we only read the fields we need — see
    integrations/categorization_adapter.py). `location` comes from the
    original problem record, not from the classifier.
    """
    classification: dict
    location: LocationInput
