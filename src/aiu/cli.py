from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from aiu import __version__
from aiu.config import ConfigError
from aiu.fixtures_synth import synth
from aiu.generators.base import build
from aiu.hardware import check as check_hardware
from aiu.hardware import probe
from aiu.journal import check_append_only, head_content
from aiu.labs.tiers import check_tiers, list_labs, manifest_paths
from aiu.secrets_scan import all_tracked_and_untracked, scan_paths, staged_paths
from aiu.postmortem import check_postmortem
from aiu.runner import estimate_summary, run_lab
from aiu.runs import create_run, default_out_dir, run_dir
from aiu.status import StatusError, check_status, write_status
from aiu.validate import validate_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aiu")
    parser.add_argument(
        "--version",
        action="version",
        version=f"aiu {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    scan = subparsers.add_parser(
        "secrets-scan",
        help="Scan tracked or staged files for secrets and forbidden files.",
    )
    scan.add_argument("--staged", action="store_true")
    scan.add_argument("--root", default=".")

    journal = subparsers.add_parser(
        "journal",
        help="Journal checks.",
    )
    journal_sub = journal.add_subparsers(dest="journal_command")
    journal_check = journal_sub.add_parser(
        "check",
        help="Fail if existing journal content was modified.",
    )
    journal_check.add_argument("--root", default=".")

    validate = subparsers.add_parser(
        "validate",
        help="Validate YAML content against the curriculum schema.",
    )
    validate.add_argument("paths", nargs="*")

    status = subparsers.add_parser(
        "status",
        help="Generate or check status.json and the README STATUS block.",
    )
    status_group = status.add_mutually_exclusive_group(required=True)
    status_group.add_argument("--write", action="store_true")
    status_group.add_argument("--check", action="store_true")

    hwcheck = subparsers.add_parser(
        "hwcheck",
        help="Probe hardware and check a lab tier.",
    )
    hwcheck.add_argument("--tier", default="API_ONLY")
    hwcheck.add_argument("--json", action="store_true")

    lab = subparsers.add_parser("lab", help="Lab run management.")
    lab_sub = lab.add_subparsers(dest="lab_command")
    new_run = lab_sub.add_parser("new-run", help="Create a new run and prediction template.")
    new_run.add_argument("lab_id")
    new_run.add_argument("--mode", choices=("fixture", "live"), required=True)
    new_run.add_argument("--out-dir", default=None)

    run_cmd = lab_sub.add_parser("run", help="Run a lab.")
    run_cmd.add_argument("lab_id")
    run_cmd.add_argument("--run-id", required=True)
    run_cmd.add_argument("--mode", choices=("fixture", "live"), required=True)
    run_cmd.add_argument("--cap", type=float, default=None)
    run_cmd.add_argument("--limit", type=int, default=None)
    run_cmd.add_argument("--record", action="store_true")
    run_cmd.add_argument("--out-dir", default=None)

    estimate = lab_sub.add_parser("estimate", help="Estimate a lab before running it.")
    estimate.add_argument("lab_id")
    estimate.add_argument("--limit", type=int, default=None)

    postmortem = lab_sub.add_parser("postmortem-check", help="Check a completed post-mortem.")
    postmortem.add_argument("lab_id")
    postmortem.add_argument("--run-id", required=True)
    postmortem.add_argument("--out-dir", default=None)

    labs = subparsers.add_parser("labs", help="Lab manifest inventory and tier checks.")
    labs_sub = labs.add_subparsers(dest="labs_command")
    labs_sub.add_parser("list", help="List every lab manifest.")
    labs_check = labs_sub.add_parser(
        "check-tiers",
        help="Check hardware tiers and local fallbacks.",
    )
    labs_check.add_argument("path", nargs="?", default=None)

    dataset = subparsers.add_parser("dataset", help="Dataset generation.")
    dataset_sub = dataset.add_subparsers(dest="dataset_command")
    dataset_build = dataset_sub.add_parser("build", help="Build a lab dataset.")
    dataset_build.add_argument("lab_id")
    dataset_build.add_argument("--check", action="store_true")

    fixtures = subparsers.add_parser("fixtures", help="Fixture generation.")
    fixtures_sub = fixtures.add_subparsers(dest="fixtures_command")
    fixtures_synth = fixtures_sub.add_parser(
        "synth",
        help="Synthesize a lab fixture file.",
    )
    fixtures_synth.add_argument("lab_id")
    fixtures_synth.add_argument("--check", action="store_true")

    return parser


