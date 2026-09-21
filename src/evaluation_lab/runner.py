"""Run a set of cases against a client and produce results and reports."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from .clients import ModelClient, ModelClientError
from .evaluator import error_result, evaluate_case
from .models import SEVERITIES, STATUS_ERROR, STATUS_FAIL, STATUS_PASS, EvalCase, EvalResult


def run_evaluation(cases: list[EvalCase], client: ModelClient) -> list[EvalResult]:
    """Evaluate every case. One case failing to run never stops the others."""
    results = []
    for case in cases:
        try:
            response = client.generate(case)
        except ModelClientError as exc:
            results.append(error_result(case, str(exc)))
            continue
        results.append(evaluate_case(case, response))
    return results


def summarize(results: list[EvalResult]) -> dict:
    """Aggregate counts. Pass rate excludes errored cases (they weren't graded)."""
    statuses = Counter(r.status for r in results)
    graded = statuses[STATUS_PASS] + statuses[STATUS_FAIL]
    failed = [r for r in results if r.status == STATUS_FAIL]

    by_category: dict[str, dict[str, int]] = {}
    for r in results:
        bucket = by_category.setdefault(r.category, {STATUS_PASS: 0, STATUS_FAIL: 0, STATUS_ERROR: 0})
        bucket[r.status] += 1

    return {
        "total": len(results),
        "passed": statuses[STATUS_PASS],
        "failed": statuses[STATUS_FAIL],
        "errors": statuses[STATUS_ERROR],
        "pass_rate": round(statuses[STATUS_PASS] / graded, 3) if graded else None,
        "failures_by_severity": {s: sum(1 for r in failed if r.severity == s) for s in SEVERITIES},
        "failures_by_type": dict(Counter(r.failure_classification for r in failed)),
        "by_category": dict(sorted(by_category.items())),
    }


def write_results_jsonl(results: list[EvalResult], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for r in results:
            handle.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")


def render_markdown_report(results: list[EvalResult], title: str, source_note: str) -> str:
    """Human-readable report. `source_note` states where responses came from,
    so a reader never mistakes fixture data for a real model measurement."""
    summary = summarize(results)
    rate = "n/a" if summary["pass_rate"] is None else f"{summary['pass_rate']:.1%}"
    lines = [
        f"# {title}",
        "",
        f"> **Response source:** {source_note}",
        "",
        "## Summary",
        "",
        "| Total | Passed | Failed | Errors | Pass rate (graded cases) |",
        "|---|---|---|---|---|",
        f"| {summary['total']} | {summary['passed']} | {summary['failed']} | {summary['errors']} | {rate} |",
        "",
        "## Results by category",
        "",
        "| Category | Pass | Fail | Error |",
        "|---|---|---|---|",
    ]
    for category, counts in summary["by_category"].items():
        lines.append(f"| {category} | {counts['pass']} | {counts['fail']} | {counts['error']} |")

    lines += ["", "## Failures by severity", "", "| Severity | Count |", "|---|---|"]
    for severity, count in summary["failures_by_severity"].items():
        lines.append(f"| {severity} | {count} |")

    problem_results = [r for r in results if r.status != STATUS_PASS]
    lines += ["", "## Failed and errored cases", ""]
    if not problem_results:
        lines.append("None.")
    for r in problem_results:
        label = r.failure_classification or "evaluation error"
        lines.append(f"### {r.test_id} ({r.status}, {r.severity}, {label})")
        lines.append("")
        lines.extend(f"- {note}" for note in r.notes)
        lines.append("")

    lines += ["## All results", "", "| Test ID | Category | Status | Severity | Classification |", "|---|---|---|---|---|"]
    for r in results:
        lines.append(
            f"| {r.test_id} | {r.category} | {r.status} | {r.severity} | {r.failure_classification or '-'} |"
        )
    return "\n".join(lines) + "\n"
