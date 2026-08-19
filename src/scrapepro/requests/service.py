"""Client data request service for ScrapePro."""

from scrapepro.core.result import ScrapeResult
from scrapepro.requests.executor import RequestExecutor
from scrapepro.requests.specification import DataSpecification


class RequestService:
    """Provide a simple service interface for client data requests."""

    def __init__(
        self,
        executor: RequestExecutor,
    ) -> None:
        """Initialize the request service."""
        self.executor = executor

    def submit(self, specification: DataSpecification) -> ScrapeResult:
        """Submit a client data request for execution."""
        return self.executor.execute(specification)
