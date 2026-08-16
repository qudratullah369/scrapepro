import csv
import json

import pytest

from scrapepro.core.record import Record
from scrapepro.exporters.csv import CSVExporter
from scrapepro.exporters.json import JSONExporter
from scrapepro.processors.export import ExportProcessor


def test_export_processor_exports_records(tmp_path):
    records = [
        Record(
            name="Cafe A",
            category="cafe",
            address="Islamabad, Pakistan",
            city="Islamabad",
            country="Pakistan",
            rating=4.7,
            reviews=120,
            source="google_maps",
            place_id="p1",
        )
    ]

    csv_path = tmp_path / "cafes.csv"
    json_path = tmp_path / "cafes.json"

    processor = ExportProcessor(
        exporters=[
            CSVExporter(),
            JSONExporter(),
        ],
        output_paths=[
            csv_path,
            json_path,
        ],
    )

    result = processor.process(records)

    assert result == records
    assert csv_path.exists()
    assert json_path.exists()

    with csv_path.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["name"] == "Cafe A"
    assert rows[0]["city"] == "Islamabad"

    with json_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    assert data[0]["name"] == "Cafe A"
    assert data[0]["country"] == "Pakistan"


def test_export_processor_handles_empty_records(tmp_path):
    csv_path = tmp_path / "empty.csv"
    json_path = tmp_path / "empty.json"

    processor = ExportProcessor(
        exporters=[
            CSVExporter(),
            JSONExporter(),
        ],
        output_paths=[
            csv_path,
            json_path,
        ],
    )

    result = processor.process([])

    assert result == []
    assert csv_path.exists()
    assert json_path.exists()

    with json_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        assert json.load(file) == []


def test_export_processor_requires_matching_exporters_and_paths(
    tmp_path,
):
    with pytest.raises(
        ValueError,
        match="exporters and output_paths must have the same length",
    ):
        ExportProcessor(
            exporters=[CSVExporter()],
            output_paths=[
                tmp_path / "one.csv",
                tmp_path / "two.json",
            ],
        )
