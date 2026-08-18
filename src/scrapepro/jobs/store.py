"""In-memory job storage for ScrapePro."""

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


JOB_QUEUED = "queued"
JOB_RUNNING = "running"
JOB_COMPLETED = "completed"
JOB_FAILED = "failed"
JOB_NOT_FOUND = "not_found"

VALID_JOB_STATUSES = frozenset(
    {
        JOB_QUEUED,
        JOB_RUNNING,
        JOB_COMPLETED,
        JOB_FAILED,
    }
)


@dataclass
class Job:
    """Represent a scraping job."""

    job_id: str
    status: str = JOB_QUEUED
    count: int = 0
    errors: list[str] = field(default_factory=list)
    records: list[Any] = field(default_factory=list)


class JobStore:
    """Store scraping jobs in memory."""

    def __init__(self) -> None:
        """Initialize an empty job store."""
        self._jobs: dict[str, Job] = {}

    def create(self) -> Job:
        """Create and store a new queued job."""
        job = Job(job_id=str(uuid4()))
        self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        """Return a job by ID, or None when it does not exist."""
        return self._jobs.get(job_id)

    def update(
        self,
        job_id: str,
        *,
        status: str | None = None,
        count: int | None = None,
        errors: list[str] | None = None,
        records: list[Any] | None = None,
    ) -> Job | None:
        """Update an existing job and return it."""
        job = self._jobs.get(job_id)

        if job is None:
            return None

        if status is not None:
            if status not in VALID_JOB_STATUSES:
                raise ValueError(f"Invalid job status: {status}")
            job.status = status

        if count is not None:
            job.count = count

        if errors is not None:
            job.errors = errors

        if records is not None:
            job.records = records

        return job
