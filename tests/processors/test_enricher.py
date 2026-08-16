from scrapepro.core.record import Record
from scrapepro.processors.enricher import Enricher, EnrichmentProvider


class MockEnrichmentProvider(EnrichmentProvider):
    def enrich(self, record: Record) -> dict[str, str | None]:
        return {
            "city": "Islamabad",
            "country": "Pakistan",
        }


class PartialEnrichmentProvider(EnrichmentProvider):
    def enrich(self, record: Record) -> dict[str, str | None]:
        return {
            "city": "Lahore",
        }


def test_enricher_adds_city_and_country():
    records = [
        Record(
            name="Cafe A",
            address="Main Street",
        )
    ]

    enricher = Enricher(MockEnrichmentProvider())

    result = enricher.process(records)

    assert result[0].city == "Islamabad"
    assert result[0].country == "Pakistan"


def test_enricher_preserves_existing_values_when_provider_omits_fields():
    records = [
        Record(
            name="Cafe A",
            address="Main Street",
            city="Lahore",
            country="Pakistan",
        )
    ]

    enricher = Enricher(PartialEnrichmentProvider())

    result = enricher.process(records)

    assert result[0].city == "Lahore"
    assert result[0].country == "Pakistan"


def test_enricher_does_not_mutate_original_record():
    record = Record(
        name="Cafe A",
        address="Main Street",
    )

    enricher = Enricher(MockEnrichmentProvider())

    result = enricher.process([record])

    assert record.city is None
    assert record.country is None
    assert result[0] is not record
