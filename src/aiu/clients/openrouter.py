from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Callable

import httpx

from aiu.config import ConfigError
from aiu.models import CallResult, PlannedCall

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
RETRY_STATUS = {408, 429, 500, 502, 503, 504}
MAX_RETRIES = 3


class AuthError(Exception):
    pass


class ProviderError(Exception):
    pass


def api_key_from_env() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        raise ConfigError("OPENROUTER_API_KEY not set")
    return key


class OpenRouterClient:
    def __init__(
        self,
        api_key: str,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
        timeout: float = 60.0,
    ):
        self._api_key = api_key
        self._transport = transport
        self._sleep = sleep
        self._timeout = timeout

    def _body(self, call: PlannedCall, model_id: str) -> dict:
        body: dict = {
            "model": model_id,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in call.messages
            ],
            "temperature": call.temperature,
            "max_tokens": call.max_tokens,
            "usage": {"include": True},
        }
        if call.seed is not None:
            body["seed"] = call.seed
        if call.response_format is not None:
            body["response_format"] = call.response_format
        if call.logprobs:
            body["logprobs"] = True
        return body

    def complete(self, call: PlannedCall, model_id: str) -> CallResult:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "X-Title": "AI University",
        }
        body = self._body(call, model_id)

        with httpx.Client(transport=self._transport, timeout=self._timeout) as client:
            for attempt in range(MAX_RETRIES + 1):
                started = time.perf_counter()
                try:
                    response = client.post(ENDPOINT, headers=headers, json=body)
                except httpx.TransportError:
                    if attempt >= MAX_RETRIES:
                        raise ProviderError("transport error after retries") from None
                    self._sleep(2**attempt)
                    continue
                latency_ms = int((time.perf_counter() - started) * 1000)

                if response.status_code == 200:
                    return self._parse(response, call, model_id, latency_ms)
                if response.status_code == 401:
                    raise AuthError("HTTP 401")
                if response.status_code in RETRY_STATUS and attempt < MAX_RETRIES:
                    self._sleep(2**attempt)
                    continue
                raise ProviderError(f"HTTP {response.status_code}")

        raise ProviderError("retries exhausted")

    def _parse(
        self,
        response: httpx.Response,
        call: PlannedCall,
        model_id: str,
        latency_ms: int,
    ) -> CallResult:
        data = response.json()
        choices = data.get("choices") or []
        content = ""
        if choices:
            content = choices[0].get("message", {}).get("content") or ""

        usage = data.get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
        completion_tokens = int(usage.get("completion_tokens", 0) or 0)
        provider_reported_usd = usage.get("cost")

        return CallResult(
            call_key=call.call_key,
            model_id=model_id,
            text=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            provider_reported_usd=provider_reported_usd,
            latency_ms=latency_ms,
            source="live",
            request_sha256=call.request_sha256(),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
