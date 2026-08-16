import csv

from scrapepro.core.record import Record
from scrapepro.exporters.csv import CSVExporter


def test_csv_exporter_writes_header_and_records(tmp_path):
    records = [
        Record(
            name="Cafe A",
            category="cafe",
            phone="+923001234567",
            website="https://example.com",
            address="Main Street, Islamabad, Pakistan",
            city="Islamabad",
            country="Pakistan",
            latitude=33.6844,
            longitude=73.0479,
            rating=4.7,
            reviews=120,
            source="google_maps",
            place_id="p1",
        )
    ]

    output_path = tmp_path / "cafes.csv"

    result = CSVExporter().export(records, output_path)

    assert result == output_path
    assert output_path.exists()

    with output_path.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["name"] == "Cafe A"
    assert rows[0]["city"] == "Islamabad"
    assert rows[0]["country"] == "Pakistan"
    assert rows[0]["rating"] == "4.7"
    assert rows[0]["reviews"] == "120"
    assert rows[0]["place_id"] == "p1"


def test_csv_exporter_writes_empty_dataset_with_header(tmp_path):
    output_path = tmp_path / "empty.csv"

    CSVExporter().export([], output_path)

    with output_path.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.reader(file)
        rows = list(reader)

    assert rows == [CSVExporter.fieldnames]
