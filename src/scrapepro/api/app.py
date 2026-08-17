"""FastAPI application for ScrapePro."""

from dataclasses import asdict

from fastapi import FastAPI
from pydantic import BaseModel

from scrapepro.config.settings import Settings
from scrapepro.core.engine import ScrapeEngine
from scrapepro.core.pipeline import Pipeline
from scrapepro.core.task import ScrapeTask
from scrapepro.processors.cleaner import Cleaner
from scrapepro.processors.deduplicator import Deduplicator
from scrapepro.processors.enricher import Enricher
from scrapepro.processors.location_enricher import LocationEnrichmentProvider
from scrapepro.processors.normalizer import Normalizer
from scrapepro.processors.storage import StorageProcessor
from scrapepro.processors.validator import Validator
from scrapepro.scrapers.google_maps import GoogleMapsScraper
from scrapepro.storage.sqlite import SQLiteStorage


app = FastAPI(
    title="ScrapePro API",
    version="0.1.0",
)


class ScrapeRequest(BaseModel):
    """Request body for a scraping task."""

    source: str
    query: str
    location: str | None = None
    output: str | None = None
    database: str | None = None


def build_scraper(source: str) -> GoogleMapsScraper:
    """Build a scraper for the requested source."""
    settings = Settings()

    if source == "google_maps":
        return GoogleMapsScraper(
            api_key=settings.require_google_maps_api_key()
        )

    raise ValueError(f"Unsupported scraping source: {source}")


def build_pipeline(database: str) -> Pipeline:
    """Build the default API processing pipeline."""
    pipeline = Pipeline()

    pipeline.add(Cleaner())
    pipeline.add(Normalizer())
    pipeline.add(Deduplicator())
    pipeline.add(Validator())
    pipeline.add(Enricher(LocationEnrichmentProvider()))

    storage = SQLiteStorage(database)
    pipeline.add(StorageProcessor(storage))

    return pipeline


@app.get("/health")
def health() -> dict[str, str]:
    """Return API health status."""
    return {
        "status": "ok",
        "service": "scrapepro",
    }


@app.post("/scrape")
def create_scrape(request: ScrapeRequest) -> dict[str, object]:
    """Run a scraping task through the ScrapeEngine."""
    task = ScrapeTask(
        source=request.source,
        query=request.query,
        location=request.location,
        output=request.output,
        database=request.database or "scrapepro.db",
    )

    scraper = build_scraper(task.source)
    pipeline = build_pipeline(task.database)

    engine = ScrapeEngine(
        scraper=scraper,
        pipeline=pipeline,
    )

    result = engine.run(task)

    return {
        "status": "completed" if result.success else "failed",
        "success": result.success,
        "count": result.count,
        "errors": result.errors,
        "records": [asdict(record) for record in result.records],
    }
