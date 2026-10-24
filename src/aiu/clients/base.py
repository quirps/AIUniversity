from __future__ import annotations

from typing import Protocol

from aiu.models import CallResult, PlannedCall


class LLMClient(Protocol):
    def complete(self, call: PlannedCall, model_id: str) -> CallResult: ...


class MissingFixture(Exception):
    pass
