from __future__ import annotations

import json

import httpx
import pytest

from aiu.clients.openrouter import (
    ENDPOINT,
    AuthError,
    OpenRouterClient,
    ProviderError,
    api_key_from_env,
)
from aiu.config import ConfigError
from aiu.models import Message, PlannedCall


def _planned(
    *,
    seed: int | None = None,
    response_format: dict | None = None,
    logprobs: bool = False,
) -> PlannedCall:
    return PlannedCall(
        call_key="call-1",
        item_id="i1",
        condition="base",
        role="cheap_a",
        sample=0,
        messages=[Message(role="user", content="hello")],
        temperature=0.0,
        max_tokens=16,
        seed=seed,
        response_format=response_format,
        logprobs=logprobs,
    )


def _ok(text: str = "hello", *, usage: bool = True) -> httpx.Response:
    payload: dict = {"choices": [{"message": {"content": text}}]}
    if usage:
        payload["usage"] = {
            "prompt_tokens": 10,
            "completion_tokens": 2,
            "cost": 0.0001,
        }
    return httpx.Response(200, json=payload)


def test_request_shape_and_headers() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return _ok()

    client = OpenRouterClient(
        "test-key-not-real",
        transport=httpx.MockTransport(handler),
    )
    result = client.complete(
        _planned(seed=7, response_format={"type": "json_object"}, logprobs=True),
        "provider/model",
    )

    request = captured["request"]
    assert str(request.url) == ENDPOINT
    assert request.headers["authorization"] == "Bearer test-key-not-real"
    assert request.headers["x-title"] == "AI University"

    body = json.loads(request.content)
    assert body["model"] == "provider/model"
    assert body["messages"] == [{"role": "user", "content": "hello"}]
    assert body["temperature"] == 0.0
    assert body["max_tokens"] == 16
    assert body["seed"] == 7
    assert body["response_format"] == {"type": "json_object"}
    assert body["logprobs"] is True
    assert body["usage"] == {"include": True}

    assert result.text == "hello"
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 2
    assert result.provider_reported_usd == 0.0001
    assert result.source == "live"


def test_retries_429_twice_then_succeeds() -> None:
    attempts: list[int] = []
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts.append(1)
        if len(attempts) < 3:
            return httpx.Response(429)
        return _ok("after retries")

    client = OpenRouterClient(
        "test-key-not-real",
        transport=httpx.MockTransport(handler),
        sleep=sleeps.append,
    )
    result = client.complete(_planned(), "provider/model")

    assert result.text == "after retries"
    assert sleeps == [1, 2]
    assert len(attempts) == 3


def test_four_503s_raise_after_retries() -> None:
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    client = OpenRouterClient(
        "test-key-not-real",
        transport=httpx.MockTransport(handler),
        sleep=sleeps.append,
    )
    with pytest.raises(ProviderError):
        client.complete(_planned(), "provider/model")

    assert sleeps == [1, 2, 4]


def test_401_raises_without_retry() -> None:
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401)

    client = OpenRouterClient(
        "test-key-not-real",
        transport=httpx.MockTransport(handler),
        sleep=sleeps.append,
    )
    with pytest.raises(AuthError):
        client.complete(_planned(), "provider/model")

    assert sleeps == []


def test_400_raises_without_retry() -> None:
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400)

    client = OpenRouterClient(
        "test-key-not-real",
        transport=httpx.MockTransport(handler),
        sleep=sleeps.append,
    )
    with pytest.raises(ProviderError):
        client.complete(_planned(), "provider/model")

    assert sleeps == []


def test_missing_usage_gives_zero_tokens() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return _ok("no usage", usage=False)

    client = OpenRouterClient(
        "test-key-not-real",
        transport=httpx.MockTransport(handler),
    )
    result = client.complete(_planned(), "provider/model")

    assert result.prompt_tokens == 0
    assert result.completion_tokens == 0
    assert result.provider_reported_usd is None


def test_exceptions_do_not_contain_the_key() -> None:
    key = "test-key-not-real"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401)

    client = OpenRouterClient(key, transport=httpx.MockTransport(handler))
    with pytest.raises(AuthError) as auth_error:
        client.complete(_planned(), "provider/model")
    assert key not in str(auth_error.value)
    assert key not in repr(auth_error.value)

    def error_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    client = OpenRouterClient(key, transport=httpx.MockTransport(error_handler))
    with pytest.raises(ProviderError) as provider_error:
        client.complete(_planned(), "provider/model")
    assert key not in str(provider_error.value)
    assert key not in repr(provider_error.value)


def test_api_key_from_env_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        api_key_from_env()


def test_api_key_from_env_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    assert api_key_from_env() == "test-key"
