from scrapepro.core.record import Record
from scrapepro.processors.location_enricher import LocationEnrichmentProvider


def test_location_enricher_extracts_city_and_country():
    record = Record(
        name="Cafe A",
        address="Main Street, Islamabad, Pakistan",
    )

    provider = LocationEnrichmentProvider()

    result = provider.enrich(record)

    assert result["city"] == "Islamabad"
    assert result["country"] == "Pakistan"


def test_location_enricher_uses_last_two_address_parts():
    record = Record(
        name="Cafe A",
        address="Shop 12, Main Market, Lahore, Pakistan",
    )

    provider = LocationEnrichmentProvider()

    result = provider.enrich(record)

    assert result["city"] == "Lahore"
    assert result["country"] == "Pakistan"


def test_location_enricher_preserves_existing_values_without_address():
    record = Record(
        name="Cafe A",
        city="Islamabad",
        country="Pakistan",
    )

    provider = LocationEnrichmentProvider()

    result = provider.enrich(record)

    assert result["city"] == "Islamabad"
    assert result["country"] == "Pakistan"


def test_location_enricher_preserves_existing_values_for_short_address():
    record = Record(
        name="Cafe A",
        address="Islamabad",
        city="Islamabad",
        country="Pakistan",
    )

    provider = LocationEnrichmentProvider()

    result = provider.enrich(record)

    assert result["city"] == "Islamabad"
    assert result["country"] == "Pakistan"
