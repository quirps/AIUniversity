from __future__ import annotations

import json
import shutil
import subprocess
from datetime import timedelta
from pathlib import Path

from aiu.generators.base import build
from aiu.labs.l003 import L003
from aiu.metrics import (
    cohen_kappa,
    compound,
    pass_at_k,
    pass_hat_k,
    rogan_gladen,
)
from aiu.runner import load_items, run_lab
from aiu.runs import create_run, prediction_commit_time

ROOT = Path(__file__).resolve().parents[1]
LAB_ID = "L-003"
AGENT_COUNTS = (5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 0, 0, 5, 4, 3)


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
    shutil.copytree(ROOT / "labs" / LAB_ID, root / "labs" / LAB_ID)
    shutil.copytree(ROOT / "experiments" / "_template", root / "experiments" / "_template")
    shutil.copytree(ROOT / "config", root / "config")

    _git(root, "init")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "init")

    run_id, rdir = create_run(root, LAB_ID, "fixture", None)
    prediction = rdir / "prediction.md"
    text = prediction.read_text(encoding="utf-8")
    text = text.replace("written_at:", "written_at: 2026-01-01T00:00:00Z")
    text = text.replace("predicted_metrics: {}", "predicted_metrics: {kappa: 0.8}")
    prediction.write_text(text, encoding="utf-8")
    _git(root, "add", prediction.relative_to(root).as_posix())
    _git(root, "commit", "-m", "prediction")

    return root, run_id, rdir, prediction_commit_time(prediction)


def test_dataset_is_deterministic_and_matches_committed_file(tmp_path: Path) -> None:
    assert build(ROOT, LAB_ID, True) == 0
    assert build(tmp_path, LAB_ID, False) == 0

    assert (
        tmp_path / "labs" / LAB_ID / "data" / "items.jsonl"
    ).read_bytes() == (ROOT / "labs" / LAB_ID / "data" / "items.jsonl").read_bytes()


def test_generator_counts() -> None:
    items = load_items(ROOT / "labs" / LAB_ID / "data" / "items.jsonl", None)
    labels = [item for item in items if item.id.startswith("j")]
    agents = [item for item in items if item.id.startswith("t")]

    assert len(labels) == 200
    assert len(agents) == 20
    assert [item.id for item in labels] == [f"j{index:03d}" for index in range(200)]

    cells = {
        (item.input["judge_label"], item.input["human_label"]) for item in labels
    }
    assert cells == {("fail", "fail"), ("pass", "fail"), ("fail", "pass"), ("pass", "pass")}
    assert sum(
        1
        for item in labels
        if item.input["judge_label"] == "fail" and item.input["human_label"] == "fail"
    ) == 24
    assert sum(
        1
        for item in labels
        if item.input["judge_label"] == "pass" and item.input["human_label"] == "fail"
    ) == 6
    assert sum(
        1
        for item in labels
        if item.input["judge_label"] == "fail" and item.input["human_label"] == "pass"
    ) == 14
    assert sum(
        1
        for item in labels
        if item.input["judge_label"] == "pass" and item.input["human_label"] == "pass"
    ) == 156
    assert [item.expected["successes"] for item in agents] == list(AGENT_COUNTS)


def test_score_matches_recomputed_statistics() -> None:
    items = load_items(ROOT / "labs" / LAB_ID / "data" / "items.jsonl", None)
    metrics = L003().score(items, [], {})

    judge = [item.input["judge_label"] for item in items if item.id.startswith("j")]
    human = [item.input["human_label"] for item in items if item.id.startswith("j")]

    kappa = cohen_kappa(judge, human)
    assert kappa is not None
    assert metrics["raw_agreement"] == 0.90
    assert metrics["kappa"] == kappa
    assert metrics["tpr"] == 0.80
    assert metrics["tnr"] == 156 / 170
    assert metrics["observed_fail_rate"] == 0.19
    assert metrics["true_fail_rate"] == 0.15
    assert metrics["corrected_fail_rate"] == rogan_gladen(0.19, 0.8, 156 / 170)
    assert metrics["agreement_minus_kappa"] == 0.90 - kappa
    assert metrics["pass_at_3"] == sum(pass_at_k(5, count, 3) for count in AGENT_COUNTS) / 20
    assert metrics["pass_hat_3"] == sum(pass_hat_k(5, count, 3) for count in AGENT_COUNTS) / 20
    assert metrics["compound_0.95_5"] == compound(0.95, 5)
    assert metrics["agreement_minus_kappa"] >= 0.15


def test_fixture_run_end_to_end(tmp_path: Path, capsys) -> None:
    root, run_id, rdir, commit_time = _setup(tmp_path)

    code = run_lab(
        root,
        LAB_ID,
        run_id,
        "fixture",
        None,
        None,
        False,
        None,
        now=commit_time + timedelta(hours=1),
    )

    assert code == 0
    assert f"run_id={run_id} status=completed" in capsys.readouterr().out

    result = json.loads((rdir / "result.json").read_text(encoding="utf-8"))
    assert result["status"] == "completed"
    assert result["hypothesis_supported"] is True
    assert result["n_calls"] == 0
    assert result["evidence_class"] == "assumed"

    metrics = json.loads((rdir / "metrics.json").read_text(encoding="utf-8"))["metrics"]
    assert set(metrics) == {
        "raw_agreement",
        "kappa",
        "tpr",
        "tnr",
        "observed_fail_rate",
        "corrected_fail_rate",
        "true_fail_rate",
        "agreement_minus_kappa",
        "pass_at_3",
        "pass_hat_3",
        "compound_0.95_5",
    }
    assert metrics["raw_agreement"] == 0.90
    assert metrics["pass_at_3"] == 0.825

    cost = json.loads((rdir / "cost.json").read_text(encoding="utf-8"))
    assert cost["actual_usd"] == 0.0
    assert cost["calls"] == 0
