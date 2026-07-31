# Wiki Ingestion Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a safe local Python foundation that lets the user complete SSO manually and fetch one explicitly allowlisted Wiki page to local raw HTML.

**Architecture:** A small `ragdemo` package separates configuration, URL security checks, Playwright session handling, and page fetching. The CLI exposes independent `login` and `fetch` commands so authentication and ingestion remain observable. Pure configuration, security, and persistence behavior is covered by unit tests; the Playwright SSO boundary is verified with a deliberate manual smoke test.

**Tech Stack:** Python 3.11+, Playwright, PyYAML, pytest, pytest-mock, Ruff

---

## Scope

This plan implements only the first independently testable slice of the approved MVP:

- repository and Python project structure;
- local configuration with example values;
- sensitive-file exclusions;
- strict Wiki hostname/path allowlisting;
- visible-browser manual SSO login and Playwright storage-state persistence;
- fetching one allowlisted URL to raw HTML and metadata;
- unit tests and local operating instructions.

Parsing, chunking, BM25, embeddings, FAISS, RRF, Ollama, and evaluation are intentionally deferred to separate implementation plans after this slice works.

## Target File Structure

```text
RAGDemo/
├── .gitignore
├── README.md
├── pyproject.toml
├── config/
│   └── example.yaml
├── data/
│   ├── raw_html/
│   └── metadata/
├── secrets/
│   └── .gitkeep
├── src/
│   └── ragdemo/
│       ├── __init__.py
│       ├── auth.py
│       ├── cli.py
│       ├── config.py
│       ├── fetch.py
│       └── security.py
└── tests/
    ├── test_config.py
    ├── test_fetch.py
    └── test_security.py
```

## Task 1: Create the Python Project and Safe Local Layout

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `config/example.yaml`
- Create: `src/ragdemo/__init__.py`
- Create: `secrets/.gitkeep`
- Modify: `README.md`

- [ ] **Step 1: Add project metadata and dependencies**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ragdemo"
version = "0.1.0"
description = "Transparent local Wiki RAG learning project"
requires-python = ">=3.11"
dependencies = [
  "playwright>=1.45,<2",
  "PyYAML>=6,<7",
]

[project.optional-dependencies]
dev = [
  "pytest>=8,<9",
  "pytest-mock>=3.14,<4",
  "ruff>=0.5,<1",
]

[project.scripts]
ragdemo = "ragdemo.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/ragdemo"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"
```

- [ ] **Step 2: Add sensitive and generated file exclusions**

Create `.gitignore`:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
*.pyc

config/local.yaml
secrets/*
!secrets/.gitkeep

data/raw_html/*
!data/raw_html/.gitkeep
data/metadata/*
!data/metadata/.gitkeep

urls.txt
```

Create empty tracked files `secrets/.gitkeep`, `data/raw_html/.gitkeep`, and `data/metadata/.gitkeep`.

- [ ] **Step 3: Add a safe example configuration**

Create `config/example.yaml`:

```yaml
wiki:
  base_url: "https://wiki.example.internal"
  allowed_host: "wiki.example.internal"
  allowed_path_prefix: "/spaces/learning/"

browser:
  storage_state_path: "secrets/storage_state.json"
  headless: false

output:
  raw_html_dir: "data/raw_html"
  metadata_dir: "data/metadata"
```

- [ ] **Step 4: Create the package marker**

Create `src/ragdemo/__init__.py`:

```python
"""Transparent local Wiki RAG learning project."""

__version__ = "0.1.0"
```

- [ ] **Step 5: Document environment setup**

Replace `README.md` with setup instructions containing these exact commands:

````markdown
# RAGDemo

一个用于逐层学习 Wiki RAG 的本地透明实现。

## 当前阶段

当前只实现：手动 SSO 登录、保存本地浏览器会话、抓取一个白名单 Wiki 页面。

