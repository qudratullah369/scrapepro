"""Command-line interface for ScrapePro."""

import argparse

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

    return parser


def main() -> None:
    """Run the ScrapePro command-line interface."""
    parser = build_parser()
    parser.parse_args()


if __name__ == "__main__":
    main()
