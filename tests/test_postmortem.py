from __future__ import annotations

from pathlib import Path

from aiu.cli import main
from aiu.postmortem import check_postmortem
from aiu.runs import freeze_prediction

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "20260101T000000Z-live-abcdef"


def _setup(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    learner = root / "learner"
    learner.mkdir()
    (learner / "trust_table.yaml").write_text(
        """kind: trust_table
schema_version: "1.0"
rows:
  - rule: Test rule
    card_id: A-001
    evidence_strength: anecdote
    my_replication: not_run
    run_ids: []
    last_reviewed: 2026-10-24
    notes: ""
""",
        encoding="utf-8",
    )

    rdir = root / "experiments" / "L-999" / RUN_ID
    rdir.mkdir(parents=True)
    (rdir / "prediction.md").write_text("# prediction\n", encoding="utf-8")
    freeze_prediction(rdir)
    return root, rdir


def _untouched_template() -> str:
    text = (ROOT / "experiments" / "_template" / "postmortem.md").read_text(encoding="utf-8")
    return text.replace(
        "trust_table_row: <rule text from learner/trust_table.yaml>",
        "trust_table_row: Test rule",
    )


def _complete() -> str:
    return """---
run_id: 20260101T000000Z-live-abcdef
lab_id: L-999
author: Test
written_at: 2026-01-01T00:00:00Z
result_status: completed
actual_cost_usd: 0.0
trust_table_row: Test rule
---

# Post-mortem

## Prediction vs outcome
The predicted direction matched the measured result, and the threshold passed.

## What surprised me
The effect was larger than expected, but the data is synthetic and small.

## Confounds observed
The model may have matched names rather than facts; the controls did not remove that.

## Rule-of-thumb update
I trust this rule for this synthetic setup only, and I will label it as such.

## Next experiment
Run the same comparison on a second model with a larger item set.
"""


def test_untouched_template_has_five_problems(tmp_path: Path) -> None:
    root, rdir = _setup(tmp_path)
    (rdir / "postmortem.md").write_text(_untouched_template(), encoding="utf-8")

    problems = check_postmortem(rdir)

    assert len(problems) == 5
    assert all("section incomplete" in problem for problem in problems)


def test_complete_postmortem_is_ok(tmp_path: Path) -> None:
    root, rdir = _setup(tmp_path)
    (rdir / "postmortem.md").write_text(_complete(), encoding="utf-8")

    assert check_postmortem(rdir) == []


def test_edited_prediction_is_detected(tmp_path: Path) -> None:
    root, rdir = _setup(tmp_path)
    (rdir / "postmortem.md").write_text(_complete(), encoding="utf-8")
    prediction = rdir / "prediction.md"
    prediction.write_text(
        prediction.read_text(encoding="utf-8") + "edited\n",
        encoding="utf-8",
    )

    problems = check_postmortem(rdir)

    assert "prediction modified after run" in problems


def test_cli_postmortem_check(tmp_path: Path, capsys, monkeypatch) -> None:
    root, rdir = _setup(tmp_path)
    (rdir / "postmortem.md").write_text(_complete(), encoding="utf-8")
    monkeypatch.chdir(root)

    code = main(["lab", "postmortem-check", "L-999", "--run-id", RUN_ID])

    assert code == 0
    assert "postmortem: OK" in capsys.readouterr().out
