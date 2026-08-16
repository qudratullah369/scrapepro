"""JSON exporter for ScrapePro."""

import json
from dataclasses import asdict
from pathlib import Path

from scrapepro.core.record import Record


class JSONExporter:
    """Export Record objects to a JSON file."""

    def export(self, records: list[Record], path: str | Path) -> Path:
        """Write records to a JSON file and return its path."""
        output_path = Path(path)

        data = [asdict(record) for record in records]

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

        return output_path
