"""Command-line interface for ScrapePro."""

import argparse

from scrapepro.core.task import ScrapeTask
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

    return parser


def build_scrape_task(args: argparse.Namespace) -> ScrapeTask:
    """Build a ScrapeTask from parsed CLI arguments."""
    return ScrapeTask(
        source=args.source,
        query=args.query,
        location=args.location,
    )


def main() -> None:
    """Run the ScrapePro command-line interface."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scrape":
        task = build_scrape_task(args)
        print(task)


if __name__ == "__main__":
    main()
