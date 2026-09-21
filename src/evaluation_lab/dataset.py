"""Load and validate evaluation cases from JSONL files.

JSONL (one JSON object per line) is used because it diffs cleanly in Git,
lets you add cases without touching others, and makes error messages easy
to point at a specific line.
"""

from __future__ import annotations

import json
from pathlib import Path

from .checks import CHECK_FUNCTIONS, REQUIRED_PARAMS
from .models import CATEGORIES, FAILURE_TYPES, SEVERITIES, Check, EvalCase

REQUIRED_FIELDS = (
    "id",
    "category",
    "prompt",
    "expected_behavior",
    "failure_conditions",
    "severity",
    "checks",
)


class DatasetError(ValueError):
    """Raised when a dataset file is malformed. Message includes the location."""


def load_cases(path: str | Path) -> list[EvalCase]:
    """Load every case from a JSONL file, failing loudly on the first problem.

    Validation is strict on purpose: a silently skipped or half-parsed case
    would make a run look more complete than it really is.
    """
    path = Path(path)
    if not path.is_file():
        raise DatasetError(f"Dataset file not found: {path}")

    cases: list[EvalCase] = []
    seen_ids: set[str] = set()

    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue  # blank lines are allowed for readability
            where = f"{path.name}:{line_number}"
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DatasetError(f"{where}: invalid JSON ({exc.msg})") from exc

            case = parse_case(raw, where)
            if case.id in seen_ids:
                raise DatasetError(f"{where}: duplicate case id '{case.id}'")
            seen_ids.add(case.id)
            cases.append(case)

    if not cases:
        raise DatasetError(f"{path.name}: dataset contains no cases")
    return cases


def parse_case(raw: object, where: str = "case") -> EvalCase:
    """Validate one decoded JSON object and convert it to an EvalCase."""
    if not isinstance(raw, dict):
        raise DatasetError(f"{where}: each line must be a JSON object")

    missing = [name for name in REQUIRED_FIELDS if name not in raw]
    if missing:
        raise DatasetError(f"{where}: missing required field(s): {', '.join(missing)}")

    for name in ("id", "prompt", "expected_behavior"):
        _require_non_empty_string(raw, name, where)

    if raw["category"] not in CATEGORIES:
        raise DatasetError(
            f"{where}: unknown category '{raw['category']}' (allowed: {', '.join(CATEGORIES)})"
        )
    if raw["severity"] not in SEVERITIES:
        raise DatasetError(
            f"{where}: unknown severity '{raw['severity']}' (allowed: {', '.join(SEVERITIES)})"
        )

    conditions = raw["failure_conditions"]
    if not isinstance(conditions, list) or not conditions:
        raise DatasetError(f"{where}: 'failure_conditions' must be a non-empty list")

    raw_checks = raw["checks"]
    if not isinstance(raw_checks, list) or not raw_checks:
        # A case with no checks would always "pass", which is misleading.
        raise DatasetError(f"{where}: 'checks' must be a non-empty list")

    checks = [_parse_check(item, f"{where} check #{i}") for i, item in enumerate(raw_checks, 1)]
    history = _parse_history(raw.get("history", []), where)

    return EvalCase(
        id=raw["id"],
        category=raw["category"],
        prompt=raw["prompt"],
        expected_behavior=raw["expected_behavior"],
        failure_conditions=list(conditions),
        severity=raw["severity"],
        checks=checks,
        context=raw.get("context", ""),
        system=raw.get("system", ""),
        history=history,
        tags=list(raw.get("tags", [])),
    )


def _require_non_empty_string(raw: dict, name: str, where: str) -> None:
    value = raw[name]
    if not isinstance(value, str) or not value.strip():
        raise DatasetError(f"{where}: '{name}' must be a non-empty string")


def _parse_check(raw: object, where: str) -> Check:
    if not isinstance(raw, dict):
        raise DatasetError(f"{where}: must be a JSON object")

    check_type = raw.get("type")
    if check_type not in CHECK_FUNCTIONS:
        raise DatasetError(
            f"{where}: unknown check type '{check_type}' "
            f"(allowed: {', '.join(sorted(CHECK_FUNCTIONS))})"
        )

    failure_type = raw.get("failure_type")
    if failure_type not in FAILURE_TYPES:
        raise DatasetError(f"{where}: unknown or missing failure_type '{failure_type}'")

    description = raw.get("description", "")
    if not isinstance(description, str) or not description.strip():
        raise DatasetError(f"{where}: 'description' is required so failures are explainable")

    # Everything that isn't a structural key is a parameter for the check.
    params = {k: v for k, v in raw.items() if k not in ("type", "failure_type", "description")}
    missing = [p for p in REQUIRED_PARAMS[check_type] if p not in params]
    if missing:
        raise DatasetError(f"{where}: check '{check_type}' is missing parameter(s): {', '.join(missing)}")

    return Check(type=check_type, failure_type=failure_type, description=description, params=params)


def _parse_history(raw: object, where: str) -> list[dict]:
    if not isinstance(raw, list):
        raise DatasetError(f"{where}: 'history' must be a list of messages")
    for i, message in enumerate(raw, 1):
        if (
            not isinstance(message, dict)
            or message.get("role") not in ("user", "assistant")
            or not isinstance(message.get("content"), str)
        ):
            raise DatasetError(
                f"{where}: history message #{i} needs role 'user'/'assistant' and string content"
            )
    return list(raw)


def load_responses(path: str | Path) -> dict[str, str]:
    """Load recorded responses: JSONL lines of {"id": ..., "response": ...}."""
    path = Path(path)
    if not path.is_file():
        raise DatasetError(f"Responses file not found: {path}")

    responses: dict[str, str] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            where = f"{path.name}:{line_number}"
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DatasetError(f"{where}: invalid JSON ({exc.msg})") from exc
            if not isinstance(raw, dict) or not isinstance(raw.get("id"), str) or not isinstance(
                raw.get("response"), str
            ):
                raise DatasetError(f"{where}: expected {{\"id\": str, \"response\": str}}")
            responses[raw["id"]] = raw["response"]
    return responses
