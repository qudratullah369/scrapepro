from scrapepro.cli.main import build_parser


def test_cli_parser_has_expected_program_name():
    parser = build_parser()

    assert parser.prog == "scrapepro"


def test_cli_parser_supports_version():
    parser = build_parser()

    action = next(
        action
        for action in parser._actions
        if "--version" in action.option_strings
    )

    assert action.dest == "version"


def test_cli_parser_supports_scrape_command():
    parser = build_parser()

    args = parser.parse_args(
        [
            "scrape",
            "--source",
            "google_maps",
            "--query",
            "restaurants",
            "--location",
            "Islamabad",
        ]
    )

    assert args.command == "scrape"
    assert args.source == "google_maps"
    assert args.query == "restaurants"
    assert args.location == "Islamabad"


def test_cli_scrape_requires_source_query_and_location():
    parser = build_parser()

    for arguments in (
        ["scrape"],
        ["scrape", "--source", "google_maps"],
        ["scrape", "--source", "google_maps", "--query", "restaurants"],
    ):
        try:
            parser.parse_args(arguments)
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError("Expected argument parsing to fail.")


def test_build_scrape_task_creates_scrape_task():
    parser = build_parser()

    args = parser.parse_args(
        [
            "scrape",
            "--source",
            "google_maps",
            "--query",
            "restaurants",
            "--location",
            "Islamabad",
        ]
    )

    from scrapepro.cli.main import build_scrape_task

    task = build_scrape_task(args)

    assert task.source == "google_maps"
    assert task.query == "restaurants"
    assert task.location == "Islamabad"


def test_build_scraper_supports_google_maps(monkeypatch):
    from scrapepro.cli.main import build_scraper
    from scrapepro.config.settings import Settings
    from scrapepro.scrapers.google_maps import GoogleMapsScraper

    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test-api-key")

    scraper = build_scraper("google_maps", Settings())

    assert isinstance(scraper, GoogleMapsScraper)
    assert scraper.api_key == "test-api-key"


def test_build_scraper_rejects_unsupported_source():
    from scrapepro.cli.main import build_scraper
    from scrapepro.config.settings import Settings

    try:
        build_scraper("unknown", Settings())
    except ValueError as exc:
        assert str(exc) == "Unsupported scraping source: unknown"
    else:
        raise AssertionError("Expected unsupported source to raise ValueError.")


def test_cli_main_executes_scrape_and_prints_result(monkeypatch, capsys):
    from scrapepro.cli import main as cli

    class FakeResult:
        records = ["record-1", "record-2"]
        errors = ["test error"]

    class FakeScraper:
        def __init__(self):
            self.received_task = None

        def scrape(self, task):
            self.received_task = task
            return FakeResult()

    fake_scraper = FakeScraper()

    monkeypatch.setattr(
        cli,
        "Settings",
        lambda: object(),
    )
    monkeypatch.setattr(
        cli,
        "build_scraper",
        lambda source, settings: fake_scraper,
    )
    monkeypatch.setattr(
        cli,
        "build_scrape_task",
        lambda args: __import__(
            "scrapepro.core.task",
            fromlist=["ScrapeTask"],
        ).ScrapeTask(
            source=args.source,
            query=args.query,
            location=args.location,
        ),
    )
    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "scrapepro",
            "scrape",
            "--source",
            "google_maps",
            "--query",
            "restaurants",
            "--location",
            "Islamabad",
        ],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Records: 2" in captured.out
    assert "Error: test error" in captured.out
    assert fake_scraper.received_task.source == "google_maps"
    assert fake_scraper.received_task.query == "restaurants"
    assert fake_scraper.received_task.location == "Islamabad"
