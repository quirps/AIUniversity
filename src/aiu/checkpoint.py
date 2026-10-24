from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from aiu.config import ConfigError
from aiu.metrics import normalize_answer


def grade(module: dict, answers: dict, now: datetime | None = None) -> dict:
    items = module.get("checkpoint", {}).get("deterministic_items")
    if not isinstance(items, list):
        raise ConfigError("module has no deterministic checkpoint items")

    results: dict[str, dict] = {}
    correct_count = 0

    for item in items:
        item_id = item["id"]
        item_type = item["type"]
        expected = item["answer"]
        given = answers.get(item_id)

        if given is None:
            correct = False
        elif item_type == "mcq":
            correct = isinstance(given, str) and given.strip() == str(expected).strip()
        elif item_type == "exact":
            correct = normalize_answer(str(given)) == normalize_answer(str(expected))
        elif item_type == "numeric":
            try:
                correct = abs(float(given) - float(expected)) <= float(
                    item["tolerance"]
                )
            except (TypeError, ValueError, KeyError):
                correct = False
        else:
            correct = False

        if correct:
            correct_count += 1
        results[item_id] = {
            "correct": correct,
            "given": given,
            "expected": expected,
        }

    moment = now or datetime.now(timezone.utc)
    return {
        "module_id": module.get("id", ""),
        "total": len(items),
        "correct": correct_count,
        "items": results,
        "graded_at": moment.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def load_module(root: Path, module_id: str) -> dict:
    path = root / "curriculum" / "modules" / f"{module_id}.yaml"
    if not path.is_file():
        raise ConfigError(f"missing module: {module_id}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigError(f"invalid module: {module_id}")
    return data


def load_answers(path: Path) -> dict:
    if not path.is_file():
        raise ConfigError(f"missing answers file: {path.as_posix()}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("answers"), dict):
        raise ConfigError("answers file must contain a mapping under 'answers'")
    return data["answers"]


def write_result(root: Path, module_id: str, result: dict) -> Path:
    out_dir = root / "learner" / "checkpoints"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{module_id}.result.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return path
