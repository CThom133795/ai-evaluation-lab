"""Core data types for evaluation cases and results.

These are plain dataclasses on purpose: they are easy to read, easy to
construct in tests, and serialize cleanly to JSON with `dataclasses.asdict`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Allowed values are kept as simple tuples so they can be shown in error
# messages and documentation without extra machinery.
CATEGORIES = (
    "instruction_following",
    "reasoning",
    "grounding",
    "tool_use",
    "adversarial",
)

SEVERITIES = ("critical", "high", "medium", "low")

# Failure classifications. Each check in a case declares which of these it
# represents when it fails. See qa_artifacts/failure_taxonomy.md.
FAILURE_TYPES = (
    "instruction_violation",
    "format_violation",
    "missing_clarification",
    "unsupported_claim",
    "factual_error",
    "overconfidence",
    "reasoning_error",
    "incorrect_tool_decision",
    "injection_compliance",
    "unsafe_compliance",
    "context_loss",
)

# Result statuses. "error" is distinct from "fail": it means the case could
# not be evaluated (e.g. no response was available), not that the model
# behaved badly. Mixing the two would inflate failure counts.
STATUS_PASS = "pass"
STATUS_FAIL = "fail"
STATUS_ERROR = "error"


@dataclass
class Check:
    """One deterministic rule applied to a model response."""

    type: str
    failure_type: str
    description: str
    # Parameters differ by check type (value, values, pattern, limit, field...),
    # so they are stored as a dict rather than a fixed set of attributes.
    params: dict = field(default_factory=dict)


@dataclass
class EvalCase:
    """A single evaluation case loaded from the dataset."""

    id: str
    category: str
    prompt: str
    expected_behavior: str
    failure_conditions: list[str]
    severity: str
    checks: list[Check]
    context: str = ""
    system: str = ""
    # Prior conversation turns for multi-turn cases:
    # [{"role": "user" | "assistant", "content": "..."}]
    history: list[dict] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class CheckResult:
    """Outcome of applying one Check to one response."""

    description: str
    passed: bool
    failure_type: str
    detail: str = ""


@dataclass
class EvalResult:
    """Structured outcome for one case."""

    test_id: str
    category: str
    status: str  # STATUS_PASS, STATUS_FAIL or STATUS_ERROR
    severity: str
    # Primary classification = failure type of the first failed check.
    # All distinct failure types are kept too, since one response can fail
    # in more than one way.
    failure_classification: str | None
    all_failure_types: list[str]
    notes: list[str]
    response: str = ""

    @property
    def passed(self) -> bool:
        return self.status == STATUS_PASS
