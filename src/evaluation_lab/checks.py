"""Deterministic checks applied to model responses.

Each check is a small function: (response, params) -> (passed, detail).
They are intentionally simple string/regex/JSON rules so that the same
response always produces the same verdict, with no second model involved.

Important limitation: these are *proxies* for behavior. "Response mentions
'clarify'" is evidence that the model asked a clarifying question, not proof.
Case authors should pick checks that are hard to satisfy by accident, and
borderline cases should still get human review (see docs/methodology.md).
"""

from __future__ import annotations

import json
import re

# Case-insensitive matching is the default because wording varies
# ("I don't know" vs "I Don't Know") without changing meaning.


def check_contains(response: str, params: dict) -> tuple[bool, str]:
    value = params["value"]
    if value.lower() in response.lower():
        return True, ""
    return False, f"expected text not found: {value!r}"


def check_not_contains(response: str, params: dict) -> tuple[bool, str]:
    value = params["value"]
    if value.lower() in response.lower():
        return False, f"forbidden text present: {value!r}"
    return True, ""


def check_contains_any(response: str, params: dict) -> tuple[bool, str]:
    values = params["values"]
    lowered = response.lower()
    if any(v.lower() in lowered for v in values):
        return True, ""
    return False, f"none of the expected phrases found: {values!r}"


def check_regex(response: str, params: dict) -> tuple[bool, str]:
    pattern = params["pattern"]
    if re.search(pattern, response, flags=re.IGNORECASE | re.MULTILINE):
        return True, ""
    return False, f"pattern did not match: {pattern!r}"


def check_not_regex(response: str, params: dict) -> tuple[bool, str]:
    pattern = params["pattern"]
    match = re.search(pattern, response, flags=re.IGNORECASE | re.MULTILINE)
    if match:
        return False, f"forbidden pattern matched: {match.group(0)!r}"
    return True, ""


def check_max_words(response: str, params: dict) -> tuple[bool, str]:
    limit = params["limit"]
    count = len(response.split())
    if count <= limit:
        return True, ""
    return False, f"{count} words exceeds limit of {limit}"


def check_json_field_equals(response: str, params: dict) -> tuple[bool, str]:
    """Parse the response as JSON and compare one top-level field.

    Used for tool-use cases, where the model is asked to reply with a JSON
    tool decision. A response that isn't valid JSON fails this check.
    """
    data = parse_json_response(response)
    if data is None:
        return False, "response is not a valid JSON object"
    field_name = params["field"]
    if field_name not in data:
        return False, f"JSON field {field_name!r} missing"
    actual = data[field_name]
    expected = params["value"]
    if actual == expected:
        return True, ""
    return False, f"JSON field {field_name!r} was {actual!r}, expected {expected!r}"


def parse_json_response(response: str) -> dict | None:
    """Return the response as a dict, or None if it isn't a JSON object.

    Models frequently wrap JSON in Markdown code fences (```json ... ```).
    That wrapper is stripped first so a correct decision isn't failed purely
    on presentation; format strictness can be tested separately if needed.
    """
    text = response.strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, flags=re.DOTALL)
    if fenced:
        text = fenced.group(1)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


# Registry: check type name (as written in the dataset) -> function.
CHECK_FUNCTIONS = {
    "contains": check_contains,
    "not_contains": check_not_contains,
    "contains_any": check_contains_any,
    "regex": check_regex,
    "not_regex": check_not_regex,
    "max_words": check_max_words,
    "json_field_equals": check_json_field_equals,
}

# Parameters each check type needs. The dataset loader uses this to reject
# malformed checks up front instead of crashing halfway through a run.
REQUIRED_PARAMS = {
    "contains": ("value",),
    "not_contains": ("value",),
    "contains_any": ("values",),
    "regex": ("pattern",),
    "not_regex": ("pattern",),
    "max_words": ("limit",),
    "json_field_equals": ("field", "value"),
}
