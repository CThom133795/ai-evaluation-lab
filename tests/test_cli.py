"""End-to-end CLI behavior (offline)."""

from evaluation_lab.cli import main


def test_validate_ok(write_jsonl, valid_case_dict, capsys):
    assert main(["validate", str(write_jsonl([valid_case_dict]))]) == 0
    assert "1 valid cases" in capsys.readouterr().out


def test_validate_bad_dataset_returns_2(write_jsonl, valid_case_dict, capsys):
    del valid_case_dict["severity"]
    assert main(["validate", str(write_jsonl([valid_case_dict]))]) == 2
    assert "missing required field" in capsys.readouterr().err


def test_run_writes_outputs_and_exit_code_reflects_failures(tmp_path, write_jsonl, valid_case_dict):
    cases = write_jsonl([valid_case_dict])
    out = tmp_path / "out"

    passing = write_jsonl([{"id": "T-001", "response": "2019"}], "pass.jsonl")
    assert main(["run", str(cases), "--responses", str(passing), "--out", str(out)]) == 0
    assert (out / "results.jsonl").is_file()
    assert (out / "report.md").is_file()

    failing = write_jsonl([{"id": "T-001", "response": "2020"}], "fail.jsonl")
    assert main(["run", str(cases), "--responses", str(failing), "--out", str(out)]) == 1


def test_base_url_requires_model(write_jsonl, valid_case_dict, capsys):
    cases = write_jsonl([valid_case_dict])
    assert main(["run", str(cases), "--base-url", "http://localhost:1234/v1"]) == 2
    assert "--model is required" in capsys.readouterr().err
