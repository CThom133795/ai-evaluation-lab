"""Running a batch, summarizing, and writing outputs."""

import json

from evaluation_lab.clients import ReplayClient
from evaluation_lab.dataset import parse_case
from evaluation_lab.runner import render_markdown_report, run_evaluation, summarize, write_results_jsonl


def make_cases(valid_case_dict):
    second = dict(valid_case_dict, id="T-002", category="reasoning", severity="low")
    third = dict(valid_case_dict, id="T-003")
    return [parse_case(valid_case_dict), parse_case(second), parse_case(third)]


def test_missing_response_is_error_and_run_continues(valid_case_dict):
    cases = make_cases(valid_case_dict)
    client = ReplayClient({"T-001": "2019", "T-002": "2021"})  # T-003 missing

    results = run_evaluation(cases, client)

    assert [r.status for r in results] == ["pass", "fail", "error"]


def test_summary_excludes_errors_from_pass_rate(valid_case_dict):
    results = run_evaluation(make_cases(valid_case_dict), ReplayClient({"T-001": "2019", "T-002": "2021"}))
    summary = summarize(results)

    assert summary["total"] == 3
    assert (summary["passed"], summary["failed"], summary["errors"]) == (1, 1, 1)
    assert summary["pass_rate"] == 0.5  # 1 of 2 graded cases
    assert summary["failures_by_severity"]["low"] == 1
    assert summary["failures_by_type"] == {"unsupported_claim": 1}
    assert summary["by_category"]["grounding"] == {"pass": 1, "fail": 0, "error": 1}


def test_summary_of_nothing_graded(valid_case_dict):
    results = run_evaluation(make_cases(valid_case_dict), ReplayClient({}))
    assert summarize(results)["pass_rate"] is None


def test_results_jsonl_round_trip(tmp_path, valid_case_dict):
    results = run_evaluation(make_cases(valid_case_dict)[:2], ReplayClient({"T-001": "2019", "T-002": "2021"}))
    out = tmp_path / "nested" / "results.jsonl"

    write_results_jsonl(results, out)
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]

    assert [row["test_id"] for row in rows] == ["T-001", "T-002"]
    assert set(rows[1]) >= {"test_id", "category", "status", "failure_classification", "severity", "notes"}
    assert rows[1]["status"] == "fail"


def test_markdown_report_states_response_source(valid_case_dict):
    results = run_evaluation(make_cases(valid_case_dict), ReplayClient({"T-001": "2019", "T-002": "2021"}))
    report = render_markdown_report(results, title="Demo", source_note="hand-written fixtures")

    assert report.startswith("# Demo")
    assert "hand-written fixtures" in report
    assert "### T-002 (fail, low, unsupported_claim)" in report
    assert "### T-003 (error, high, evaluation error)" in report
