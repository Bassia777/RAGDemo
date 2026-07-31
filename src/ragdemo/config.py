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
        storage_state_path=root / str(_required(data, "browser", "storage_state_path")),
        headless=bool(_required(data, "browser", "headless")),
        raw_html_dir=root / str(_required(data, "output", "raw_html_dir")),
        metadata_dir=root / str(_required(data, "output", "metadata_dir")),
    )
