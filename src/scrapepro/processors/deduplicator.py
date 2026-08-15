"""Deduplicator processor for ScrapePro."""

from typing import List, Optional, Set

from scrapepro.core.record import Record
from scrapepro.processors.base import BaseProcessor


class Deduplicator(BaseProcessor):
    """Remove duplicate records based on various strategies."""

    def process(self, records: List[Record]) -> List[Record]:
        seen: Set[str] = set()
        unique: List[Record] = []

        for record in records:
            key = self._get_key(record)
            if key and key not in seen:
                seen.add(key)
                unique.append(record)

        return unique

    @staticmethod
    def _get_key(record: Record) -> Optional[str]:
        """Generate a unique key for deduplication."""
        # Prioritize place_id
        if record.place_id:
            return f"place_id:{record.place_id}"

        # Then phone (only digits)
        if record.phone:
            phone_clean = ''.join(filter(str.isdigit, record.phone))
            if phone_clean:
                return f"phone:{phone_clean}"

        # Then website
        if record.website:
            return f"website:{record.website}"

        # Then name + address (both present, normalized)
        if record.name and record.address:
            name_key = ' '.join(record.name.lower().split())
            addr_key = ' '.join(record.address.lower().split())
            return f"name_addr:{name_key}|{addr_key}"

        # No reliable key; treat as unique (but could be improved)
        return None
