"""Location resolution for ScrapePro."""

from typing import Tuple, Optional
import requests


class LocationResolver:
    """Convert location strings to lat/lng using Google Geocoding API."""

    GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def resolve(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Convert a location string to (latitude, longitude).

        Args:
            location: e.g., "Islamabad", "Lahore, Pakistan"

        Returns:
            (lat, lng) tuple or None if resolution fails.
        """
        params = {
            "address": location,
            "key": self.api_key,
        }
        try:
            response = requests.get(self.GEOCODE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data["status"] == "OK" and data["results"]:
                loc = data["results"][0]["geometry"]["location"]
                return (loc["lat"], loc["lng"])
            return None
        except requests.exceptions.RequestException:
            return None
