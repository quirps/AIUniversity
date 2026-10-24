from __future__ import annotations

import argparse

from aiu import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aiu")
    parser.add_argument(
        "--version",
        action="version",
        version=f"aiu {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    return 0


def _entry() -> None:
    raise SystemExit(main())
