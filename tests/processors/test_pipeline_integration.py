from scrapepro.core.engine import ScrapeEngine
from scrapepro.core.pipeline import Pipeline
from scrapepro.core.record import Record
from scrapepro.core.result import ScrapeResult
from scrapepro.core.task import ScrapeTask
from scrapepro.processors.cleaner import Cleaner
from scrapepro.processors.deduplicator import Deduplicator
from scrapepro.processors.enricher import Enricher
from scrapepro.processors.location_enricher import LocationEnrichmentProvider
from scrapepro.processors.normalizer import Normalizer
from scrapepro.processors.validator import Validator
from scrapepro.scrapers.base import BaseScraper


class MockPipelineScraper(BaseScraper):
    def scrape(self, task: ScrapeTask) -> ScrapeResult:
        return ScrapeResult(
            records=[
                Record(
                    name="  Cafe A  ",
                    address="  Main Street, Islamabad, Pakistan  ",
                    phone="+92 300 1234567",
                    place_id="p1",
                ),
                Record(
                    name="Cafe A",
                    address="Main Street, Islamabad, Pakistan",
                    phone="+92 300 1234567",
                    place_id="p1",
                ),
                Record(
                    name="  ",
                    address=None,
                ),
            ]
        )


def test_full_processing_pipeline():
    pipeline = Pipeline()
    pipeline.add(Cleaner())
    pipeline.add(Normalizer())
    pipeline.add(Deduplicator())
    pipeline.add(Validator())
    pipeline.add(Enricher(LocationEnrichmentProvider()))

    engine = ScrapeEngine(
        scraper=MockPipelineScraper(),
        pipeline=pipeline,
    )

    task = ScrapeTask(
        source="test",
        query="cafes",
        location="Islamabad",
    )

    result = engine.run(task)

    assert result.success is True
    assert result.errors == []

    # Duplicate removed and invalid record rejected.
    assert result.count == 1

    record = result.records[0]

    assert record.name == "Cafe A"
    assert record.address == "Main Street, Islamabad, Pakistan"
    assert record.city == "Islamabad"
    assert record.country == "Pakistan"
    assert record.place_id == "p1"
