"""Base scraper interface for ScrapePro."""

from abc import ABC, abstractmethod

from scrapepro.core.result import ScrapeResult
from scrapepro.core.task import ScrapeTask


class BaseScraper(ABC):
    """Abstract base class for all ScrapePro scrapers."""

    @abstractmethod
    def scrape(self, task: ScrapeTask) -> ScrapeResult:
        """Execute a scraping task and return the result."""
        raise NotImplementedError
