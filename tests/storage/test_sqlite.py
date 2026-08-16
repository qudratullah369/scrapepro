from scrapepro.core.record import Record
from scrapepro.storage.sqlite import SQLiteStorage


def test_sqlite_storage_starts_empty(tmp_path):
    storage = SQLiteStorage(tmp_path / "records.db")

    assert storage.count() == 0

    storage.close()


def test_sqlite_storage_saves_record(tmp_path):
    storage = SQLiteStorage(tmp_path / "records.db")

    record = Record(
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

    storage.save(record)

    assert storage.count() == 1

    storage.close()


def test_sqlite_storage_saves_multiple_records(tmp_path):
    storage = SQLiteStorage(tmp_path / "records.db")

    records = [
        Record(
            name="Cafe A",
            address="Islamabad, Pakistan",
            city="Islamabad",
            country="Pakistan",
        ),
        Record(
            name="Cafe B",
            address="Lahore, Pakistan",
            city="Lahore",
            country="Pakistan",
        ),
    ]

    storage.save_many(records)

    assert storage.count() == 2

    storage.close()


def test_sqlite_storage_persists_data(tmp_path):
    database_path = tmp_path / "records.db"

    storage = SQLiteStorage(database_path)

    storage.save(
        Record(
            name="Cafe A",
            address="Islamabad, Pakistan",
            city="Islamabad",
            country="Pakistan",
        )
    )

    storage.close()

    reopened = SQLiteStorage(database_path)

    assert reopened.count() == 1

    reopened.close()


def test_sqlite_storage_handles_empty_save_many(tmp_path):
    storage = SQLiteStorage(tmp_path / "records.db")

    storage.save_many([])

    assert storage.count() == 0

    storage.close()
