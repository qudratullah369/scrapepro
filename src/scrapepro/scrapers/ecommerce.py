"""Generic public e-commerce product scraper for ScrapePro."""

import json
from html.parser import HTMLParser
from typing import Any

import requests

from scrapepro.core.record import Record
from scrapepro.core.result import ScrapeResult
from scrapepro.core.task import ScrapeTask
from scrapepro.scrapers.base import BaseScraper


class _JSONLDParser(HTMLParser):
    """Extract JSON-LD script contents from an HTML page."""

    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[str] = []
        self._in_jsonld = False
        self._parts: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag.lower() != "script":
            return

        attributes = dict(attrs)

        if attributes.get("type", "").lower() == "application/ld+json":
            self._in_jsonld = True
            self._parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._in_jsonld:
            content = "".join(self._parts).strip()

            if content:
                self.scripts.append(content)

            self._in_jsonld = False
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._in_jsonld:
            self._parts.append(data)


class EcommerceScraper(BaseScraper):
    """Extract basic product information from a public product page."""

    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout

    def scrape(self, task: ScrapeTask) -> ScrapeResult:
        """Fetch a product page and extract Product structured data."""
        url = task.query.strip()

        if not url:
            return ScrapeResult(
                records=[],
                errors=["Product URL is required."],
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
                errors=[f"E-commerce request failed: {exc}"],
            )

        parser = _JSONLDParser()
        parser.feed(response.text)

        product = self._find_product(parser.scripts)

        if not product:
            return ScrapeResult(
                records=[],
                errors=["No Product structured data found."],
            )

        name = product.get("name")

        if not name:
            return ScrapeResult(
                records=[],
                errors=["Product name not found."],
            )

        offers = product.get("offers", {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}

        price = None
        if isinstance(offers, dict):
            price = offers.get("price")

        record = Record(
            name=str(name),
            category=product.get("category"),
            website=url,
            source="ecommerce",
            rating=self._float_value(
                product.get("aggregateRating", {}).get("ratingValue")
                if isinstance(product.get("aggregateRating"), dict)
                else None
            ),
            reviews=self._int_value(
                product.get("aggregateRating", {}).get("reviewCount")
                if isinstance(product.get("aggregateRating"), dict)
                else None
            ),
        )

        # Keep extracted price available without changing Record yet.
        # Price support will be added to the data model as a separate step.

        return ScrapeResult(records=[record])

    @staticmethod
    def _find_product(scripts: list[str]) -> dict[str, Any] | None:
        """Find a Product object inside JSON-LD data."""
        for script in scripts:
            try:
                data = json.loads(script)
            except json.JSONDecodeError:
                continue

            candidates: list[Any]

            if isinstance(data, list):
                candidates = data
            elif isinstance(data, dict) and "@graph" in data:
                graph = data.get("@graph")
                candidates = graph if isinstance(graph, list) else [data]
            else:
                candidates = [data]

            for item in candidates:
                if not isinstance(item, dict):
                    continue

                item_type = item.get("@type")

                if item_type == "Product":
                    return item

                if isinstance(item_type, list) and "Product" in item_type:
                    return item

        return None

    @staticmethod
    def _float_value(value: Any) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _int_value(value: Any) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None
