from pathlib import Path
from dataclasses import dataclass

from fastapi.testclient import TestClient

import scrapepro.api.app as app_module
from scrapepro.core.result import ScrapeResult
from scrapepro.jobs.service import JobService
from scrapepro.jobs.store import JOB_COMPLETED, JOB_NOT_FOUND, Job


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


class FakeJobService:
    def __init__(self, result, job_store):
        self.result = result
        self.job_store = job_store

    def create_and_run(self, task):
        result = self.result.run(task)

        job = self.job_store.create()

        self.job_store.update(
            job.job_id,
            status=JOB_COMPLETED,
            count=result.count,
            errors=[str(error) for error in result.errors],
            records=[
                {
                    "name": record.name,
                    "address": record.address,
                    "source": record.source,
                }
                for record in result.records
            ],
        )

        return self.job_store.get(job.job_id)


def test_scrape_endpoint_creates_job(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "build_job_service",
        lambda source, database, job_store: FakeJobService(
            FakeEngine(
                ScrapeResult(
                    records=[
                        FakeRecord(
                            name="Cafe A",
                            address="Main Street, Islamabad, Pakistan",
                        )
                    ]
                )
            ),
            job_store,
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
        "status": JOB_NOT_FOUND,
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
        "build_job_service",
        lambda source, database, job_store: FakeJobService(
            FakeEngine(
                ScrapeResult(
                    records=[
                        FakeRecord(
                            name="Cafe Export",
                            address="Islamabad",
                        )
                    ]
                )
            ),
            job_store,
        ),
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
    assert exported["records"][0]["name"] if isinstance(
        exported["records"][0], dict
    ) else exported["records"][0].name == "Cafe Export"
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
    monkeypatch.setattr(
        app_module,
        "build_job_service",
        lambda source, database, job_store: FakeJobService(
            FakeEngine(
                ScrapeResult(
                    records=[
                        FakeRecord(
                            name="Example Website",
                            address="",
                            source="website",
                        )
                    ]
                )
            ),
            job_store,
        ),
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
    monkeypatch.setattr(
        app_module,
        "build_job_service",
        lambda source, database, job_store: FakeJobService(
            FakeEngine(
                ScrapeResult(
                    records=[
                        FakeRecord(
                            name="Test Product",
                            address="",
                            source="ecommerce",
                        )
                    ]
                )
            ),
            job_store,
        ),
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
