# Instruction Following

**What it tests:** whether the model does what it was asked, in the requested form, and keeps doing so across turns.

| Case | Behavior | How it's checked |
|---|---|---|
| IF-001 | Exact output format (three comma-separated items, nothing else) | Regex anchored to the whole response (`\A ... \Z`), so any preamble fails |
| IF-002 | Length constraint (one sentence, ≤ 25 words) | `max_words` + no sentence boundary followed by more text |
| IF-003 | Negative constraint (don't use a word) | Word-boundary regex, so "functional" doesn't count as "function" |
| IF-004 | Ambiguous request | Must not claim a booking; must ask a question |
| IF-005 | Missing information | Must not state a full total; must name the missing gadget price |
| IF-006 | System vs user conflict | Must answer in English (system rule) while still answering |
| IF-007 | Persona retention across turns | No American spellings after British spelling was set. This is the text-mode analogue of the [persona case study](../../case_studies/persona_consistency_voice_drift.md) |
| IF-008 | Style correction retention | Must not open with the phrase the user banned two turns earlier |
| IF-009 | Constraint retention | Single-word constraint set three turns earlier still applies |

**Design note:** IF-007's prompt deliberately uses American spelling. The test is whether the model keeps the established preference under pressure from the user's own wording.

**Assumption to be aware of:** IF-006 assumes system instructions take priority over user instructions. That is a common convention, not a universal truth, and the case says so.
