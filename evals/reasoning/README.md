# Reasoning

**What it tests:** multi-step problems where a plausible shortcut leads to a wrong answer.

| Case | Trap | Correct answer |
|---|---|---|
| RS-001 | Forgetting the free-pen rule, or counting free pens wrongly | $24 |
| RS-002 | Scaling time with quantity | 5 minutes |
| RS-003 | Date overflow (Jan 31 + 1 month → "March 3") | February 28 |
| RS-004 | Affirming the consequent | Cannot be determined |
| RS-005 | Unit conversion before division | 125 seconds |

**How it's checked:** every prompt asks for a final `Answer: ...` line. The checks are:

1. `format_violation` if there is no answer line, listed first so a format failure is classified as one.
2. `reasoning_error` if the answer line has the wrong value.

This keeps grading deterministic without parsing free-form working. The limitation: a model that reasons correctly but ignores the answer-line instruction is recorded as a format failure, not a reasoning success.
