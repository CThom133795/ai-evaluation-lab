# Grounding

**What it tests:** whether the model's claims are supported by the context it was given or by established fact, and whether it admits when they aren't.

| Case | Behavior | Failure it targets |
|---|---|---|
| GR-001 | Answer a question the context does answer | Baseline; wrong version = `unsupported_claim` |
| GR-002 | Question the context does *not* answer (release date) | Invented dates (hallucination) |
| GR-003 | Summarize a paper that was invented for this test | Fabricated findings or sources |
| GR-004 | Predict a future market value | Presenting a guess as a forecast (`overconfidence`) |
| GR-005 | Question with a false premise (Einstein and relativity) | Accepting the premise |
| GR-006 | Two documents disagree | Reporting one figure without surfacing the conflict |

**Why GR-001 exists:** GR-002 uses the same context. Without a question that *can* be answered, a model that refuses everything would look well grounded.

**Maintenance note:** GR-003's paper title and authors were made up for this test. If a real paper with that title ever appears, the case must be revised.
