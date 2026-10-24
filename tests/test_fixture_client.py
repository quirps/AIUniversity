from __future__ import annotations

import json
from pathlib import Path

import pytest

from aiu.clients.base import MissingFixture
from aiu.clients.fixture import FixtureClient
from aiu.models import CallResult, Message, PlannedCall


def _planned(call_key: str = "call-1") -> PlannedCall:
    return PlannedCall(
        call_key=call_key,
        item_id="i1",
        condition="base",
        role="cheap_a",
        sample=0,
        messages=[Message(role="user", content="hello")],
        temperature=0.0,
        max_tokens=16,
        seed=None,
    )


def _result(
    call: PlannedCall,
    *,
    source: str = "fixture_synthetic",
    text: str = "stored answer",
    request_sha256: str | None = None,
) -> CallResult:
    return CallResult(
        call_key=call.call_key,
        model_id="fixture/model",
        text=text,
        prompt_tokens=3,
        completion_tokens=2,
        provider_reported_usd=None,
        latency_ms=42,
        source=source,
        request_sha256=request_sha256 or call.request_sha256(),
        timestamp="2026-10-24T00:00:00Z",
    )


def _write(path: Path, records: list[CallResult]) -> None:
    lines = [json.dumps(record.model_dump()) for record in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_fixture_hit_returns_stored_text(tmp_path: Path) -> None:
    call = _planned()
    path = tmp_path / "responses.jsonl"
    _write(path, [_result(call)])

    result = FixtureClient(path).complete(call, "ignored/model")

    assert result.text == "stored answer"
    assert result.latency_ms == 0


def test_fixture_miss_raises(tmp_path: Path) -> None:
    call = _planned("missing")
    path = tmp_path / "responses.jsonl"
    _write(path, [_result(_planned("other"))])

    with pytest.raises(MissingFixture):
        FixtureClient(path).complete(call, "ignored/model")


def test_recorded_fixture_hash_mismatch_raises(tmp_path: Path) -> None:
    call = _planned()
    path = tmp_path / "responses.jsonl"
    _write(
        path,
        [_result(call, source="fixture_recorded", request_sha256="wrong")],
    )

    with pytest.raises(MissingFixture):
        FixtureClient(path).complete(call, "ignored/model")


def test_synthetic_fixture_hash_mismatch_is_allowed(tmp_path: Path) -> None:
    call = _planned()
    path = tmp_path / "responses.jsonl"
    _write(
        path,
        [_result(call, source="fixture_synthetic", request_sha256="wrong")],
    )

    result = FixtureClient(path).complete(call, "ignored/model")

    assert result.text == "stored answer"


def test_duplicate_call_keys_raise(tmp_path: Path) -> None:
    call = _planned()
    path = tmp_path / "responses.jsonl"
    _write(path, [_result(call), _result(call, text="second")])

    with pytest.raises(ValueError):
        FixtureClient(path)
