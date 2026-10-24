from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_env_example_has_empty_key() -> None:
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.startswith("OPENROUTER_API_KEY=")]
    assert lines == ["OPENROUTER_API_KEY="]


def test_gitignore_has_required_lines() -> None:
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in lines
    assert ".runs/" in lines
    assert ".venv/" in lines


def test_env_is_ignored_but_example_is_not() -> None:
    ignored = subprocess.run(
        ["git", "check-ignore", ".env"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert ignored.returncode == 0
    assert ".env" in ignored.stdout

    allowed = subprocess.run(
        ["git", "check-ignore", ".env.example"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert allowed.returncode == 1
