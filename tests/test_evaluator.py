"""Result generation and failure classification."""

from evaluation_lab.dataset import parse_case
from evaluation_lab.evaluator import error_result, evaluate_case


def test_passing_response(valid_case_dict):
    result = evaluate_case(parse_case(valid_case_dict), "According to the context, it launched in 2019.")

    assert result.status == "pass"
    assert result.passed
    assert result.test_id == "T-001"
    assert result.category == "grounding"
    assert result.severity == "high"
    assert result.failure_classification is None
    assert result.notes == []


def test_failing_response_is_classified(valid_case_dict):
    result = evaluate_case(parse_case(valid_case_dict), "It launched in 2021.")

    assert result.status == "fail"
    assert not result.passed
    assert result.failure_classification == "unsupported_claim"
    # Both checks fail: wrong year present, correct year absent
    assert len(result.notes) == 2
    assert any("2021" in note for note in result.notes)


def test_primary_classification_is_first_failed_check(valid_case_dict):
    valid_case_dict["checks"] = [
        {"type": "max_words", "limit": 3, "failure_type": "format_violation", "description": "Short"},
        {"type": "contains", "value": "2019", "failure_type": "unsupported_claim", "description": "Year"},
    ]
    case = parse_case(valid_case_dict)

    only_second_fails = evaluate_case(case, "2020")
    assert only_second_fails.failure_classification == "unsupported_claim"
    assert only_second_fails.all_failure_types == ["unsupported_claim"]

    both_fail = evaluate_case(case, "I believe it was probably 2020")
    assert both_fail.failure_classification == "format_violation"
    assert both_fail.all_failure_types == ["format_violation", "unsupported_claim"]


def test_duplicate_failure_types_are_collapsed(valid_case_dict):
    result = evaluate_case(parse_case(valid_case_dict), "2022")
    assert result.all_failure_types == ["unsupported_claim"]


def test_evaluation_is_deterministic(valid_case_dict):
    case = parse_case(valid_case_dict)
    first = evaluate_case(case, "It was 2021, or maybe 2019.")
    second = evaluate_case(case, "It was 2021, or maybe 2019.")
    assert first == second


def test_empty_response_fails_rather_than_crashing(valid_case_dict):
    result = evaluate_case(parse_case(valid_case_dict), "")
    assert result.status == "fail"


def test_error_result_is_not_a_failure(valid_case_dict):
    result = error_result(parse_case(valid_case_dict), "timeout")
    assert result.status == "error"
    assert result.failure_classification is None
    assert result.notes == ["timeout"]
