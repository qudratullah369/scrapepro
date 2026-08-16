"""Google Places API client for ScrapePro (New)."""

import requests
from typing import Dict, List, Any


class GoogleAPIError(Exception):
    """Custom exception for Google API errors."""

    pass


class GoogleMapsClient:
    """Client for Google Places API (New) – requires lat/lng."""

    BASE_URL = "https://places.googleapis.com/v1"
    DEFAULT_MAX_PAGES = 3

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
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> List[Dict[str, Any]]:
        """
        Perform Google Places Text Search with pagination.

        Args:
            query: Text query, e.g. "restaurants".
            lat: Latitude of search center.
            lng: Longitude of search center.
            radius: Search radius in meters.
            max_pages: Maximum number of API pages to retrieve.

        Returns:
            Combined list of places from all retrieved pages.

        Raises:
            GoogleAPIError: If the API request fails.
            ValueError: If max_pages is less than 1.
        """
        if max_pages < 1:
            raise ValueError("max_pages must be at least 1.")

        payload = {
            "textQuery": query,
            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng,
                    },
                    "radius": float(radius),
                }
            },
        }

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
            "places.id,"
            "nextPageToken"
        )

        self.session.headers["X-Goog-FieldMask"] = field_mask

        all_places: List[Dict[str, Any]] = []
        page_token = None

        try:
            for _ in range(max_pages):
                request_payload = dict(payload)

                if page_token:
                    request_payload["pageToken"] = page_token

                response = self.session.post(
                    f"{self.BASE_URL}/places:searchText",
                    json=request_payload,
                    timeout=30,
                )
                response.raise_for_status()

                data = response.json()

                all_places.extend(data.get("places", []))

                page_token = data.get("nextPageToken")

                if not page_token:
                    break

            return all_places

        except requests.exceptions.RequestException as e:
            raise GoogleAPIError(f"Google API error: {e}") from e
