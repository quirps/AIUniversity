from __future__ import annotations

from pathlib import Path

from aiu.secrets_scan import scan_paths


def test_openrouter_key_is_found_and_masked(tmp_path: Path) -> None:
    key = "sk-or-v1-" + "a" * 20
    path = tmp_path / "leak.txt"
    path.write_text(f"token={key}\n", encoding="utf-8")

    findings = scan_paths([path])

    assert len(findings) == 1
    assert findings[0].rule == "openrouter_key"
    assert key not in findings[0].excerpt


def test_forbidden_env_file(tmp_path: Path) -> None:
    path = tmp_path / ".env"
    path.write_text("OPENROUTER_API_KEY=secret\n", encoding="utf-8")

    findings = scan_paths([path])

    assert any(finding.rule == "forbidden_file" for finding in findings)


def test_env_example_with_empty_key_is_clean(tmp_path: Path) -> None:
    path = tmp_path / ".env.example"
    path.write_text("OPENROUTER_API_KEY=\n", encoding="utf-8")

    assert scan_paths([path]) == []


def test_oversize_file_is_flagged(tmp_path: Path) -> None:
    path = tmp_path / "big.txt"
    path.write_bytes(b"x" * 5_000_001)

    findings = scan_paths([path])

    assert any(finding.rule == "oversize" for finding in findings)


def test_clean_file_has_no_findings(tmp_path: Path) -> None:
    path = tmp_path / "clean.txt"
    path.write_text("hello world\n", encoding="utf-8")

    assert scan_paths([path]) == []


def test_documented_example_secret_is_allowed(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text("sk-or-v1-abcdefghijklmnopqrstuvwx\n", encoding="utf-8")

    assert scan_paths([path]) == []
