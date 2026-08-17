from dataclasses import dataclass

from fastapi.testclient import TestClient

import scrapepro.api.app as app_module
from scrapepro.core.result import ScrapeResult


client = TestClient(app_module.app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "scrapepro",
    }


@dataclass
class FakeRecord:
    name: str
    address: str
    source: str = "google_maps"


class FakeEngine:
    def __init__(self, scraper, pipeline):
        self.scraper = scraper
        self.pipeline = pipeline

    def run(self, task):
        assert task.source == "google_maps"
        assert task.query == "cafes"
        assert task.location == "Islamabad"

        return ScrapeResult(
            records=[
                FakeRecord(
                    name="Cafe A",
                    address="Main Street, Islamabad, Pakistan",
                )
            ]
        )


def test_scrape_endpoint_runs_engine(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "build_scraper",
        lambda source: object(),
    )

    monkeypatch.setattr(
        app_module,
        "build_pipeline",
        lambda database: object(),
    )

    monkeypatch.setattr(
        app_module,
        "ScrapeEngine",
        FakeEngine,
    )

    response = client.post(
        "/scrape",
        json={
            "source": "google_maps",
            "query": "cafes",
            "location": "Islamabad",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "completed",
        "success": True,
        "count": 1,
        "errors": [],
        "records": [
            {
                "name": "Cafe A",
                "address": "Main Street, Islamabad, Pakistan",
                "source": "google_maps",
            }
        ],
    }


def test_scrape_endpoint_rejects_missing_source():
    response = client.post(
        "/scrape",
        json={
            "query": "cafes",
            "location": "Islamabad",
        },
    )

    assert response.status_code == 422
