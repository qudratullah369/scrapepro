"""Export processor for ScrapePro."""

from pathlib import Path

from scrapepro.core.record import Record
from scrapepro.processors.base import BaseProcessor


class ExportProcessor(BaseProcessor):
    """Export Record objects using configured exporters."""

    def __init__(
        self,
        exporters: list[object],
        output_paths: list[str | Path],
    ) -> None:
        """Initialize the export processor."""
        if len(exporters) != len(output_paths):
            raise ValueError(
                "exporters and output_paths must have the same length."
            )

        self.exporters = exporters
        self.output_paths = [Path(path) for path in output_paths]

    def process(self, records: list[Record]) -> list[Record]:
        """Export records and return them unchanged."""
        for exporter, path in zip(
            self.exporters,
            self.output_paths,
        ):
            exporter.export(records, path)

        return records
