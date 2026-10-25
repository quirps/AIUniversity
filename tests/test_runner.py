from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import timedelta
from pathlib import Path

from aiu.cli import main
from aiu.runner import estimate_summary, run_lab
from aiu.runs import create_run, prediction_commit_time, prediction_unchanged

ROOT = Path(__file__).resolve().parents[1]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _setup(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    shutil.copytree(ROOT / "tests" / "fixtures" / "toy_lab", root / "labs" / "L-999")
    shutil.copytree(ROOT / "experiments" / "_template", root / "experiments" / "_template")
    shutil.copytree(ROOT / "config", root / "config")

    _git(root, "init")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "init")

    run_id, rdir = create_run(root, "L-999", "fixture", None)
    prediction = rdir / "prediction.md"
    text = prediction.read_text(encoding="utf-8")
    text = text.replace("written_at:", "written_at: 2026-01-01T00:00:00Z")
    text = text.replace("predicted_metrics: {}", "predicted_metrics: {accuracy: 0.8}")
    prediction.write_text(text, encoding="utf-8")
    _git(root, "add", prediction.relative_to(root).as_posix())
    _git(root, "commit", "-m", "prediction")

    return root, run_id, rdir, prediction_commit_time(prediction)


def test_fixture_run_completes_and_writes_artifacts(tmp_path: Path, capsys) -> None:
    root, run_id, rdir, commit_time = _setup(tmp_path)

    code = run_lab(
        root, "L-999", run_id, "fixture", None, None, False, None,
        now=commit_time + timedelta(hours=1),
    )

    assert code == 0
    stdout = capsys.readouterr().out
    assert re.fullmatch(
        rf"run_id={re.escape(run_id)} status=completed cost_usd=0\.0000\n",
        stdout,
    )
    for name in (
        "prediction.md",
        "prediction.sha256",
        "config.json",
        "responses.jsonl",
        "result.json",
        "metrics.json",
        "cost.json",
        "postmortem.md",
    ):
        assert (rdir / name).is_file(), name

    result = json.loads((rdir / "result.json").read_text(encoding="utf-8"))
    metrics = json.loads((rdir / "metrics.json").read_text(encoding="utf-8"))
    cost = json.loads((rdir / "cost.json").read_text(encoding="utf-8"))
    assert result["status"] == "completed"
    assert result["evidence_class"] == "assumed"
    assert metrics["evidence_class"] == "assumed"
    assert cost["actual_usd"] == 0.0


def test_missing_prediction_returns_7(tmp_path: Path) -> None:
    root, run_id, rdir, commit_time = _setup(tmp_path)
    (rdir / "prediction.md").unlink()

    code = run_lab(
        root, "L-999", run_id, "fixture", None, None, False, None,
        now=commit_time + timedelta(hours=1),
    )

    assert code == 7


def test_cost_cap_aborts_and_writes_result(tmp_path: Path) -> None:
    root, run_id, rdir, commit_time = _setup(tmp_path)

    code = run_lab(
        root, "L-999", run_id, "fixture", 0.0000001, None, False, None,
        now=commit_time + timedelta(hours=1),
    )

    assert code == 4
    result = json.loads((rdir / "result.json").read_text(encoding="utf-8"))
    assert result["status"] == "aborted_cost"


def test_removed_fixture_returns_3(tmp_path: Path) -> None:
    root, run_id, rdir, commit_time = _setup(tmp_path)
    fixtures = root / "labs" / "L-999" / "fixtures" / "responses.jsonl"
    lines = fixtures.read_text(encoding="utf-8").splitlines()
    fixtures.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

    code = run_lab(
        root, "L-999", run_id, "fixture", None, None, False, None,
        now=commit_time + timedelta(hours=1),
    )

    assert code == 3


def test_live_mode_unpinned_returns_6(tmp_path: Path, monkeypatch) -> None:
    root, run_id, rdir, commit_time = _setup(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    code = run_lab(
        root, "L-999", run_id, "live", None, None, False, None,
        now=commit_time + timedelta(hours=1),
    )

    assert code == 6


def test_fixture_record_mode_returns_6(tmp_path: Path) -> None:
    root, run_id, rdir, commit_time = _setup(tmp_path)

    code = run_lab(
        root, "L-999", run_id, "fixture", None, None, True, None,
        now=commit_time + timedelta(hours=1),
    )

    assert code == 6


def test_prediction_edit_is_detected(tmp_path: Path) -> None:
    root, run_id, rdir, commit_time = _setup(tmp_path)
    assert (
        run_lab(
            root, "L-999", run_id, "fixture", None, None, False, None,
            now=commit_time + timedelta(hours=1),
        )
        == 0
    )

    prediction = rdir / "prediction.md"
    prediction.write_text(
        prediction.read_text(encoding="utf-8") + "\nedited\n",
        encoding="utf-8",
    )

    assert prediction_unchanged(rdir) is False


def test_estimate_summary(tmp_path: Path) -> None:
    root, _, _, _ = _setup(tmp_path)
    summary = estimate_summary(root, "L-999", None)

    assert summary["calls"] == 4
    assert summary["basis"] == "pinned"
    assert summary["usd"] > 0


def test_cli_run(tmp_path: Path, monkeypatch) -> None:
    root, run_id, _, _ = _setup(tmp_path)
    monkeypatch.chdir(root)

    assert main(["lab", "run", "L-999", "--run-id", run_id, "--mode", "fixture"]) == 0


def test_cli_estimate(tmp_path: Path, capsys, monkeypatch) -> None:
    root, _, _, _ = _setup(tmp_path)
    monkeypatch.chdir(root)

    assert main(["lab", "estimate", "L-999"]) == 0
    assert "estimate_usd=" in capsys.readouterr().out
