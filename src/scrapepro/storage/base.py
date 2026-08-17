"""Base storage interface for ScrapePro."""

from abc import ABC, abstractmethod

from scrapepro.core.record import Record


class BaseStorage(ABC):
    """Abstract interface for ScrapePro storage backends."""

    @abstractmethod
    def save(self, record: Record) -> None:
        """Save one Record."""
        raise NotImplementedError

    @abstractmethod
    def save_many(self, records: list[Record]) -> None:
        """Save multiple Records."""
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Return the number of stored records."""
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> list[Record]:
        """Return all stored records."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, record_id: int) -> Record | None:
        """Return a Record by database ID."""
        raise NotImplementedError

    @abstractmethod
    def find_by_place_id(self, place_id: str) -> Record | None:
        """Return a Record by place ID."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Close the storage connection."""
        raise NotImplementedError
