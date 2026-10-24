from __future__ import annotations

import json
from pathlib import Path

import yaml

from aiu.fixtures_synth import synth
from aiu.generators.base import build
from aiu.generators.e9 import ATTRIBUTES, levenshtein
from aiu.labs.e9 import CONDITION_ORDER, E9
from aiu.runner import estimate_summary, load_items

from helpers import run_fixture

ROOT = Path(__file__).resolve().parents[1]
LAB_ID = "E9"


def _manifest() -> dict:
    return yaml.safe_load(
        (ROOT / "labs" / LAB_ID / "manifest.yaml").read_text(encoding="utf-8")
    )


def _items():
    return load_items(ROOT / "labs" / LAB_ID / "data" / "items.jsonl", None)


def test_dataset_and_fixture_are_current() -> None:
    assert build(ROOT, LAB_ID, True) == 0
    assert synth(ROOT, LAB_ID, True) == 0


def test_generator_structure() -> None:
    items = _items()

    assert len(items) == 60
    assert [item.id for item in items] == [f"e{index:03d}" for index in range(60)]
    assert {item.meta["attribute"] for item in items} == set(ATTRIBUTES)

    for item in items:
        assert set(item.input) == {"question", "key_passage", "distractors"}
        assert len(item.input["distractors"]) == 20
        assert item.expected["answer"] in item.input["key_passage"]

        passages = [item.input["key_passage"], *item.input["distractors"]]
        for passage in passages:
            assert 60 <= len(passage.split()) <= 90

        names = [passage.split(" is ")[0] for passage in item.input["distractors"]]
        assert len(set(names)) == 20
        for name in names:
            assert 0 < levenshtein(item.meta["entity"], name) <= 2


def test_plan_has_300_calls_and_places_key_at_index_10() -> None:
    items = _items()
    manifest = _manifest()
    calls = E9().plan(items, manifest, None)

    assert len(calls) == 300
    assert {call.condition for call in calls} == set(CONDITION_ORDER)
    for condition in CONDITION_ORDER:
        assert sum(1 for call in calls if call.condition == condition) == 60
    assert all(
        call.call_key == f"{call.item_id}|{call.condition}|cheap_a|0"
        for call in calls
    )

    middle = next(call for call in calls if call.condition == "d20_middle")
    lines = [
        line
        for line in middle.messages[1].content.splitlines()
        if line.startswith("[")
    ]
    assert len(lines) == 21
    assert lines[10] == f"[11] {items[0].input['key_passage']}"


def test_fixture_run_end_to_end(tmp_path: Path, capsys) -> None:
    code, rdir = run_fixture(ROOT, LAB_ID, tmp_path)

    assert code == 0
    assert "status=completed" in capsys.readouterr().out

    result = json.loads((rdir / "result.json").read_text(encoding="utf-8"))
    assert result["status"] == "completed"
    assert result["validity_passed"] is True
    assert result["evidence_class"] == "assumed"
    assert result["n_calls"] == 300

    metrics = json.loads((rdir / "metrics.json").read_text(encoding="utf-8"))["metrics"]
    assert set(metrics) == {metric["name"] for metric in _manifest()["metric"]}
    assert metrics["accuracy:oracle"] >= 0.80


def test_estimate_reports_assumed_cost() -> None:
    summary = estimate_summary(ROOT, LAB_ID, None)

    assert summary["calls"] == 300
    assert summary["basis"] == "assumed"
