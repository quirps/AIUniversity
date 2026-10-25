from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from aiu.clients.deepseek import DEEPSEEK_ENDPOINT, DeepSeekClient
from aiu.clients.deepseek import api_key_from_env as deepseek_api_key_from_env
from aiu.clients.live import LiveClient
from aiu.clients.openrouter import ENDPOINT
from aiu.config import ConfigError, load_config
from aiu.models import Message, PlannedCall

ROOT = Path(__file__).resolve().parents[1]


def _planned(role: str = "cheap_a") -> PlannedCall:
    return PlannedCall(
        call_key="call-1",
        item_id="i1",
        condition="base",
        role=role,
        sample=0,
        messages=[Message(role="user", content="hello")],
        temperature=0.0,
        max_tokens=16,
        seed=7,
    )


def _ok() -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "choices": [{"message": {"content": "hello"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 2},
        },
    )


def test_deepseek_request_shape() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return _ok()

    client = DeepSeekClient("test-key-not-real", transport=httpx.MockTransport(handler))
    result = client.complete(_planned(), "deepseek-flash")

    request = captured["request"]
    assert str(request.url) == DEEPSEEK_ENDPOINT
    assert request.headers["authorization"] == "Bearer test-key-not-real"
    body = json.loads(request.content)
    assert body["model"] == "deepseek-flash"
    assert body["seed"] == 7
    assert body["thinking"] == {"type": "disabled"}
    assert "usage" not in body
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 2
    assert result.provider_reported_usd is None


def test_deepseek_api_key_from_env_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        deepseek_api_key_from_env()


def test_live_client_routes_by_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        return _ok()

    client = LiveClient(
        load_config(ROOT),
        transport=httpx.MockTransport(handler),
    )
    client.complete(_planned("cheap_a"), "deepseek-flash")
    client.complete(_planned("cheap_b"), "google/gemini-2.5-flash")

    assert seen == [DEEPSEEK_ENDPOINT, ENDPOINT]
