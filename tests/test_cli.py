from ragdemo.cli import build_parser


def test_parser_accepts_login_command() -> None:
    args = build_parser().parse_args(["--config", "config/local.yaml", "login"])

    assert args.command == "login"
    assert str(args.config) == "config/local.yaml"


def test_parser_accepts_fetch_command() -> None:
    args = build_parser().parse_args(
        [
            "--config",
            "config/local.yaml",
            "fetch",
            "https://wiki.example.internal/spaces/learning/page-1",
        ]
    )

    assert args.command == "fetch"
    assert args.url.endswith("/page-1")
