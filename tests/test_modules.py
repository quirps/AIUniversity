from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import yaml

from aiu.checkpoint import grade
from aiu.traceability import parse_rows
from aiu.validate import load_schema, validate_file

ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = ROOT / "curriculum" / "modules"
EXPECTED_MODULES = {
    "M-A1", "M-A2", "M-B1", "M-B2", "M-B3", "M-C1", "M-C2", "M-C3",
    "M-D1", "M-D2", "M-E1", "M-F1", "M-F2",
}
CARD_RE = re.compile(r"^[A-F]-[0-9]{3}$")


def _modules() -> dict[str, dict]:
    modules = {}
    for path in sorted(MODULE_DIR.glob("M-*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        modules[data["id"]] = data
    return modules


def _traceability_cards() -> set[str]:
    rows = parse_rows((ROOT / "TRACEABILITY.md").read_text(encoding="utf-8"))
    return {row.card for row in rows if CARD_RE.fullmatch(row.card)}


def test_all_modules_exist_and_validate() -> None:
    modules = _modules()
    schema = load_schema(ROOT)

    assert set(modules) == EXPECTED_MODULES
    assert len(modules) == 13
    for path in sorted(MODULE_DIR.glob("M-*.yaml")):
        assert validate_file(path, schema) == []


def test_every_card_appears_in_exactly_one_module() -> None:
    modules = _modules()
    counts = Counter(
        card_id
        for module in modules.values()
        for card_id in module["card_ids"]
    )

    assert set(counts) == _traceability_cards()
    assert all(count == 1 for count in counts.values())


def test_traceability_card_set_is_complete() -> None:
    expected = (
        {f"A-{index:03d}" for index in range(1, 11)}
        | {f"B-{index:03d}" for index in range(1, 15)}
        | {f"C-{index:03d}" for index in range(1, 20)}
        | {f"D-{index:03d}" for index in range(1, 16)}
        | {f"E-{index:03d}" for index in range(1, 8)}
        | {f"F-{index:03d}" for index in range(1, 11)}
    )

    assert _traceability_cards() == expected


def test_every_lab_id_has_a_manifest() -> None:
    for module in _modules().values():
        for lab_id in module["lab_ids"]:
            assert (ROOT / "labs" / lab_id / "manifest.yaml").is_file(), lab_id


def test_module_metadata_and_portfolio_paths() -> None:
    for module_id, module in _modules().items():
        assert module["objective"].startswith("Can ")
        assert module["portfolio_artifact"]["path_pattern"] == (
            f"learner/portfolio/{module_id}/"
        )
        assert len(module["checkpoint"]["deterministic_items"]) >= 3
        assert len(module["checkpoint"]["human_rubric"]) >= 2


def test_m_a1_checkpoint_items_and_answers() -> None:
    module = _modules()["M-A1"]
    items = {
        item["id"]: item for item in module["checkpoint"]["deterministic_items"]
    }

    assert items["Q01"]["type"] == "numeric"
    assert items["Q01"]["answer"] == 0.15
    assert items["Q01"]["tolerance"] == 0.001
    assert items["Q02"]["type"] == "mcq"
    assert items["Q02"]["choices"] == ["Step 1", "Step 2", "Step 5", "Step 7"]
    assert items["Q02"]["answer"] == "Step 2"
    assert items["Q03"]["type"] == "exact"
    assert items["Q03"]["answer"] == "ceiling test"

    answers = yaml.safe_load(
        (ROOT / "tests" / "fixtures" / "M-A1.answers.yaml").read_text(
            encoding="utf-8"
        )
    )["answers"]
    result = grade(module, answers)
    assert result["correct"] == 3
    assert result["total"] == 3
