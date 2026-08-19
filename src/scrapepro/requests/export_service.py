"""Export client request results using ScrapePro exporters."""

from pathlib import Path

from scrapepro.core.result import ScrapeResult
from scrapepro.exporters.service import ExportService
from scrapepro.requests.service import RequestService
from scrapepro.requests.specification import DataSpecification


class RequestExportService:
    """Execute a client request and optionally export its results."""

    def __init__(
        self,
        request_service: RequestService,
        export_service: ExportService | None = None,
    ) -> None:
        """Initialize the request export service."""
        self.request_service = request_service
        self.export_service = export_service or ExportService()

    def submit(
        self,
        specification: DataSpecification,
    ) -> tuple[ScrapeResult, Path | None]:
        """Execute a client request and export its results when requested."""
        result = self.request_service.submit(specification)

        if result.errors or specification.output is None:
            return result, None

        output_path = self.export_service.export(
            result.records,
            specification.output,
            specification.category,
            specification.location,
        )

        return result, output_path
