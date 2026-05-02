"""Tests for asking-price regex fallback and reconciliation."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from main import (
    extract_asking_price_usd_from_text,
    fill_missing_asking_price_from_source,
    reconcile_asking_price_from_source,
)

CLEARWATER_PROMPT = (
    "Subject property is 5111 Clearwater Rd, listed 4/16/2026, asking $675k, 7 beds, 4.5 baths, "
    "3,370 total SF, 2 units, built in 2007. RentCast rent estimate is $4070 per month total"
)


def test_extract_asking_price_prefers_asking_over_listed_date_fragment() -> None:
    assert extract_asking_price_usd_from_text(CLEARWATER_PROMPT) == 675_000


def test_extract_asking_price_returns_none_for_empty_text() -> None:
    assert extract_asking_price_usd_from_text("") is None
    assert extract_asking_price_usd_from_text("   ") is None


def test_fill_missing_asking_price_inserts_hint_when_null(
    field_schema: Dict[str, Any],
) -> None:
    parsed: Dict[str, Any] = {
        "StreetAddress": "5111 Clearwater Rd",
        "YearBuilt": 2007,
        "AskingPrice": None,
    }
    out = fill_missing_asking_price_from_source(parsed, field_schema, CLEARWATER_PROMPT)
    assert out["AskingPrice"] == 675_000


def test_reconcile_replaces_model_confusion_with_date_digit_as_price(
    field_schema: Dict[str, Any],
) -> None:
    parsed: Dict[str, Any] = {
        "StreetAddress": "5111 Clearwater Rd",
        "YearBuilt": 2007,
        "AskingPrice": "4",
    }
    out = reconcile_asking_price_from_source(parsed, field_schema, CLEARWATER_PROMPT)
    assert out["AskingPrice"] == 675_000
