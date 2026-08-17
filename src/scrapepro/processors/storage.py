"""Storage processor for ScrapePro."""

from scrapepro.core.record import Record
from scrapepro.processors.base import BaseProcessor
from scrapepro.storage.base import BaseStorage


class StorageProcessor(BaseProcessor):
    """Persist Record objects using a storage backend."""

    def __init__(self, storage: BaseStorage) -> None:
        """Initialize the storage processor."""
        self.storage = storage

    def process(self, records: list[Record]) -> list[Record]:
        """Store records and return them unchanged."""
        self.storage.save_many(records)
        return records
