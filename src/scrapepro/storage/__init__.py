"""Storage backends for ScrapePro."""

from scrapepro.storage.base import BaseStorage
from scrapepro.storage.sqlite import SQLiteStorage

__all__ = ["BaseStorage", "SQLiteStorage"]
