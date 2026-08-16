import json

from scrapepro.core.record import Record
from scrapepro.exporters.json import JSONExporter


def test_json_exporter_writes_records(tmp_path):
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

    output_path = tmp_path / "cafes.json"

    result = JSONExporter().export(records, output_path)

    assert result == output_path
    assert output_path.exists()

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    assert len(data) == 1
    assert data[0]["name"] == "Cafe A"
    assert data[0]["city"] == "Islamabad"
    assert data[0]["country"] == "Pakistan"
    assert data[0]["rating"] == 4.7
    assert data[0]["reviews"] == 120
    assert data[0]["place_id"] == "p1"


def test_json_exporter_writes_empty_list(tmp_path):
    output_path = tmp_path / "empty.json"

    JSONExporter().export([], output_path)

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    assert data == []


def test_json_exporter_preserves_unicode(tmp_path):
    records = [
        Record(
            name="چائے خانہ",
            address="Islamabad, Pakistan",
            city="اسلام آباد",
            country="پاکستان",
        )
    ]

    output_path = tmp_path / "unicode.json"

    JSONExporter().export(records, output_path)

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    assert data[0]["name"] == "چائے خانہ"
    assert data[0]["city"] == "اسلام آباد"
    assert data[0]["country"] == "پاکستان"
