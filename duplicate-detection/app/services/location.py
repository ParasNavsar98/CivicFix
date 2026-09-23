"""
Phase 4 — Location Service
Implementation Decision (not mandated by SRS):
Computes geographic distance in kilometers using the Haversine formula.
SRS does NOT specify a fixed geographic threshold radius.
"""

import math
from typing import Optional, Tuple, Union


class LocationError(Exception):
    """Base exception for location operations."""
    pass


class InvalidLocationDataError(LocationError):
    """Raised when latitude/longitude coordinates are out of valid range."""
    pass


class LocationService:
    EARTH_RADIUS_KM = 6371.0  # Mean radius of Earth in km

    @classmethod
    def validate_coordinates(cls, lat: float, long: float) -> None:
        """Validates that latitude is in [-90, 90] and longitude is in [-180, 180]."""
        if not isinstance(lat, (int, float)) or math.isnan(lat):
            raise InvalidLocationDataError("Latitude must be a valid numeric value.")
        if not isinstance(long, (int, float)) or math.isnan(long):
            raise InvalidLocationDataError("Longitude must be a valid numeric value.")
        if not (-90.0 <= lat <= 90.0):
            raise InvalidLocationDataError(f"Latitude {lat} is out of range [-90, 90].")
        if not (-180.0 <= long <= 180.0):
            raise InvalidLocationDataError(f"Longitude {long} is out of range [-180, 180].")

    def haversine_distance(
        self,
        lat1: Optional[float],
        long1: Optional[float],
        lat2: Optional[float],
        long2: Optional[float],
    ) -> Optional[float]:
        """
        Computes the Haversine distance in kilometers between two geographic points.

        :param lat1: Latitude of point 1.
        :param long1: Longitude of point 1.
        :param lat2: Latitude of point 2.
        :param long2: Longitude of point 2.
        :return: Distance in kilometers rounded to 3 decimal places, or None if coordinates are missing.
        """
        if lat1 is None or long1 is None or lat2 is None or long2 is None:
            return None

        self.validate_coordinates(lat1, long1)
        self.validate_coordinates(lat2, long2)

        # Convert degrees to radians
        phi1, lambda1 = math.radians(lat1), math.radians(long1)
        phi2, lambda2 = math.radians(lat2), math.radians(long2)

        dphi = phi2 - phi1
        dlambda = lambda2 - lambda1

        a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
        # Guard against domain errors due to floating point inaccuracies
        a = min(1.0, max(0.0, a))
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

        distance = self.EARTH_RADIUS_KM * c
        return round(distance, 3)

    def calculate_location_score(
        self, distance_km: Optional[float], max_radius_km: float = 5.0
    ) -> float:
        """
        Calculates a location proximity score between 0.0 and 1.0 based on distance.
        If distance is 0 km, score is 1.0.
        If distance is >= max_radius_km, score drops to 0.0.
        Linear decay: score = max(0.0, 1.0 - (distance_km / max_radius_km)).
        If distance_km is None (missing coordinates), returns neutral score 0.0.

        :param distance_km: Distance in km or None.
        :param max_radius_km: Maximum radius in km for non-zero score.
        :return: Proximity score between 0.0 and 1.0.
        """
        if distance_km is None or max_radius_km <= 0.0:
            return 0.0
        score = max(0.0, 1.0 - (distance_km / max_radius_km))
        return round(score, 4)
