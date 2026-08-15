"""Google Maps scraper implementation with location resolution."""

from typing import Optional, Dict, Any

from scrapepro.scrapers.base import BaseScraper
from scrapepro.core.task import ScrapeTask
from scrapepro.core.result import ScrapeResult
from scrapepro.core.record import Record
from .google_maps_client import GoogleMapsClient, GoogleAPIError
from .location_resolver import LocationResolver


class GoogleMapsScraper(BaseScraper):
    """Scraper for Google Places API with location resolution."""

    def __init__(
        self,
        api_key: str,
        client: Optional[GoogleMapsClient] = None,
        resolver: Optional[LocationResolver] = None,
    ) -> None:
        self.api_key = api_key
        self.client = client or GoogleMapsClient(api_key)
        self.resolver = resolver or LocationResolver(api_key)

    def scrape(self, task: ScrapeTask) -> ScrapeResult:
        if not task.location:
            return ScrapeResult(
                records=[],
                errors=["Location is required for Google Maps scraping."],
            )

        # 1. Resolve location → lat/lng
        coords = self.resolver.resolve(task.location)
        if coords is None:
            return ScrapeResult(
                records=[],
                errors=[f"Could not resolve location: {task.location}"],
            )
        lat, lng = coords

        try:
            # 2. Call Places API
            raw_places = self.client.search_text(
                query=task.query,
                lat=lat,
                lng=lng,
            )

            # 3. Convert to Records
            records = []
            for place in raw_places:
                record = self._to_record(place)
                if record:
                    records.append(record)

            return ScrapeResult(records=records)

        except GoogleAPIError as e:
            return ScrapeResult(records=[], errors=[str(e)])

    def _to_record(self, place: Dict[str, Any]) -> Optional[Record]:
        """Convert Google Place dict to ScrapePro Record."""
        name = place.get("displayName", {}).get("text", "")
        address = place.get("formattedAddress", "")

        if not name or not address:
            return None

        return Record(
            name=name,
            address=address,
            source="google_maps",
            place_id=place.get("id"),
            rating=place.get("rating"),
            reviews=place.get("userRatingCount"),
            phone=place.get("internationalPhoneNumber"),
            website=place.get("websiteUri"),
            latitude=place.get("location", {}).get("latitude"),
            longitude=place.get("location", {}).get("longitude"),
            category=", ".join(place.get("types", [])) if place.get("types") else None,
        )
