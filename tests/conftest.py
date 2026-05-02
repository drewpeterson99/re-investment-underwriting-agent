"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def field_schema(project_root: Path) -> Dict[str, Any]:
    from main import load_schema

    return load_schema(project_root / "field_schema.yaml")
