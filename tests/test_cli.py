from ragdemo.cli import build_parser


def test_parser_accepts_login_command() -> None:
    args = build_parser().parse_args(["--config", "config/local.yaml", "login"])

    assert args.command == "login"
    assert str(args.config) == "config/local.yaml"
