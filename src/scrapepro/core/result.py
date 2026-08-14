"""Result definitions for ScrapePro."""


class ScrapeResult:
    """Represent the result of a scraping task."""

    def __init__(
        self,
        records: list | None = None,
        errors: list | None = None,
    ) -> None:
        """Initialize a scrape result."""
        self.records = records if records is not None else []
        self.errors = errors if errors is not None else []

    @property
    def success(self) -> bool:
        """Return True when no errors occurred."""
        return not self.errors

    @property
    def count(self) -> int:
        """Return the number of records."""
        return len(self.records)
