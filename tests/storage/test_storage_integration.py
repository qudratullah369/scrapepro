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
from scrapepro.processors.storage import StorageProcessor
from scrapepro.processors.validator import Validator
from scrapepro.scrapers.base import BaseScraper
from scrapepro.storage.sqlite import SQLiteStorage


class MockStorageScraper(BaseScraper):
    def scrape(self, task: ScrapeTask) -> ScrapeResult:
        return ScrapeResult(
            records=[
                Record(
                    name="  Cafe A  ",
                    address="  Main Street, Islamabad, Pakistan  ",
                    phone="+92 300 1234567",
                    source="google_maps",
                    place_id="p1",
                ),
                Record(
                    name="Cafe A",
                    address="Main Street, Islamabad, Pakistan",
                    phone="+92 300 1234567",
                    source="google_maps",
                    place_id="p1",
                ),
            ]
        )


def test_full_pipeline_stores_processed_records(tmp_path):
    storage = SQLiteStorage(tmp_path / "records.db")

    pipeline = Pipeline()
    pipeline.add(Cleaner())
    pipeline.add(Normalizer())
    pipeline.add(Deduplicator())
    pipeline.add(Validator())
    pipeline.add(Enricher(LocationEnrichmentProvider()))
    pipeline.add(StorageProcessor(storage))

    engine = ScrapeEngine(
        scraper=MockStorageScraper(),
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
    assert result.count == 1

    assert storage.count() == 1

    stored = storage.get_by_id(1)

    assert stored is not None
    assert stored.name == "Cafe A"
    assert stored.address == "Main Street, Islamabad, Pakistan"
    assert stored.city == "Islamabad"
    assert stored.country == "Pakistan"
    assert stored.place_id == "p1"

    storage.close()
