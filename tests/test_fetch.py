import json
from pathlib import Path

import pytest

from ragdemo.fetch import fetch_page, save_page


def test_save_page_writes_html_and_metadata(tmp_path: Path) -> None:
    result = save_page(
        url="https://wiki.example.internal/spaces/learning/page-1",
        title="Page One",
        html="<html><body>hello</body></html>",
        raw_html_dir=tmp_path / "raw",
        metadata_dir=tmp_path / "metadata",
    )

    assert result.html_path.read_text(encoding="utf-8") == "<html><body>hello</body></html>"
    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["url"] == "https://wiki.example.internal/spaces/learning/page-1"
    assert metadata["title"] == "Page One"
    assert len(metadata["content_hash"]) == 64


def test_fetch_page_rejects_missing_sso_session(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="run the login command first"):
        fetch_page(
            url="https://wiki.example.internal/spaces/learning/page-1",
            storage_state_path=tmp_path / "missing.json",
            raw_html_dir=tmp_path / "raw",
            metadata_dir=tmp_path / "metadata",
            headless=True,
        )
