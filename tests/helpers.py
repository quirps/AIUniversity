from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from aiu.runner import run_lab
from aiu.runs import create_run, prediction_commit_time


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def fill_prediction(rdir: Path, metrics: dict) -> None:
    path = rdir / "prediction.md"
    text = path.read_text(encoding="utf-8")
    stamp = (datetime.now(timezone.utc) - timedelta(seconds=60)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    text = text.replace("written_at:", f"written_at: {stamp}", 1)
    text = text.replace(
        "predicted_metrics: {}",
        f"predicted_metrics: {json.dumps(metrics)}",
        1,
    )
    path.write_text(text, encoding="utf-8")


def run_fixture(
    root: Path,
    lab_id: str,
    tmp: Path,
    limit: int | None = None,
) -> tuple[int, Path]:
    repo = tmp / "repo"
    repo.mkdir()
    shutil.copytree(root / "labs" / lab_id, repo / "labs" / lab_id)
    shutil.copytree(root / "experiments" / "_template", repo / "experiments" / "_template")
    shutil.copytree(root / "config", repo / "config")

    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "init")

    manifest = yaml.safe_load(
        (repo / "labs" / lab_id / "manifest.yaml").read_text(encoding="utf-8")
    )
    metrics = {metric["name"]: 0.5 for metric in manifest["metric"]}

    run_id, rdir = create_run(repo, lab_id, "fixture", None)
    fill_prediction(rdir, metrics)
    _git(repo, "add", rdir.relative_to(repo).as_posix())
    _git(repo, "commit", "-m", "prediction")

    commit_time = prediction_commit_time(rdir / "prediction.md")
    code = run_lab(
        repo,
        lab_id,
        run_id,
        "fixture",
        None,
        limit,
        False,
        None,
        now=commit_time + timedelta(hours=1),
    )
    return code, rdir
