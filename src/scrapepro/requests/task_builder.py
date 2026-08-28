"""Build ScrapePro tasks from client data specifications."""

from scrapepro.core.task import ScrapeTask
from scrapepro.requests.specification import DataSpecification
from scrapepro.requests.validator import RequestValidator


class TaskBuilder:
    """Convert validated client specifications into scrape tasks."""

    def __init__(
        self,
        validator: RequestValidator | None = None,
    ) -> None:
        """Initialize the task builder."""
        self.validator = validator or RequestValidator()

    def build(self, specification: DataSpecification) -> ScrapeTask:
        """Validate a specification and build a scrape task."""
        self.validator.validate(specification)

        source = specification.source or "google_maps"

        return ScrapeTask(
            source=source,
            query=specification.category,
            location=specification.location,
            output=specification.output,
            fields=[field.name for field in specification.fields],
            limit=specification.limit,
        )
