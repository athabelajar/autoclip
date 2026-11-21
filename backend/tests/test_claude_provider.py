"""ClaudeProvider: request shape, response mapping, env fallbacks. No network."""
from types import SimpleNamespace

import pytest

from backend.core import llm_providers
from backend.core.llm_providers import ClaudeProvider, LLMProviderFactory, ProviderType


class _FakeStream:
    def __init__(self, message):
        self._message = message

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self._message


def _message(text="ok", stop_reason="end_turn"):
    return SimpleNamespace(
        content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=11, output_tokens=7),
    )


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.delenv("CLAUDE_EFFORT", raising=False)
    p = ClaudeProvider("sk-ant-test-key-123", "claude-haiku-5-5")
    calls = []

    def fake_stream(**request):
        calls.append(request)
        return _FakeStream(_message('[{"a": 1}]'))

    monkeypatch.setattr(p.client.messages, "stream", fake_stream)
    p.calls = calls
    return p


def test_factory_creates_claude():
    p = LLMProviderFactory.create_provider(ProviderType.ANTHROPIC, "sk-ant-x-1234567890", "claude-haiku-5-5")
    assert isinstance(p, ClaudeProvider)


def test_call_maps_request_and_response(provider):
    result = provider.call("PROMPT", {"text": "halo"}, temperature=0.3, max_tokens=500)
    request = provider.calls[0]
    assert request["model"] == "claude-haiku-5-5"
    assert request["max_tokens"] == 500
    assert "temperature" not in request
    assert request["output_config"] == {"effort": "low"}
    assert "PROMPT" in request["messages"][0]["content"] and "halo" in request["messages"][0]["content"]
    assert result.content == '[{"a": 1}]'
    assert result.usage["total_tokens"] == 18
    assert result.finish_reason == "stop"


def test_refusal_raises(provider, monkeypatch):
    monkeypatch.setattr(provider.client.messages, "stream", lambda **r: _FakeStream(_message("", "refusal")))
    with pytest.raises(Exception):
        provider.call("x")


def test_env_fallbacks(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-from-env-123456")
    monkeypatch.setenv("CLAUDE_MODEL", "claude-sonnet-5-5")
    monkeypatch.setenv("CLAUDE_EFFORT", "medium")
    p = ClaudeProvider("", "")
    assert p.api_key == "sk-ant-from-env-123456"
    assert p.model_name == "claude-sonnet-5-5"
    assert llm_providers.claude_effort() == "medium"


def test_models_listed():
    names = [m.name for m in ClaudeProvider("sk-ant-x-1234567890").get_available_models()]
    assert names[0] == "claude-haiku-5-5"
