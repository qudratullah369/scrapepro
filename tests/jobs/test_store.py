from scrapepro.jobs.store import JobStore


def test_create_job():
    store = JobStore()

    job = store.create()

    assert job.job_id
    assert job.status == "queued"
    assert job.count == 0
    assert job.errors == []
    assert job.records == []


def test_get_job():
    store = JobStore()

    job = store.create()

    result = store.get(job.job_id)

    assert result is job


def test_get_missing_job_returns_none():
    store = JobStore()

    assert store.get("missing-job") is None


def test_update_job():
    store = JobStore()

    job = store.create()

    updated = store.update(
        job.job_id,
        status="completed",
        count=2,
        errors=[],
        records=["record-1", "record-2"],
    )

    assert updated is job
    assert job.status == "completed"
    assert job.count == 2
    assert job.errors == []
    assert job.records == ["record-1", "record-2"]


def test_update_missing_job_returns_none():
    store = JobStore()

    assert store.update("missing-job", status="failed") is None
