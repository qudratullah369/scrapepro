"""FastAPI application for ScrapePro."""

from fastapi import FastAPI
from pydantic import BaseModel


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


@app.get("/health")
def health() -> dict[str, str]:
    """Return API health status."""
    return {
        "status": "ok",
        "service": "scrapepro",
    }


@app.post("/scrape")
def create_scrape(request: ScrapeRequest) -> dict[str, object]:
    """Validate and accept a scraping request."""
    return {
        "status": "accepted",
        "task": request.model_dump(),
    }
