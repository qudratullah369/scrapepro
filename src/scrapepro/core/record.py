"""Business record model for ScrapePro."""

from dataclasses import dataclass


@dataclass
class Record:
    """Represent a structured business record."""

    name: str
    category: str | None = None
    phone: str | None = None
    website: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    rating: float | None = None
    reviews: int | None = None
    source: str = "unknown"
    place_id: str | None = None
