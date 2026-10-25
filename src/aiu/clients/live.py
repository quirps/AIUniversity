from __future__ import annotations

import httpx

from aiu.clients.deepseek import DeepSeekClient
from aiu.clients.deepseek import api_key_from_env as deepseek_api_key_from_env
from aiu.clients.openrouter import OpenRouterClient
from aiu.clients.openrouter import api_key_from_env as openrouter_api_key_from_env
from aiu.config import Config, resolve_role
from aiu.models import CallResult, PlannedCall


class LiveClient:
    def __init__(
        self,
        cfg: Config,
        transport: httpx.BaseTransport | None = None,
        openrouter_key: str | None = None,
        deepseek_key: str | None = None,
    ):
        self._cfg = cfg
        self._transport = transport
        self._openrouter_key = openrouter_key
        self._deepseek_key = deepseek_key
        self._clients: dict[str, OpenRouterClient] = {}

    def _client(self, provider: str) -> OpenRouterClient:
        if provider not in self._clients:
            if provider == "deepseek":
                key = self._deepseek_key or deepseek_api_key_from_env()
                self._clients[provider] = DeepSeekClient(key, transport=self._transport)
            else:
                key = self._openrouter_key or openrouter_api_key_from_env()
                self._clients[provider] = OpenRouterClient(key, transport=self._transport)
        return self._clients[provider]

    def complete(self, call: PlannedCall, model_id: str) -> CallResult:
        role = resolve_role(self._cfg, call.role, "live")
        return self._client(role.provider).complete(call, model_id)
