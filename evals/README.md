# Evaluation Areas

All cases live in one file, [`datasets/sample_eval_cases.jsonl`](../datasets/sample_eval_cases.jsonl), so the dataset has a single source of truth. Each folder here explains one area: what it tests, why it matters, and how the checks work.

| Area | Cases | Focus |
|---|---|---|
| [instruction_following](instruction_following/) | IF-001 to IF-009 | Format, length and negative constraints; ambiguity; missing information; conflicting instructions; multi-turn retention |
| [reasoning](reasoning/) | RS-001 to RS-005 | Multi-step arithmetic, invalid assumptions, date edge cases, logical inference |
| [grounding](grounding/) | GR-001 to GR-006 | Answering from context, hallucination traps, false premises, uncertainty, conflicting sources |
| [tool_use](tool_use/) | TU-001 to TU-004 | Choosing the right tool, avoiding unnecessary calls, refusing to invent arguments |
| [adversarial](adversarial/) | ADV-001 to ADV-006 | Prompt injection (direct, indirect, via tool output), secret extraction, jailbreak framing, social engineering |

To see only one area's cases:

```bash
grep '"category": "grounding"' datasets/sample_eval_cases.jsonl
```
