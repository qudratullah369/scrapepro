"""Pydantic schemas for the ScrapePro API."""

from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    """Request body for a scraping task."""

    source: str = Field(..., pattern="^google_maps$")
    query: str = Field(..., min_length=1)
    location: str | None = None
    output: str | None = Field(None, pattern="^(csv|excel|json)$")
    database: str | None = None


class ScrapeResponse(BaseModel):
    """Response returned after executing a scraping job."""

    job_id: str
    status: str
    count: int
    errors: list[str]
    records: list[dict]
    output: str | None = None
    export_path: str | None = None


class JobResponse(BaseModel):
    """Response returned when retrieving a scraping job."""

    job_id: str
    status: str
    count: int
    errors: list[str]
    records: list[dict]
    output: str | None = None
    export_path: str | None = None


class JobNotFoundResponse(BaseModel):
    """Response returned when a scraping job does not exist."""

    job_id: str
    status: str
