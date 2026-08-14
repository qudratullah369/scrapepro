"""Cleaner processor for ScrapePro."""

from dataclasses import replace

from scrapepro.core.record import Record
from scrapepro.processors.base import BaseProcessor


class Cleaner(BaseProcessor):
    """Clean basic whitespace from Record values."""

    def process(self, records: list[Record]) -> list[Record]:
        """Return cleaned Record objects."""
        cleaned = []

        for record in records:
            cleaned.append(
                replace(
                    record,
                    name=record.name.strip(),
                    category=record.category.strip()
                    if record.category is not None
                    else None,
                    phone=record.phone.strip()
                    if record.phone is not None
                    else None,
                    website=record.website.strip()
                    if record.website is not None
                    else None,
                    address=record.address.strip()
                    if record.address is not None
                    else None,
                    source=record.source.strip(),
                    place_id=record.place_id.strip()
                    if record.place_id is not None
                    else None,
                )
            )

        return cleaned
