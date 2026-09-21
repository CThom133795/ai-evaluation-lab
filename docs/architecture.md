# Architecture

The framework is a short pipeline of small modules. Each has one job, and the data passed between them is a plain dataclass.

```
 datasets/*.jsonl
       │
       ▼
 dataset.load_cases()          validate schema → list[EvalCase]
       │
       ▼
 client.generate(case)         ReplayClient (file)  or  OpenAICompatibleClient (HTTP)
       │                        └── raises ModelClientError → result status "error"
       ▼
 evaluator.evaluate_case()     run every check in checks.py → EvalResult
       │
       ▼
 runner.summarize()            counts by status, category, severity, failure type
 runner.write_results_jsonl()  machine-readable, one result per line
 runner.render_markdown_report()  human-readable report
```

## Modules

| File | Responsibility |
|---|---|
| `models.py` | Dataclasses (`EvalCase`, `Check`, `EvalResult`) and the allowed categories, severities and failure types |
| `dataset.py` | Reads JSONL, validates every field, and reports errors with file and line number |
| `checks.py` | The deterministic check functions and a registry that maps names to functions |
| `evaluator.py` | Applies a case's checks to one response and builds the result, including classification |
| `clients.py` | Where responses come from: replay from a file, or any OpenAI-compatible endpoint |
| `runner.py` | Runs all cases, keeps going past individual errors, and writes the summary and reports |
| `cli.py` | `validate` and `run` commands |

## Design decisions

**Standard library only at runtime.** The HTTP client uses `urllib`, so there is no `requests` or provider SDK to install. It keeps installation trivial and makes clear that nothing is tied to one vendor. pytest is the only development dependency.

**Clients share one method.** The runner only calls `client.generate(case)`. Replaying recorded responses, calling LM Studio, or calling a hosted API are interchangeable. That is also what lets the whole pipeline be tested offline.

**Context goes in the user turn, not the system prompt.** Case `context` is often untrusted content (a review, a search result). Putting it in the system prompt would give it more authority than it should have and would weaken the prompt-injection cases. See `build_messages()` in `clients.py`.

**Checks are declared in data, not code.** Adding a case never requires Python changes, which keeps the dataset reviewable by people who don't write code. Adding a new *check type* means adding one function and one registry entry.

**Strict validation up front.** A malformed case stops the run before any model call. A silently skipped case would make results look more complete than they are.

**`error` is separate from `fail`.** Infrastructure problems should never look like model regressions.

## Extending

| To add… | Change |
|---|---|
| A case | Append a line to the dataset; add alternate-response tests if its checks are non-trivial |
| A check type | Add a function to `checks.py`, add it to `CHECK_FUNCTIONS` and `REQUIRED_PARAMS`, and add tests |
| A failure type | Add it to `FAILURE_TYPES` in `models.py` and document it in `qa_artifacts/failure_taxonomy.md` |
| A model provider with a different API | Write a class with `generate(case) -> str` that raises `ModelClientError` on failure |
