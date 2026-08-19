from scrapepro.core.result import ScrapeResult
from scrapepro.requests.service import RequestService
from scrapepro.requests.specification import DataSpecification


class FakeExecutor:
    def __init__(self):
        self.specification = None
        self.result = ScrapeResult()

    def execute(self, specification):
        self.specification = specification
        return self.result


def test_request_service_submits_specification():
    executor = FakeExecutor()
    service = RequestService(executor)

    specification = DataSpecification(
        category="Restaurants",
        location="Islamabad",
        limit=100,
    )

    result = service.submit(specification)

    assert result is executor.result
    assert executor.specification is specification
