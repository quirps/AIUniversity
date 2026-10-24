from __future__ import annotations

import importlib
import json
import math
import random
from pathlib import Path
from typing import Callable

from aiu.config import load_config
from aiu.generators.base import SEED, _module_slug, _write_or_check
from aiu.labs.base import REGISTRY
from aiu.models import CallResult, Item, PlannedCall
from aiu.runner import load_items, load_manifest

SYNTH: dict[
    str,
    Callable[[list[Item], list[PlannedCall], random.Random], list[CallResult]],
] = {}


def register_synth(
    lab_id: str,
) -> Callable[
    [Callable[[list[Item], list[PlannedCall], random.Random], list[CallResult]]],
    Callable[[list[Item], list[PlannedCall], random.Random], list[CallResult]],
]:
    def decorator(
        fn: Callable[[list[Item], list[PlannedCall], random.Random], list[CallResult]],
    ) -> Callable[[list[Item], list[PlannedCall], random.Random], list[CallResult]]:
        SYNTH[lab_id] = fn
        return fn

    return decorator


def _load_lab_modules(lab_id: str) -> None:
    for module in (
        f"aiu.generators.{_module_slug(lab_id)}",
        f"aiu.labs.{_module_slug(lab_id)}",
    ):
        try:
            importlib.import_module(module)
        except ImportError:
            pass


def _prompt_bytes(call: PlannedCall) -> int:
    return sum(len(message.content.encode("utf-8")) for message in call.messages)


def _normalize(
    calls: list[PlannedCall],
    results: list[CallResult],
) -> list[CallResult]:
    by_key = {result.call_key: result for result in results}
    normalized: list[CallResult] = []
    for call in calls:
        result = by_key.get(call.call_key)
        if result is None:
            raise ValueError(f"missing synthetic result for {call.call_key}")
        normalized.append(
            result.model_copy(
                update={
                    "model_id": "fixture",
                    "prompt_tokens": math.ceil(_prompt_bytes(call) / 3),
                    "completion_tokens": len(result.text) // 4 + 1,
                    "provider_reported_usd": None,
                    "latency_ms": 0,
                    "source": "fixture_synthetic",
                    "request_sha256": call.request_sha256(),
                    "timestamp": "1970-01-01T00:00:00Z",
                    "logprobs": None,
                }
            )
        )
    return normalized


def _serialize_results(results: list[CallResult]) -> bytes:
    lines = [
        json.dumps(
            result.model_dump(mode="json"),
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        for result in results
    ]
    if not lines:
        return b""
    return ("\n".join(lines) + "\n").encode("utf-8")


def _fixture_path(manifest: dict, lab_id: str) -> Path:
    fixtures = manifest.get("fixtures")
    if isinstance(fixtures, dict) and isinstance(fixtures.get("path"), str):
        return Path(fixtures["path"])
    return Path("labs") / lab_id / "fixtures" / "responses.jsonl"


def synth(root: Path, lab_id: str, check: bool) -> int:
    if lab_id not in SYNTH:
        _load_lab_modules(lab_id)
    generator = SYNTH.get(lab_id)
    if generator is None:
        return 6

    impl_cls = REGISTRY.get(lab_id)
    if impl_cls is None:
        _load_lab_modules(lab_id)
        impl_cls = REGISTRY.get(lab_id)
    if impl_cls is None:
        return 6

    manifest = load_manifest(root, lab_id)
    cfg = load_config(root)
    items = load_items(root / manifest["dataset"]["path"], None)
    calls = impl_cls().plan(items, manifest, cfg)

    results = generator(items, calls, random.Random(SEED))
    payload = _serialize_results(_normalize(calls, results))
    target = root / _fixture_path(manifest, lab_id)
    return _write_or_check(target, payload, check)
