from __future__ import annotations

import argparse
from pathlib import Path

from aiu.cli import build_parser

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "LEARNER_GUIDE.md"

SECTIONS = [
    "## Setup",
    "## The learning loop",
    "## Module M-A1 walkthrough",
    "## Fixture mode practice",
    "## Costs",
    "## What the harness will refuse to do",
]


def _guide_text() -> str:
    return GUIDE.read_text(encoding="utf-8")


def _code_lines(text: str) -> list[str]:
    lines: list[str] = []
    in_block = False
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_block = not in_block
            continue
        if in_block:
            lines.append(stripped)
    return lines


def _registered_subcommands() -> set[str]:
    parser = build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return set(action.choices)
    raise AssertionError("build_parser() has no subcommands")


def test_sections_are_present_in_order() -> None:
    headings = [line for line in _guide_text().splitlines() if line.startswith("## ")]
    assert headings == SECTIONS


def test_every_aiu_command_names_a_registered_subcommand() -> None:
    subcommands = _registered_subcommands()
    commands = [
        line for line in _code_lines(_guide_text()) if line.startswith("uv run aiu")
    ]

    assert commands
    for line in commands:
        parts = line.split()
        assert len(parts) >= 4, f"command has no subcommand: {line}"
        assert parts[3] in subcommands, f"unknown subcommand in guide: {line}"


def test_m_a1_artifacts_are_named() -> None:
    text = _guide_text()
    assert "learner/checkpoints/M-A1.answers.yaml" in text
    assert "learner/portfolio/M-A1/" in text


def test_fixture_results_are_labeled_assumed_not_measured() -> None:
    text = _guide_text().lower()
    assert "assumed, not measured" in text
