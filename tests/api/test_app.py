from pathlib import Path
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
        return self.result


def test_scrape_endpoint_runs_engine(monkeypatch):
    fake_engine = FakeEngine(
        ScrapeResult(
            records=[
                FakeRecord(
                    name="Cafe A",
                    address="Main Street, Islamabad, Pakistan",
                )
            ]
        )
    )

    monkeypatch.setattr(
        app_module,
        "build_engine",
        lambda source, database: fake_engine,
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

    assert "job_id" not in data
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


def test_jobs_endpoint_is_removed():
    response = client.get("/jobs/test-job")

    assert response.status_code == 404


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
    fake_engine = FakeEngine(
        ScrapeResult(
            records=[
                FakeRecord(
                    name="Cafe Export",
                    address="Islamabad",
                )
            ]
        )
    )

    monkeypatch.setattr(
        app_module,
        "build_engine",
        lambda source, database: fake_engine,
    )

    exported = {}

    class FakeExportService:
        def export(self, records, output_format, query, location):
            exported["records"] = records
            exported["output_format"] = output_format
            exported["query"] = query
            exported["location"] = location

            output_path = tmp_path / "cafes_Islamabad.csv"
            exported["path"] = output_path

            return output_path

    monkeypatch.setattr(
        app_module,
        "ExportService",
        lambda: FakeExportService(),
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
    assert Path(data["export_path"]).name == "cafes_Islamabad.csv"

    assert len(exported["records"]) == 1

    record = exported["records"][0]

    if isinstance(record, dict):
        assert record["name"] == "Cafe Export"
    else:
        assert record.name == "Cafe Export"

    assert Path(exported["path"]).name == "cafes_Islamabad.csv"


def test_scrape_endpoint_rejects_unsupported_source():
    response = client.post(
        "/scrape",
        json={
            "source": "unknown",
            "query": "cafes",
            "location": "Islamabad",
        },
    )

    assert response.status_code == 422


def test_scrape_endpoint_rejects_empty_query():
    response = client.post(
        "/scrape",
        json={
            "source": "google_maps",
            "query": "",
            "location": "Islamabad",
        },
    )

    assert response.status_code == 422


def test_scrape_endpoint_rejects_invalid_output():
    response = client.post(
        "/scrape",
        json={
            "source": "google_maps",
            "query": "cafes",
            "location": "Islamabad",
            "output": "pdf",
        },
    )

    assert response.status_code == 422


def test_scrape_endpoint_accepts_website_source(monkeypatch):
    fake_engine = FakeEngine(
        ScrapeResult(
            records=[
                FakeRecord(
                    name="Example Website",
                    address="",
                    source="website",
                )
            ]
        )
    )

    monkeypatch.setattr(
        app_module,
        "build_engine",
        lambda source, database: fake_engine,
    )

    response = client.post(
        "/scrape",
        json={
            "source": "website",
            "query": "https://example.com",
            "location": "International",
        },
    )

    assert response.status_code == 200


def test_scrape_endpoint_accepts_ecommerce_source(monkeypatch):
    fake_engine = FakeEngine(
        ScrapeResult(
            records=[
                FakeRecord(
                    name="Test Product",
                    address="",
                    source="ecommerce",
                )
            ]
        )
    )

    monkeypatch.setattr(
        app_module,
        "build_engine",
        lambda source, database: fake_engine,
    )

    response = client.post(
        "/scrape",
        json={
            "source": "ecommerce",
            "query": "https://example.com/product",
            "location": "International",
        },
    )

    assert response.status_code == 200


def test_data_request_endpoint_uses_request_export_service(monkeypatch):
    """Verify /data-request executes the request and optional export."""
    class FakeRequestExportService:
        def __init__(self):
            self.specification = None

        def submit(self, specification):
            self.specification = specification

            return (
                ScrapeResult(records=[]),
                Path("Restaurants_Islamabad.csv"),
            )

    fake_service = FakeRequestExportService()

    monkeypatch.setattr(
        app_module,
        "build_engine",
        lambda source, database: object(),
    )

    monkeypatch.setattr(
        app_module,
        "build_request_export_service",
        lambda engine: fake_service,
    )

    response = client.post(
        "/data-request",
        json={
            "category": "Restaurants",
            "location": "Islamabad",
            "fields": ["name", "phone", "website"],
            "limit": 100,
            "source": "google_maps",
            "output": "csv",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 0
    assert data["errors"] == []
    assert data["output"] == "csv"
    assert data["export_path"] == "Restaurants_Islamabad.csv"
    assert fake_service.specification.category == "Restaurants"
    assert fake_service.specification.location == "Islamabad"
    assert fake_service.specification.output == "csv"


def test_data_request_endpoint_without_output(monkeypatch):
    """Verify /data-request works without optional export."""
    class FakeRequestExportService:
        def submit(self, specification):
            return (
                ScrapeResult(records=[]),
                None,
            )

    fake_service = FakeRequestExportService()

    monkeypatch.setattr(
        app_module,
        "build_engine",
        lambda source, database: object(),
    )

    monkeypatch.setattr(
        app_module,
        "build_request_export_service",
        lambda engine: fake_service,
    )

    response = client.post(
        "/data-request",
        json={
            "category": "Restaurants",
            "location": "Islamabad",
            "fields": ["name", "phone"],
            "limit": 10,
            "source": "google_maps",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 0
    assert data["errors"] == []
    assert data["output"] is None
    assert data["export_path"] is None