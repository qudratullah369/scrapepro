"""Location enrichment provider for ScrapePro."""

from scrapepro.core.record import Record
from scrapepro.processors.enricher import EnrichmentProvider


class LocationEnrichmentProvider(EnrichmentProvider):
    """Extract city and country from a Record address."""

    def enrich(self, record: Record) -> dict[str, str | None]:
        """Return city and country inferred from the address."""
        if not record.address:
            return {
                "city": record.city,
                "country": record.country,
            }

        parts = [part.strip() for part in record.address.split(",") if part.strip()]

        if len(parts) < 2:
            return {
                "city": record.city,
                "country": record.country,
            }

        country = parts[-1]
        city = parts[-2]

        return {
            "city": city,
            "country": country,
        }