## 环境准备

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
playwright install chromium
cp config/example.yaml config/local.yaml
```

编辑 `config/local.yaml`，填写真实 Wiki 域名和允许抓取的路径前缀。不要提交该文件。
````

- [ ] **Step 6: Install dependencies and verify the package imports**

Run:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
python -c "import ragdemo; print(ragdemo.__version__)"
```

Expected: the final command prints `0.1.0`.

- [ ] **Step 7: Run formatting and repository safety checks**

Run:

```bash
ruff check .
git check-ignore config/local.yaml secrets/storage_state.json data/raw_html/example.html
```

Expected: Ruff exits successfully; all three sensitive/generated paths are printed by `git check-ignore`.

- [ ] **Step 8: Commit the project skeleton**

```bash
git add .gitignore README.md pyproject.toml config/example.yaml src/ragdemo/__init__.py secrets/.gitkeep data/raw_html/.gitkeep data/metadata/.gitkeep
git commit -m "chore: scaffold local Wiki ingestion project"
```

## Task 2: Load and Validate Local Configuration

**Files:**
- Create: `src/ragdemo/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing configuration tests**

Create `tests/test_config.py`:

```python
from pathlib import Path

import pytest

from ragdemo.config import AppConfig, load_config


def test_load_config_resolves_project_relative_paths(tmp_path: Path) -> None:
    config_file = tmp_path / "local.yaml"
    config_file.write_text(
        """
wiki:
  base_url: https://wiki.example.internal
  allowed_host: wiki.example.internal
  allowed_path_prefix: /spaces/learning/
browser:
  storage_state_path: secrets/state.json
  headless: false
output:
  raw_html_dir: data/raw_html
  metadata_dir: data/metadata
""".strip(),
        encoding="utf-8",
    )

    result = load_config(config_file, project_root=tmp_path)

    assert isinstance(result, AppConfig)
    assert result.storage_state_path == tmp_path / "secrets/state.json"
    assert result.raw_html_dir == tmp_path / "data/raw_html"


def test_load_config_rejects_missing_required_section(tmp_path: Path) -> None:
    config_file = tmp_path / "local.yaml"
    config_file.write_text("wiki: {}", encoding="utf-8")

    with pytest.raises(ValueError, match="missing configuration value"):
        load_config(config_file, project_root=tmp_path)
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
pytest tests/test_config.py -v
```

Expected: FAIL because `ragdemo.config` does not exist.

- [ ] **Step 3: Implement the configuration loader**

Create `src/ragdemo/config.py`:

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class AppConfig:
    base_url: str
    allowed_host: str
    allowed_path_prefix: str
    storage_state_path: Path
    headless: bool
    raw_html_dir: Path
    metadata_dir: Path


def _required(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"missing configuration value: {'.'.join(keys)}")
        current = current[key]
    return current


def load_config(path: Path, project_root: Path | None = None) -> AppConfig:
    root = project_root or Path.cwd()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    return AppConfig(
        base_url=str(_required(data, "wiki", "base_url")),
        allowed_host=str(_required(data, "wiki", "allowed_host")),
        allowed_path_prefix=str(_required(data, "wiki", "allowed_path_prefix")),
        storage_state_path=root / str(
            _required(data, "browser", "storage_state_path")
        ),
        headless=bool(_required(data, "browser", "headless")),
        raw_html_dir=root / str(_required(data, "output", "raw_html_dir")),
        metadata_dir=root / str(_required(data, "output", "metadata_dir")),
    )
```

- [ ] **Step 4: Run tests and lint**

Run:

```bash
pytest tests/test_config.py -v
ruff check src/ragdemo/config.py tests/test_config.py
```

Expected: two tests pass; Ruff exits successfully.

- [ ] **Step 5: Commit configuration loading**

```bash
git add src/ragdemo/config.py tests/test_config.py
git commit -m "feat: load local Wiki configuration"
```

## Task 3: Enforce the Wiki URL Allowlist

**Files:**
- Create: `src/ragdemo/security.py`
- Create: `tests/test_security.py`

