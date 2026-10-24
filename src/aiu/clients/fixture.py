from __future__ import annotations

import json
from pathlib import Path

from aiu.clients.base import MissingFixture
from aiu.models import CallResult, PlannedCall


class FixtureClient:
    def __init__(self, path: Path):
        self.path = path
        self._records: dict[str, CallResult] = {}

        if not path.is_file():
            return

        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = CallResult.model_validate(json.loads(line))
            if record.call_key in self._records:
                raise ValueError(f"duplicate fixture call_key: {record.call_key}")
            self._records[record.call_key] = record

    def complete(self, call: PlannedCall, model_id: str) -> CallResult:
        record = self._records.get(call.call_key)
        if record is None:
            raise MissingFixture(call.call_key)

        if (
            record.source == "fixture_recorded"
            and record.request_sha256 != call.request_sha256()
        ):
            raise MissingFixture(
                f"recorded fixture request hash mismatch for {call.call_key}"
            )

        return record.model_copy(update={"latency_ms": 0})
