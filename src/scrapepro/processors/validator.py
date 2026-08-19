"""Validator processor for ScrapePro."""

from typing import List

from scrapepro.core.record import Record
from scrapepro.processors.base import BaseProcessor


class Validator(BaseProcessor):
    """Ensure records have minimum required fields."""

    def process(self, records: List[Record]) -> List[Record]:
        """Return only records that pass validation."""
        valid = []
        for record in records:
            if self._is_valid(record):
                valid.append(record)
        return valid

    @staticmethod
    def _is_valid(record: Record) -> bool:
        """Check if a record meets basic requirements."""
        # Name must be present and non-empty
        if not record.name or not record.name.strip():
            return False

        # Website records are valid when they have a name and website URL.
        if record.source == "website":
            return bool(record.website and record.website.strip())

        # Business records must have either phone or address.
        has_phone = record.phone and record.phone.strip()
        has_address = record.address and record.address.strip()
        if not (has_phone or has_address):
            return False

        return True
