"""Dependencies for client data request API."""

from scrapepro.core.engine import ScrapeEngine
from scrapepro.requests.export_service import RequestExportService
from scrapepro.requests.executor import RequestExecutor
from scrapepro.requests.service import RequestService


def build_request_service(engine: ScrapeEngine) -> RequestService:
    """Build a client request service from a scrape engine."""
    executor = RequestExecutor(engine)
    return RequestService(executor)


def build_request_export_service(
    engine: ScrapeEngine,
) -> RequestExportService:
    """Build a client request export service from a scrape engine."""
    request_service = build_request_service(engine)
    return RequestExportService(request_service)
