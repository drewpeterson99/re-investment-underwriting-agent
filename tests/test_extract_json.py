"""Tests for parsing JSON from model output."""

from __future__ import annotations

import pytest

from main import extract_json_from_response


def test_extract_json_from_plain_object() -> None:
    text = '{"StreetAddress": "1 Main St", "YearBuilt": 1990}'
    assert extract_json_from_response(text)["StreetAddress"] == "1 Main St"


def test_extract_json_strips_markdown_fence() -> None:
    text = """Here is the result:
```json
{"AskingPrice": 100}
```
"""
    assert extract_json_from_response(text)["AskingPrice"] == 100


def test_extract_json_raises_when_no_braces() -> None:
    with pytest.raises(ValueError, match="Could not locate JSON"):
        extract_json_from_response("no json here")
