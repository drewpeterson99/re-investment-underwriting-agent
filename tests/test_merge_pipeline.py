"""End-to-end merge tests without loading the LLM (same steps as run_extraction post-model)."""

from __future__ import annotations

from typing import Any, Dict

from main import (
    coerce_and_validate,
    fill_missing_asking_price_from_source,
    fill_missing_rentcast_rent_from_source,
    reconcile_asking_price_from_source,
)

CLEARWATER_PROMPT = (
    "Subject property is 5111 Clearwater Rd, listed 4/16/2026, asking $675k, 7 beds, 4.5 baths, "
    "3,370 total SF, 2 units, built in 2007. RentCast rent estimate is $4070 per month total"
)


def test_pipeline_repairs_bad_asking_price_and_fills_rentcast(
    field_schema: Dict[str, Any],
) -> None:
    parsed: Dict[str, Any] = {
        "StreetAddress": "5111 Clearwater Rd",
        "YearBuilt": 2007,
        "AskingPrice": "4",
        "AssessedValue": 400_000,
        "Bedrooms": 7,
        "Bathrooms": 4.5,
        "ListingDate": "04/16/2026",
        "SquareFootage": 3370,
        "Units": 2,
        "RentCastRent": None,
    }
    parsed = fill_missing_asking_price_from_source(parsed, field_schema, CLEARWATER_PROMPT)
    parsed = reconcile_asking_price_from_source(parsed, field_schema, CLEARWATER_PROMPT)
    parsed = fill_missing_rentcast_rent_from_source(parsed, field_schema, CLEARWATER_PROMPT)

    out = coerce_and_validate(parsed, field_schema)

    assert out["AskingPrice"] == 675_000
    assert out["RentCastRent"] == 4070
    assert out["ListingDate"] == "4/16/2026"
