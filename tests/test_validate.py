from __future__ import annotations

from pathlib import Path

import yaml

from aiu.validate import (
    iter_yaml,
    load_schema,
    validate_file,
    validate_ids,
    validate_paths,
)

ROOT = Path(__file__).resolve().parents[1]


def test_exemplar_cards_are_valid() -> None:
    schema = load_schema(ROOT)
    for path in sorted((ROOT / "curriculum").rglob("*.yaml")):
        assert validate_file(path, schema) == []


def test_trust_table_is_valid() -> None:
    schema = load_schema(ROOT)
    assert validate_file(ROOT / "learner" / "trust_table.yaml", schema) == []


def test_invalid_card_missing_misconception() -> None:
    schema = load_schema(ROOT)
    errors = validate_file(
        ROOT / "tests" / "fixtures" / "invalid_card_missing_misconception.yaml",
        schema,
    )
    assert any("misconceptions" in error.message for error in errors)


def test_invalid_local_lab_without_fallback() -> None:
    schema = load_schema(ROOT)
    errors = validate_file(
        ROOT / "tests" / "fixtures" / "invalid_lab_local_no_fallback.yaml",
        schema,
    )
    assert any("api_fallback" in error.message for error in errors)


def test_k_card_requires_verify(tmp_path: Path) -> None:
    schema = load_schema(ROOT)
    data = yaml.safe_load((ROOT / "curriculum" / "A" / "A-001.yaml").read_text(encoding="utf-8"))
    data["verify"] = []
    path = tmp_path / "A-001.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    assert validate_file(path, schema) != []


def test_null_experiment_requires_reason(tmp_path: Path) -> None:
    schema = load_schema(ROOT)
    data = yaml.safe_load((ROOT / "curriculum" / "A" / "A-001.yaml").read_text(encoding="utf-8"))
    data["experiment_id"] = None
    data.pop("experiment_null_reason", None)
    path = tmp_path / "A-001.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    assert validate_file(path, schema) != []


def test_filename_id_mismatch_is_detected() -> None:
    path = ROOT / "tests" / "fixtures" / "invalid_card_missing_misconception.yaml"
    errors = validate_ids([path])
    assert any("filename stem" in error.message for error in errors)


def test_default_scope_counts_all_curriculum_files() -> None:
    files, errors = validate_paths(
        ROOT,
        [ROOT / "curriculum", ROOT / "learner"],
    )
    assert len(files) == 89
    assert errors == []
    assert list(iter_yaml([ROOT / "curriculum"]))


def test_checkpoint_answers_are_not_schema_validated() -> None:
    files = list(iter_yaml([ROOT / "learner"]))

    assert all("checkpoints" not in path.parts for path in files)
