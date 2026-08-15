"""Google Maps scraper for ScrapePro."""

from scrapepro.core.record import Record
from scrapepro.core.result import ScrapeResult
from scrapepro.core.task import ScrapeTask
from scrapepro.scrapers.base import BaseScraper
from scrapepro.scrapers.google_maps_client import GoogleMapsClient


class GoogleMapsScraper(BaseScraper):
    """Scraper implementation for Google Maps."""

    def __init__(self, api_key: str) -> None:
        """Initialize the Google Maps scraper."""
        self.client = GoogleMapsClient(api_key)

    def scrape(self, task: ScrapeTask) -> ScrapeResult:
        """Execute a Google Maps scraping task."""
        if task.location is None:
            return ScrapeResult(
                errors=["Location is required for Google Maps scraping."]
            )

        raw_records = self.client.search_nearby(
            query=task.query,
            location=task.location,
        )

        records = [self._to_record(item) for item in raw_records]

        return ScrapeResult(records=records)

    def _to_record(self, item: dict) -> Record:
        """Convert a Google Maps result into a Record."""
        return Record(
            name=item.get("name", ""),
            address=item.get("vicinity"),
            rating=item.get("rating"),
            reviews=item.get("user_ratings_total"),
            source="google_maps",
            place_id=item.get("place_id"),
        )
