from pathlib import Path

from scrapepro.core.record import Record
from scrapepro.core.result import ScrapeResult
from scrapepro.requests.export_service import RequestExportService
from scrapepro.requests.specification import DataSpecification


class FakeRequestService:
    def __init__(self, result):
        self.result = result
        self.specification = None

    def submit(self, specification):
        self.specification = specification
        return self.result


class FakeExportService:
    def __init__(self):
        self.calls = []

    def export(self, records, output_format, query, location):
        self.calls.append(
            {
                "records": records,
                "output_format": output_format,
                "query": query,
                "location": location,
            }
        )
        return Path("Restaurants_Islamabad.csv")


def test_request_export_service_submits_and_exports():
    records = [
        Record(
            name="Cafe A",
            category="Restaurants",
            address="Islamabad",
            city="Islamabad",
            country="Pakistan",
            source="google_maps",
        )
    ]

    result = ScrapeResult(records=records)
    request_service = FakeRequestService(result)
    export_service = FakeExportService()

    service = RequestExportService(
        request_service=request_service,
        export_service=export_service,
    )

    specification = DataSpecification(
        category="Restaurants",
        location="Islamabad",
        output="csv",
    )

    returned_result, output_path = service.submit(specification)

    assert returned_result is result
    assert output_path == Path("Restaurants_Islamabad.csv")
    assert request_service.specification is specification

    assert export_service.calls == [
        {
            "records": records,
            "output_format": "csv",
            "query": "Restaurants",
            "location": "Islamabad",
        }
    ]


def test_request_export_service_does_not_export_without_output():
    result = ScrapeResult(records=[])
    request_service = FakeRequestService(result)
    export_service = FakeExportService()

    service = RequestExportService(
        request_service=request_service,
        export_service=export_service,
    )

    specification = DataSpecification(
        category="Restaurants",
        location="Islamabad",
    )

    returned_result, output_path = service.submit(specification)

    assert returned_result is result
    assert output_path is None
    assert export_service.calls == []


def test_request_export_service_does_not_export_failed_result():
    result = ScrapeResult(errors=["scraping failed"])
    request_service = FakeRequestService(result)
    export_service = FakeExportService()

    service = RequestExportService(
        request_service=request_service,
        export_service=export_service,
    )

    specification = DataSpecification(
        category="Restaurants",
        location="Islamabad",
        output="csv",
    )

    returned_result, output_path = service.submit(specification)

    assert returned_result is result
    assert output_path is None
    assert export_service.calls == []
