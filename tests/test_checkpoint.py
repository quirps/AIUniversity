from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from aiu.checkpoint import grade
from aiu.cli import main

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "module_test.yaml"


def _module() -> dict:
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def _answers() -> dict:
    return {"Q01": "B", "Q02": 0.77, "Q03": "ceiling test"}


def test_all_correct() -> None:
    result = grade(_module(), _answers())

    assert result["module_id"] == "M-A9"
    assert result["total"] == 3
    assert result["correct"] == 3
    assert all(item["correct"] for item in result["items"].values())
    assert result["graded_at"]


def test_mcq_is_trimmed_and_exact_is_normalized() -> None:
    result = grade(_module(), {"Q01": " B ", "Q02": 0.77, "Q03": " Ceiling Test. "})

    assert result["correct"] == 3


def test_numeric_tolerance_and_missing_answers() -> None:
    within = grade(_module(), {"Q01": "B", "Q02": 0.775, "Q03": "ceiling test"})
    assert within["items"]["Q02"]["correct"] is True

    outside = grade(_module(), {"Q01": "B", "Q02": 0.79, "Q03": "ceiling test"})
    assert outside["items"]["Q02"]["correct"] is False

    missing = grade(_module(), {"Q01": "B", "Q02": 0.77})
    assert missing["items"]["Q03"] == {
        "correct": False,
        "given": None,
        "expected": "ceiling test",
    }
    assert missing["correct"] == 2


def _cli_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "curriculum" / "modules").mkdir(parents=True)
    shutil.copyfile(FIXTURE, root / "curriculum" / "modules" / "M-A9.yaml")
    return root


def test_cli_all_correct_writes_result(tmp_path: Path, monkeypatch, capsys) -> None:
    root = _cli_root(tmp_path)
    answers = root / "answers.yaml"
    answers.write_text(
        yaml.safe_dump({"module_id": "M-A9", "answers": _answers()}),
        encoding="utf-8",
    )
    monkeypatch.chdir(root)

    assert main(["checkpoint", "grade", "M-A9", "--answers", str(answers)]) == 0
    assert "checkpoint: 3/3" in capsys.readouterr().out

    result = json.loads(
        (root / "learner" / "checkpoints" / "M-A9.result.json").read_text(
            encoding="utf-8"
        )
    )
    assert result["correct"] == 3
    assert result["items"]["Q01"]["given"] == "B"


def test_cli_one_wrong_returns_1(tmp_path: Path, monkeypatch, capsys) -> None:
    root = _cli_root(tmp_path)
    answers = root / "answers.yaml"
    answers.write_text(
        yaml.safe_dump(
            {"module_id": "M-A9", "answers": {"Q01": "A", "Q02": 0.77, "Q03": "ceiling test"}}
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(root)

    assert main(["checkpoint", "grade", "M-A9", "--answers", str(answers)]) == 1
    assert "checkpoint: 2/3" in capsys.readouterr().out


def test_cli_missing_module_returns_6(tmp_path: Path, monkeypatch, capsys) -> None:
    answers = tmp_path / "answers.yaml"
    answers.write_text(
        yaml.safe_dump({"module_id": "M-A9", "answers": _answers()}),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    assert main(["checkpoint", "grade", "M-A9", "--answers", str(answers)]) == 6
    assert "missing module" in capsys.readouterr().out
