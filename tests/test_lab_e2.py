from __future__ import annotations

import json
from pathlib import Path

import yaml

from aiu.fixtures_synth import synth
from aiu.generators.base import build
from aiu.generators.e2 import ATTRIBUTES
from aiu.labs.e2 import parse_verdict
from aiu.runner import load_items

from helpers import run_fixture

ROOT = Path(__file__).resolve().parents[1]
LAB_ID = "E2"


def _manifest() -> dict:
    return yaml.safe_load(
        (ROOT / "labs" / LAB_ID / "manifest.yaml").read_text(encoding="utf-8")
    )


def _items():
    return load_items(ROOT / "labs" / LAB_ID / "data" / "items.jsonl", None)


def test_dataset_and_fixture_are_current() -> None:
    assert build(ROOT, LAB_ID, True) == 0
    assert synth(ROOT, LAB_ID, True) == 0


def test_generator_structure_and_single_attribute_changes() -> None:
    items = _items()

    assert len(items) == 80
    assert sum(1 for item in items if item.expected["label"] == "entailed") == 40
    assert sum(1 for item in items if item.expected["label"] == "not_entailed") == 40

    for item in items:
        assert 80 <= len(item.input["passage"].split()) <= 120
        assert item.meta["evidence_sentence"] in item.input["passage"]
        assert item.meta["claim_attr"] in ATTRIBUTES

        if item.expected["label"] == "entailed":
            assert item.meta["changed_attr"] is None
            assert item.meta["claim_value"] == item.meta["passage_value"]
            assert item.meta["claim_value"] in item.input["claim"]
        else:
            assert item.meta["changed_attr"] == item.meta["claim_attr"]
            assert item.meta["claim_value"] != item.meta["passage_value"]
            assert item.meta["claim_value"] in item.input["claim"]
            assert item.meta["passage_value"] not in item.input["claim"]


def test_parser_accepts_leading_prose_and_rejects_bad_verdicts() -> None:
    assert (
        parse_verdict('Here is the result: {"verdict": "entailed", "reasoning": "ok"}')
        == "entailed"
    )
    assert parse_verdict('{"verdict": "maybe"}') is None
    assert parse_verdict("not json") is None
    assert parse_verdict(None) is None


def test_fixture_run_end_to_end(tmp_path: Path, capsys) -> None:
    code, rdir = run_fixture(ROOT, LAB_ID, tmp_path)

    assert code == 0
    assert "status=completed" in capsys.readouterr().out

    result = json.loads((rdir / "result.json").read_text(encoding="utf-8"))
    assert result["status"] == "completed"
    assert result["validity_passed"] is True
    assert result["evidence_class"] == "assumed"
    assert result["n_calls"] == 240

    metrics = json.loads((rdir / "metrics.json").read_text(encoding="utf-8"))["metrics"]
    assert set(metrics) == {metric["name"] for metric in _manifest()["metric"]}
    assert metrics["parse_rate:verdict_first"] >= 0.90
    assert metrics["parse_rate:reasoning_first"] >= 0.90
    assert metrics["parse_rate:evidence_first"] >= 0.90
