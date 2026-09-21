"""Model clients: where responses come from.

Everything else in the framework only needs an object with a
`generate(case) -> str` method. That keeps the evaluator independent of any
particular provider, and lets tests run offline with recorded responses.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Protocol

from .models import EvalCase


class ModelClientError(RuntimeError):
    """Raised when a client cannot produce a response for a case."""


class ModelClient(Protocol):
    def generate(self, case: EvalCase) -> str: ...


class ReplayClient:
    """Returns pre-recorded responses keyed by case id. No network access.

    Used for CI, for re-grading saved outputs after changing a check, and for
    the demonstration run in reports/.
    """

    def __init__(self, responses: dict[str, str]):
        self.responses = responses

    def generate(self, case: EvalCase) -> str:
        if case.id not in self.responses:
            raise ModelClientError(f"no recorded response for case '{case.id}'")
        return self.responses[case.id]


def build_messages(case: EvalCase) -> list[dict]:
    """Convert a case into OpenAI-style chat messages.

    Context (e.g. a retrieved document) goes in the *user* turn, clearly
    delimited, rather than in the system prompt. Putting untrusted document
    text in the system prompt would give it more authority than it should
    have, which would distort the prompt-injection cases.
    """
    messages: list[dict] = []
    if case.system:
        messages.append({"role": "system", "content": case.system})
    messages.extend(case.history)

    user_content = case.prompt
    if case.context:
        user_content = f"<context>\n{case.context}\n</context>\n\n{case.prompt}"
    messages.append({"role": "user", "content": user_content})
    return messages


class OpenAICompatibleClient:
    """Calls any OpenAI-compatible /chat/completions endpoint.

    Works with LM Studio (default http://localhost:1234/v1), other local
    servers that implement the same API, or hosted APIs. Uses only the
    standard library so the project has no required runtime dependencies.
    """

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str | None = None,
        temperature: float = 0.0,
        timeout_seconds: float = 120.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        # Read the key from the environment rather than a file in the repo.
        # Local servers like LM Studio typically don't need one.
        self.api_key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY", "")
        # Temperature 0 reduces (but does not eliminate) run-to-run variation.
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds

    def build_payload(self, case: EvalCase) -> dict:
        return {
            "model": self.model,
            "messages": build_messages(case),
            "temperature": self.temperature,
        }

    def generate(self, case: EvalCase) -> str:
        request = urllib.request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(self.build_payload(case)).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ModelClientError(f"request failed for case '{case.id}': {exc}") from exc
        return extract_content(body, case.id)

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


def extract_content(body: object, case_id: str) -> str:
    """Pull the assistant text out of a chat-completions response body."""
    try:
        content = body["choices"][0]["message"]["content"]  # type: ignore[index]
    except (KeyError, IndexError, TypeError) as exc:
        raise ModelClientError(f"unexpected response shape for case '{case_id}'") from exc
    if not isinstance(content, str):
        raise ModelClientError(f"response content for case '{case_id}' is not text")
    return content
