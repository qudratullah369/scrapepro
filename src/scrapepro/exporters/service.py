"""Shared export service for ScrapePro."""

from pathlib import Path

from scrapepro.core.record import Record


class ExportService:
    """Select an exporter and export records to a file."""

    def export(
        self,
        records: list[Record],
        output_format: str,
        query: str,
        location: str | None,
    ) -> Path:
        """Export records using the requested format."""
        exporter = self._build_exporter(output_format)
        output_path = self.build_export_path(
            output_format,
            query,
            location,
        )
        return exporter.export(records, output_path)

    @staticmethod
    def _build_exporter(output_format: str):
        """Build an exporter for the requested format."""
        if output_format == "csv":
            from scrapepro.exporters.csv import CSVExporter

            return CSVExporter()

        if output_format == "json":
            from scrapepro.exporters.json import JSONExporter

            return JSONExporter()

        if output_format == "excel":
            from scrapepro.exporters.excel import ExcelExporter

            return ExcelExporter()

        raise ValueError(
            f"Unsupported output format: {output_format}"
        )

    @staticmethod
    def build_export_path(
        output_format: str,
        query: str,
        location: str | None,
    ) -> Path:
        """Build the default export file path."""
        extensions = {
            "csv": ".csv",
            "json": ".json",
            "excel": ".xlsx",
        }

        if output_format not in extensions:
            raise ValueError(
                f"Unsupported output format: {output_format}"
            )

        safe_location = location or "unknown"
        filename = (
            f"{query}_{safe_location}"
            f"{extensions[output_format]}"
        )

        return Path(filename)