- [ ] **Step 1: Write failing URL validation tests**

Create `tests/test_security.py`:

```python
import pytest

from ragdemo.security import validate_wiki_url


def test_accepts_https_url_inside_allowed_path() -> None:
    result = validate_wiki_url(
        "https://wiki.example.internal/spaces/learning/page-1",
        allowed_host="wiki.example.internal",
        allowed_path_prefix="/spaces/learning/",
    )
    assert result == "https://wiki.example.internal/spaces/learning/page-1"


@pytest.mark.parametrize(
    "url",
    [
        "http://wiki.example.internal/spaces/learning/page-1",
        "https://evil.example/spaces/learning/page-1",
        "https://wiki.example.internal/admin/page-1",
        "https://wiki.example.internal.evil.example/spaces/learning/page-1",
        "javascript:alert(1)",
    ],
)
def test_rejects_url_outside_allowlist(url: str) -> None:
    with pytest.raises(ValueError, match="URL is not allowed"):
        validate_wiki_url(
            url,
            allowed_host="wiki.example.internal",
            allowed_path_prefix="/spaces/learning/",
        )
```

- [ ] **Step 2: Run tests and verify they fail**

Run:

```bash
pytest tests/test_security.py -v
```

Expected: FAIL because `ragdemo.security` does not exist.

- [ ] **Step 3: Implement strict URL validation**

Create `src/ragdemo/security.py`:

```python
from urllib.parse import urlsplit, urlunsplit


def validate_wiki_url(
    url: str,
    *,
    allowed_host: str,
    allowed_path_prefix: str,
) -> str:
    parsed = urlsplit(url)
    normalized_host = (parsed.hostname or "").lower()
    normalized_allowed_host = allowed_host.lower()

    valid = (
        parsed.scheme == "https"
        and normalized_host == normalized_allowed_host
        and parsed.port in (None, 443)
        and parsed.path.startswith(allowed_path_prefix)
        and not parsed.username
        and not parsed.password
    )
    if not valid:
        raise ValueError("URL is not allowed by the Wiki hostname/path policy")

    return urlunsplit(("https", normalized_allowed_host, parsed.path, parsed.query, ""))
```

- [ ] **Step 4: Run tests and lint**

Run:

```bash
pytest tests/test_security.py -v
ruff check src/ragdemo/security.py tests/test_security.py
```

Expected: six tests pass; Ruff exits successfully.

- [ ] **Step 5: Commit URL security policy**

```bash
git add src/ragdemo/security.py tests/test_security.py
git commit -m "feat: restrict Wiki fetching to allowlisted URLs"
```

## Task 4: Implement Manual SSO Session Capture

**Files:**
- Create: `src/ragdemo/auth.py`
- Create: `src/ragdemo/cli.py`

- [ ] **Step 1: Implement visible-browser login**

Create `src/ragdemo/auth.py`:

```python
from pathlib import Path

from playwright.sync_api import sync_playwright


def capture_session(*, base_url: str, storage_state_path: Path) -> None:
    storage_state_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(base_url, wait_until="domcontentloaded")
        input("请在浏览器完成 SSO 登录，确认已进入 Wiki 后按 Enter 保存会话：")
        context.storage_state(path=storage_state_path)
        browser.close()
```

- [ ] **Step 2: Add the initial CLI with a login command**

Create `src/ragdemo/cli.py`:

```python
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
```

- [ ] **Step 3: Run static checks**

Run:

```bash
ruff check src/ragdemo/auth.py src/ragdemo/cli.py
python -m ragdemo.cli --help
```

Expected: Ruff exits successfully; help output includes the `login` command.

- [ ] **Step 4: Perform the manual SSO smoke test**

First create the real untracked configuration:

```bash
cp config/example.yaml config/local.yaml
```

Edit `base_url`, `allowed_host`, and `allowed_path_prefix`, then run:

```bash
ragdemo --config config/local.yaml login
```

