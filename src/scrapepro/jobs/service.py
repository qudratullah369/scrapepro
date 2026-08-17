"""Job execution service for ScrapePro."""

from dataclasses import asdict
from typing import Any

from scrapepro.core.engine import ScrapeEngine
from scrapepro.core.task import ScrapeTask
from scrapepro.jobs.store import Job, JobStore


class JobService:
    """Create and execute scraping jobs."""

    def __init__(self, store: JobStore, engine: ScrapeEngine) -> None:
        """Initialize the job service."""
        self.store = store
        self.engine = engine

    def create_and_run(self, task: ScrapeTask) -> Job:
        """Create a job, execute the task, and update the job result."""
        job = self.store.create()
        self.store.update(job.job_id, status="running")

        try:
            result = self.engine.run(task)

            records: list[Any] = [
                asdict(record) for record in result.records
            ]

            status = "completed" if result.success else "failed"

            self.store.update(
                job.job_id,
                status=status,
                count=result.count,
                errors=[str(error) for error in result.errors],
                records=records,
            )
        except Exception as exc:
            self.store.update(
                job.job_id,
                status="failed",
                errors=[str(exc)],
            )

        return self.store.get(job.job_id) or job
