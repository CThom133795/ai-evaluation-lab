"""Turn a (case, response) pair into a structured EvalResult."""

from __future__ import annotations

from .checks import CHECK_FUNCTIONS
from .models import STATUS_ERROR, STATUS_FAIL, STATUS_PASS, CheckResult, EvalCase, EvalResult


def run_checks(case: EvalCase, response: str) -> list[CheckResult]:
    """Apply every check in the case to the response, in dataset order."""
    results = []
    for check in case.checks:
        check_function = CHECK_FUNCTIONS[check.type]
        passed, detail = check_function(response, check.params)
        results.append(
            CheckResult(
                description=check.description,
                passed=passed,
                failure_type=check.failure_type,
                detail=detail,
            )
        )
    return results


def evaluate_case(case: EvalCase, response: str) -> EvalResult:
    """Evaluate one response. A case passes only if every check passes."""
    check_results = run_checks(case, response)
    failed = [c for c in check_results if not c.passed]

    if not failed:
        return EvalResult(
            test_id=case.id,
            category=case.category,
            status=STATUS_PASS,
            severity=case.severity,
            failure_classification=None,
            all_failure_types=[],
            notes=[],
            response=response,
        )

    # Order matters: case authors list the most important check first, so
    # the first failure becomes the primary classification.
    all_types = list(dict.fromkeys(c.failure_type for c in failed))  # de-dupe, keep order
    notes = [f"{c.description}: {c.detail}" for c in failed]

    return EvalResult(
        test_id=case.id,
        category=case.category,
        status=STATUS_FAIL,
        severity=case.severity,
        failure_classification=all_types[0],
        all_failure_types=all_types,
        notes=notes,
        response=response,
    )


def error_result(case: EvalCase, reason: str) -> EvalResult:
    """Result for a case that could not be evaluated at all."""
    return EvalResult(
        test_id=case.id,
        category=case.category,
        status=STATUS_ERROR,
        severity=case.severity,
        failure_classification=None,
        all_failure_types=[],
        notes=[reason],
    )
