# Test Plan: AI Evaluation Lab

This plan covers two things under test:

1. **The evaluation framework itself** (Python code: loader, checks, evaluator, clients, runner, CLI).
2. **Model behavior**, measured with the evaluation dataset.

Testing the framework comes first. If the tool that measures model behavior has defects, its results about models can't be trusted.

---

## 1. Scope

### In scope
| Area | What is tested |
|---|---|
| Dataset loading | JSONL parsing, required fields, allowed values, duplicate IDs, malformed lines, line-numbered errors |
| Checks | Each check type's pass/fail logic, case-insensitivity, boundaries, JSON parsing |
| Evaluation | Pass/fail/error status, primary and secondary failure classification, determinism |
| Clients | Offline replay, message construction, request payload, response parsing, network-failure handling |
| Runner and reporting | Batch behavior when single cases error, summary math, JSONL output, Markdown report |
| CLI | Exit codes, argument validation, output files |
| Dataset checks | That each case's checks accept good responses, reject bad ones, and avoid known false positives |
| Model behavior | 30 cases across instruction following, reasoning, grounding, tool use and adversarial robustness |

### Out of scope (current version)
- Statistical significance testing across repeated runs
- LLM-as-judge grading
- Voice/audio evaluation (manual only; see `test_case_template.md` TC-001)
- Load or performance testing of model endpoints

---

## 2. Test Approach

| Test type | How it applies here | Where |
|---|---|---|
| **Unit / functional testing** | Each check and loader rule tested alone with small inputs | `tests/test_checks.py`, `tests/test_dataset.py` |
| **Negative testing** | Malformed JSON, missing fields, unknown enums, empty lists, bad history, malformed API responses | `tests/test_dataset.py`, `tests/test_clients.py` |
| **Boundary testing** | Word limits at exactly N and N+1, empty responses, zero limits | `tests/test_checks.py`, `tests/test_evaluator.py` |
| **Integration testing** | Loader → client → evaluator → runner → report, through the CLI | `tests/test_cli.py`, `tests/test_runner.py` |
| **Regression testing** | Shipped dataset checks run against a fixed set of good and bad responses | `tests/test_sample_dataset.py` |
| **Exploratory testing** | Unscripted interaction with live systems to find new failure patterns | `case_studies/` |
| **Defect reproduction** | Every fixed defect gets a failing-then-passing regression test | `qa_artifacts/bug_report_template.md` (BUG-001) |

### Offline-first principle
All automated tests run **without network access or API keys**. Model responses are replayed from files. The only client test that touches a socket connects to `127.0.0.1` on a closed port to confirm connection failures are handled. It never leaves the machine.

---

## 3. Entry and Exit Criteria

**Entry (before a test cycle):** the code installs cleanly (`pip install -e ".[dev]"`) and the dataset validates (`python -m evaluation_lab validate ...`).

**Exit / release validation (before merging to `main`):**
- All pytest tests pass locally and in GitHub Actions.
- The dataset validates with no errors.
- Every change to a dataset check has an accompanying case in `tests/test_sample_dataset.py`.
- No secrets, virtual environments or private source material are staged (check `git status` and `git diff --cached`).

---

## 4. Test Coverage Map

| Requirement | Covered by |
|---|---|
| Required fields are enforced | `test_each_required_field_is_enforced` (parametrized over all 7 fields) |
| Errors identify the file and line | `test_error_message_points_at_line_number` |
| A case with no checks is rejected (it would always pass) | `test_empty_checks_list_is_rejected` |
| Results classify the first failed check as primary | `test_primary_classification_is_first_failed_check` |
| Evaluation is deterministic | `test_evaluation_is_deterministic` |
| An unevaluable case is an error, not a failure | `test_error_result_is_not_a_failure`, `test_missing_response_is_error_and_run_continues` |
| The pass rate excludes errors | `test_summary_excludes_errors_from_pass_rate` |
| Document context is not given system-level authority | `test_messages_put_context_in_user_turn_not_system` |
| The API key is never sent unless configured | `test_api_key_only_sent_when_present` |
| Dataset checks catch realistic failures and avoid false positives | `test_checks_on_alternate_responses` |

---

## 5. Risks

| Risk | Mitigation |
|---|---|
| Keyword/regex checks give false positives or false negatives | Regression tests with alternate responses; case descriptions document assumptions; ambiguous behaviors noted for human review |
| Non-deterministic model output makes runs hard to compare | Temperature 0 by default; rerun before declaring a regression (see `regression_report_template.md`) |
| Expectations reflect one evaluator's judgment | `expected_behavior` states assumptions explicitly (for example, IF-006's instruction hierarchy) |
| Fixture data mistaken for real model results | Every report states its response source; `reports/example_report.md` says explicitly that the data is not model output |
