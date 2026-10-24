from __future__ import annotations

import argparse
from pathlib import Path

from aiu import __version__
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "secrets-scan":
        return _secrets_scan(args)

    return 0


def _entry() -> None:
    raise SystemExit(main())
