from dataclasses import dataclass

from scrapepro.core.result import ScrapeResult
from scrapepro.core.task import ScrapeTask
from scrapepro.jobs.service import JobService
from scrapepro.jobs.store import (
    JOB_COMPLETED,
    JOB_FAILED,
    JobStore,
)


@dataclass
class FakeRecord:
    name: str
    address: str


class FakeEngine:
    def __init__(self, result):
        self.result = result

    def run(self, task):
        assert task.source == "google_maps"
        assert task.query == "cafes"
        assert task.location == "Islamabad"
        return self.result


def make_task():
    return ScrapeTask(
        source="google_maps",
        query="cafes",
        location="Islamabad",
    )


def test_create_and_run_completed_job():
    store = JobStore()

    engine = FakeEngine(
        ScrapeResult(
            records=[
                FakeRecord(
                    name="Cafe A",
                    address="Islamabad",
                )
            ]
        )
    )

    service = JobService(store, engine)

    job = service.create_and_run(make_task())

    assert job.status == JOB_COMPLETED
    assert job.count == 1
    assert job.errors == []
    assert job.records == [
        {
            "name": "Cafe A",
            "address": "Islamabad",
        }
    ]


def test_create_and_run_failed_job():
    store = JobStore()

    engine = FakeEngine(
        ScrapeResult(
            records=[],
            errors=["Google Maps API error"],
        )
    )

    service = JobService(store, engine)

    job = service.create_and_run(make_task())

    assert job.status == JOB_FAILED
    assert job.count == 0
    assert job.errors == ["Google Maps API error"]
    assert job.records == []


class RaisingEngine:
    def run(self, task):
        raise RuntimeError("Unexpected scraper failure")


def test_create_and_run_handles_exception():
    store = JobStore()
    service = JobService(store, RaisingEngine())

    job = service.create_and_run(make_task())

    assert job.status == JOB_FAILED
    assert job.count == 0
    assert job.errors == ["Unexpected scraper failure"]
