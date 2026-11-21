"""Connection test and trial run talk to Claude through the Anthropic SDK, not /chat/completions."""
from backend.services import provider_validation as pv


def test_anthropic_base_detected():
    assert pv._is_anthropic_base("https://api.anthropic.com")
    assert pv._is_anthropic_base("https://api.anthropic.com/v1/")
    assert not pv._is_anthropic_base("https://api.deepseek.com")
    assert not pv._is_anthropic_base("https://api.minimax.io/anthropic")


def test_probe_ok(monkeypatch):
    monkeypatch.setattr(pv, "_anthropic_message", lambda *a, **k: (200, "", "ok", ""))
    assert pv._probe("https://api.anthropic.com", "sk-ant-x", "claude-haiku-5-5") is None


def test_probe_bad_key(monkeypatch):
    body = '{"type":"error","error":{"type":"authentication_error","message":"invalid x-api-key"}}'
    monkeypatch.setattr(pv, "_anthropic_message", lambda *a, **k: (401, body, "", ""))
    error = pv._probe("https://api.anthropic.com", "sk-ant-bad", "claude-haiku-5-5")
    assert error is not None and error.http_status == 401


def test_probe_overloaded_and_network(monkeypatch):
    monkeypatch.setattr(pv, "_anthropic_message", lambda *a, **k: (529, "{}", "", ""))
    assert pv._probe("https://api.anthropic.com", "k", "m").error_type is pv.UpstreamErrorType.UPSTREAM_UNAVAILABLE
    monkeypatch.setattr(pv, "_anthropic_message", lambda *a, **k: (None, "", "", "TimeoutError"))
    assert pv._probe("https://api.anthropic.com", "k", "m") is not None


def test_trial_once(monkeypatch):
    monkeypatch.setattr(pv, "_anthropic_message", lambda *a, **k: (200, "", '{"outline": []}', ""))
    monkeypatch.setattr(pv, "_parse_trial_json", lambda text: text.startswith("{"))
    result = pv._trial_once("https://api.anthropic.com", "k", "claude-haiku-5-5", "prompt")
    assert result["ok_http"] and result["json_ok"] and not result["rate_limited"]
