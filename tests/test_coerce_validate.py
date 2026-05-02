"""Tests for schema coercion and validation."""

from __future__ import annotations

from typing import Any, Dict

import pytest

from coercion_payloads import full_required_parsed
from main import coerce_and_validate


def test_coerce_listing_date_to_m_d_yyyy(field_schema: Dict[str, Any]) -> None:
    parsed = full_required_parsed(ListingDate="2024-03-15")
    out = coerce_and_validate(parsed, field_schema)
    assert out["ListingDate"] == "3/15/2024"


def test_coerce_assessed_value_currency(field_schema: Dict[str, Any]) -> None:
    parsed = full_required_parsed(AssessedValue="$325k")
    out = coerce_and_validate(parsed, field_schema)
    assert out["AssessedValue"] == 325_000


def test_coerce_bathrooms_number_decimal(field_schema: Dict[str, Any]) -> None:
    parsed = full_required_parsed(Bathrooms="4.5")
    out = coerce_and_validate(parsed, field_schema)
    assert out["Bathrooms"] == 4.5


def test_coerce_purchase_price_and_seller_concessions_currency(
    field_schema: Dict[str, Any],
) -> None:
    parsed = full_required_parsed(PurchasePrice="$250k", SellerConcessions="5K")
    out = coerce_and_validate(parsed, field_schema)
    assert out["PurchasePrice"] == 250_000
    assert out["SellerConcessions"] == 5_000


def test_coerce_seller_concessions_min_zero(field_schema: Dict[str, Any]) -> None:
    parsed = full_required_parsed(SellerConcessions=-100)
    with pytest.raises(ValueError, match="SellerConcessions"):
        coerce_and_validate(parsed, field_schema)


def test_coerce_city_state_format(field_schema: Dict[str, Any]) -> None:
    parsed = full_required_parsed(CityState="Cleveland , OH")
    out = coerce_and_validate(parsed, field_schema)
    assert out["CityState"] == "Cleveland, OH"


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
