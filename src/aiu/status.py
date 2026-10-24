from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from aiu import __version__

STATUS_BEGIN = "<!-- STATUS:BEGIN -->"
STATUS_END = "<!-- STATUS:END -->"
IGNORED_KEYS = ("generated_at", "tests")


class StatusError(Exception):
    pass


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


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
            sorted(
                path
                for path in level_dir.glob("*.yaml")
                if re.fullmatch(r"[A-F]-[0-9]{3}\.yaml", path.name)
            )
        )
    return files


def _module_files(root: Path) -> list[Path]:
    base = root / "curriculum" / "modules"
    if not base.is_dir():
        return []
    return sorted(base.glob("M-*.yaml"))


def _lab_manifests(root: Path) -> list[Path]:
    base = root / "labs"
    if not base.is_dir():
        return []
    return sorted(base.glob("*/manifest.yaml"))


def _provenance_counts(root: Path) -> dict[str, int]:
    counts = {"total": 0, "unverified": 0, "verified": 0, "disputed": 0}
    path = root / "PROVENANCE.md"
    if not path.is_file():
        return counts
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| P-"):
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) >= 10:
            status = parts[4]
        elif len(parts) >= 8:
            status = parts[3]
        else:
            continue
        counts["total"] += 1
        if status in ("unverified", "verified", "disputed"):
            counts[status] += 1
    return counts


def _live_run_dirs(root: Path):
    base = root / "experiments"
    if not base.is_dir():
        return
    for lab_dir in sorted(path for path in base.iterdir() if path.is_dir()):
        if lab_dir.name == "_template":
            continue
        for run_dir in sorted(path for path in lab_dir.iterdir() if path.is_dir()):
            if (run_dir / "cost.json").is_file():
                yield run_dir


def _live_run_counts(root: Path) -> tuple[dict[str, int], float, str | None]:
    counts = {"total": 0, "completed": 0, "aborted": 0, "failed": 0}
    total_cost = 0.0
    run_ids: list[str] = []

    for run_dir in _live_run_dirs(root):
        counts["total"] += 1
        run_ids.append(run_dir.name)

        cost = _read_json(run_dir / "cost.json") or {}
        value = cost.get("actual_usd", cost.get("usd", 0.0))
        try:
            total_cost += float(value or 0.0)
        except (TypeError, ValueError):
            pass

        result = _read_json(run_dir / "result.json") or {}
        status = result.get("status")
        if status == "completed":
            counts["completed"] += 1
        elif status in ("aborted", "aborted_cost"):
            counts["aborted"] += 1
        elif status == "failed":
            counts["failed"] += 1

    return counts, round(total_cost, 4), (max(run_ids) if run_ids else None)


