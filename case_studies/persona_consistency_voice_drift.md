# Case Study: Persona Consistency and Voice Drift in a Live Multi-Turn Voice Session

| Field | Value |
|---|---|
| Case ID | CS-001 |
| Date observed | September 20, 2026 |
| Evaluator | Repository author (direct observation) |
| System under evaluation | A publicly available conversational AI system with a spoken voice mode (vendor and model version not recorded in this public write-up) |
| Interaction type | Live, multi-turn voice conversation |
| Evaluation type | Exploratory testing, direct observation |
| Primary themes | Persona consistency, behavioral drift, multi-turn instruction adherence |
| Secondary themes | Style preference adherence, handling of user corrections |
| Source material | Private transcript curated by the author. It is not included in this repository (see [Source and Evidence](#source-and-evidence)) |

---

## Summary

During an ongoing voice session, the assistant was using a British-style voice and persona that had been established earlier in the conversation. Partway through, its spoken accent noticeably drifted toward one that sounded Scottish. The user questioned the change and restated the expected persona. Recovery was inconsistent over the next several turns, but the assistant eventually returned to the established behavior.

In the same session, the user flagged repeated use of the phrase "and honestly" as an unwanted stylistic habit and asked the assistant to stop. The assistant acknowledged the correction and changed its subsequent behavior.

This document records the behavior as an **evaluation case**. It does not claim to know the internal cause of the drift. See [Limitations](#limitations).

---

## Environment and Context

- **Mode:** Real-time spoken conversation (voice input and voice output).
- **Session state:** An ongoing session in which a British-style voice/persona preference had already been established before the drift occurred.
- **Configuration visibility:** The evaluator could see only the conversation itself. System prompts, voice-selection settings, model version and server-side session state were not visible.
- **Tooling:** None. Observation was manual, in real time.

---

## Expected Behavior

Once a voice/persona preference is established in a session, the assistant should keep it on every later turn unless the user explicitly asks for a change. In particular:

1. The accent and persona should stay consistent across turns.
2. If the user points out a deviation and restates the preference, the assistant should return to it promptly and stay there.
3. An explicit style correction (for example, "stop using this phrase") should apply to all later turns, not just the next one.

---

## Observed Behavior

### Primary finding: accent/persona drift

| Step | Observation |
|---|---|
| 1 | The session was running with the established British-style voice/persona. |
| 2 | During the ongoing multi-turn interaction, the spoken accent noticeably drifted toward one that sounded Scottish. The user had not asked for a change. |
| 3 | The user noticed immediately and explicitly asked why the accent had changed. |
| 4 | The user restated the desired voice/persona. |
| 5 | Recovery was inconsistent over several turns: the assistant did not reliably return to the requested behavior and hold it. |
| 6 | The user kept interacting, specifically to test whether the assistant would return to the requested behavior. |
| 7 | The assistant eventually realigned with the established preference. |

### Secondary finding: unwanted phrase repetition

| Step | Observation |
|---|---|
| 1 | The user noticed repeated use of the phrase "and honestly" in the assistant's responses. |
| 2 | The user explicitly said this phrasing was unwanted. |
| 3 | The assistant acknowledged the correction. |
| 4 | Later responses reflected the change. |

---

## Observation Sequence (Reproduction Notes)

This was an exploratory observation, not a scripted test. Here is the sequence in a form that could be reused as the starting point for a reproduction attempt:

1. Start a voice-mode session with the conversational AI system.
2. Establish a British-style voice/persona preference early in the session.
3. Continue a normal multi-turn conversation.
4. Monitor each spoken turn for accent or persona changes.
5. If drift happens, ask about the change and restate the preference.
6. Record, turn by turn, whether the requested behavior is restored and whether it holds.
7. Separately, correct a repeated stylistic habit (such as a filler phrase) and check whether the correction persists on later turns.

**Reproducibility status:** Observed once. No reproduction has been attempted yet. The trigger conditions (session length, topic, number of turns before drift) were not isolated.

---

## User Intervention

| Intervention | Type | Outcome |
|---|---|---|
| Asked why the accent had changed | Deviation report | Surfaced the drift explicitly within the conversation |
| Restated the desired voice/persona | Corrective instruction | Recovery was inconsistent at first, then realigned eventually |
| Kept interacting to test whether recovery held | Exploratory verification | Confirmed eventual realignment |
| Asked the assistant to stop saying "and honestly" | Style correction | Acknowledged, and later behavior changed |

---

## Result

| Finding | Result |
|---|---|
| Persona held across turns without prompting | **Fail**: the accent drifted during the session with no request to change |
| Prompt recovery after an explicit correction | **Partial**: recovery was inconsistent across several turns |
| Eventual recovery | **Pass**: the assistant realigned with the established preference |
| Style correction ("and honestly") was applied | **Pass**: acknowledged, and later behavior changed |

---

## Evaluation Classification

Classifications use this repository's [failure taxonomy](../qa_artifacts/failure_taxonomy.md).

| Attribute | Value |
|---|---|
| Primary failure type | `context_loss`: an established session preference was not kept |
| Behavior pattern | Behavioral drift across a multi-turn session |
| Secondary observation | Delayed or inconsistent recovery after a user correction |
| Severity (per [rubric](../docs/evaluation_rubric.md)) | **Medium.** The failure is noticeable to the user, degrades the experience and requires corrective effort. It involves no safety, privacy or data-integrity impact, and the assistant eventually recovered. |
| Style finding | Not a defect in the primary sense. It is an observation that the system handled an explicit style correction successfully. |

---

## Limitations

- **Single observation.** One session does not establish how often this happens or what triggers it.
- **Perceptual judgment.** "British-style" and "Scottish-sounding" are the evaluator's auditory perceptions. They were not measured by an objective acoustic method, and another listener might describe the accents differently.
- **No visibility into the system.** The evaluator had no access to voice configuration, system prompts, model version or session state. **No internal root cause is claimed.** The drift could come from the speech-synthesis layer, the language model, how conversation state is managed, or something else. This case study makes no claim about which.
- **No turn-level timestamps in this write-up.** Exact turn counts before drift and during recovery are not given here. Stating them from memory would risk inaccuracy.
- **Transcript not public.** Readers cannot independently check the observations from this document alone.

---

## Source and Evidence

The original transcript is a **curated private-source artifact** held by the author. It is **not** included in this public repository, and it will be added only if the author explicitly decides to publish a reviewed, redacted version later. The repository's `.gitignore` excludes a `private/` directory so raw source material stored locally cannot be committed by accident.

---

## Follow-Up Tests That Could Be Designed

These tests would turn this single observation into repeatable evaluation. They are proposals and have not been run.

| ID | Test idea | What it would measure |
|---|---|---|
| FU-1 | **Long-session persona hold.** Set a voice/persona preference, run a scripted conversation of N turns, and rate the accent on every turn. | Turn at which drift first appears, if at all; drift rate across repeated sessions |
| FU-2 | **Recovery latency.** Once drift is detected, apply a standard corrective instruction and count the turns until the requested behavior is stable (for example, 3 consecutive compliant turns). | Turns to recovery; whether recovery holds |
| FU-3 | **Topic-pressure test.** Include topics with strong regional associations (such as Scottish place names) to see whether content pulls the persona away from the preference. | Whether conversation content predicts drift |
| FU-4 | **Text-mode analogue.** Run the same preference-retention test in text with a measurable proxy (such as British vs American spelling). This repository already includes one such case: [`IF-007`](../datasets/sample_eval_cases.jsonl). | Whether preference retention also degrades without the speech layer |
| FU-5 | **Style-correction persistence.** Ban a phrase, then check the next K turns automatically (for example, a `not_regex` check on each turn's transcript). | Whether corrections persist, and for how long |
| FU-6 | **Multi-rater accent judgment.** Have several independent listeners label the same audio clips without knowing the expected answer. | Inter-rater agreement; lowers the dependence on a single listener's perception |

Tests FU-4 and FU-5 fit this repository's existing check types directly. FU-1, FU-2 and FU-6 would need audio capture and human rating, which the framework does not support yet.
