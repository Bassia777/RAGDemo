import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from playwright.sync_api import sync_playwright


@dataclass(frozen=True)
class SavedPage:
    html_path: Path
    metadata_path: Path


def _page_id(url: str) -> str:
    readable = re.sub(r"[^a-zA-Z0-9]+", "-", url).strip("-").lower()
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
    return f"{readable[-60:]}-{digest}"


def save_page(
    *,
    url: str,
    title: str,
    html: str,
    raw_html_dir: Path,
    metadata_dir: Path,
) -> SavedPage:
    raw_html_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    page_id = _page_id(url)
    html_path = raw_html_dir / f"{page_id}.html"
    metadata_path = metadata_dir / f"{page_id}.json"
    content_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()

    html_path.write_text(html, encoding="utf-8")
    metadata_path.write_text(
        json.dumps(
            {
                "page_id": page_id,
                "url": url,
                "title": title,
                "fetched_at": datetime.now(UTC).isoformat(),
                "content_hash": content_hash,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return SavedPage(html_path=html_path, metadata_path=metadata_path)


def fetch_page(
    *,
    url: str,
    storage_state_path: Path,
    raw_html_dir: Path,
    metadata_dir: Path,
    headless: bool,
) -> SavedPage:
    if not storage_state_path.exists():
        raise FileNotFoundError("SSO session is missing; run the login command first")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=storage_state_path)
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        title = page.title()
        html = page.content()
        browser.close()

    return save_page(
        url=url,
        title=title,
        html=html,
        raw_html_dir=raw_html_dir,
        metadata_dir=metadata_dir,
    )
