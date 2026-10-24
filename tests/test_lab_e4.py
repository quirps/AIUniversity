from __future__ import annotations

import json
from pathlib import Path

import yaml

from aiu.fixtures_synth import synth
from aiu.generators.base import build
from aiu.labs.e4 import ESCAPE_LABELS, IN_TAX_LABELS, parse_label
from aiu.runner import load_items

from helpers import run_fixture

ROOT = Path(__file__).resolve().parents[1]
LAB_ID = "E4"


def _manifest() -> dict:
    return yaml.safe_load(
        (ROOT / "labs" / LAB_ID / "manifest.yaml").read_text(encoding="utf-8")
    )


def _items():
    return load_items(ROOT / "labs" / LAB_ID / "data" / "items.jsonl", None)


def test_dataset_and_fixture_are_current() -> None:
    assert build(ROOT, LAB_ID, True) == 0
    assert synth(ROOT, LAB_ID, True) == 0


def test_label_counts_match_the_spec() -> None:
    items = _items()
    in_tax = [item for item in items if item.expected["in_taxonomy"]]
    oot = [item for item in items if not item.expected["in_taxonomy"]]

    assert len(items) == 80
    assert len(in_tax) == 60
    assert len(oot) == 20
    for label in IN_TAX_LABELS:
        assert sum(1 for item in in_tax if item.expected["label"] == label) == 12
    assert sum(1 for item in oot if item.expected["label"] == "feature_request") == 7
    assert sum(1 for item in oot if item.expected["label"] == "partnership") == 7
    assert sum(1 for item in oot if item.expected["label"] == "press") == 6


def test_escape_labels_parse_only_when_allowed() -> None:
    assert parse_label("other", IN_TAX_LABELS) is None
    assert parse_label("other", ESCAPE_LABELS) == "other"
    assert parse_label(" insufficient_info. ", ESCAPE_LABELS) == "insufficient_info"
    assert parse_label("billing", IN_TAX_LABELS) == "billing"


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
    assert metrics["in_tax_accuracy:no_escape"] >= 0.80
    assert metrics["oot_error_drop"] >= 0.30
    assert metrics["in_tax_cost"] <= 0.05
