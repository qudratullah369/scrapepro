"""Task definitions for ScrapePro."""


class ScrapeTask:
    """Represent a scraping task."""

    def __init__(
        self,
        source: str,
        query: str,
        location: str | None = None,
        output: str | None = None,
        database: str | None = None,
        fields: list[str] | None = None,
        limit: int | None = None,
    ) -> None:
        """Initialize a scraping task."""
        self.source = source
        self.query = query
        self.location = location
        self.output = output
        self.database = database
        self.fields = fields or []
        self.limit = limit

    def __repr__(self) -> str:
        """Return a readable representation of the task."""
        return (
            f"ScrapeTask("
            f"source={self.source!r}, "
            f"query={self.query!r}, "
            f"location={self.location!r}, "
            f"output={self.output!r}, "
            f"database={self.database!r}, "
            f"fields={self.fields!r}, "
            f"limit={self.limit!r}"
            f")"
        )
