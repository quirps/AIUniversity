from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from aiu.cli import main
from aiu.provenance import check, parse_ledger

HEADER = (
    "| ID | Claim | Tag | Status | Source | Date | Method | Cards |\n"
    "|---|---|---|---|---|---|---|---|\n"
)


def _row(
    claim_id: str,
    *,
    claim: str = "Claim text",
    tag: str = "K",
    status: str = "unverified",
    source: str = "source",
    date: str = "TBD",
    method: str = "-",
    cards: str = "-",
) -> str:
    return (
        f"| {claim_id} | {claim} | {tag} | {status} | {source} | {date} | "
        f"{method} | {cards} |\n"
    )


def _write_ledger(root: Path, rows: list[str]) -> None:
    (root / "PROVENANCE.md").write_text(HEADER + "".join(rows), encoding="utf-8")


def _write_card(
    root: Path,
    card_id: str = "A-001",
    claim_id: str = "P-001",
    status: str = "unverified",
    level: str = "A",
) -> None:
    level_dir = root / "curriculum" / level
    level_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "kind": "card",
        "id": card_id,
        "verify": [
            {
                "claim_id": claim_id,
                "claim": "Claim text",
                "status": status,
                "source": None,
                "date": None,
                "method": "test",
            }
        ],
    }
    (level_dir / f"{card_id}.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )


def test_matching_ledger_and_card_is_ok(tmp_path: Path) -> None:
    _write_ledger(tmp_path, [_row("P-001", cards="A-001")])
    _write_card(tmp_path)

    assert check(tmp_path) == []


def test_missing_claim_is_a_problem(tmp_path: Path) -> None:
    _write_ledger(tmp_path, [_row("P-001")])
    _write_card(tmp_path, claim_id="P-999")

    problems = check(tmp_path)
    assert any("missing claim P-999" in problem for problem in problems)


def test_status_mismatch_is_a_problem(tmp_path: Path) -> None:
    _write_ledger(tmp_path, [_row("P-001", cards="A-001")])
    _write_card(tmp_path, status="verified")

    problems = check(tmp_path)
    assert any("disagrees with ledger" in problem for problem in problems)


def test_verified_row_requires_source(tmp_path: Path) -> None:
    _write_ledger(
        tmp_path,
        [
            _row(
                "P-001",
                status="verified",
                source="-",
                date="2026-01-01",
                method="read the source",
            )
        ],
    )

    problems = check(tmp_path)
    assert any("empty source" in problem for problem in problems)


def test_verified_row_requires_valid_date_and_method(tmp_path: Path) -> None:
    _write_ledger(
        tmp_path,
        [_row("P-001", status="verified", date="TBD", method="-")],
    )

    problems = check(tmp_path)
    assert any("YYYY-MM-DD" in problem for problem in problems)
    assert any("empty method" in problem for problem in problems)


def test_cards_column_must_point_to_a_citing_card(tmp_path: Path) -> None:
    _write_ledger(
        tmp_path,
        [
            _row("P-001", cards="A-001"),
            _row("P-002"),
        ],
    )
    _write_card(tmp_path, claim_id="P-002")

    problems = check(tmp_path)
    assert any("Cards lists A-001" in problem for problem in problems)


def test_duplicate_claim_ids_raise() -> None:
    with pytest.raises(ValueError, match="duplicate claim id"):
        parse_ledger(HEADER + _row("P-001") + _row("P-001"))


def test_cli_check(tmp_path: Path, monkeypatch, capsys) -> None:
    _write_ledger(tmp_path, [_row("P-001", cards="A-001")])
    _write_card(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(["provenance", "check"]) == 0
    assert "provenance: OK (1 claims)" in capsys.readouterr().out


def test_cli_check_failure(tmp_path: Path, monkeypatch, capsys) -> None:
    _write_ledger(tmp_path, [_row("P-001")])
    _write_card(tmp_path, claim_id="P-999")
    monkeypatch.chdir(tmp_path)

    assert main(["provenance", "check"]) == 1
    assert "missing claim P-999" in capsys.readouterr().out
