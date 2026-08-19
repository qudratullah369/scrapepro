"""Generic public website scraper for ScrapePro."""

from html.parser import HTMLParser

import requests

from scrapepro.core.record import Record
from scrapepro.core.result import ScrapeResult
from scrapepro.core.task import ScrapeTask
from scrapepro.scrapers.base import BaseScraper


class _PageParser(HTMLParser):
    """Extract basic information from an HTML page."""

    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self._in_title = False
        self._in_h1 = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
        elif tag.lower() == "h1":
            self._in_h1 = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
        elif tag.lower() == "h1":
            self._in_h1 = False

    def handle_data(self, data: str) -> None:
        text = data.strip()

        if not text:
            return

        if self._in_title:
            self.title_parts.append(text)

        if self._in_h1:
            self.h1_parts.append(text)

    @property
    def title(self) -> str:
        """Return the extracted page title."""
        return " ".join(self.title_parts).strip()

    @property
    def h1(self) -> str:
        """Return the first extracted H1 heading."""
        return " ".join(self.h1_parts).strip()


class WebsiteScraper(BaseScraper):
    """Scrape basic information from a public webpage."""

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout

    def scrape(self, task: ScrapeTask) -> ScrapeResult:
        """Fetch a webpage and return its basic information."""
        url = task.query.strip()

        if not url:
            return ScrapeResult(
                records=[],
                errors=["Website URL is required."],
            )

        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; ScrapePro/0.1)"
                    )
                },
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            return ScrapeResult(
                records=[],
                errors=[f"Website request failed: {exc}"],
            )

        parser = _PageParser()
        parser.feed(response.text)

        name = parser.title or parser.h1

        if not name:
            name = url

        record = Record(
            name=name,
            website=url,
            source="website",
        )

        return ScrapeResult(records=[record])
