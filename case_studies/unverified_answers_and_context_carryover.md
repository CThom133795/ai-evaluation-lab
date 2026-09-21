# Case Study: Incorrect Answers on an Unfamiliar Topic and Carryover of Unrelated Prior Context

| Field | Value |
|---|---|
| Case ID | CS-002 |
| Date observed | On or before 2026-09-21 (exact date not recorded) |
| Evaluator | Repository author (direct observation) |
| System under evaluation | Project Pulse, the author's own local-first AI desktop companion under development ([CThom133795/gaming-content-pipeline](https://github.com/CThom133795/gaming-content-pipeline)) |
| Build / model configuration | Not recorded in this write-up |
| Interaction type | Multi-turn conversation |
| Evaluation type | Exploratory testing, direct observation |
| Primary themes | Grounding, unsupported claims, uncertainty handling |
| Secondary themes | Relevance of retained context, capability transparency |
| Source material | Not included in this repository |

---

## Summary

The evaluator asked the application about *Fallen Aces*, an independently developed video game. The evaluator believed at the time that the application could look information up on the internet. Across several attempts, the application's answers about the game were incorrect. They also repeatedly drew on earlier, unrelated conversation context, including topics from light coding sessions the evaluator had previously carried out with ChatGPT, instead of addressing the question asked.

This document records the behavior as an **evaluation case**. It does not claim to know why the application answered this way. See [Limitations](#limitations).

---

## Environment and Context

- **Application:** Project Pulse, a Windows application in active development that combines speech, a language model and conversational state.
- **Evaluator's assumption:** At the time, the evaluator believed the application had internet access. Whether it did, and whether the application said anything about it during the session, was not recorded.
- **Prior context:** The evaluator had earlier held coding-related conversations with ChatGPT. How material from those sessions reached this application's context is not established here.
- **Configuration visibility:** The language model, context/memory settings and build version in use were not recorded for this observation.

---

## Expected Behavior

1. **Grounding and uncertainty.** When the application has no reliable information about a topic, it should say so rather than present uncertain or incorrect details as fact.
2. **Capability transparency.** If a question seems to assume a capability the application does not have (such as live internet lookup), the application should make that limitation clear.
3. **Relevant context use.** Answers should address the current question. Earlier conversation context should be used only when it is relevant, and unrelated earlier topics should not be carried into the answer.

---

## Observed Behavior

| Step | Observation |
|---|---|
| 1 | The evaluator asked the application about *Fallen Aces*, expecting it could find current information. |
| 2 | The application gave answers the evaluator identified as incorrect. |
| 3 | Further attempts produced further incorrect answers ("it keeps assuming wrong"). |
| 4 | Responses repeatedly drew on earlier, unrelated context, including topics from the evaluator's prior coding sessions with ChatGPT, instead of the game being asked about. |

The specific incorrect statements are not reproduced here, because the source transcript is not part of this repository.

---

## Result

| Expectation | Result |
|---|---|
| Admits uncertainty instead of giving incorrect details | **Fail:** incorrect answers were given, repeatedly |
| Makes its capability limits clear | **Not determined:** not recorded |
| Keeps unrelated prior context out of the answer | **Fail:** unrelated earlier context repeatedly appeared in responses |

---

## Evaluation Classification

Classifications use this repository's [failure taxonomy](../qa_artifacts/failure_taxonomy.md).

| Attribute | Value |
|---|---|
| Primary failure type | `unsupported_claim`: gave details about the game that had no reliable basis and were incorrect |
| Secondary observation | Unrelated prior context appeared in responses. **The current taxonomy has no type for this.** `context_loss` covers the opposite problem (context that should have been kept but was dropped). See follow-up FU-5. |
| Severity (per [rubric](../docs/evaluation_rubric.md)) | **Medium.** The answers were wrong and needed the user to notice and correct them. No safety, privacy or data-integrity impact was observed. |

---

## Limitations

- **Single session, not reproduced.** How often this happens, and under what conditions, is unknown.
- **Configuration not recorded.** Without the model, build and context settings, the observation cannot be tied to a specific configuration.
- **Internet access unconfirmed.** Whether the application could reach the internet at the time is not established. The expectations above apply either way.
- **No root cause is claimed.** The context carryover could come from the application's memory or context handling, the model's own behavior, how context was supplied, or something else. This document does not say which.
- **Accuracy judged by the evaluator.** The specific incorrect statements, and the correct information they were compared against, are not recorded here.

---

## Source and Evidence

No transcript or log from this session is included in this repository. Any source material should be kept in the git-ignored `private/` directory unless a reviewed, redacted version is deliberately published later.

---

## Follow-Up Tests That Could Be Designed

These are proposals and have not been run.

| ID | Test idea | What it would measure |
|---|---|---|
| FU-1 | **Reproduce with configuration recorded.** Repeat the question with the build, model and context settings written down. | Whether the behavior reproduces, and under which configuration |
| FU-2 | **Fresh-session control.** Ask the same question in a new session with no retained context. | Whether the incorrect answers depend on carried-over context |
| FU-3 | **Capability disclosure.** Ask a question that needs current information (for example, a game's latest update) and check whether the application says it cannot look it up. | Capability transparency |
| FU-4 | **Unknown-topic handling.** Ask about specific facts the model is unlikely to know reliably and check for an admission of uncertainty. The dataset already covers this pattern in [GR-003](../evals/grounding/) (a made-up paper) and [GR-004](../evals/grounding/) (an unpredictable value). | Grounding and overconfidence |
| FU-5 | **Context-isolation test.** Put an unrelated topic early in a conversation, switch topics, and check that later answers do not bring back the unrelated material. Would need a new failure type (for example, `irrelevant_context_carryover`) added to the taxonomy. | Irrelevant context carried into answers |

FU-4 and FU-5 could be automated with this repository's existing check types. FU-5 would also need the taxonomy change described above.
