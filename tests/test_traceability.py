from __future__ import annotations

from pathlib import Path

import yaml

from aiu.cli import main
from aiu.traceability import check, parse_rows

HEADER = "| Src | Concept | Card | Experiment | Tag | Status |\n|---|---|---|---|---|---|\n"


def _row(
    src: str,
    card: str,
    experiment: str,
    *,
    concept: str = "Concept",
    tag: str = "K",
    status: str = "in scope",
) -> str:
    return f"| {src} | {concept} | {card} | {experiment} | {tag} | {status} |\n"


def _write_trace(root: Path, rows: list[str]) -> None:
    (root / "TRACEABILITY.md").write_text(HEADER + "".join(rows), encoding="utf-8")


def _write_card(
    root: Path,
    card_id: str = "A-001",
    source_section: str = "§1.1",
    experiment_id: str | None = "E9",
) -> None:
    level_dir = root / "curriculum" / card_id[0]
    level_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "kind": "card",
        "id": card_id,
        "source_section": source_section,
        "experiment_id": experiment_id,
    }
    (level_dir / f"{card_id}.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )


def _write_manifest(root: Path, lab_id: str = "E9") -> None:
    path = root / "labs" / lab_id / "manifest.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("kind: lab\n", encoding="utf-8")


def test_matching_card_and_row_is_ok(tmp_path: Path) -> None:
    _write_trace(tmp_path, [_row("§1.1", "A-001", "E9")])
    _write_card(tmp_path)
    _write_manifest(tmp_path)

    assert check(tmp_path, False) == []


def test_source_section_mismatch_is_a_problem(tmp_path: Path) -> None:
    _write_trace(tmp_path, [_row("§1.1", "A-001", "E9")])
    _write_card(tmp_path, source_section="§1.2")
    _write_manifest(tmp_path)

    problems = check(tmp_path, False)
    assert any("source_section" in problem for problem in problems)


def test_experiment_null_mismatch_is_a_problem(tmp_path: Path) -> None:
    _write_trace(tmp_path, [_row("§1.1", "A-001", "E9")])
    _write_card(tmp_path, experiment_id=None)
    _write_manifest(tmp_path)

    problems = check(tmp_path, False)
    assert any("experiment_id" in problem for problem in problems)


def test_card_absent_from_table_is_a_problem(tmp_path: Path) -> None:
    _write_trace(tmp_path, [])
    _write_card(tmp_path)

    problems = check(tmp_path, False)
    assert any("appears in 0" in problem for problem in problems)


def test_referenced_experiment_needs_a_manifest(tmp_path: Path) -> None:
    _write_trace(tmp_path, [_row("§1.1", "A-001", "E9")])
    _write_card(tmp_path)

    problems = check(tmp_path, False)
    assert any("has no manifest" in problem for problem in problems)


def test_require_all_cards(tmp_path: Path) -> None:
    _write_trace(tmp_path, [_row("§1.2", "A-002", "—")])

    assert check(tmp_path, False) == []
    problems = check(tmp_path, True)
    assert any("A-002 has no file" in problem for problem in problems)


def test_parse_rows_accepts_none_source() -> None:
    rows = parse_rows(HEADER + _row("none", "C-019", "L-003"))

    assert len(rows) == 1
    assert rows[0].src == "none"
    assert rows[0].card == "C-019"


def test_cli_check(tmp_path: Path, monkeypatch, capsys) -> None:
    _write_trace(tmp_path, [_row("§1.1", "A-001", "E9")])
    _write_card(tmp_path)
    _write_manifest(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(["traceability", "check"]) == 0
    assert "traceability: OK (1 rows, 1 cards)" in capsys.readouterr().out


def test_cli_require_all_fails_before_all_cards_exist(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    _write_trace(tmp_path, [_row("§1.2", "A-002", "—")])
    monkeypatch.chdir(tmp_path)

    assert main(["traceability", "check", "--require-all"]) == 1
    assert "A-002 has no file" in capsys.readouterr().out
