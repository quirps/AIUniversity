from __future__ import annotations

import os

from aiu.clients.openrouter import OpenRouterClient
from aiu.config import ConfigError
from aiu.models import PlannedCall

DEEPSEEK_ENDPOINT = "https://api.deepseek.com/chat/completions"


def api_key_from_env() -> str:
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise ConfigError("DEEPSEEK_API_KEY not set")
    return key


class DeepSeekClient(OpenRouterClient):
    def __init__(self, api_key: str, **kwargs):
        kwargs.setdefault("endpoint", DEEPSEEK_ENDPOINT)
        kwargs.setdefault("include_usage", False)
        super().__init__(api_key, **kwargs)

    def _body(self, call: PlannedCall, model_id: str) -> dict:
        body = super()._body(call, model_id)
        body["thinking"] = {"type": "disabled"}
        return body
