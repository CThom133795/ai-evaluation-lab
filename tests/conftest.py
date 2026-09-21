"""Shared test helpers."""

import copy
import json

import pytest

# A minimal valid case. Tests copy and modify it to exercise one rule at a time.
VALID_CASE = {
    "id": "T-001",
    "category": "grounding",
    "prompt": "What year was the product launched?",
    "context": "The product launched in 2019.",
    "expected_behavior": "States 2019 based on the context.",
    "failure_conditions": ["Gives a year other than 2019"],
    "severity": "high",
    "checks": [
        {
            "type": "contains",
            "value": "2019",
            "failure_type": "unsupported_claim",
            "description": "Answer uses the year from the context",
        },
        {
            "type": "not_regex",
            "pattern": r"\b20(1[0-8]|2\d)\b",
            "failure_type": "unsupported_claim",
            "description": "No other launch year is asserted",
        },
    ],
}


@pytest.fixture
def valid_case_dict():
    # deepcopy so one test's edits can't leak into another
    return copy.deepcopy(VALID_CASE)


@pytest.fixture
def write_jsonl(tmp_path):
    """Write a list of objects (or raw strings) to a JSONL file and return its path."""

    def _write(rows, name="cases.jsonl"):
        path = tmp_path / name
        lines = [row if isinstance(row, str) else json.dumps(row) for row in rows]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    return _write
