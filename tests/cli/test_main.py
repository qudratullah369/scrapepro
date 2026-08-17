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
    from scrapepro.core.record import Record

    class FakeResult:
        records = [
            Record(
                name="Cafe Test A",
                address="Islamabad, Pakistan",
                rating=4.5,
            ),
            Record(
                name="Cafe Test B",
                address="Blue Area, Islamabad, Pakistan",
                rating=4.2,
            ),
        ]
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
            database=args.database,
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
            "--database",
            "scrapepro.db",
        ],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Records: 2" in captured.out
    assert "Error: test error" in captured.out
    assert fake_scraper.received_task.source == "google_maps"
    assert fake_scraper.received_task.query == "restaurants"
    assert fake_scraper.received_task.location == "Islamabad"


def test_cli_main_prints_scraped_records(monkeypatch, capsys):
    from scrapepro.cli import main as cli
    from scrapepro.core.record import Record

    class FakeResult:
        records = [
            Record(
                name="Cafe A",
                address="Main Street, Islamabad, Pakistan",
                rating=4.7,
            ),
            Record(
                name="Cafe B",
                address="Blue Area, Islamabad, Pakistan",
                rating=4.2,
            ),
        ]
        errors = []

    class FakeScraper:
        def scrape(self, task):
            return FakeResult()

    monkeypatch.setattr(cli, "Settings", lambda: object())
    monkeypatch.setattr(
        cli,
        "build_scraper",
        lambda source, settings: FakeScraper(),
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
            "cafes",
            "--location",
            "Islamabad",
        ],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Records: 2" in captured.out
    assert "1. Cafe A | Main Street, Islamabad, Pakistan | Rating: 4.7" in captured.out
    assert "2. Cafe B | Blue Area, Islamabad, Pakistan | Rating: 4.2" in captured.out


def test_cli_parser_supports_output_format():
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
            "--output",
            "csv",
        ]
    )

    assert args.output == "csv"


def test_build_scrape_task_includes_output_format():
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
            "--output",
            "json",
        ]
    )

    from scrapepro.cli.main import build_scrape_task

    task = build_scrape_task(args)

    assert task.output == "json"

def test_build_exporter_supports_output_formats():
    from scrapepro.cli.main import build_exporter
    from scrapepro.exporters.csv import CSVExporter
    from scrapepro.exporters.json import JSONExporter
    from scrapepro.exporters.excel import ExcelExporter

    assert isinstance(build_exporter("csv"), CSVExporter)
    assert isinstance(build_exporter("json"), JSONExporter)
    assert isinstance(build_exporter("excel"), ExcelExporter)
    assert build_exporter(None) is None

def test_build_export_path_uses_query_and_location():
    from scrapepro.cli.main import build_export_path

    path = build_export_path(
        output_format="csv",
        query="restaurants",
        location="Islamabad",
    )

    assert path.name == "restaurants_Islamabad.csv"

def test_cli_main_exports_records_when_output_requested(
    monkeypatch,
    capsys,
    tmp_path,
):
    from scrapepro.cli import main as cli
    from scrapepro.core.record import Record

    class FakeResult:
        records = [
            Record(
                name="Cafe Export",
                address="Islamabad, Pakistan",
                rating=4.5,
            )
        ]
        errors = []

    class FakeScraper:
        def scrape(self, task):
            return FakeResult()

    class FakeExportService:
        def export(self, records, output_format, query, location):
            assert len(records) == 1
            assert records[0].name == "Cafe Export"
            assert output_format == "csv"
            assert query == "cafes"
            assert location == "Islamabad"

            output_path = tmp_path / "cafes.csv"
            output_path.write_text(
                "name\\nCafe Export\\n",
                encoding="utf-8",
            )
            return output_path

    monkeypatch.setattr(cli, "Settings", lambda: object())
    monkeypatch.setattr(
        cli,
        "build_scraper",
        lambda source, settings: FakeScraper(),
    )
    monkeypatch.setattr(
        cli,
        "ExportService",
        lambda: FakeExportService(),
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
            "cafes",
            "--location",
            "Islamabad",
            "--output",
            "csv",
        ],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Records: 1" in captured.out
    assert "Cafe Export" in captured.out
    assert "Exported:" in captured.out
    assert "cafes.csv" in captured.out

def test_cli_main_runs_scrape_through_engine(monkeypatch, capsys):
    from scrapepro.cli import main as cli
    from scrapepro.core.record import Record

    class FakeResult:
        records = [
            Record(
                name="Engine Cafe",
                address="Islamabad, Pakistan",
                rating=4.8,
            )
        ]
        errors = []

    class FakeEngine:
        def __init__(self):
            self.received_task = None

        def run(self, task):
            self.received_task = task
            return FakeResult()

    fake_engine = FakeEngine()

    monkeypatch.setattr(cli, "Settings", lambda: object())
    monkeypatch.setattr(
        cli,
        "build_scraper",
        lambda source, settings: object(),
    )
    monkeypatch.setattr(
        cli,
        "ScrapeEngine",
        lambda scraper, pipeline=None: fake_engine,
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
            "cafes",
            "--location",
            "Islamabad",
        ],
    )

    cli.main()

    captured = capsys.readouterr()

    assert fake_engine.received_task.source == "google_maps"
    assert fake_engine.received_task.query == "cafes"
    assert fake_engine.received_task.location == "Islamabad"
    assert "Records: 1" in captured.out
    assert "Engine Cafe" in captured.out

