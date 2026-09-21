# Case Study: Unverified Answers, Capability Statements and Context Carryover in a Game Companion

| Field | Value |
|---|---|
| Case ID | CS-002 |
| Date observed | 2026-09-20 to 2026-09-21 (from application log timestamps) |
| Evaluator | Repository author (direct observation, plus review of the application's own logs) |
| System under evaluation | Project Pulse, the author's own local-first AI gaming companion under development ([CThom133795/gaming-content-pipeline](https://github.com/CThom133795/gaming-content-pipeline)) |
| Configured language model | `qwen3-vl-8b-instruct`, served locally through an OpenAI-compatible endpoint (from the application's saved settings; see [Limitations](#limitations)) |
| Web lookup setting | Enabled (`game_web_search_enabled = true`, which is also the default) |
| Interaction type | Multi-turn voice conversation |
| Evaluation type | Exploratory testing, with log review |
| Primary themes | Grounding, unsupported claims, uncertainty handling |
| Secondary themes | Accuracy of capability statements, relevance of retained context |
| Source material | Application logs, kept locally and not included in this repository |

---

## Summary

While playing *Fallen Aces*, an independently developed video game, the evaluator asked the companion about the game. Its answers were incorrect across several turns. When the evaluator corrected it and asked it to research online, it said it did not have internet access, even though the application has a web lookup feature that was enabled. Its answers also kept drawing on earlier, unrelated conversation context, including coding-related topics, instead of addressing the game.

The application's logs record lookup attempts that returned no reliable result, followed by answers marked as unverified. This document records the behavior as an **evaluation case**. It does not claim to know why the application answered this way. See [Limitations](#limitations).

---

## Environment and Context

- **Application:** Project Pulse, a Windows application combining speech recognition, a local language model, text-to-speech, game detection, per-game memory and optional web lookup.
- **Web lookup:** The application includes a lookup feature (Wikipedia and a web search engine) for game questions, controlled by a setting that was enabled. The application decides per turn whether to use it.
- **Memory:** The application keeps its own per-game memory. It does **not** share a memory file with ChatGPT or any other assistant. How coding-related topics came to appear in its answers is not established here.
- **Game detection:** The application identified the running game as *Fallen Aces* with high confidence.

---

## Expected Behavior

1. **Grounding and uncertainty.** When no reliable information is available, the companion should say so rather than present unverified details as fact, especially after a lookup has failed.
2. **Accurate capability statements.** Statements about its own abilities, such as internet access, should match how the application is actually configured.
3. **Relevant context use.** Answers should address the current question. Earlier context should be used only when it is relevant.

---

## Observed Behavior

| Step | Observation | Source |
|---|---|---|
| 1 | The evaluator asked about *Fallen Aces*. The companion gave answers the evaluator identified as incorrect. | Evaluator |
| 2 | These turns were answered without any knowledge lookup. | Log: `route=chat`, `knowledge_action=pass` |
| 3 | The evaluator corrected a factual error (the game's publisher) and asked the companion to check its reasoning. | Log: speech transcript |
| 4 | A background research task was queued because no reliable search result was found. The next answer was marked unverified. The research task later finished with no result. | Log: `research_queued`, `knowledge_action=unverified`, `research_completed outcome=no result` |
| 5 | In a later exchange, the evaluator said the answer was wrong again and explicitly asked the companion to use the internet and stop relying on past conversation context. | Log: speech transcript |
| 6 | The companion said it did not have internet access. | Evaluator (response text is not logged) |
| 7 | For that turn, a research task was again queued with no reliable result, and the answer was marked unverified. The turn record shows five stored memory items were retrieved. | Log: `research_queued`, `knowledge_action=unverified`, `memories=5` |
| 8 | Across the session, answers repeatedly drew on earlier unrelated context, including coding-related topics. | Evaluator |

---

## Result

| Expectation | Result |
|---|---|
| Admits uncertainty instead of giving incorrect details | **Fail:** incorrect answers were given repeatedly, including after lookups found no reliable result |
| Capability statements match configuration | **Inconsistent:** the companion said it had no internet access, while web lookup was enabled and lookups were attempted |
| Keeps unrelated prior context out of answers | **Fail:** unrelated earlier context repeatedly appeared in answers |

---

## Evaluation Classification

Classifications use this repository's [failure taxonomy](../qa_artifacts/failure_taxonomy.md).

| Attribute | Value |
|---|---|
| Primary failure type | `unsupported_claim`: gave details about the game that had no reliable basis, as the application's own `unverified` marking shows |
| Secondary: capability statement | Also `unsupported_claim`: a statement about its own capabilities that did not match its configuration |
| Secondary: context carryover | **Not covered by the current taxonomy.** `context_loss` covers the opposite problem (context that should have been kept but was dropped). See follow-up FU-5. |
| Severity (per [rubric](../docs/evaluation_rubric.md)) | **Medium.** The answers were wrong and needed repeated user correction. No safety, privacy or data-integrity impact was observed. |

---

## Limitations

- **Response text is not logged.** The logs record the user's transcribed speech and per-turn metadata, but not the companion's replies. The incorrect answers and the "no internet access" statement come from the evaluator's observation.
- **Model loaded at the time is inferred.** The model name comes from the saved settings, read after the session. The model actually loaded in the local model server was not logged.
- **Build not pinned.** The exact application build running at the time was not recorded, and the source repository had changes in progress.
- **Not reproduced.** How often this happens, and under what conditions, is unknown.
- **No root cause is claimed.** The logs show what the application recorded, not why the model answered as it did. The context carryover could involve retrieved memory items, the model's behavior, how context is assembled, or something else. This document does not say which. The contents of the retrieved memory items were not examined.
- **Accuracy judged by the evaluator.** The specific incorrect statements are not recorded here.

---

## Source and Evidence

The application's logs remain on the evaluator's machine and are **not** included in this repository, because they contain transcribed personal speech. This document summarizes only event names and fields. A redacted log excerpt could be added later if deliberately reviewed.

---

## Follow-Up Tests That Could Be Designed

These are proposals and have not been run.

| ID | Test idea | What it would measure |
|---|---|---|
| FU-1 | **Reproduce with configuration pinned.** Repeat the question with the build, loaded model and settings recorded. | Whether the behavior reproduces, and under which configuration |
| FU-2 | **Fresh-memory control.** Ask the same questions with the game's stored memory cleared. | Whether the incorrect answers and carryover depend on retrieved memory |
| FU-3 | **Capability statement check.** With web lookup enabled, ask "Can you look things up online?" and compare the answer with the configuration. Repeat with lookup disabled. | Whether capability statements match configuration |
| FU-4 | **Failed-lookup handling.** Ask a question whose lookup returns no result and check that the reply says it could not verify the answer. Related dataset cases: [GR-003 and GR-004](../evals/grounding/). | Grounding after a failed lookup |
| FU-5 | **Context-isolation test.** Put an unrelated topic early in a conversation, switch topics, and check that later answers do not bring back the unrelated material. Would need a new failure type (for example, `irrelevant_context_carryover`) in the taxonomy. | Irrelevant context carried into answers |
| FU-6 | **Inspect retrieved memory.** For a turn showing carryover, record which memory items were retrieved and whether they relate to the question. | Whether memory retrieval supplies irrelevant context |

Supporting this kind of evaluation in the future would also mean logging the companion's reply text per turn, so answers could be checked afterwards rather than only from memory.
