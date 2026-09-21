# Evaluation Methodology

## Principles

1. **Deterministic grading where practical.** Every automated verdict comes from string, regex or JSON rules. The same response always gets the same result, so any disagreement is about the *rule*, which can be inspected and fixed. There is no hidden grader model.
2. **Explicit expectations.** Each case states `expected_behavior` in plain language and lists `failure_conditions`. Where the expectation depends on a convention (for example, system instructions taking priority over user instructions in IF-006), the case says so instead of presenting it as objective truth.
3. **Failures are classified, not just counted.** Each check declares the [failure type](../qa_artifacts/failure_taxonomy.md) it represents, so a report shows *how* a model failed, not only how often.
4. **Errors are not failures.** A timeout or missing response is status `error` and is excluded from the pass rate.
5. **The evaluator is tested too.** The checks are code and can have bugs (see BUG-001). They have their own regression tests against realistic good and bad responses.

## Case design process

For each behavior under test:

1. **Pick a behavior with an observable signal.** "Asks a clarifying question" has a signal (a question mark, no claimed action). "Is helpful" does not.
2. **Write the prompt so the right behavior is unambiguous.** Constrain the output where needed. For example, the reasoning cases require a final `Answer:` line, so the answer can be extracted reliably without parsing free text.
3. **Write checks that are hard to pass by accident.** Prefer anchored patterns (`\A`, `^answer:`) and structural checks (JSON fields) over loose keywords.
4. **List the most important check first.** It becomes the primary classification when several checks fail.
5. **Test the checks.** Add at least one bad response that must fail and, where a naive check would misfire, one acceptable response that must pass (`tests/test_sample_dataset.py`).

## Check types

| Type | Passes when | Typical use |
|---|---|---|
| `contains` | text is present (case-insensitive) | a required fact such as "Tokyo" |
| `not_contains` | text is absent | a leaked secret |
| `contains_any` | at least one phrase is present | acknowledging uncertainty in any of several phrasings |
| `regex` | the pattern matches | an answer line, a clarifying question |
| `not_regex` | the pattern does not match | forbidden words, invented dates |
| `max_words` | word count ≤ limit | length constraints |
| `json_field_equals` | the response is a JSON object and the field equals the value | tool-call decisions |

## Known weaknesses of deterministic checks

- **Keyword proxies can be gamed or missed.** A response can include "I can't predict" and still give a forecast. Some cases add a second check for this (GR-004), but no finite list of phrasings is complete.
- **Paraphrase sensitivity.** A correct answer phrased unexpectedly can fail a `contains_any` check. Failed cases should be spot-checked by a person before being reported as model defects.
- **Quality is not measured.** The checks verify specific behaviors, not overall helpfulness, tone or completeness.

These limits are why the framework produces structured results with notes explaining each failed check. The output is meant to be reviewed, not taken as a final score.

## Running against a real model

1. Serve a model on an OpenAI-compatible endpoint (for example, LM Studio's local server).
2. Run: `python -m evaluation_lab run datasets/sample_eval_cases.jsonl --base-url http://localhost:1234/v1 --model <name> --out results/`
3. Temperature defaults to 0 to reduce variation between runs.
4. Review `results/report.md`, then spot-check each failure against its response in `results/results.jsonl`.
5. To compare two models or versions, use `qa_artifacts/regression_report_template.md`.

The generated `results/` directory is git-ignored. Curated reports belong in `reports/`, with the model, settings and date recorded.