def test_cli_main_builds_processing_pipeline(monkeypatch, capsys):
    from scrapepro.cli import main as cli
    from scrapepro.core.record import Record

    class FakeResult:
        records = [
            Record(
                name="Pipeline Cafe",
                address="Main Street, Islamabad, Pakistan",
                rating=4.9,
            )
        ]
        errors = []

    class FakeScraper:
        def scrape(self, task):
            raise AssertionError("CLI should use ScrapeEngine.")

    class FakeEngine:
        def __init__(self, scraper, pipeline=None):
            self.scraper = scraper
            self.pipeline = pipeline
            self.received_task = None

        def run(self, task):
            self.received_task = task
            return FakeResult()

    fake_engine = FakeEngine

    monkeypatch.setattr(cli, "Settings", lambda: object())
    monkeypatch.setattr(
        cli,
        "build_scraper",
        lambda source, settings: FakeScraper(),
    )
    monkeypatch.setattr(cli, "ScrapeEngine", fake_engine)

    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "scrapepro",
            "scrape",
            "--source",
            "google_maps",
            "--query",
            "cafes",
            "--location",
            "Islamabad",
        ],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Records: 1" in captured.out
    assert "Pipeline Cafe" in captured.out

def test_cli_main_passes_processing_pipeline_to_engine(
    monkeypatch,
    capsys,
):
    from scrapepro.cli import main as cli
    from scrapepro.core.pipeline import Pipeline
    from scrapepro.core.record import Record

    class FakeResult:
        records = [
            Record(
                name="Pipeline Cafe",
                address="Main Street, Islamabad, Pakistan",
                rating=4.9,
            )
        ]
        errors = []

    class FakeScraper:
        def scrape(self, task):
            raise AssertionError("Scraper should be called by ScrapeEngine.")

    class FakeEngine:
        def __init__(self, scraper, pipeline=None):
            self.pipeline = pipeline

        def run(self, task):
            return FakeResult()

    captured_pipeline = {}

    def fake_engine(scraper, pipeline=None):
        captured_pipeline["value"] = pipeline
        return FakeEngine(scraper, pipeline)

    monkeypatch.setattr(cli, "Settings", lambda: object())
    monkeypatch.setattr(
        cli,
        "build_scraper",
        lambda source, settings: FakeScraper(),
    )
    monkeypatch.setattr(cli, "ScrapeEngine", fake_engine)

    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "scrapepro",
            "scrape",
            "--source",
            "google_maps",
            "--query",
            "cafes",
            "--location",
            "Islamabad",
        ],
    )

    cli.main()

    pipeline = captured_pipeline["value"]

    assert isinstance(pipeline, Pipeline)
    assert len(pipeline.steps) == 6

    assert pipeline.steps[0].__class__.__name__ == "Cleaner"
    assert pipeline.steps[1].__class__.__name__ == "Normalizer"
    assert pipeline.steps[2].__class__.__name__ == "Deduplicator"
    assert pipeline.steps[3].__class__.__name__ == "Validator"
    assert pipeline.steps[4].__class__.__name__ == "Enricher"
    assert pipeline.steps[5].__class__.__name__ == "StorageProcessor"
    assert "Records: 1" in capsys.readouterr().out


def test_cli_main_reports_scraping_errors(monkeypatch, capsys):
    from scrapepro.cli import main as cli
    from scrapepro.core.result import ScrapeResult

    class FakeScraper:
        pass

    class FakeEngine:
        def __init__(self, scraper, pipeline=None):
            pass

        def run(self, task):
            return ScrapeResult(
                records=[],
                errors=["Google Maps request failed"],
            )

    monkeypatch.setattr(cli, "Settings", lambda: object())
    monkeypatch.setattr(
        cli,
        "build_scraper",
        lambda source, settings: FakeScraper(),
    )
    monkeypatch.setattr(cli, "ScrapeEngine", FakeEngine)

    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "scrapepro",
            "scrape",
            "--source",
            "google_maps",
            "--query",
            "cafes",
            "--location",
            "Islamabad",
        ],
    )

    cli.main()

    captured = capsys.readouterr()

    assert "Records: 0" in captured.out
    assert "Error: Google Maps request failed" in captured.out


def test_cli_main_handles_missing_google_maps_api_key(
    monkeypatch,
    capsys,
):
    from scrapepro.cli import main as cli

    class FakeSettings:
        def require_google_maps_api_key(self):
            raise ValueError(
                "GOOGLE_MAPS_API_KEY environment variable is not set."
            )

    monkeypatch.setattr(cli, "Settings", FakeSettings)

    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "scrapepro",
            "scrape",
            "--source",
            "google_maps",
            "--query",
            "cafes",
            "--location",
            "Islamabad",
        ],
    )

    cli.main()

    captured = capsys.readouterr()

    assert (
        "Error: GOOGLE_MAPS_API_KEY environment variable is not set."
        in captured.out
    )
