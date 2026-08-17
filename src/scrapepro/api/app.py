"""FastAPI application for ScrapePro."""

from pathlib import Path

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
from scrapepro.jobs.service import JobService
from scrapepro.jobs.store import JobStore


app = FastAPI(
    title="ScrapePro API",
    version="0.1.0",
)

job_store = JobStore()


def build_exporter(output_format: str | None):
    """Build an exporter for the requested output format."""
    if output_format is None:
        return None

    if output_format == "csv":
        from scrapepro.exporters.csv import CSVExporter
        return CSVExporter()

    if output_format == "json":
        from scrapepro.exporters.json import JSONExporter
        return JSONExporter()

    if output_format == "excel":
        from scrapepro.exporters.excel import ExcelExporter
        return ExcelExporter()

    raise ValueError(f"Unsupported output format: {output_format}")


def build_export_path(
    output_format: str,
    query: str,
    location: str | None,
) -> Path:
    """Build the default API export file path."""
    extensions = {
        "csv": ".csv",
        "json": ".json",
        "excel": ".xlsx",
    }

    if output_format not in extensions:
        raise ValueError(f"Unsupported output format: {output_format}")

    safe_location = location or "unknown"
    filename = f"{query}_{safe_location}{extensions[output_format]}"
    return Path(filename)


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
    """Create and execute a scraping job."""
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

    service = JobService(job_store, engine)
    job = service.create_and_run(task)

    response: dict[str, object] = {
        "job_id": job.job_id,
        "status": job.status,
        "count": job.count,
        "errors": job.errors,
        "records": job.records,
    }

    if job.status == "completed" and task.output:
        exporter = build_exporter(task.output)
        output_path = build_export_path(
            task.output,
            task.query,
            task.location,
        )
        exporter.export(job.records, output_path)
        response["output"] = task.output
        response["export_path"] = str(output_path)

    return response


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, object]:
    """Return the current state of a scraping job."""
    job = job_store.get(job_id)

    if job is None:
        return {
            "status": "not_found",
            "job_id": job_id,
        }

    return {
        "job_id": job.job_id,
        "status": job.status,
        "count": job.count,
        "errors": job.errors,
        "records": job.records,
    }
