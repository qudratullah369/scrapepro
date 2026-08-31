"""FastAPI application for ScrapePro."""

from fastapi import FastAPI

from scrapepro.api.dependencies import build_engine
from scrapepro.api.request_dependencies import (
    build_request_export_service,
)
from scrapepro.api.request_schemas import (
    DataRequestBody,
    DataRequestResponse,
)
from scrapepro.api.schemas import (
    ScrapeRequest,
    ScrapeResponse,
)
from scrapepro.core.task import ScrapeTask
from scrapepro.exporters.service import ExportService


app = FastAPI(
    title="ScrapePro API",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return API health status."""
    return {
        "status": "ok",
        "service": "scrapepro",
    }


@app.post("/scrape", response_model=ScrapeResponse)
def create_scrape(request: ScrapeRequest) -> ScrapeResponse:
    """Create and execute a scraping request."""
    task = ScrapeTask(
        source=request.source,
        query=request.query,
        location=request.location,
        output=request.output,
        database=request.database or "scrapepro.db",
    )

    engine = build_engine(
        source=task.source,
        database=task.database,
    )
    result = engine.run(task)

    response = {
        "status": "completed" if result.success else "failed",
        "count": result.count,
        "errors": [str(error) for error in result.errors],
        "records": [
            record.__dict__
            for record in result.records
        ],
        "output": None,
        "export_path": None,
    }

    if result.success and task.output:
        export_service = ExportService()
        output_path = export_service.export(
            result.records,
            task.output,
            task.query,
            task.location,
        )
        response["output"] = task.output
        response["export_path"] = str(output_path)

    return ScrapeResponse(**response)


@app.post("/data-request", response_model=DataRequestResponse)
def create_data_request(
    request: DataRequestBody,
) -> DataRequestResponse:
    """Submit a client data request."""
    from scrapepro.requests.fields import FieldRequirement
    from scrapepro.requests.specification import DataSpecification

    engine = build_engine(
        source=request.source or "google_maps",
        database="scrapepro.db",
    )

    service = build_request_export_service(engine)

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