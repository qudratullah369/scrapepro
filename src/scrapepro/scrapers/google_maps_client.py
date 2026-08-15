"""Google Places API client for ScrapePro (New)."""

import requests
from typing import Dict, List, Any, Optional


class GoogleAPIError(Exception):
    """Custom exception for Google API errors."""
    pass


class GoogleMapsClient:
    """Client for Google Places API (New) – requires lat/lng."""

    BASE_URL = "https://places.googleapis.com/v1"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
        })

    def search_text(
        self,
        query: str,
        lat: float,
        lng: float,
        radius: int = 5000,
    ) -> List[Dict[str, Any]]:
        """
        Perform Text Search (New) with explicit lat/lng.

        Args:
            query: Text query (e.g., "restaurants")
            lat: Latitude of search center
            lng: Longitude of search center
            radius: Search radius in meters

        Returns:
            List of place dictionaries.

        Raises:
            GoogleAPIError: If the API request fails.
        """
        payload = {
            "textQuery": query,
            "locationBias": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": float(radius),
                }
            },
        }

        # Field mask – only request required fields
        field_mask = (
            "places.displayName,"
            "places.formattedAddress,"
            "places.rating,"
            "places.userRatingCount,"
            "places.internationalPhoneNumber,"
            "places.websiteUri,"
            "places.location,"
            "places.priceLevel,"
            "places.types,"
            "places.id"
        )
        self.session.headers["X-Goog-FieldMask"] = field_mask

        try:
            response = self.session.post(
                f"{self.BASE_URL}/places:searchText",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("places", [])
        except requests.exceptions.RequestException as e:
            raise GoogleAPIError(f"Google API error: {e}") from e
