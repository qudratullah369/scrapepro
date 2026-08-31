"""Dependencies and service builders for the ScrapePro API."""

from scrapepro.config.settings import Settings
from scrapepro.core.engine import ScrapeEngine
from scrapepro.core.pipeline import Pipeline
from scrapepro.processors.cleaner import Cleaner
from scrapepro.processors.deduplicator import Deduplicator
from scrapepro.processors.enricher import Enricher
from scrapepro.processors.location_enricher import LocationEnrichmentProvider
from scrapepro.processors.normalizer import Normalizer
from scrapepro.processors.storage import StorageProcessor
from scrapepro.processors.validator import Validator
from scrapepro.scrapers.ecommerce import EcommerceScraper
from scrapepro.scrapers.google_maps import GoogleMapsScraper
from scrapepro.scrapers.website import WebsiteScraper
from scrapepro.storage.sqlite import SQLiteStorage


def build_scraper(source: str):
    """Build a scraper for the requested source."""
    settings = Settings()

    if source == "google_maps":
        return GoogleMapsScraper(
            api_key=settings.require_google_maps_api_key()
        )

    if source == "website":
        return WebsiteScraper()

    if source == "ecommerce":
        return EcommerceScraper()

    raise ValueError(f"Unsupported scraping source: {source}")


def build_pipeline(database: str) -> Pipeline:
    """Build the default API processing pipeline."""
    pipeline = Pipeline()

    pipeline.add(Cleaner())
    pipeline.add(Normalizer())
    pipeline.add(Deduplicator())
    pipeline.add(Validator())
    pipeline.add(Enricher(LocationEnrichmentProvider()))

    storage = SQLiteStorage(database)
    pipeline.add(StorageProcessor(storage))

    return pipeline


def build_engine(
    source: str,
    database: str,
) -> ScrapeEngine:
    """Build a scraping engine for the requested source."""
    scraper = build_scraper(source)
    pipeline = build_pipeline(database)

    return ScrapeEngine(
        scraper=scraper,
        pipeline=pipeline,
    )
