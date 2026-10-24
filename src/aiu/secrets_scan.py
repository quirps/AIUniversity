from __future__ import annotations

import fnmatch
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

MAX_FILE_BYTES = 5_000_000
ALLOWED = [".env.example"]
FORBIDDEN_GLOBS = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.gguf",
    "*.safetensors",
    "*.pt",
    "*.bin",
    "*.onnx",
]

SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "openrouter_key": re.compile(r"sk-or-v1-[A-Za-z0-9]{16,}"),
    "generic_sk_key": re.compile(r"\bsk-(?!or-v1-)[A-Za-z0-9_-]{20,}"),
    "bearer_token": re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    "env_assignment": re.compile(r"^\s*OPENROUTER_API_KEY\s*=\s*\S+", re.MULTILINE),
}

# Documented dummy values that appear in the project's own tests and specs.
# These are not credentials and must not be treated as leaks.
EXAMPLE_SECRETS = frozenset({"sk-or-v1-abcdefghijklmnopqrstuvwx"})


@dataclass(frozen=True)
class Finding:
    path: str
    line: int | None
    rule: str
    excerpt: str


def _mask(value: str) -> str:
    if len(value) <= 6:
        return value
    return value[:6] + "..." + "*" * (len(value) - 6)


def _display_path(path: Path) -> str:
    return path.as_posix()


def _is_allowed(path: Path) -> bool:
    return path.name in ALLOWED


def _forbidden_rule(path: Path) -> str | None:
    if _is_allowed(path):
        return None
    candidates = [path.name, path.as_posix()]
    for pattern in FORBIDDEN_GLOBS:
        if any(fnmatch.fnmatch(candidate, pattern) for candidate in candidates):
            return "forbidden_file"
    return None


def _is_binary(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return b"\x00" in handle.read(8192)
    except OSError:
        return False


def scan_paths(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(paths, key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        display = _display_path(path)

        forbidden = _forbidden_rule(path)
        if forbidden:
            findings.append(Finding(display, None, forbidden, path.name))
            continue

        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > MAX_FILE_BYTES:
            findings.append(Finding(display, None, "oversize", f"{size} bytes"))
            continue
        if _is_binary(path):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            for rule, pattern in SECRET_PATTERNS.items():
                for match in pattern.finditer(line):
                    value = match.group(0)
                    if value in EXAMPLE_SECRETS:
                        continue
                    findings.append(Finding(display, line_number, rule, _mask(value)))

    return sorted(findings, key=lambda item: (item.path, item.line or 0, item.rule))


def _git_paths(root: Path, *args: str) -> list[Path]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        root / line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def staged_paths(root: Path) -> list[Path]:
    return _git_paths(root, "diff", "--cached", "--name-only", "--diff-filter=ACM")


def all_tracked_and_untracked(root: Path) -> list[Path]:
    return _git_paths(root, "ls-files", "-co", "--exclude-standard")
