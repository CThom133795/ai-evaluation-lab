# Manual Test Case Template

Use this template for behaviors that are not automated yet, or that need human judgment (for example, spoken-voice evaluation). When a manual test becomes stable and has an objective pass criterion, convert it into a JSONL case with deterministic checks.

---

## Template

```markdown
# TC-<number>: <title>

| Field | Value |
|---|---|
| Area | instruction_following / reasoning / grounding / tool_use / adversarial |
| Test type | functional / negative / boundary / regression / exploratory |
| Priority | P1 / P2 / P3 |
| Severity if failed | critical / high / medium / low |
| Automation status | manual / candidate for automation / automated as <case ID> |
| Author / Date | |

## Objective
What behavior this verifies, and why it matters.

## Preconditions
System state, configuration, and conversation history needed before step 1.

## Test Data
Exact prompts, context documents, and inputs.

## Steps
| # | Action | Expected result |
|---|---|---|
| 1 | | |
| 2 | | |

## Pass Criteria
Objective conditions that must all hold.

## Fail Criteria
Conditions that mean a failure, each mapped to a failure type
(see qa_artifacts/failure_taxonomy.md).

## Execution Record
| Date | Tester | Build / model version | Result | Notes / defect ID |
|---|---|---|---|---|
```

---

## Example: manual test derived from the persona case study

# TC-001: Persona and style preference retention over a scripted voice session

| Field | Value |
|---|---|
| Area | instruction_following |
| Test type | functional, regression |
| Priority | P2 |
| Severity if failed | medium |
| Automation status | Manual. The text-mode analogue is automated as IF-007 |
| Author / Date | Repository author / 2026-09-21 |

### Objective
Check that a voice/persona preference set at the start of a session is kept through the whole session without further prompting. Based on the observation in [`case_studies/persona_consistency_voice_drift.md`](../case_studies/persona_consistency_voice_drift.md).

### Preconditions
- New voice-mode session with no prior history.
- The tester records every turn, with audio if available.

### Test Data
A fixed script of 20 neutral conversational prompts, prepared in advance and used unchanged on every run.

### Steps
| # | Action | Expected result |
|---|---|---|
| 1 | Ask the assistant to use a British-style voice and persona for the whole session. | The assistant confirms and responds in a British-style voice. |
| 2 | Ask the assistant not to use the phrase "and honestly". | The assistant acknowledges. |
| 3 | Deliver the 20 scripted prompts one at a time. | Every response keeps the persona and never uses "and honestly". |
| 4 | For each turn, record: persona held (Y/N) and banned phrase used (Y/N). | All turns: Y / N. |
| 5 | If drift occurs, restate the preference once, then continue the script. | The persona returns within 1 turn and holds for the rest of the script. |

### Pass Criteria
- The persona holds on all 20 scripted turns, **and**
- the banned phrase appears in 0 turns.

### Fail Criteria
- Any turn with persona drift → `context_loss`
- Any use of the banned phrase after step 2 → `context_loss`
- After a restated preference, recovery takes more than 1 turn or does not hold → `context_loss` (note the recovery latency)

### Execution Record
| Date | Tester | Build / model version | Result | Notes / defect ID |
|---|---|---|---|---|
| (not yet executed) | | | | |
