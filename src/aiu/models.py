from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class PlannedCall(BaseModel):
    call_key: str
    item_id: str
    condition: str
    role: str
    sample: int
    messages: list[Message]
    temperature: float
    max_tokens: int
    seed: int | None
    response_format: dict | None = None
    logprobs: bool = False

    def request_sha256(self) -> str:
        payload = self.model_dump(exclude={"call_key"})
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class CallResult(BaseModel):
    call_key: str
    model_id: str
    text: str
    prompt_tokens: int
    completion_tokens: int
    provider_reported_usd: float | None
    latency_ms: int
    source: Literal["fixture_synthetic", "fixture_recorded", "live"]
    request_sha256: str
    timestamp: str
    logprobs: list | None = None


class Item(BaseModel):
    id: str
    input: dict
    expected: dict
    meta: dict
