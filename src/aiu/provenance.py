from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

STATUSES = {"unverified", "verified", "disputed"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CLAIM_ID_RE = re.compile(r"^P-[0-9]{3}$")
CARD_FILE_RE = re.compile(r"^[A-F]-[0-9]{3}\.yaml$")


@dataclass(frozen=True)
class Claim:
    id: str
    claim: str
    tag: str
    status: str
    source: str
    date: str
    method: str
    cards: list[str]


def _split_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def parse_ledger(text: str) -> dict[str, Claim]:
    claims: dict[str, Claim] = {}
    for line in text.splitlines():
        if not line.strip().startswith("| P-"):
            continue
        parts = _split_row(line)
        if len(parts) != 8:
            raise ValueError(
                f"ledger row has {len(parts)} columns, expected 8: {line.strip()}"
            )
        claim_id, claim_text, tag, status, source, date, method, cards = parts
        if not CLAIM_ID_RE.fullmatch(claim_id):
            raise ValueError(f"invalid claim id: {claim_id}")
        if claim_id in claims:
            raise ValueError(f"duplicate claim id: {claim_id}")
        if status not in STATUSES:
            raise ValueError(f"unknown status {status!r} for claim {claim_id}")
        card_ids = [] if cards in ("", "-") else [item.strip() for item in cards.split(",") if item.strip()]
        claims[claim_id] = Claim(
            id=claim_id,
            claim=claim_text,
            tag=tag,
            status=status,
            source=source,
            date=date,
            method=method,
            cards=card_ids,
        )
    return claims


def _card_files(root: Path) -> list[Path]:
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


def check(root: Path) -> list[str]:
    problems: list[str] = []
    ledger_path = root / "PROVENANCE.md"
    if not ledger_path.is_file():
        return ["PROVENANCE.md missing"]

    try:
        claims = parse_ledger(ledger_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"ledger: {exc}"]

    card_claims: dict[str, set[str]] = {}
    card_statuses: dict[str, dict[str, str | None]] = {}
    for path in _card_files(root):
        card, error = _load_card(path)
        if error is not None:
            problems.append(error)
            continue
        card_id = card.get("id")
        if not isinstance(card_id, str):
            problems.append(f"{path.as_posix()}: card id missing")
            continue
        statuses: dict[str, str | None] = {}
        verify = card.get("verify")
        if isinstance(verify, list):
            for item in verify:
                if isinstance(item, dict) and isinstance(item.get("claim_id"), str):
                    status = item.get("status")
                    statuses[item["claim_id"]] = (
                        status if isinstance(status, str) else None
                    )
        card_claims[card_id] = set(statuses)
        card_statuses[card_id] = statuses

    for card_id, statuses in card_statuses.items():
        for claim_id, status in statuses.items():
            if claim_id not in claims:
                problems.append(f"card {card_id} cites missing claim {claim_id}")
                continue
            if claims[claim_id].status != status:
                problems.append(
                    f"card {card_id} status for {claim_id} disagrees with ledger"
                )

    for claim in claims.values():
        if claim.status != "verified":
            continue
        if claim.source.strip() in ("", "-"):
            problems.append(f"{claim.id}: verified claim has empty source")
        if not DATE_RE.fullmatch(claim.date.strip()):
            problems.append(f"{claim.id}: verified claim needs a YYYY-MM-DD date")
        if claim.method.strip() in ("", "-"):
            problems.append(f"{claim.id}: verified claim has empty method")

    for claim in claims.values():
        for card_id in claim.cards:
            if card_id in card_claims and claim.id not in card_claims[card_id]:
                problems.append(
                    f"{claim.id}: Cards lists {card_id}, but that card does not cite it"
                )

    return problems
