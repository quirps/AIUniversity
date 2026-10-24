from __future__ import annotations

import subprocess
from pathlib import Path


def _normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def head_content(root: Path, rel: str = "JOURNAL.md") -> str | None:
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", errors="replace")


def check_append_only(old: str | None, new: str) -> bool:
    if old is None:
        return True
    return _normalize(new).startswith(_normalize(old))
