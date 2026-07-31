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
