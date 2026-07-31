import argparse
from pathlib import Path

from ragdemo.auth import capture_session
from ragdemo.config import load_config
from ragdemo.fetch import fetch_page
from ragdemo.security import validate_wiki_url


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ragdemo")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/local.yaml"),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("login", help="手动完成 SSO 并保存本地会话")
    fetch_parser = subparsers.add_parser("fetch", help="抓取一个白名单 Wiki 页面")
    fetch_parser.add_argument("url")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)

    if args.command == "login":
        capture_session(
            base_url=config.base_url,
            storage_state_path=config.storage_state_path,
        )
    elif args.command == "fetch":
        url = validate_wiki_url(
            args.url,
            allowed_host=config.allowed_host,
            allowed_path_prefix=config.allowed_path_prefix,
        )
        saved = fetch_page(
            url=url,
            storage_state_path=config.storage_state_path,
            raw_html_dir=config.raw_html_dir,
            metadata_dir=config.metadata_dir,
            headless=config.headless,
        )
        print(f"HTML: {saved.html_path}")
        print(f"Metadata: {saved.metadata_path}")


if __name__ == "__main__":
    main()
