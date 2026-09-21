"""Behavior of each deterministic check, including boundaries."""

import pytest

from evaluation_lab.checks import (
    CHECK_FUNCTIONS,
    REQUIRED_PARAMS,
    check_contains,
    check_contains_any,
    check_json_field_equals,
    check_max_words,
    check_not_contains,
    check_not_regex,
    check_regex,
    parse_json_response,
)


def test_every_check_declares_its_parameters():
    # Keeps the two registries in sync; the loader relies on REQUIRED_PARAMS.
    assert set(CHECK_FUNCTIONS) == set(REQUIRED_PARAMS)


def test_contains_is_case_insensitive():
    assert check_contains("The answer is PARIS.", {"value": "paris"}) == (True, "")


def test_contains_failure_explains_itself():
    passed, detail = check_contains("London", {"value": "Paris"})
    assert not passed
    assert "Paris" in detail


def test_not_contains():
    assert check_not_contains("All good", {"value": "password"})[0] is True
    passed, detail = check_not_contains("Your PASSWORD is...", {"value": "password"})
    assert not passed and "forbidden" in detail


def test_contains_any():
    params = {"values": ["not sure", "cannot determine"]}
    assert check_contains_any("I cannot determine that.", params)[0] is True
    assert check_contains_any("It is definitely 42.", params)[0] is False


def test_regex_uses_search_and_ignores_case():
    assert check_regex("Total: 42 apples", {"pattern": r"\b42\b"})[0] is True
    assert check_regex("CLARIFY please", {"pattern": r"^clarify"})[0] is True
    assert check_regex("4200", {"pattern": r"\b42\b"})[0] is False


def test_not_regex_reports_matched_text():
    passed, detail = check_not_regex("Launched in 2021.", {"pattern": r"\b20\d\d\b"})
    assert not passed
    assert "2021" in detail


@pytest.mark.parametrize(
    "text, limit, expected",
    [
        ("", 0, True),  # boundary: empty response, zero limit
        ("one two three", 3, True),  # boundary: exactly at the limit
        ("one two three four", 3, False),  # boundary: one over
        ("  spaced   out\n words ", 3, True),  # whitespace doesn't count as words
    ],
)
def test_max_words_boundaries(text, limit, expected):
    assert check_max_words(text, {"limit": limit})[0] is expected


def test_json_field_equals_passes_on_match():
    response = '{"tool": "get_weather", "arguments": {"city": "Oslo"}}'
    assert check_json_field_equals(response, {"field": "tool", "value": "get_weather"}) == (True, "")


def test_json_field_equals_supports_null():
    # null is the expected value when the correct decision is "no tool call"
    assert check_json_field_equals('{"tool": null}', {"field": "tool", "value": None})[0] is True
    assert check_json_field_equals('{"tool": "search"}', {"field": "tool", "value": None})[0] is False


@pytest.mark.parametrize(
    "response, fragment",
    [
        ("Sure! I'll call get_weather.", "not a valid JSON object"),
        ('["get_weather"]', "not a valid JSON object"),
        ('{"name": "get_weather"}', "missing"),
        ('{"tool": "search"}', "expected 'get_weather'"),
    ],
)
def test_json_field_equals_failures(response, fragment):
    passed, detail = check_json_field_equals(response, {"field": "tool", "value": "get_weather"})
    assert not passed
    assert fragment in detail


def test_parse_json_strips_markdown_fence():
    assert parse_json_response('```json\n{"tool": null}\n```') == {"tool": None}
    assert parse_json_response('```\n{"a": 1}\n```') == {"a": 1}


def test_parse_json_rejects_trailing_prose():
    # Deliberately strict: prose around JSON means the format was not followed.
    assert parse_json_response('{"tool": null} Let me know if you need more!') is None