Expected: a visible Chromium window opens; the user completes SSO; after Enter is pressed, `secrets/storage_state.json` exists and `git status --short` does not list it.

- [ ] **Step 5: Commit SSO session capture**

```bash
git add src/ragdemo/auth.py src/ragdemo/cli.py
git commit -m "feat: capture local Wiki SSO session"
```

## Task 5: Fetch One Allowlisted Wiki Page

**Files:**
- Create: `src/ragdemo/fetch.py`
- Modify: `src/ragdemo/cli.py`
- Create: `tests/test_fetch.py`
- Modify: `README.md`

- [ ] **Step 1: Write failing fetch tests**

Create `tests/test_fetch.py`:

```python
import json
from pathlib import Path

from ragdemo.fetch import save_page


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
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```bash
pytest tests/test_fetch.py -v
```

Expected: FAIL because `ragdemo.fetch` does not exist.

- [ ] **Step 3: Implement page persistence and browser fetching**

Create `src/ragdemo/fetch.py`:

```python
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
```

- [ ] **Step 4: Add the fetch CLI command**

Update `src/ragdemo/cli.py` so `build_parser()` adds:

```python
    fetch_parser = subparsers.add_parser("fetch", help="抓取一个白名单 Wiki 页面")
    fetch_parser.add_argument("url")
```

Add imports:

```python
from ragdemo.fetch import fetch_page
from ragdemo.security import validate_wiki_url
```

Add this branch after the login branch:

```python
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
```

- [ ] **Step 5: Run unit tests and lint**

Run:

```bash
pytest -v
ruff check .
```

Expected: all tests pass; Ruff exits successfully.

- [ ] **Step 6: Verify rejection happens before browser access**

Run:

```bash
ragdemo --config config/local.yaml fetch https://example.com/not-wiki
```

Expected: command exits with `URL is not allowed` and no browser window opens.

- [ ] **Step 7: Fetch one real Wiki page**

Copy one allowed Wiki page URL from the browser, then run:

```bash
wiki_page_url="$(pbpaste)"
ragdemo --config config/local.yaml fetch "$wiki_page_url"
```

Expected:

- one HTML file appears under `data/raw_html/`;
- one JSON file appears under `data/metadata/`;
- the HTML file contains the page正文；
- the metadata URL and title match the page；
- `git status --short` does not list the session, HTML, metadata, or local configuration files.

- [ ] **Step 8: Document login and one-page fetch commands**

Append to `README.md`:

````markdown
## 登录与抓取一个页面

先登录并保存本地会话：

```bash
ragdemo --config config/local.yaml login
```

复制一个允许的 Wiki 页面 URL，然后执行：

```bash
wiki_page_url="$(pbpaste)"
ragdemo --config config/local.yaml fetch "$wiki_page_url"
```

`config/local.yaml`、`secrets/`、`data/` 和真实 URL 清单都属于本地数据，不提交到 Git。
````

- [ ] **Step 9: Run the complete verification suite**

Run:

```bash
pytest -v
ruff check .
git diff --check
git status --short
```

Expected: tests and Ruff pass; no whitespace errors; only intended source, test, README, and plan changes are shown.

- [ ] **Step 10: Commit one-page ingestion**

```bash
git add src/ragdemo/fetch.py src/ragdemo/cli.py tests/test_fetch.py README.md
git commit -m "feat: fetch one allowlisted Wiki page"
```

## Phase Completion Check

Before moving to HTML parsing, verify all of the following:

- `config/local.yaml` contains the real host only on the local machine；
- the SSO session file is ignored by Git；
- a non-Wiki URL is rejected before Playwright opens it；
- one real allowlisted page is saved as HTML and JSON metadata；
- the saved HTML visibly contains the expected Wiki正文；
- all unit tests and Ruff checks pass；
- `git status` contains no internal Wiki data or authentication material。

The next plan should cover HTML parsing and structure-preserving JSON output only after this phase passes.
