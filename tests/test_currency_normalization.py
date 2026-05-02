"""Tests for currency parsing helpers."""

from __future__ import annotations

import pytest

from main import normalize_currency_text_to_int


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("675k", 675_000),
        ("$675k", 675_000),
        ("$1.2m", 1_200_000),
        ("450,000", 450_000),
        ("$450,000.01", 450_001),
    ],
)
def test_normalize_currency_text_to_int_parses_shorthand_and_commas(
    raw: str, expected: int
) -> None:
    assert normalize_currency_text_to_int(raw) == expected


def test_normalize_currency_text_to_int_rejects_empty() -> None:
    with pytest.raises(ValueError, match="Could not parse"):
        normalize_currency_text_to_int("")
