"""Minimal parsed dicts that satisfy required fields in `field_schema.yaml` for coercion tests."""

from __future__ import annotations

from typing import Any, Dict


def full_required_parsed(**overrides: Any) -> Dict[str, Any]:
    """All schema-required fields with bland defaults; override per test."""
    base: Dict[str, Any] = {
        "StreetAddress": "123 Main St",
        "YearBuilt": 2000,
        "AskingPrice": 100_000,
        "AssessedValue": 300_000,
        "Bedrooms": 3,
        "Bathrooms": 2.5,
        "SquareFootage": 1800,
        "Units": 1,
        "RentCastRent": 2000,
    }
    base.update(overrides)
    return base
