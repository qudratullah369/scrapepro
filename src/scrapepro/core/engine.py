"""Core execution engine for ScrapePro."""

from scrapepro.core.pipeline import Pipeline
from scrapepro.core.result import ScrapeResult
from scrapepro.core.task import ScrapeTask
from scrapepro.scrapers.base import BaseScraper


class ScrapeEngine:
    """Coordinate scraping and record processing."""

    def __init__(
        self,
        scraper: BaseScraper,
        pipeline: Pipeline | None = None,
    ) -> None:
        """Initialize the scraping engine."""
        self.name = "scrapepro"
        self.scraper = scraper
        self.pipeline = pipeline or Pipeline()

    def run(self, task: ScrapeTask) -> ScrapeResult:
        """Execute a scraping task and process its records."""
        result = self.scraper.scrape(task)

        if result.errors:
            return result

        records = self.pipeline.run(result.records)

        return ScrapeResult(
            records=records,
            errors=result.errors,
        )
