"""Tests for YAML schema loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from main import load_schema


def test_load_schema_reads_project_field_schema(project_root: Path) -> None:
    schema = load_schema(project_root / "field_schema.yaml")
    assert schema["version"] == 1
    assert "StreetAddress" in schema["fields"]
    assert schema["fields"]["AskingPrice"]["required"] is True


def test_load_schema_rejects_missing_file(project_root: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_schema(project_root / "nonexistent_schema.yaml")
