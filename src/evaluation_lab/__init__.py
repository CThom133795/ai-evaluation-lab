"""AI Evaluation Lab: structured, deterministic evaluation of model responses."""

from .clients import OpenAICompatibleClient, ReplayClient
from .dataset import DatasetError, load_cases, load_responses
from .evaluator import evaluate_case
from .runner import run_evaluation, summarize

__all__ = [
    "DatasetError",
    "OpenAICompatibleClient",
    "ReplayClient",
    "evaluate_case",
    "load_cases",
    "load_responses",
    "run_evaluation",
    "summarize",
]
