"""SQLite storage for ScrapePro."""

import sqlite3
from pathlib import Path

from scrapepro.core.record import Record


class SQLiteStorage:
    """Store Record objects in a SQLite database."""

    def __init__(self, path: str | Path) -> None:
        """Initialize SQLite storage."""
        self.path = Path(path)
        self.connection = sqlite3.connect(self.path)

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                phone TEXT,
                website TEXT,
                address TEXT,
                city TEXT,
                country TEXT,
                latitude REAL,
                longitude REAL,
                rating REAL,
                reviews INTEGER,
                source TEXT NOT NULL,
                place_id TEXT
            )
            """
        )

        self.connection.commit()

    def save(self, record: Record) -> None:
        """Save one Record to the database."""
        self.connection.execute(
            """
            INSERT INTO records (
                name,
                category,
                phone,
                website,
                address,
                city,
                country,
                latitude,
                longitude,
                rating,
                reviews,
                source,
                place_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.name,
                record.category,
                record.phone,
                record.website,
                record.address,
                record.city,
                record.country,
                record.latitude,
                record.longitude,
                record.rating,
                record.reviews,
                record.source,
                record.place_id,
            ),
        )

        self.connection.commit()

    def save_many(self, records: list[Record]) -> None:
        """Save multiple Records to the database."""
        self.connection.executemany(
            """
            INSERT INTO records (
                name,
                category,
                phone,
                website,
                address,
                city,
                country,
                latitude,
                longitude,
                rating,
                reviews,
                source,
                place_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    record.name,
                    record.category,
                    record.phone,
                    record.website,
                    record.address,
                    record.city,
                    record.country,
                    record.latitude,
                    record.longitude,
                    record.rating,
                    record.reviews,
                    record.source,
                    record.place_id,
                )
                for record in records
            ],
        )

        self.connection.commit()

    def count(self) -> int:
        """Return the number of stored records."""
        cursor = self.connection.execute(
            "SELECT COUNT(*) FROM records"
        )

        return cursor.fetchone()[0]

    def close(self) -> None:
        """Close the database connection."""
        self.connection.close()
