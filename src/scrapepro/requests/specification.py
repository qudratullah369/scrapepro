"""Client data specification models for ScrapePro."""

from dataclasses import dataclass, field


@dataclass
class DataSpecification:
    """Define the business data a client wants to collect."""

    category: str
    location: str | None = None
    fields: list[str] = field(default_factory=list)
    limit: int | None = None
    source: str | None = None
    output: str | None = None

    def __post_init__(self) -> None:
        """Validate the specification."""
        if not self.category.strip():
            raise ValueError("Category is required.")

        if self.limit is not None and self.limit < 1:
            raise ValueError("Limit must be greater than zero.")

        if self.output is not None and self.output not in {
            "csv",
            "json",
            "excel",
        }:
            raise ValueError(
                "Output must be csv, json, or excel."
            )
