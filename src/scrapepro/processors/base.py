"""Base processor interface for ScrapePro."""

from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    """Abstract base class for all ScrapePro processors."""

    @abstractmethod
    def process(self, records: list) -> list:
        """Process records and return the processed records."""
        raise NotImplementedError
