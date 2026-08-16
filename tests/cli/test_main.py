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
