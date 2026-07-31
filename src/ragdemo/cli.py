import argparse
from pathlib import Path

from ragdemo.auth import capture_session
from ragdemo.config import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ragdemo")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/local.yaml"),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("login", help="手动完成 SSO 并保存本地会话")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)

    if args.command == "login":
        capture_session(
            base_url=config.base_url,
            storage_state_path=config.storage_state_path,
        )


if __name__ == "__main__":
    main()
