from scrapepro.core.record import Record
from scrapepro.processors.storage import StorageProcessor
from scrapepro.storage.sqlite import SQLiteStorage


def test_storage_processor_saves_records(tmp_path):
    storage = SQLiteStorage(tmp_path / "records.db")

    records = [
        Record(
            name="Cafe A",
            address="Islamabad, Pakistan",
            city="Islamabad",
            country="Pakistan",
            source="google_maps",
            place_id="p1",
        ),
        Record(
            name="Cafe B",
            address="Lahore, Pakistan",
            city="Lahore",
            country="Pakistan",
            source="google_maps",
            place_id="p2",
        ),
    ]

    processor = StorageProcessor(storage)

    result = processor.process(records)

    assert result == records
    assert storage.count() == 2
    assert storage.get_by_id(1) == records[0]
    assert storage.get_by_id(2) == records[1]

    storage.close()


def test_storage_processor_handles_empty_records(tmp_path):
    storage = SQLiteStorage(tmp_path / "records.db")

    processor = StorageProcessor(storage)

    result = processor.process([])

    assert result == []
    assert storage.count() == 0

    storage.close()
