from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB_ID_RE = re.compile(r"^(E([1-9]|1[0-3])|L-[0-9]{3})$")
RUN_ID_RE = re.compile(r"^[0-9]{8}T[0-9]{6}Z-live-[0-9a-f]{6}$")


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _layout_top_level_entries() -> set[str]:
    text = (ROOT / "REPO_LAYOUT.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
    tree = next(block for block in blocks if "AIUniversity/" in block)

    entries: set[str] = set()
    for line in tree.splitlines():
        if not line.startswith(("├", "└")):
            continue
        name = line[4:].strip().split()[0]
        entries.add(name.rstrip("/").split("/", 1)[0])
    return entries


def _tracked_top_level_entries() -> set[str]:
    result = _git("ls-files")
    assert result.returncode == 0, result.stderr
    entries = {
        line.split("/", 1)[0] for line in result.stdout.splitlines() if line.strip()
    }
    if (ROOT / ".runs").exists():
        entries.add(".runs")
    return entries


def test_tracked_top_level_entries_match_layout() -> None:
    tracked = _tracked_top_level_entries()
    allowed = _layout_top_level_entries()

    unexpected = sorted(tracked - allowed)
    assert unexpected == [], f"top-level entries missing from REPO_LAYOUT.md: {unexpected}"


def test_lab_directories_use_lab_ids() -> None:
    for path in sorted((ROOT / "labs").iterdir()):
        if not path.is_dir():
            continue
        assert LAB_ID_RE.fullmatch(path.name), f"invalid lab directory: {path.name}"


def test_experiments_contain_only_template_and_live_runs() -> None:
    experiments = ROOT / "experiments"
    for lab_dir in sorted(experiments.iterdir()):
        assert lab_dir.is_dir(), f"unexpected file in experiments/: {lab_dir.name}"
        if lab_dir.name == "_template":
            continue
        assert LAB_ID_RE.fullmatch(lab_dir.name), f"invalid experiments lab: {lab_dir.name}"
        for run_dir in sorted(lab_dir.iterdir()):
            assert run_dir.is_dir(), f"unexpected file in {lab_dir.name}: {run_dir.name}"
            assert RUN_ID_RE.fullmatch(
                run_dir.name
            ), f"invalid live run directory: {run_dir.name}"


def test_runs_directory_is_not_tracked() -> None:
    result = _git("ls-files", "--", ".runs")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "", ".runs must not be tracked"
