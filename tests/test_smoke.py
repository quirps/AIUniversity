from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from aiu.cli import main
from aiu.runs import PredictionGateError, check_prediction
from aiu.smoke import SMOKE_PLAN, run_smoke

ROOT = Path(__file__).resolve().parents[1]


def _setup(root: Path) -> None:
    for lab_id, _ in SMOKE_PLAN:
        shutil.copytree(ROOT / "labs" / lab_id, root / "labs" / lab_id)
    shutil.copytree(ROOT / "experiments" / "_template", root / "experiments" / "_template")
    shutil.copytree(ROOT / "config", root / "config")


def test_fixture_smoke_completes_five_labs(tmp_path: Path, monkeypatch, capsys) -> None:
    _setup(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(["smoke", "--mode", "fixture"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[-1].endswith("OK")
    assert "total_cost_usd=0.0000" in lines[-1]

    summaries = list((tmp_path / ".runs").glob("smoke-*.json"))
    assert len(summaries) == 1
    summary = json.loads(summaries[0].read_text(encoding="utf-8"))
    assert summary["mode"] == "fixture"
    assert len(summary["labs"]) == 5
    assert {lab["lab_id"] for lab in summary["labs"]} == {
        lab_id for lab_id, _ in SMOKE_PLAN
    }
    assert all(lab["status"] == "completed" for lab in summary["labs"])
    assert summary["total_cost_usd"] == 0.0


def test_smoke_cap_above_default_returns_6(tmp_path: Path, monkeypatch, capsys) -> None:
    _setup(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(["smoke", "--mode", "fixture", "--cap", "6"]) == 6
    assert "exceeds default" in capsys.readouterr().out
    assert not (tmp_path / ".runs").exists()


def test_live_preflight_aborts_before_any_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _setup(tmp_path)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    called: list[str] = []

    def factory(mode: str):
        called.append(mode)
        raise AssertionError("client factory must not be called")

    code = run_smoke(tmp_path, "live", 0.0001, client_factory=factory)

    assert code == 4
    assert called == []
    for lab_id, _ in SMOKE_PLAN:
        assert not (tmp_path / "experiments" / lab_id).exists()


def test_smoke_prediction_accepts_null_metrics(tmp_path: Path) -> None:
    now = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    path = tmp_path / "prediction.md"
    front = {
        "run_id": "20260101T000000Z-fixture-abcdef",
        "lab_id": "E9",
        "mode": "fixture",
        "written_at": "2025-12-31T23:59:00Z",
        "smoke": True,
        "predicted_metrics": {"accuracy:oracle": None},
    }
    path.write_text(
        "---\n"
        + yaml.safe_dump(front, sort_keys=False)
        + "---\n\n# Smoke run\n",
        encoding="utf-8",
    )

    assert check_prediction(path, {"accuracy:oracle"}, now)["smoke"] is True


def test_non_smoke_prediction_rejects_null_metrics(tmp_path: Path) -> None:
    now = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    path = tmp_path / "prediction.md"
    front = {
        "run_id": "20260101T000000Z-fixture-abcdef",
        "lab_id": "E9",
        "mode": "fixture",
        "written_at": "2025-12-31T23:59:00Z",
        "predicted_metrics": {"accuracy:oracle": None},
    }
    path.write_text(
        "---\n"
        + yaml.safe_dump(front, sort_keys=False)
        + "---\n\n# Prediction\n",
        encoding="utf-8",
    )

    with pytest.raises(PredictionGateError, match="null unless smoke"):
        check_prediction(path, {"accuracy:oracle"}, now)
