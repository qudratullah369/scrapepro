"""FastAPI application for ScrapePro."""

from fastapi import FastAPI


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
