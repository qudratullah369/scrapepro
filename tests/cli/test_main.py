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
