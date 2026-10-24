from __future__ import annotations

import argparse
from pathlib import Path

from aiu import __version__
from aiu.journal import check_append_only, head_content
from aiu.secrets_scan import all_tracked_and_untracked, scan_paths, staged_paths


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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "secrets-scan":
        return _secrets_scan(args)

    if args.command == "journal" and args.journal_command == "check":
        return _journal_check(Path(args.root).resolve())

    return 0


def _entry() -> None:
    raise SystemExit(main())
