"""Execute validated client data requests for ScrapePro."""

from scrapepro.core.engine import ScrapeEngine
from scrapepro.core.result import ScrapeResult
from scrapepro.requests.specification import DataSpecification
from scrapepro.requests.task_builder import TaskBuilder


class RequestExecutor:
    """Convert client specifications into scrape results."""

    def __init__(
        self,
        engine: ScrapeEngine,
        task_builder: TaskBuilder | None = None,
    ) -> None:
        """Initialize the request executor."""
        self.engine = engine
        self.task_builder = task_builder or TaskBuilder()

    def execute(self, specification: DataSpecification) -> ScrapeResult:
        """Build and execute a scrape task."""
        task = self.task_builder.build(specification)
        return self.engine.run(task)
