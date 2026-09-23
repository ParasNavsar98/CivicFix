"""
Unit tests for LocationService (Phase 4)
"""

import pytest
from app.services.location import LocationService, InvalidLocationDataError


@pytest.fixture
def location_service():
    return LocationService()


def test_identical_coordinates(location_service):
    lat, long = 23.3441, 85.3096  # Ranchi coordinates
    dist = location_service.haversine_distance(lat, long, lat, long)
    assert dist == 0.0
    score = location_service.calculate_location_score(dist, max_radius_km=5.0)
    assert score == 1.0


def test_nearby_coordinates(location_service):
    # ~1.2 km distance
    lat1, long1 = 23.3441, 85.3096
    lat2, long2 = 23.3540, 85.3120
    dist = location_service.haversine_distance(lat1, long1, lat2, long2)
    assert dist is not None
    assert 1.0 <= dist <= 1.5
    score = location_service.calculate_location_score(dist, max_radius_km=5.0)
    assert 0.7 <= score <= 0.85


def test_distant_coordinates(location_service):
    # Ranchi to Delhi ~1000+ km
    lat1, long1 = 23.3441, 85.3096
    lat2, long2 = 28.6139, 77.2090
    dist = location_service.haversine_distance(lat1, long1, lat2, long2)
    assert dist is not None
    assert dist > 900.0
    score = location_service.calculate_location_score(dist, max_radius_km=5.0)
    assert score == 0.0


def test_missing_coordinates(location_service):
    assert location_service.haversine_distance(None, 85.3096, 23.3441, 85.3096) is None
    assert location_service.haversine_distance(23.3441, None, 23.3441, 85.3096) is None
    assert location_service.haversine_distance(None, None, None, None) is None
    assert location_service.calculate_location_score(None) == 0.0


def test_invalid_coordinates(location_service):
    with pytest.raises(InvalidLocationDataError):
        location_service.haversine_distance(95.0, 85.0, 23.0, 85.0)  # Invalid lat > 90

    with pytest.raises(InvalidLocationDataError):
        location_service.haversine_distance(23.0, 185.0, 23.0, 85.0)  # Invalid long > 180

    with pytest.raises(InvalidLocationDataError):
        location_service.haversine_distance("invalid", 85.0, 23.0, 85.0)  # Non-numeric
