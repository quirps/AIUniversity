from __future__ import annotations

import json
from pathlib import Path

import yaml

from aiu.fixtures_synth import synth
from aiu.generators.base import build
from aiu.labs.e5 import E5, parse_choice
from aiu.models import CallResult
from aiu.runner import load_items

from helpers import run_fixture

ROOT = Path(__file__).resolve().parents[1]
LAB_ID = "E5"


def _manifest() -> dict:
    return yaml.safe_load(
        (ROOT / "labs" / LAB_ID / "manifest.yaml").read_text(encoding="utf-8")
    )


def _items():
    return load_items(ROOT / "labs" / LAB_ID / "data" / "items.jsonl", None)


def _result(call_key: str, text: str) -> CallResult:
    return CallResult(
        call_key=call_key,
        model_id="fixture",
        text=text,
        prompt_tokens=0,
        completion_tokens=0,
        provider_reported_usd=None,
        latency_ms=0,
        source="fixture_synthetic",
        request_sha256="",
        timestamp="1970-01-01T00:00:00Z",
    )


def test_dataset_and_fixture_are_current() -> None:
    assert build(ROOT, LAB_ID, True) == 0
    assert synth(ROOT, LAB_ID, True) == 0


def test_generator_structure() -> None:
    items = _items()

    assert len(items) == 40
    assert [item.id for item in items] == [f"e5{index:03d}" for index in range(40)]
    for item in items:
        assert set(item.input) == {"question", "correct", "wrong", "padding"}
        assert item.expected == {"better": "correct"}
        assert item.input["correct"] != item.input["wrong"]
        assert 2 <= item.input["padding"].count(".") <= 3


def test_parser_uses_first_non_space_character() -> None:
    assert parse_choice(" A") == "A"
    assert parse_choice("  b\n") == "B"
    assert parse_choice("Answer: B") == "A"
    assert parse_choice("maybe") is None
    assert parse_choice("") is None
    assert parse_choice(None) is None


def test_hand_built_flip_and_first_slot() -> None:
    item = _items()[0]
    results = [
        _result(f"{item.id}|cw_plain|judge_a|0", "A"),
        _result(f"{item.id}|wc_plain|judge_a|0", "B"),
    ]

    metrics = E5().score([item], results, _manifest())

    assert metrics["flip_rate"] == 0.0
    assert metrics["first_slot_rate"] == 0.5


def test_fixture_run_end_to_end(tmp_path: Path, capsys) -> None:
    code, rdir = run_fixture(ROOT, LAB_ID, tmp_path)

    assert code == 0
    assert "status=completed" in capsys.readouterr().out

    result = json.loads((rdir / "result.json").read_text(encoding="utf-8"))
    assert result["status"] == "completed"
    assert result["validity_passed"] is True
    assert result["evidence_class"] == "assumed"
    assert result["n_calls"] == 160

    metrics = json.loads((rdir / "metrics.json").read_text(encoding="utf-8"))["metrics"]
    assert set(metrics) == {metric["name"] for metric in _manifest()["metric"]}
    assert metrics["parse_rate"] == 1.0
