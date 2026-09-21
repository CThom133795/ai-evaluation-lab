# Regression Report Template

A regression report compares two evaluation runs of the **same dataset version**: a baseline (for example, the previous model version or prompt) and a candidate. Its purpose is to support a release decision.

Build it from two `results.jsonl` files produced by `python -m evaluation_lab run`. Comparing per case (not only overall pass rates) is the important part: two runs can have the same pass rate while different cases fail.

---

## Template

```markdown
# Regression Report: <candidate> vs <baseline>

| Field | Value |
|---|---|
| Date | YYYY-MM-DD |
| Dataset | datasets/sample_eval_cases.jsonl @ commit <sha> |
| Baseline | model / prompt / config, run date, results file |
| Candidate | model / prompt / config, run date, results file |
| Sampling settings | temperature, max tokens, and any others |
| Prepared by | |

## 1. Summary
| Metric | Baseline | Candidate | Change |
|---|---|---|---|
| Graded cases | | | |
| Passed | | | |
| Failed | | | |
| Errors (not graded) | | | |
| Critical/high failures | | | |

## 2. Per-case changes
| Case ID | Category | Severity | Baseline | Candidate | Change |
|---|---|---|---|---|---|
| | | | pass | fail | **Regression** |
| | | | fail | pass | Fix |

Only changed cases are listed. Unchanged cases are summarized in section 1.

## 3. New failures (regressions): analysis
For each regression: failure classification, failure notes, and whether it
reproduces on a rerun (checks for run-to-run variation).

## 4. Errors
Cases that could not be graded, with cause. Errors are not model failures,
but a high error rate makes the comparison unreliable.

## 5. Known limitations of this comparison
e.g. single run per configuration, keyword-based checks, dataset size.

## 6. Release recommendation
Go / No-go / Go with conditions, and the reasoning. Any new critical-severity
failure should block release by default (see docs/evaluation_rubric.md).
```

---

## Guidance

- **Rerun before declaring a regression.** Even at temperature 0, some endpoints are not fully deterministic. A case that flips on a rerun should be reported as *unstable*, not as a regression.
- **Keep the dataset fixed.** If cases or checks changed between runs, the comparison is not valid. Rerun the baseline on the new dataset.
- **Separate check changes from model changes.** If a check is fixed (see BUG-001 in `bug_report_template.md`), results can change without the model changing. Note check fixes explicitly.
