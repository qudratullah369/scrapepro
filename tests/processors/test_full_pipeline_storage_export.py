import csv
import json

from scrapepro.core.engine import ScrapeEngine
from scrapepro.core.pipeline import Pipeline
from scrapepro.core.record import Record
from scrapepro.core.result import ScrapeResult
from scrapepro.core.task import ScrapeTask
from scrapepro.exporters.csv import CSVExporter
from scrapepro.exporters.json import JSONExporter
from scrapepro.processors.cleaner import Cleaner
from scrapepro.processors.deduplicator import Deduplicator
from scrapepro.processors.enricher import Enricher
from scrapepro.processors.export import ExportProcessor
from scrapepro.processors.location_enricher import LocationEnrichmentProvider
from scrapepro.processors.normalizer import Normalizer
from scrapepro.processors.storage import StorageProcessor
from scrapepro.processors.validator import Validator
from scrapepro.scrapers.base import BaseScraper
from scrapepro.storage.sqlite import SQLiteStorage


class MockFullPipelineScraper(BaseScraper):
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


def test_full_pipeline_stores_and_exports_records(tmp_path):
    database_path = tmp_path / "records.db"
    csv_path = tmp_path / "cafes.csv"
    json_path = tmp_path / "cafes.json"

    storage = SQLiteStorage(database_path)

    pipeline = Pipeline()

    pipeline.add(Cleaner())
    pipeline.add(Normalizer())
    pipeline.add(Deduplicator())
    pipeline.add(Validator())
    pipeline.add(Enricher(LocationEnrichmentProvider()))
    pipeline.add(StorageProcessor(storage))
    pipeline.add(
        ExportProcessor(
            exporters=[
                CSVExporter(),
                JSONExporter(),
            ],
            output_paths=[
                csv_path,
                json_path,
            ],
        )
    )

    engine = ScrapeEngine(
        scraper=MockFullPipelineScraper(),
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

    record = result.records[0]

    assert record.name == "Cafe A"
    assert record.address == "Main Street, Islamabad, Pakistan"
    assert record.city == "Islamabad"
    assert record.country == "Pakistan"
    assert record.place_id == "p1"

    assert storage.count() == 1

    stored = storage.get_by_id(1)

    assert stored == record

    assert csv_path.exists()
    assert json_path.exists()

    with csv_path.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["name"] == "Cafe A"
    assert rows[0]["city"] == "Islamabad"
    assert rows[0]["country"] == "Pakistan"

    with json_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    assert len(data) == 1
    assert data[0]["name"] == "Cafe A"
    assert data[0]["city"] == "Islamabad"
    assert data[0]["country"] == "Pakistan"

    storage.close()
