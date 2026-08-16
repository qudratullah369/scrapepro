"""Command-line interface for ScrapePro."""

import argparse
import sys

from scrapepro.config.settings import Settings
from scrapepro.core.task import ScrapeTask
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

    return parser


def build_scrape_task(args: argparse.Namespace) -> ScrapeTask:
    """Build a ScrapeTask from parsed CLI arguments."""
    return ScrapeTask(
        source=args.source,
        query=args.query,
        location=args.location,
        output=args.output,
    )


def build_scraper(source: str, settings: Settings):
    """Build the scraper for a configured source."""
    if source == "google_maps":
        return GoogleMapsScraper(
            api_key=settings.require_google_maps_api_key()
        )

    raise ValueError(f"Unsupported scraping source: {source}")


def main() -> None:
    """Run the ScrapePro command-line interface."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scrape":
        settings = Settings()
        task = build_scrape_task(args)
        scraper = build_scraper(task.source, settings)
        result = scraper.scrape(task)

        print(f"Records: {len(result.records)}")

        for index, record in enumerate(result.records, start=1):
            print(
                f"{index}. {record.name} | "
                f"{record.address} | "
                f"Rating: {record.rating}"
            )

        if result.errors:
            for error in result.errors:
                print(f"Error: {error}")


if __name__ == "__main__":
    main()
