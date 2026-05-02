"""Tests for default output workbook path and location segment."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from main import location_segment_for_output_filename, resolve_output_workbook_path


def test_location_segment_default_when_missing() -> None:
    assert location_segment_for_output_filename(None) == "Charlotte NC"
    assert location_segment_for_output_filename("") == "Charlotte NC"


def test_location_segment_omits_comma_for_city_state() -> None:
    assert location_segment_for_output_filename("Cleveland, OH") == "Cleveland OH"


def test_resolve_output_workbook_path_directory_with_city_state() -> None:
    out_dir = Path("Output")
    d = date(2026, 5, 2)
    p = resolve_output_workbook_path(out_dir, "123 Main St", d, "Cleveland, OH")
    assert p == out_dir / "123 Main St - Cleveland OH - Model 2026-05-02.xlsx"


def test_resolve_output_workbook_path_directory_default_location() -> None:
    out_dir = Path("Output")
    d = date(2026, 5, 2)
    p = resolve_output_workbook_path(out_dir, "123 Main St", d, None)
    assert p == out_dir / "123 Main St - Charlotte NC - Model 2026-05-02.xlsx"


def test_resolve_output_workbook_path_exact_xlsx_unchanged() -> None:
    exact = Path(r"C:\reports\deal.xlsx")
    d = date(2026, 1, 1)
    assert resolve_output_workbook_path(exact, "ignored", d, "ignored") == exact
