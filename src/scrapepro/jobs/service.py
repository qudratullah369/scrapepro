"""Job execution service for ScrapePro."""

from dataclasses import asdict
from typing import Any

from scrapepro.core.engine import ScrapeEngine
from scrapepro.core.task import ScrapeTask
from scrapepro.jobs.store import (
    JOB_COMPLETED,
    JOB_FAILED,
    JOB_RUNNING,
    Job,
    JobStore,
)


class JobService:
    """Create and execute scraping jobs."""

    def __init__(self, store: JobStore, engine: ScrapeEngine) -> None:
        """Initialize the job service."""
        self.store = store
        self.engine = engine

    def create_and_run(self, task: ScrapeTask) -> Job:
        """Create a job, execute the task, and update the job result."""
        job = self.store.create()
        self.store.update(job.job_id, status=JOB_RUNNING)

        try:
            result = self.engine.run(task)

            records: list[Any] = [
                asdict(record) for record in result.records
            ]

            status = JOB_COMPLETED if result.success else JOB_FAILED

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
                status=JOB_FAILED,
                errors=[str(exc)],
            )

        return self.store.get(job.job_id) or job
