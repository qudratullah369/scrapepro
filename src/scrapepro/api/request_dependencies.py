"""Dependencies for client data request API."""

from scrapepro.core.engine import ScrapeEngine
from scrapepro.requests.executor import RequestExecutor
from scrapepro.requests.service import RequestService


def build_request_service(engine: ScrapeEngine) -> RequestService:
    """Build a client request service from a scrape engine."""
    executor = RequestExecutor(engine)
    return RequestService(executor)