def compute_status(root: Path, previous: dict | None) -> dict:
    cards = _card_files(root)
    by_level = {level: 0 for level in "ABCDEF"}
    for card in cards:
        by_level[card.parent.name] += 1

    modules = _module_files(root)
    labs = _lab_manifests(root)
    runnable = 0
    for lab in labs:
        try:
            data = yaml.safe_load(lab.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        if data.get("status") == "runnable":
            runnable += 1

    live_runs, cumulative_cost, last_live_run = _live_run_counts(root)
    ledger = _provenance_counts(root)

    tests = previous.get("tests") if previous else None
    known_gaps = previous.get("known_gaps", []) if previous else []
    stage = previous.get("stage", "building") if previous else "building"
    last_verified = previous.get("last_verified") if previous else None

    return {
        "schema_version": 1,
        "aiu_version": __version__,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stage": stage,
        "cards": {"drafted": len(cards), "by_level": by_level},
        "labs": {"total": len(labs), "runnable": runnable},
        "modules": {"total": len(modules), "authored": len(modules)},
        "live_runs": live_runs,
        "cumulative_cost_usd": cumulative_cost,
        "ledger": {
            "total": ledger["total"],
            "unverified": ledger["unverified"],
            "verified": ledger["verified"],
            "disputed": ledger["disputed"],
        },
        "last_verified": last_verified,
        "last_live_run": last_live_run,
        "tests": tests,
        "known_gaps": known_gaps,
    }


def render_readme_block(status: dict) -> str:
    tests = status.get("tests")
    if tests:
        tests_text = (
            f"{tests.get('passed', 0)} passed / {tests.get('failed', 0)} failed "
            f"(at {tests.get('at') or 'unknown'})"
        )
    else:
        tests_text = "not run"

    gaps = status.get("known_gaps", [])
    lines = [
        "| Metric | Value | Basis |",
        "|---|---:|---|",
        f"| Cards written | {status['cards']['drafted']} | counted |",
        f"| Modules | {status['modules']['authored']} authored / {status['modules']['total']} manifests | counted |",
        f"| Labs runnable | {status['labs']['runnable']} of {status['labs']['total']} manifests | counted |",
        f"| Labs specified | {max(0, status['labs']['total'] - status['labs']['runnable'])} | counted |",
        f"| Claims verified | {status['ledger']['verified']} | counted |",
        f"| Claims unverified | {status['ledger']['unverified']} | counted |",
        f"| Claims disputed | {status['ledger']['disputed']} | counted |",
        f"| Live runs | {status['live_runs']['total']} | measured |",
        f"| Cumulative spend (USD) | {status['cumulative_cost_usd']:.4f} | measured |",
        f"| Last live run | {status.get('last_live_run') or 'none'} | measured |",
        f"| Tests | {tests_text} | measured |",
        f"| Known gaps | {len(gaps)} | counted |",
        "",
        "Known gaps:",
    ]
    if gaps:
        lines.extend(f"- {gap['ticket']}: {gap['title']}" for gap in gaps)
    else:
        lines.append("- none")
    return "\n".join(lines).strip("\n")


def _read_readme(root: Path) -> str:
    path = root / "README.md"
    if not path.is_file():
        raise StatusError("README.md missing")
    text = path.read_text(encoding="utf-8")
    if STATUS_BEGIN not in text or STATUS_END not in text:
        raise StatusError("README markers missing")
    return text


def _extract_block(readme: str) -> str:
    start = readme.index(STATUS_BEGIN) + len(STATUS_BEGIN)
    end = readme.index(STATUS_END)
    return readme[start:end].strip("\n")


def _replace_block(readme: str, block: str) -> str:
    start = readme.index(STATUS_BEGIN) + len(STATUS_BEGIN)
    end = readme.index(STATUS_END)
    return readme[:start] + "\n" + block + "\n" + readme[end:]


def _strip_tests_row(block: str) -> str:
    return "\n".join(
        line for line in block.splitlines() if not line.startswith("| Tests |")
    )


def write_status(root: Path) -> None:
    readme = _read_readme(root)
    previous = _read_json(root / "status.json")
    status = compute_status(root, previous)

    (root / "status.json").write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    block = render_readme_block(status)
    (root / "README.md").write_text(_replace_block(readme, block), encoding="utf-8")


def check_status(root: Path) -> list[str]:
    mismatches: list[str] = []
    readme = _read_readme(root)
    committed = _read_json(root / "status.json")
    if committed is None:
        return ["status.json missing"]

    schema_path = root / "schemas" / "status.schema.json"
    if schema_path.is_file():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        try:
            Draft202012Validator(schema).validate(committed)
        except Exception as exc:
            message = getattr(exc, "message", str(exc))
            mismatches.append(f"status.json schema error: {message}")

    computed = compute_status(root, committed)
    ignored = set(IGNORED_KEYS) | {"cumulative_cost_usd"}
    left = {key: value for key, value in committed.items() if key not in ignored}
    right = {key: value for key, value in computed.items() if key not in ignored}
    if left != right:
        mismatches.append("status.json differs from computed state")
    if committed.get("cumulative_cost_usd") != computed.get("cumulative_cost_usd"):
        mismatches.append("cumulative_cost_usd mismatch")

    actual = _extract_block(readme)
    expected = render_readme_block(committed)
    if _strip_tests_row(actual) != _strip_tests_row(expected):
        mismatches.append("README STATUS block differs from status.json")

    results_path = root / "RESULTS.md"
    results = results_path.read_text(encoding="utf-8") if results_path.is_file() else ""
    for run_dir in _live_run_dirs(root):
        if run_dir.name not in results:
            mismatches.append(f"run {run_dir.name} missing from RESULTS.md")

    return mismatches
