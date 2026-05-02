"""Tests for schema coercion and validation."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from main import coerce_and_validate


def test_coerce_listing_date_to_m_d_yyyy(field_schema: Dict[str, Any]) -> None:
    parsed: Dict[str, Any] = {
        "StreetAddress": "123 Main",
        "YearBuilt": 2000,
        "AskingPrice": 100_000,
        "ListingDate": "2024-03-15",
    }
    out = coerce_and_validate(parsed, field_schema)
    assert out["ListingDate"] == "3/15/2024"


def test_coerce_assessed_value_currency(field_schema: Dict[str, Any]) -> None:
    parsed: Dict[str, Any] = {
        "StreetAddress": "123 Main",
        "YearBuilt": 2000,
        "AskingPrice": 100_000,
        "AssessedValue": "$325k",
    }
    out = coerce_and_validate(parsed, field_schema)
    assert out["AssessedValue"] == 325_000


def test_coerce_bathrooms_number_decimal(field_schema: Dict[str, Any]) -> None:
    parsed: Dict[str, Any] = {
        "StreetAddress": "123 Main",
        "YearBuilt": 2000,
        "AskingPrice": 100_000,
        "Bathrooms": "4.5",
    }
    out = coerce_and_validate(parsed, field_schema)
    assert out["Bathrooms"] == 4.5


def test_coerce_raises_when_required_integer_missing(
    field_schema: Dict[str, Any],
) -> None:
    parsed: Dict[str, Any] = {
        "StreetAddress": "123 Main",
        "YearBuilt": 2000,
        "AskingPrice": None,
    }
    with pytest.raises(ValueError, match="AskingPrice"):
        coerce_and_validate(parsed, field_schema)
