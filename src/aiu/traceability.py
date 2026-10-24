from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

CARD_ID_RE = re.compile(r"^[A-F]-[0-9]{3}$")
CARD_FILE_RE = re.compile(r"^[A-F]-[0-9]{3}\.yaml$")
NULL_EXPERIMENT = {"", "-", "—", "–"}
EXPIRED_EXPERIMENT = {"E1-E13", "E1–E13"}


@dataclass(frozen=True)
class Row:
    src: str
    concept: str
    card: str
    experiment: str
    tag: str
    status: str


def _split_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def parse_rows(text: str) -> list[Row]:
    rows: list[Row] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not (
            stripped.startswith("| §")
            or stripped.startswith("| none")
            or stripped.startswith("| P-")
        ):
            continue
        parts = _split_row(line)
        if len(parts) != 6:
            raise ValueError(
                f"traceability row has {len(parts)} columns, expected 6: {stripped}"
            )
        src, concept, card, experiment, tag, status = parts
        rows.append(Row(src, concept, card, experiment, tag, status))
    return rows


def card_files(root: Path) -> list[Path]:
    base = root / "curriculum"
    files: list[Path] = []
    if not base.is_dir():
        return files
    for level in "ABCDEF":
        level_dir = base / level
        if not level_dir.is_dir():
            continue
        files.extend(
            sorted(path for path in level_dir.glob("*.yaml") if CARD_FILE_RE.match(path.name))
        )
    return files


def _load_card(path: Path) -> tuple[dict | None, str | None]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, f"{path.as_posix()}: YAML error: {exc}"
    if not isinstance(data, dict):
        return None, f"{path.as_posix()}: card is not a mapping"
    return data, None


def _is_null_experiment(value: str) -> bool:
    return value.strip() in NULL_EXPERIMENT


def _normalized_experiment(value: str) -> str:
    return value.strip().replace("—", "-").replace("–", "-")


def check(root: Path, require_all_cards: bool) -> list[str]:
    problems: list[str] = []
    trace_path = root / "TRACEABILITY.md"
    if not trace_path.is_file():
        return ["TRACEABILITY.md missing"]

    try:
        rows = parse_rows(trace_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"traceability: {exc}"]

    rows_by_card: dict[str, list[Row]] = {}
    for row in rows:
        if CARD_ID_RE.fullmatch(row.card):
            rows_by_card.setdefault(row.card, []).append(row)

    for row in rows:
        experiment = _normalized_experiment(row.experiment)
        if _is_null_experiment(row.experiment) or experiment in EXPIRED_EXPERIMENT:
            continue
        manifest = root / "labs" / experiment / "manifest.yaml"
        if not manifest.is_file():
            problems.append(
                f"row {row.src}: experiment {row.experiment} has no manifest"
            )

    cards = card_files(root)
    card_ids = set()
    for path in cards:
        card, error = _load_card(path)
        if error is not None:
            problems.append(error)
            continue
        card_id = card.get("id")
        if not isinstance(card_id, str):
            problems.append(f"{path.as_posix()}: card id missing")
            continue
        card_ids.add(card_id)
        matched = rows_by_card.get(card_id, [])
        if len(matched) != 1:
            problems.append(
                f"card {card_id} appears in {len(matched)} traceability rows"
            )
            continue
        row = matched[0]
        if card.get("source_section") != row.src:
            problems.append(
                f"card {card_id} source_section {card.get('source_section')!r} "
                f"does not match row src {row.src!r}"
            )

        card_experiment = card.get("experiment_id")
        if _is_null_experiment(row.experiment):
            if card_experiment is not None:
                problems.append(
                    f"card {card_id} experiment_id {card_experiment!r} "
                    "but the row has no experiment"
                )
        elif card_experiment != row.experiment:
            problems.append(
                f"card {card_id} experiment_id {card_experiment!r} "
                f"does not match row experiment {row.experiment!r}"
            )

    if require_all_cards:
        for row in rows:
            if not CARD_ID_RE.fullmatch(row.card):
                continue
            path = root / "curriculum" / row.card[0] / f"{row.card}.yaml"
            if row.card not in card_ids and not path.is_file():
                problems.append(
                    f"row {row.src}: card {row.card} has no file"
                )

    return problems
