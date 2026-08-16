"""CSV exporter for ScrapePro."""

import csv
from pathlib import Path

from scrapepro.core.record import Record


class CSVExporter:
    """Export Record objects to a CSV file."""

    fieldnames = [
        "name",
        "category",
        "phone",
        "website",
        "address",
        "city",
        "country",
        "latitude",
        "longitude",
        "rating",
        "reviews",
        "source",
        "place_id",
    ]

    def export(self, records: list[Record], path: str | Path) -> Path:
        """Write records to a CSV file and return its path."""
        output_path = Path(path)

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.fieldnames,
            )

            writer.writeheader()

            for record in records:
                writer.writerow(
                    {
                        field: getattr(record, field)
                        for field in self.fieldnames
                    }
                )

        return output_path
