"""Model clients. No test here makes a network call."""

import pytest

from evaluation_lab.clients import (
    ModelClientError,
    OpenAICompatibleClient,
    ReplayClient,
    build_messages,
    extract_content,
)
from evaluation_lab.dataset import parse_case


def test_replay_client_returns_recorded_response(valid_case_dict):
    case = parse_case(valid_case_dict)
    assert ReplayClient({"T-001": "2019"}).generate(case) == "2019"


def test_replay_client_missing_response_raises(valid_case_dict):
    with pytest.raises(ModelClientError, match="no recorded response"):
        ReplayClient({}).generate(parse_case(valid_case_dict))


def test_messages_put_context_in_user_turn_not_system(valid_case_dict):
    valid_case_dict["system"] = "Be concise."
    messages = build_messages(parse_case(valid_case_dict))

    assert messages[0] == {"role": "system", "content": "Be concise."}
    assert messages[-1]["role"] == "user"
    assert "<context>\nThe product launched in 2019.\n</context>" in messages[-1]["content"]
    assert messages[-1]["content"].endswith("What year was the product launched?")
    assert "2019" not in messages[0]["content"]


def test_messages_preserve_history_order(valid_case_dict):
    valid_case_dict["context"] = ""
    valid_case_dict["history"] = [
        {"role": "user", "content": "Please answer in French."},
        {"role": "assistant", "content": "D'accord."},
    ]
    messages = build_messages(parse_case(valid_case_dict))

    assert [m["role"] for m in messages] == ["user", "assistant", "user"]
    assert messages[-1]["content"] == "What year was the product launched?"


def test_openai_payload_shape(valid_case_dict):
    client = OpenAICompatibleClient(base_url="http://localhost:1234/v1/", model="local-model", api_key="")
    payload = client.build_payload(parse_case(valid_case_dict))

    assert client.base_url == "http://localhost:1234/v1"  # trailing slash removed
    assert payload["model"] == "local-model"
    assert payload["temperature"] == 0.0
    assert payload["messages"][-1]["role"] == "user"


def test_api_key_only_sent_when_present(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert "Authorization" not in OpenAICompatibleClient("http://x", "m")._headers()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    assert OpenAICompatibleClient("http://x", "m")._headers()["Authorization"] == "Bearer test-key"


def test_extract_content_from_valid_body():
    body = {"choices": [{"message": {"role": "assistant", "content": "hi"}}]}
    assert extract_content(body, "T") == "hi"


@pytest.mark.parametrize(
    "body",
    [{}, {"choices": []}, {"choices": [{"message": {}}]}, {"choices": [{"message": {"content": None}}]}, "x"],
)
def test_extract_content_rejects_malformed_bodies(body):
    with pytest.raises(ModelClientError):
        extract_content(body, "T")


def test_unreachable_endpoint_becomes_client_error(valid_case_dict):
    # Port 9 on localhost ("discard") is almost never listening, so this fails
    # fast without leaving the machine.
    client = OpenAICompatibleClient("http://127.0.0.1:9/v1", "m", api_key="", timeout_seconds=2)
    with pytest.raises(ModelClientError, match="request failed"):
        client.generate(parse_case(valid_case_dict))
