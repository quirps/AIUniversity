from __future__ import annotations

import re
from pathlib import Path

import yaml

from aiu.runs import prediction_unchanged

REQUIRED_HEADINGS: tuple[str, ...] = (
    "Prediction vs outcome",
    "What surprised me",
    "Confounds observed",
    "Rule-of-thumb update",
    "Next experiment",
)


def _find_root(rdir: Path) -> Path:
    current = rdir.resolve()
    for candidate in (current, *current.parents):
        if (candidate / "learner" / "trust_table.yaml").is_file():
            return candidate
        if (candidate / ".git").exists():
            return candidate
    return current


def _front_matter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return {}
    try:
        data = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def _sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buffer)
            current = line[3:].strip()
            buffer = []
        elif current is not None:
            buffer.append(line)
    if current is not None:
        sections[current] = "\n".join(buffer)
    return sections


def _trust_rules(root: Path) -> list[str]:
    path = root / "learner" / "trust_table.yaml"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = data.get("rows", []) if isinstance(data, dict) else []
    return [
        row["rule"]
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("rule"), str)
    ]


def check_postmortem(rdir: Path) -> list[str]:
    path = rdir / "postmortem.md"
    if not path.is_file():
        return ["missing postmortem.md"]

    text = path.read_text(encoding="utf-8")
    problems: list[str] = []
    sections = _sections(text)

    for heading in REQUIRED_HEADINGS:
        if heading not in sections:
            problems.append(f"missing heading: ## {heading}")
            continue
        body = sections[heading]
        if len(re.sub(r"\s", "", body)) < 20 or "TODO" in body:
            problems.append(f"section incomplete: ## {heading}")

    front_matter = _front_matter(text)
    trust_row = front_matter.get("trust_table_row")
    if not isinstance(trust_row, str) or not trust_row.strip():
        problems.append("trust_table_row missing")
    else:
        rules = _trust_rules(_find_root(rdir))
        if trust_row.strip() not in rules:
            problems.append("trust_table_row not found in learner/trust_table.yaml")

    if not (rdir / "prediction.sha256").is_file() or not prediction_unchanged(rdir):
        problems.append("prediction modified after run")

    return problems
