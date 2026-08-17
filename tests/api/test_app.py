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
    def __init__(self, result):
        self.result = result

    def run(self, task):
        assert task.source == "google_maps"
        assert task.query == "cafes"
        assert task.location == "Islamabad"
        return self.result


def test_scrape_endpoint_creates_job(monkeypatch):
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
        lambda scraper, pipeline: FakeEngine(
            ScrapeResult(
                records=[
                    FakeRecord(
                        name="Cafe A",
                        address="Main Street, Islamabad, Pakistan",
                    )
                ]
            )
        ),
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

    data = response.json()

    assert data["job_id"]
    assert data["status"] == "completed"
    assert data["count"] == 1
    assert data["errors"] == []
    assert data["records"] == [
        {
            "name": "Cafe A",
            "address": "Main Street, Islamabad, Pakistan",
            "source": "google_maps",
        }
    ]

    job_id = data["job_id"]

    job_response = client.get(f"/jobs/{job_id}")

    assert job_response.status_code == 200
    assert job_response.json() == data


def test_get_missing_job():
    response = client.get("/jobs/missing-job")

    assert response.status_code == 200
    assert response.json() == {
        "status": "not_found",
        "job_id": "missing-job",
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


def test_scrape_endpoint_exports_csv(monkeypatch, tmp_path):
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
        lambda scraper, pipeline: FakeEngine(
            ScrapeResult(
                records=[
                    FakeRecord(
                        name="Cafe Export",
                        address="Islamabad",
                    )
                ]
            )
        ),
    )

    exported = {}

    class FakeExporter:
        def export(self, records, path):
            exported["records"] = records
            exported["path"] = path
            return path

    monkeypatch.setattr(
        app_module,
        "build_exporter",
        lambda output_format: FakeExporter(),
    )

    monkeypatch.chdir(tmp_path)

    response = client.post(
        "/scrape",
        json={
            "source": "google_maps",
            "query": "cafes",
            "location": "Islamabad",
            "output": "csv",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["count"] == 1
    assert data["output"] == "csv"
    assert data["export_path"] == "cafes_Islamabad.csv"

    assert len(exported["records"]) == 1
    assert exported["records"][0]["name"] if isinstance(
        exported["records"][0], dict
    ) else exported["records"][0].name == "Cafe Export"
    assert str(exported["path"]) == "cafes_Islamabad.csv"
