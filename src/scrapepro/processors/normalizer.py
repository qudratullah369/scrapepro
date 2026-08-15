"""Normalizer processor for ScrapePro."""

from dataclasses import replace

from scrapepro.core.record import Record
from scrapepro.processors.base import BaseProcessor


class Normalizer(BaseProcessor):
    """Normalize basic textual values in Record objects."""

    def process(self, records: list[Record]) -> list[Record]:
        """Return normalized Record objects."""
        normalized = []

        for record in records:
            normalized.append(
                replace(
                    record,
                    name=self._normalize_text(record.name),
                    category=self._normalize_optional_text(record.category),
                    phone=self._normalize_optional_text(record.phone),
                    website=self._normalize_optional_text(record.website),
                    address=self._normalize_optional_text(record.address),
                    source=self._normalize_text(record.source),
                    place_id=self._normalize_optional_text(record.place_id),
                )
            )

        return normalized

    @staticmethod
    def _normalize_text(value: str) -> str:
        """Normalize a required text value."""
        return " ".join(value.split())

    @staticmethod
    def _normalize_optional_text(value: str | None) -> str | None:
        """Normalize an optional text value."""
        if value is None:
            return None

        return " ".join(value.split())
