"""Tests for extraction input normalization."""

from __future__ import annotations

from main import extract_asking_price_usd_from_text, normalize_extraction_source_text


def test_normalize_maps_fullwidth_dollar_to_ascii() -> None:
    s = "asking \uff04675k"
    assert "$" in normalize_extraction_source_text(s)
    assert extract_asking_price_usd_from_text(s) == 675_000


def test_strip_bom() -> None:
    s = "\ufeffasking $500k"
    assert normalize_extraction_source_text(s).startswith("asking")

