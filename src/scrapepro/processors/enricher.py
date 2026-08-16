"""Enricher processor for ScrapePro."""

from abc import ABC, abstractmethod
from dataclasses import replace

from scrapepro.core.record import Record
from scrapepro.processors.base import BaseProcessor


class EnrichmentProvider(ABC):
    """Provide enrichment data for a Record."""

    @abstractmethod
    def enrich(self, record: Record) -> dict[str, str | None]:
        """Return enrichment fields for a record."""
        raise NotImplementedError


class Enricher(BaseProcessor):
    """Enrich Record objects using an external provider."""

    def __init__(self, provider: EnrichmentProvider) -> None:
        """Initialize the enricher with an enrichment provider."""
        self.provider = provider

    def process(self, records: list[Record]) -> list[Record]:
        """Return enriched Record objects."""
        enriched = []

        for record in records:
            data = self.provider.enrich(record)

            enriched.append(
                replace(
                    record,
                    city=data.get("city", record.city),
                    country=data.get("country", record.country),
                )
            )

        return enriched