def _secrets_scan(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    paths = staged_paths(root) if args.staged else all_tracked_and_untracked(root)
    findings = scan_paths(paths)

    for finding in findings:
        if finding.line is None:
            print(f"{finding.rule} {finding.path} {finding.excerpt}")
        else:
            print(f"{finding.rule} {finding.path}:{finding.line} {finding.excerpt}")

    if findings:
        return 1

    print("secrets-scan: 0 findings")
    return 0


def _journal_check(root: Path) -> int:
    path = root / "JOURNAL.md"
    if not path.is_file():
        print("journal: JOURNAL.md missing")
        return 1

    old = head_content(root)
    new = path.read_text(encoding="utf-8")
    if check_append_only(old, new):
        print("journal: append-only OK")
        return 0

    print("journal: existing entries modified")
    return 1


def _validate(root: Path, paths: list[Path]) -> int:
    if paths:
        missing = [path for path in paths if not path.exists()]
        if missing:
            for path in missing:
                print(f"{path.as_posix()} path does not exist")
            print(f"validate: 0 files, {len(missing)} errors")
            return 1
    else:
        paths = [
            path
            for path in (root / "curriculum", root / "labs", root / "learner")
            if path.exists()
        ]

    files, errors = validate_paths(root, paths)
    for error in errors:
        print(f"{error.path} {error.pointer} {error.message}")
    print(f"validate: {len(files)} files, {len(errors)} errors")
    return 0 if not errors else 1


def _hwcheck(args: argparse.Namespace) -> int:
    result = check_hardware(args.tier, probe(Path(".").resolve()))

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        verdict = "PASS" if result["passed"] else "FAIL"
        print(f"hwcheck: {result['tier']} {verdict}")
        for failure in result["failures"]:
            print(f"  failure: {failure}")
        for warning in result["warnings"]:
            print(f"  warning: {warning}")

    return 0 if result["passed"] else 5


def _lab_new_run(args: argparse.Namespace) -> int:
    root = Path(".").resolve()
    try:
        run_id, rdir = create_run(
            root,
            args.lab_id,
            args.mode,
            Path(args.out_dir) if args.out_dir else None,
        )
    except ConfigError as exc:
        print(f"lab new-run: {exc}")
        return 6

    print(f"run_id={run_id} dir={rdir.as_posix()}")
    return 0


def _lab_run(args: argparse.Namespace) -> int:
    return run_lab(
        Path(".").resolve(),
        args.lab_id,
        args.run_id,
        args.mode,
        args.cap,
        args.limit,
        args.record,
        Path(args.out_dir) if args.out_dir else None,
    )


def _lab_estimate(args: argparse.Namespace) -> int:
    try:
        summary = estimate_summary(Path(".").resolve(), args.lab_id, args.limit)
    except ConfigError as exc:
        print(f"lab estimate: {exc}")
        return 6

    suffix = " basis=assumed" if summary["basis"] == "assumed" else ""
    print(
        f"estimate_usd={summary['usd']:.4f} calls={summary['calls']} "
        f"cap_usd={summary['cap_usd']:.2f}{suffix}"
    )
    return 0


def _lab_postmortem(args: argparse.Namespace) -> int:
    match = re.search(r"-(fixture|live)-[0-9a-f]{6}$", args.run_id)
    mode = match.group(1) if match else "live"
    root = Path(".").resolve()
    out_dir = root / (Path(args.out_dir) if args.out_dir else default_out_dir(mode))
    rdir = run_dir(out_dir, args.lab_id, args.run_id)

    problems = check_postmortem(rdir)
    for problem in problems:
        print(problem)
    if problems:
        print(f"postmortem: {len(problems)} problems")
        return 1
    print("postmortem: OK")
    return 0


def _labs_list(root: Path) -> int:
    for lab_id, status, tier, title in list_labs(root):
        print(f"{lab_id}\t{status}\t{tier}\t{title}")
    return 0


def _labs_check_tiers(root: Path, value: str | None) -> int:
    path = Path(value) if value else None
    problems = check_tiers(root, path)
    for problem in problems:
        print(problem)
    if problems:
        print(f"tiers: {len(problems)} problems")
        return 1
    count = len(manifest_paths(root, path))
    print(f"tiers: OK ({count} labs)")
    return 0


def _dataset_build(args: argparse.Namespace) -> int:
    code = build(Path(".").resolve(), args.lab_id, args.check)
    if code == 6:
        print(f"dataset: {args.lab_id} no generator")
    elif code == 1:
        print(f"dataset: {args.lab_id} DIFF")
    elif args.check:
        print(f"dataset: {args.lab_id} OK")
    else:
        print(f"dataset: {args.lab_id} WRITTEN")
    return code


def _fixtures_synth(args: argparse.Namespace) -> int:
    code = synth(Path(".").resolve(), args.lab_id, args.check)
    if code == 6:
        print(f"fixtures: {args.lab_id} no generator")
    elif code == 1:
        print(f"fixtures: {args.lab_id} DIFF")
    elif args.check:
        print(f"fixtures: {args.lab_id} OK")
    else:
        print(f"fixtures: {args.lab_id} WRITTEN")
    return code


def _status(args: argparse.Namespace) -> int:
    root = Path(".").resolve()
    try:
        if args.write:
            write_status(root)
            print("status: written")
            return 0

        mismatches = check_status(root)
        for mismatch in mismatches:
            print(mismatch)
        if mismatches:
            print(f"status: {len(mismatches)} mismatches")
            return 1
        print("status: OK")
        return 0
    except StatusError as exc:
        print(f"status: {exc}")
        return 6


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "secrets-scan":
        return _secrets_scan(args)

    if args.command == "journal" and args.journal_command == "check":
        return _journal_check(Path(args.root).resolve())

    if args.command == "validate":
        return _validate(Path(".").resolve(), [Path(path) for path in args.paths])

    if args.command == "status":
        return _status(args)

    if args.command == "hwcheck":
        return _hwcheck(args)

    if args.command == "lab" and args.lab_command == "new-run":
        return _lab_new_run(args)

    if args.command == "lab" and args.lab_command == "run":
        return _lab_run(args)

    if args.command == "lab" and args.lab_command == "estimate":
        return _lab_estimate(args)

    if args.command == "lab" and args.lab_command == "postmortem-check":
        return _lab_postmortem(args)

    if args.command == "labs" and args.labs_command == "list":
        return _labs_list(Path(".").resolve())

    if args.command == "labs" and args.labs_command == "check-tiers":
        return _labs_check_tiers(Path(".").resolve(), args.path)

    if args.command == "dataset" and args.dataset_command == "build":
        return _dataset_build(args)

    if args.command == "fixtures" and args.fixtures_command == "synth":
        return _fixtures_synth(args)

    return 0


def _entry() -> None:
    raise SystemExit(main())
