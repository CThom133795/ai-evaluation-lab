"""Dataset parsing and schema validation."""

import pytest

from evaluation_lab.dataset import REQUIRED_FIELDS, DatasetError, load_cases, load_responses, parse_case


def test_loads_valid_case(write_jsonl, valid_case_dict):
    cases = load_cases(write_jsonl([valid_case_dict]))

    assert len(cases) == 1
    case = cases[0]
    assert case.id == "T-001"
    assert case.category == "grounding"
    assert case.context == "The product launched in 2019."
    assert [c.type for c in case.checks] == ["contains", "not_regex"]
    # Non-structural keys become check parameters
    assert case.checks[0].params == {"value": "2019"}


def test_optional_fields_default_to_empty(valid_case_dict):
    del valid_case_dict["context"]
    case = parse_case(valid_case_dict)
    assert case.context == ""
    assert case.system == ""
    assert case.history == []
    assert case.tags == []


def test_blank_lines_are_ignored(write_jsonl, valid_case_dict):
    second = dict(valid_case_dict, id="T-002")
    path = write_jsonl([valid_case_dict, "", "   ", second])
    assert [c.id for c in load_cases(path)] == ["T-001", "T-002"]


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_each_required_field_is_enforced(valid_case_dict, field):
    del valid_case_dict[field]
    with pytest.raises(DatasetError, match=f"missing required field.*{field}"):
        parse_case(valid_case_dict)


def test_error_message_points_at_line_number(write_jsonl, valid_case_dict):
    bad = dict(valid_case_dict, id="T-002", severity="urgent")
    path = write_jsonl([valid_case_dict, bad])
    with pytest.raises(DatasetError, match=r"cases\.jsonl:2: unknown severity 'urgent'"):
        load_cases(path)


def test_invalid_json_line_is_reported(write_jsonl, valid_case_dict):
    path = write_jsonl([valid_case_dict, '{"id": "broken",'])
    with pytest.raises(DatasetError, match=r":2: invalid JSON"):
        load_cases(path)


def test_non_object_line_is_rejected(write_jsonl):
    with pytest.raises(DatasetError, match="must be a JSON object"):
        load_cases(write_jsonl(['["not", "an", "object"]']))


def test_duplicate_ids_are_rejected(write_jsonl, valid_case_dict):
    with pytest.raises(DatasetError, match="duplicate case id 'T-001'"):
        load_cases(write_jsonl([valid_case_dict, valid_case_dict]))


def test_unknown_category_is_rejected(valid_case_dict):
    valid_case_dict["category"] = "vibes"
    with pytest.raises(DatasetError, match="unknown category 'vibes'"):
        parse_case(valid_case_dict)


@pytest.mark.parametrize("value", ["", "   ", None, 42])
def test_prompt_must_be_non_empty_string(valid_case_dict, value):
    valid_case_dict["prompt"] = value
    with pytest.raises(DatasetError, match="'prompt' must be a non-empty string"):
        parse_case(valid_case_dict)


def test_empty_checks_list_is_rejected(valid_case_dict):
    # A case with no checks would always pass, which would be misleading.
    valid_case_dict["checks"] = []
    with pytest.raises(DatasetError, match="'checks' must be a non-empty list"):
        parse_case(valid_case_dict)


def test_empty_failure_conditions_rejected(valid_case_dict):
    valid_case_dict["failure_conditions"] = []
    with pytest.raises(DatasetError, match="failure_conditions"):
        parse_case(valid_case_dict)


def test_unknown_check_type_is_rejected(valid_case_dict):
    valid_case_dict["checks"][0]["type"] = "sounds_good"
    with pytest.raises(DatasetError, match="check #1: unknown check type 'sounds_good'"):
        parse_case(valid_case_dict)


def test_check_missing_parameter_is_rejected(valid_case_dict):
    del valid_case_dict["checks"][1]["pattern"]
    with pytest.raises(DatasetError, match="check #2: check 'not_regex' is missing parameter.*pattern"):
        parse_case(valid_case_dict)


def test_check_requires_known_failure_type(valid_case_dict):
    valid_case_dict["checks"][0]["failure_type"] = "bad_vibes"
    with pytest.raises(DatasetError, match="unknown or missing failure_type"):
        parse_case(valid_case_dict)


def test_check_requires_description(valid_case_dict):
    del valid_case_dict["checks"][0]["description"]
    with pytest.raises(DatasetError, match="'description' is required"):
        parse_case(valid_case_dict)


@pytest.mark.parametrize(
    "history",
    [
        "not a list",
        [{"role": "system", "content": "hi"}],  # system belongs in its own field
        [{"role": "user"}],
        [{"role": "user", "content": 5}],
    ],
)
def test_malformed_history_is_rejected(valid_case_dict, history):
    valid_case_dict["history"] = history
    with pytest.raises(DatasetError, match="history"):
        parse_case(valid_case_dict)


def test_missing_file_raises_dataset_error(tmp_path):
    with pytest.raises(DatasetError, match="not found"):
        load_cases(tmp_path / "nope.jsonl")


def test_empty_file_is_rejected(write_jsonl):
    with pytest.raises(DatasetError, match="no cases"):
        load_cases(write_jsonl([""]))


def test_load_responses(write_jsonl):
    path = write_jsonl([{"id": "A", "response": "hello"}, {"id": "B", "response": ""}], "r.jsonl")
    assert load_responses(path) == {"A": "hello", "B": ""}


def test_load_responses_rejects_wrong_shape(write_jsonl):
    path = write_jsonl([{"id": "A", "text": "hello"}], "r.jsonl")
    with pytest.raises(DatasetError, match=r"r\.jsonl:1"):
        load_responses(path)
