from scrapepro.api.request_dependencies import build_request_service
from scrapepro.core.engine import ScrapeEngine
from scrapepro.requests.service import RequestService


def test_build_request_service():
    engine = ScrapeEngine(scraper=None)

    service = build_request_service(engine)

    assert isinstance(service, RequestService)
    assert service.executor.engine is engine
