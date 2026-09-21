# Evidence Index

This index maps each capability to the files in this repository that show it. Every entry points to something that can be opened and checked.

| Capability | Evidence | What to look at |
|---|---|---|
| **AI evaluation design** | [`datasets/sample_eval_cases.jsonl`](../datasets/sample_eval_cases.jsonl), [`evals/`](../evals/) | 30 cases across 5 areas, each with expected behavior, failure conditions, severity and deterministic checks. The READMEs in `evals/` explain the reasoning for each area |
| **Evaluation framework (Python)** | [`src/evaluation_lab/`](../src/evaluation_lab/) | Loader, checks, evaluator, clients, runner, CLI. Standard library only |
| **Model behavior testing** | Dataset categories; [`reports/example_report.md`](../reports/example_report.md) | Instruction following, reasoning, grounding, tool use and adversarial cases, plus a structured report format |
| **Multi-turn and persona evaluation** | [`case_studies/persona_consistency_voice_drift.md`](../case_studies/persona_consistency_voice_drift.md), cases IF-007 to IF-009, ADV-006 | Observed persona drift written up as an evaluation case; automated multi-turn retention cases |
| **Prompt-injection and adversarial testing** | Cases ADV-001 to ADV-006 | Indirect injection, system-prompt extraction, role-play jailbreak, tool-output injection, authority claims, multi-turn social engineering |
| **Failure classification** | [`qa_artifacts/failure_taxonomy.md`](../qa_artifacts/failure_taxonomy.md), [`evaluator.py`](../src/evaluation_lab/evaluator.py) | 11 failure types with definitions, examples and rules for telling similar types apart; implemented as primary and secondary classification |
| **Software QA: test planning** | [`qa_artifacts/test_plan.md`](../qa_artifacts/test_plan.md) | Scope, test types, entry/exit criteria, coverage map, risks |
| **Defect reporting and reproduction** | [`qa_artifacts/bug_report_template.md`](../qa_artifacts/bug_report_template.md) | Template plus BUG-001, a real false-positive defect found in this project's own dataset, with reproduction steps and fix verification |
| **Manual test case design** | [`qa_artifacts/test_case_template.md`](../qa_artifacts/test_case_template.md) | Template plus TC-001 (persona retention), derived from the case study |
| **Regression testing** | [`tests/test_sample_dataset.py`](../tests/test_sample_dataset.py), [`qa_artifacts/regression_report_template.md`](../qa_artifacts/regression_report_template.md) | Regression tests that keep the dataset checks correct; a template for comparing two runs |
| **Automated testing (pytest)** | [`tests/`](../tests/) | Unit, negative, boundary and integration tests; parametrized cases; fixtures; offline by design |
| **Continuous integration** | [`.github/workflows/tests.yml`](../.github/workflows/tests.yml), the repository's Actions tab | Tests run on every push and pull request across two Python versions |
| **Model API integration** | [`src/evaluation_lab/clients.py`](../src/evaluation_lab/clients.py) | OpenAI-compatible chat-completions client for LM Studio or hosted APIs; API key read from the environment, never stored |
| **Git workflow** | Commit history | A feature branch merged into `main`; each commit describes one logical change |
| **Technical writing** | [`docs/`](./), [`README.md`](../README.md) | Methodology, rubric, architecture, and documented limitations |

## What this repository does *not* show

To keep this index honest:

- **No results from a real model are published yet.** The example report uses hand-written fixture responses and says so. The live-model client is implemented and unit-tested, but no live evaluation has been recorded in `reports/`.
- **No professional QA employment** is implied. This is an independent portfolio project.
- **The case study is a single observation** of a live system, with no access to that system's internals.
