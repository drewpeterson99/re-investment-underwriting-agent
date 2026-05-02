"""Tests for RentCast / monthly rent text extraction."""

from __future__ import annotations

from typing import Any, Dict

from main import extract_rentcast_monthly_total_usd_from_text, fill_missing_rentcast_rent_from_source

PROMPT_WITH_RENTCAST = (
    "5111 Clearwater Rd. RentCast rent estimate is $4070 per month total. Asking $500k."
)


def test_extract_rentcast_monthly_total_from_rentcast_line() -> None:
    assert extract_rentcast_monthly_total_usd_from_text(PROMPT_WITH_RENTCAST) == 4070


def test_fill_missing_rentcast_when_null(field_schema: Dict[str, Any]) -> None:
    parsed: Dict[str, Any] = {"RentCastRent": None}
    out = fill_missing_rentcast_rent_from_source(parsed, field_schema, PROMPT_WITH_RENTCAST)
    assert out["RentCastRent"] == 4070
