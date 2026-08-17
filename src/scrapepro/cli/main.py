"""Command-line interface for ScrapePro."""

import argparse
import sys
from pathlib import Path
from scrapepro.processors.storage import StorageProcessor
from scrapepro.storage.sqlite import SQLiteStorage
from scrapepro.config.settings import Settings
from scrapepro.core.task import ScrapeTask
from scrapepro.core.engine import ScrapeEngine
from scrapepro.core.pipeline import Pipeline
from scrapepro.processors.cleaner import Cleaner
from scrapepro.processors.deduplicator import Deduplicator
from scrapepro.processors.enricher import Enricher
from scrapepro.processors.location_enricher import LocationEnrichmentProvider
from scrapepro.processors.normalizer import Normalizer
from scrapepro.processors.validator import Validator
from scrapepro.scrapers.google_maps import GoogleMapsScraper
from scrapepro.version import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build and return the ScrapePro argument parser."""
    parser = argparse.ArgumentParser(
        prog="scrapepro",
        description="A modular business data scraping and processing platform.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
    )

    scrape_parser = subparsers.add_parser(
        "scrape",
        help="Run a scraping task.",
    )

    scrape_parser.add_argument(
        "--source",
        required=True,
        help="Data source to scrape from.",
    )

    scrape_parser.add_argument(
        "--query",
        required=True,
        help="Search query.",
    )

    scrape_parser.add_argument(
        "--location",
        required=True,
        help="Search location.",
    )

    scrape_parser.add_argument(
        "--output",
        choices=["csv", "json", "excel"],
        default=None,
        help="Export format.",
    )
    scrape_parser.add_argument(
        "--database",
        default="scrapepro.db",
        help="SQLite database path.",
    )

    return parser


def build_scrape_task(args: argparse.Namespace) -> ScrapeTask:
    """Build a ScrapeTask from parsed CLI arguments."""
    return ScrapeTask(
        source=args.source,
        query=args.query,
        location=args.location,
        output=args.output,
        database=args.database,
    )


def build_scraper(source: str, settings: Settings):
    """Build the scraper for a configured source."""
    if source == "google_maps":
        return GoogleMapsScraper(
            api_key=settings.require_google_maps_api_key()
        )

    raise ValueError(f"Unsupported scraping source: {source}")


def build_pipeline(database: str | Path) -> Pipeline:
    """Build the default ScrapePro processing pipeline."""
    pipeline = Pipeline()

    pipeline.add(Cleaner())
    pipeline.add(Normalizer())
    pipeline.add(Deduplicator())
    pipeline.add(Validator())
    pipeline.add(Enricher(LocationEnrichmentProvider()))

    storage = SQLiteStorage(database)
    pipeline.add(StorageProcessor(storage))

    return pipeline


def build_exporter(output_format: str | None):
    """Build an exporter for the requested output format."""
    if output_format == "csv":
        from scrapepro.exporters.csv import CSVExporter

        return CSVExporter()

    if output_format == "json":
        from scrapepro.exporters.json import JSONExporter

        return JSONExporter()

    if output_format == "excel":
        from scrapepro.exporters.excel import ExcelExporter

        return ExcelExporter()

    if output_format is None:
        return None

    raise ValueError(f"Unsupported output format: {output_format}")


def build_export_path(
    output_format: str,
    query: str,
    location: str,
) -> Path:
    """Build the default export file path."""
    extensions = {
        "csv": ".csv",
        "json": ".json",
        "excel": ".xlsx",
    }

    if output_format not in extensions:
        raise ValueError(f"Unsupported output format: {output_format}")

    filename = f"{query}_{location}{extensions[output_format]}"
    return Path(filename)


def main() -> None:
    """Run the ScrapePro command-line interface."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scrape":
        try:
            settings = Settings()
            task = build_scrape_task(args)
            scraper = build_scraper(task.source, settings)
            pipeline = build_pipeline(task.database)

            engine = ScrapeEngine(scraper, pipeline=pipeline)
            result = engine.run(task)
        except ValueError as exc:
            print(f"Error: {exc}")
            return

        print(f"Records: {len(result.records)}")

        for index, record in enumerate(result.records, start=1):
            print(
                f"{index}. {record.name} | "
                f"{record.address} | "
                f"Rating: {record.rating}"
            )

        if task.output:
            exporter = build_exporter(task.output)
            output_path = build_export_path(
                task.output,
                task.query,
                task.location,
            )
            exporter.export(result.records, output_path)
            print(f"Exported: {output_path}")

        if result.errors:
            for error in result.errors:
                print(f"Error: {error}")


if __name__ == "__main__":
    main()
