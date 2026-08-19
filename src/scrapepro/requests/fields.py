"""Client field requirements for ScrapePro."""

from dataclasses import dataclass


ALLOWED_FIELDS = frozenset(
    {
        "name",
        "category",
        "phone",
        "website",
        "address",
        "latitude",
        "longitude",
        "rating",
        "reviews",
        "place_id",
        "city",
        "country",
    }
)


@dataclass(frozen=True)
class FieldRequirement:
    """Define a field requested by a data client."""

    name: str
    required: bool = True

    def __post_init__(self) -> None:
        """Validate the requested field."""
        if self.name not in ALLOWED_FIELDS:
            raise ValueError(
                f"Unsupported data field: {self.name}"
            )
