from __future__ import annotations

import importlib
import json
import random
from pathlib import Path
from typing import Callable

from aiu.models import Item

SEED = 1337

GENERATORS: dict[str, Callable[[random.Random], list[Item]]] = {}


def register_generator(
    lab_id: str,
) -> Callable[[Callable[[random.Random], list[Item]]], Callable[[random.Random], list[Item]]]:
    def decorator(
        fn: Callable[[random.Random], list[Item]],
    ) -> Callable[[random.Random], list[Item]]:
        GENERATORS[lab_id] = fn
        return fn

    return decorator


def _module_slug(lab_id: str) -> str:
    return lab_id.lower().replace("-", "")


def _load_generator(lab_id: str) -> None:
    try:
        importlib.import_module(f"aiu.generators.{_module_slug(lab_id)}")
    except ImportError:
        pass


def _as_record(item: Item | dict) -> dict:
    if isinstance(item, dict):
        return item
    return item.model_dump()


def serialize(items: list[Item]) -> bytes:
    records = sorted((_as_record(item) for item in items), key=lambda item: item["id"])
    lines = [
        json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        for record in records
    ]
    if not lines:
        return b""
    return ("\n".join(lines) + "\n").encode("utf-8")


def _write_or_check(path: Path, payload: bytes, check: bool) -> int:
    if check:
        if not path.is_file() or path.read_bytes() != payload:
            return 1
        return 0

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return 0


def build(root: Path, lab_id: str, check: bool) -> int:
    generator = GENERATORS.get(lab_id)
    if generator is None:
        _load_generator(lab_id)
        generator = GENERATORS.get(lab_id)
    if generator is None:
        return 6

    items = generator(random.Random(SEED))
    payload = serialize(items)
    target = root / "labs" / lab_id / "data" / "items.jsonl"
    return _write_or_check(target, payload, check)
