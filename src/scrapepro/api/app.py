"""FastAPI application for ScrapePro."""

from pathlib import Path

from fastapi import FastAPI

from scrapepro.core.task import ScrapeTask
from scrapepro.exporters.service import ExportService
from scrapepro.jobs.store import (
    JOB_COMPLETED,
    JOB_NOT_FOUND,
    JobStore,
)
from scrapepro.api.dependencies import (
    build_job_service,
)

from scrapepro.api.schemas import (
    JobNotFoundResponse,
    JobResponse,
    ScrapeRequest,
    ScrapeResponse,
)


app = FastAPI(
    title="ScrapePro API",
    version="0.1.0",
)

job_store = JobStore()


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

    service = build_job_service(
        source=task.source,
        database=task.database,
        job_store=job_store,
    )
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


@app.get(
    "/jobs/{job_id}",
    response_model=JobResponse | JobNotFoundResponse,
)
def get_job(job_id: str) -> JobResponse | JobNotFoundResponse:
    """Return the current state of a scraping job."""
    job = job_store.get(job_id)

    if job is None:
        return JobNotFoundResponse(
            status=JOB_NOT_FOUND,
            job_id=job_id,
        )

    return JobResponse(
        job_id=job.job_id,
        status=job.status,
        count=job.count,
        errors=job.errors,
        records=job.records,
        output=None,
        export_path=None,
    )
