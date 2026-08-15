"""Filter processor for ScrapePro."""

from collections.abc import Callable

from scrapepro.core.record import Record
from scrapepro.processors.base import BaseProcessor


class FilterRecordsProcessor(BaseProcessor):
    """Filter Record objects using a predicate function."""

    def __init__(self, predicate: Callable[[Record], bool]) -> None:
        """Initialize the filter with a predicate."""
        self.predicate = predicate

    def process(self, records: list[Record]) -> list[Record]:
        """Return records that satisfy the predicate."""
        return [record for record in records if self.predicate(record)]
