"""FastAPI application for ScrapePro."""

from pathlib import Path

from fastapi import FastAPI

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
from scrapepro.exporters.service import ExportService
from scrapepro.jobs.store import (
    JOB_COMPLETED,
    JOB_NOT_FOUND,
    JobStore,
)
from scrapepro.api.schemas import ScrapeRequest, ScrapeResponse


app = FastAPI(
    title="ScrapePro API",
    version="0.1.0",
)

job_store = JobStore()


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


@app.post("/scrape", response_model=ScrapeResponse)
def create_scrape(request: ScrapeRequest) -> ScrapeResponse:
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

    response = {
        "job_id": job.job_id,
        "status": job.status,
        "count": job.count,
        "errors": job.errors,
        "records": job.records,
    }

    if job.status == JOB_COMPLETED and task.output:
        export_service = ExportService()
        output_path = export_service.export(
            job.records,
            task.output,
            task.query,
            task.location,
        )
        response["output"] = task.output
        response["export_path"] = str(output_path)

    return ScrapeResponse(**response)


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, object]:
    """Return the current state of a scraping job."""
    job = job_store.get(job_id)

    if job is None:
        return {
            "status": JOB_NOT_FOUND,
            "job_id": job_id,
        }

    return {
        "job_id": job.job_id,
        "status": job.status,
        "count": job.count,
        "errors": job.errors,
        "records": job.records,
        "output": None,
        "export_path": None,
    }
