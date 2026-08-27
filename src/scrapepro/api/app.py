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

from scrapepro.api.request_dependencies import (
    build_request_export_service,
    build_request_service,
)
from scrapepro.api.request_schemas import (
    DataRequestBody,
    DataRequestResponse,
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


@app.post("/data-request", response_model=DataRequestResponse)
def create_data_request(
    request: DataRequestBody,
) -> DataRequestResponse:
    """Submit a client data request."""
    from scrapepro.requests.fields import FieldRequirement
    from scrapepro.requests.specification import DataSpecification

    job_service = build_job_service(
        source=request.source or "google_maps",
        database="scrapepro.db",
        job_store=job_store,
    )

    service = build_request_export_service(job_service.engine)

    specification = DataSpecification(
        category=request.category,
        location=request.location,
        fields=[
            FieldRequirement(field)
            for field in request.fields
        ],
        limit=request.limit,
        source=request.source,
        output=request.output,
    )

    result, output_path = service.submit(specification)

    return DataRequestResponse(
        count=result.count,
        errors=[str(error) for error in result.errors],
        records=[
            record.__dict__
            for record in result.records
        ],
        output=request.output,
        export_path=str(output_path) if output_path else None,
    )
