"""Excel exporter for ScrapePro."""

from pathlib import Path

from openpyxl import Workbook

from scrapepro.core.record import Record


class ExcelExporter:
    """Export Record objects to an Excel file."""

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
        """Write records to an Excel file and return its path."""
        output_path = Path(path)

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Records"

        worksheet.append(self.fieldnames)

        for record in records:
            worksheet.append(
                [
                    getattr(record, field)
                    for field in self.fieldnames
                ]
            )

        workbook.save(output_path)

        return output_path
