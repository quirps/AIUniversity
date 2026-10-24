from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from aiu.cli import main
from aiu.status import check_status, write_status

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "status_repo"


def _copy_fixture(tmp_path: Path) -> Path:
    destination = tmp_path / "repo"
    shutil.copytree(FIXTURE, destination)
    schemas = destination / "schemas"
    schemas.mkdir(exist_ok=True)
    shutil.copy(ROOT / "schemas" / "status.schema.json", schemas / "status.schema.json")
    return destination


def test_write_then_check_is_clean(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    write_status(root)
    assert check_status(root) == []


def test_missing_run_id_in_results_is_a_mismatch(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    write_status(root)
    (root / "RESULTS.md").write_text("# Results\n", encoding="utf-8")

    mismatches = check_status(root)

    assert len(mismatches) == 1
    assert "missing from RESULTS.md" in mismatches[0]


def test_readme_block_edit_is_a_mismatch(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    write_status(root)
    readme = (root / "README.md").read_text(encoding="utf-8")
    (root / "README.md").write_text(
        readme.replace("Cards written", "Cards WRONG"),
        encoding="utf-8",
    )

    assert len(check_status(root)) == 1


def test_cumulative_cost_edit_is_a_mismatch(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    write_status(root)
    status_path = root / "status.json"
    data = json.loads(status_path.read_text(encoding="utf-8"))
    data["cumulative_cost_usd"] = 9.99
    status_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    mismatches = check_status(root)

    assert any("cumulative_cost_usd" in mismatch for mismatch in mismatches)


def test_tests_key_change_alone_is_ignored(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    write_status(root)
    status_path = root / "status.json"
    data = json.loads(status_path.read_text(encoding="utf-8"))
    data["tests"] = {
        "passed": 1,
        "failed": 0,
        "at": "2026-10-24T00:00:00Z",
    }
    status_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    assert check_status(root) == []


@pytest.mark.parametrize("flag", ["--write", "--check"])
def test_missing_markers_exit_6(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    flag: str,
) -> None:
    root = _copy_fixture(tmp_path)
    (root / "README.md").write_text("# no markers\n", encoding="utf-8")
    monkeypatch.chdir(root)

    code = main(["status", flag])

    assert code == 6
    assert "README markers missing" in capsys.readouterr().out
