from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

from aiu.cli import main
from aiu.config import ConfigError
from aiu.runs import (
    RUN_ID_RE,
    PredictionGateError,
    check_prediction,
    create_run,
    freeze_prediction,
    new_run_id,
    prediction_commit_time,
    prediction_unchanged,
)

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


def _init_repo(repo: Path) -> None:
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")


def _prediction_text(written_at: str, metrics: str) -> str:
    return f"""---
run_id: 20260101T000000Z-live-abcdef
lab_id: L-001
mode: live
author: Test
written_at: {written_at}
predicted_metrics: {metrics}
---

# Prediction
"""


def _commit(repo: Path, path: Path) -> None:
    _git(repo, "add", path.name)
    _git(repo, "commit", "-m", "prediction")


def _make_root(tmp_path: Path) -> Path:
    root = tmp_path / "root"
    template_dir = root / "experiments" / "_template"
    template_dir.mkdir(parents=True)
    shutil.copy(
        ROOT / "experiments" / "_template" / "prediction.md",
        template_dir / "prediction.md",
    )
    lab_dir = root / "labs" / "L-001"
    lab_dir.mkdir(parents=True)
    (lab_dir / "manifest.yaml").write_text("kind: lab\nid: L-001\nstatus: runnable\n")
    return root


def test_new_run_id_matches_pattern() -> None:
    run_id = new_run_id(
        "live",
        now=datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        rand_hex="abcdef",
    )
    assert run_id == "20260102T030405Z-live-abcdef"
    assert RUN_ID_RE.match(run_id)


def test_create_run_fills_front_matter(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    run_id, rdir = create_run(root, "L-001", "fixture", None)

    assert rdir.is_dir()
    assert rdir.parent.name == "L-001"
    text = (rdir / "prediction.md").read_text(encoding="utf-8")
    front_matter = yaml.safe_load(text.split("---")[1])
    assert front_matter["run_id"] == run_id
    assert front_matter["lab_id"] == "L-001"
    assert front_matter["mode"] == "fixture"
    assert front_matter["written_at"] is None
    assert front_matter["predicted_metrics"] == {}


def test_create_run_requires_manifest(tmp_path: Path) -> None:
    root = tmp_path / "root"
    template_dir = root / "experiments" / "_template"
    template_dir.mkdir(parents=True)
    shutil.copy(
        ROOT / "experiments" / "_template" / "prediction.md",
        template_dir / "prediction.md",
    )

    with pytest.raises(ConfigError):
        create_run(root, "L-001", "fixture", None)


def test_committed_prediction_passes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    path = repo / "prediction.md"
    path.write_text(_prediction_text("2026-01-01T00:00:00Z", "{accuracy: 0.8}"))
    _commit(repo, path)

    commit_time = prediction_commit_time(path)
    data = check_prediction(
        path,
        {"accuracy"},
        commit_time + timedelta(hours=1),
    )

    assert data["lab_id"] == "L-001"


def test_empty_predicted_metrics_raise(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    path = repo / "prediction.md"
    path.write_text(_prediction_text("2026-01-01T00:00:00Z", "{}"))
    _commit(repo, path)

    with pytest.raises(PredictionGateError):
        check_prediction(path, {"accuracy"}, datetime.now(timezone.utc) + timedelta(hours=1))


def test_unknown_metric_raises(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    path = repo / "prediction.md"
    path.write_text(_prediction_text("2026-01-01T00:00:00Z", "{bogus: 1}"))
    _commit(repo, path)

    with pytest.raises(PredictionGateError):
        check_prediction(path, {"accuracy"}, datetime.now(timezone.utc) + timedelta(hours=1))


def test_future_written_at_raises(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    path = repo / "prediction.md"
    path.write_text(_prediction_text("2099-01-01T00:00:00Z", "{accuracy: 0.8}"))
    _commit(repo, path)

    with pytest.raises(PredictionGateError):
        check_prediction(path, {"accuracy"}, datetime.now(timezone.utc) + timedelta(hours=1))


def test_uncommitted_prediction_raises(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    path = repo / "prediction.md"
    path.write_text(_prediction_text("2026-01-01T00:00:00Z", "{accuracy: 0.8}"))

    with pytest.raises(ConfigError):
        check_prediction(path, {"accuracy"}, datetime.now(timezone.utc) + timedelta(hours=1))


def test_prediction_committed_after_run_start_raises(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    path = repo / "prediction.md"
    path.write_text(_prediction_text("2026-01-01T00:00:00Z", "{accuracy: 0.8}"))
    _commit(repo, path)

    commit_time = prediction_commit_time(path)
    with pytest.raises(PredictionGateError):
        check_prediction(path, {"accuracy"}, commit_time - timedelta(seconds=1))


def test_freeze_and_detect_edit(tmp_path: Path) -> None:
    rdir = tmp_path / "run"
    rdir.mkdir()
    (rdir / "prediction.md").write_text("# prediction\n", encoding="utf-8")

    digest = freeze_prediction(rdir)

    assert len(digest) == 64
    assert prediction_unchanged(rdir) is True
    (rdir / "prediction.md").write_text("# edited\n", encoding="utf-8")
    assert prediction_unchanged(rdir) is False


def test_cli_new_run(tmp_path: Path, capsys, monkeypatch) -> None:
    root = _make_root(tmp_path)
    monkeypatch.chdir(root)

    code = main(["lab", "new-run", "L-001", "--mode", "fixture"])

    assert code == 0
    assert "run_id=" in capsys.readouterr().out


def test_cli_new_run_missing_manifest(tmp_path: Path, capsys, monkeypatch) -> None:
    root = tmp_path / "root"
    template_dir = root / "experiments" / "_template"
    template_dir.mkdir(parents=True)
    shutil.copy(
        ROOT / "experiments" / "_template" / "prediction.md",
        template_dir / "prediction.md",
    )
    monkeypatch.chdir(root)

    code = main(["lab", "new-run", "L-001", "--mode", "fixture"])

    assert code == 6
    assert "missing manifest" in capsys.readouterr().out
