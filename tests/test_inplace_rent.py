"""Tests for InPlaceRent extraction and coercion."""

from __future__ import annotations

from typing import Any, Dict

from coercion_payloads import full_required_parsed
from main import (
    coerce_and_validate,
    extract_inplace_rent_monthly_total_usd_from_text,
    fill_missing_inplace_rent_from_source,
)


def test_extract_inplace_rent_from_phrases() -> None:
    assert extract_inplace_rent_monthly_total_usd_from_text(
        "In-place rent is $5200 per month for the whole building."
    ) == 5200
    assert extract_inplace_rent_monthly_total_usd_from_text(
        "Current collected rent $3800 monthly."
    ) == 3800


def test_fill_missing_inplace_rent(field_schema: Dict[str, Any]) -> None:
    parsed: Dict[str, Any] = {"InPlaceRent": None}
    text = "Duplex. In-place rent $4100."
    out = fill_missing_inplace_rent_from_source(parsed, field_schema, text)
    assert out["InPlaceRent"] == 4100


def test_coerce_inplace_rent_currency(field_schema: Dict[str, Any]) -> None:
    parsed = full_required_parsed(
        StreetAddress="1 Main",
        AskingPrice=500_000,
        InPlaceRent="$4.2k",
    )
    out = coerce_and_validate(parsed, field_schema)
    assert out["InPlaceRent"] == 4200
