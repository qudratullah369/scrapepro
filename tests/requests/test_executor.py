from scrapepro.core.result import ScrapeResult
from scrapepro.core.task import ScrapeTask
from scrapepro.requests.executor import RequestExecutor
from scrapepro.requests.specification import DataSpecification


class FakeTaskBuilder:
    def __init__(self):
        self.specification = None

    def build(self, specification):
        self.specification = specification
        return ScrapeTask(
            source="google_maps",
            query=specification.category,
            location=specification.location,
        )


class FakeEngine:
    def __init__(self):
        self.task = None
        self.result = ScrapeResult()

    def run(self, task):
        self.task = task
        return self.result


def test_request_executor_builds_and_runs_task():
    builder = FakeTaskBuilder()
    engine = FakeEngine()
    executor = RequestExecutor(
        engine=engine,
        task_builder=builder,
    )

    specification = DataSpecification(
        category="Restaurants",
        location="Islamabad",
    )

    result = executor.execute(specification)

    assert result is engine.result
    assert builder.specification is specification
    assert engine.task.source == "google_maps"
    assert engine.task.query == "Restaurants"
    assert engine.task.location == "Islamabad"
