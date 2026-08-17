from dataclasses import dataclass

import pytest

from scrapepro.exporters.service import ExportService


@dataclass
class FakeRecord:
    name: str


def test_build_csv_export_path():
    path = ExportService.build_export_path(
        "csv",
        "cafes",
        "Islamabad",
    )

    assert path.name == "cafes_Islamabad.csv"


def test_build_json_export_path():
    path = ExportService.build_export_path(
        "json",
        "restaurants",
        "Lahore",
    )

    assert path.name == "restaurants_Lahore.json"


def test_build_excel_export_path():
    path = ExportService.build_export_path(
        "excel",
        "shops",
        "Multan",
    )

    assert path.name == "shops_Multan.xlsx"


def test_missing_location_uses_unknown():
    path = ExportService.build_export_path(
        "csv",
        "cafes",
        None,
    )

    assert path.name == "cafes_unknown.csv"


def test_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported output format"):
        ExportService.build_export_path(
            "pdf",
            "cafes",
            "Islamabad",
        )


def test_export_csv(tmp_path):
    service = ExportService()

    output = tmp_path / "result.csv"

    class TestExporter:
        def export(self, records, path):
            path.write_text("name\nCafe A\n", encoding="utf-8")
            return path

    service._build_exporter = lambda output_format: TestExporter()

    result = service.export(
        [FakeRecord("Cafe A")],
        "csv",
        "cafes",
        "Islamabad",
    )

    assert result.name == "cafes_Islamabad.csv"
    assert result.exists()
