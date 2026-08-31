"""Pydantic schemas for the ScrapePro API."""

from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    """Request body for a scraping task."""

    source: str = Field(..., pattern="^(google_maps|website|ecommerce)$")
    query: str = Field(..., min_length=1)
    location: str | None = None
    output: str | None = Field(None, pattern="^(csv|excel|json)$")
    database: str | None = None


class ScrapeResponse(BaseModel):
    """Response returned after executing a scraping request."""

    status: str
    count: int
    errors: list[str]
    records: list[dict]
    output: str | None = None
    export_path: str | None = None
