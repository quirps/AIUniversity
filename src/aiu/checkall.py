from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from aiu.status import check_status, write_status


def _load_manifest_status(path: Path) -> str | None:
    import yaml

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(data, dict):
        return None
    status = data.get("status")
    return status if isinstance(status, str) else None


def _lab_dirs(root: Path) -> list[Path]:
    base = root / "labs"
    if not base.is_dir():
        return []
    return sorted(path for path in base.iterdir() if path.is_dir())


def _generator_labs(root: Path) -> list[str]:
    labs: list[str] = []
    for lab_dir in _lab_dirs(root):
        slug = lab_dir.name.lower().replace("-", "")
        if (root / "src" / "aiu" / "generators" / f"{slug}.py").is_file():
            labs.append(lab_dir.name)
    return labs


def _runnable_labs(root: Path) -> list[str]:
    labs: list[str] = []
    for lab_dir in _lab_dirs(root):
        manifest = lab_dir / "manifest.yaml"
        if _load_manifest_status(manifest) == "runnable":
            labs.append(lab_dir.name)
    return labs


def checks(root: Path) -> list[list[str]]:
    checks_list: list[list[str]] = [
        ["secrets-scan"],
        ["journal", "check"],
        ["validate"],
        ["labs", "check-tiers"],
        ["provenance", "check"],
        ["traceability", "check", "--require-all"],
    ]
    for lab_id in _generator_labs(root):
        checks_list.append(["dataset", "build", lab_id, "--check"])
    for lab_id in _runnable_labs(root):
        checks_list.append(["fixtures", "synth", lab_id, "--check"])
    checks_list.append(["smoke", "--mode", "fixture"])
    return checks_list


def _pytest_command() -> list[str]:
    import shutil

    uv = shutil.which("uv")
    if uv:
        return [uv, "run", "pytest"]
    return [sys.executable, "-m", "pytest"]


def _count_tests(output: str, returncode: int) -> tuple[int, int]:
    passed_match = re.search(r"(\d+)\s+passed", output)
    failed_match = re.search(r"(\d+)\s+failed", output)
    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0
    if returncode != 0 and failed == 0:
        failed = 1
    return passed, failed


def _write_tests(root: Path, passed: int, failed: int) -> None:
    path = root / "status.json"
    status = json.loads(path.read_text(encoding="utf-8"))
    status["tests"] = {
        "passed": passed,
        "failed": failed,
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_all(root: Path) -> int:
    from aiu.cli import main

    planned = checks(root)
    succeeded = 0
    for argv in planned:
        code = main(argv)
        status = "OK" if code == 0 else "FAIL"
        print(f"check-all: {status} {' '.join(argv)}")
        if code == 0:
            succeeded += 1

    pytest_result = subprocess.run(
        _pytest_command(),
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    output = (pytest_result.stdout or "") + (pytest_result.stderr or "")
    passed, failed = _count_tests(output, pytest_result.returncode)
    tests_ok = pytest_result.returncode == 0 and failed == 0 and passed > 0
    print(
        f"check-all: {'OK' if tests_ok else 'FAIL'} pytest "
        f"(passed={passed} failed={failed})"
    )
    if tests_ok:
        succeeded += 1

    total = len(planned) + 1
    try:
        _write_tests(root, passed, failed)
        write_status(root)
        status_problems = check_status(root)
    except Exception as exc:  # noqa: BLE001 - report, do not hide a status failure
        print(f"check-all: FAIL status ({exc})")
        status_problems = [str(exc)]
    if status_problems:
        for problem in status_problems:
            print(f"check-all: status problem: {problem}")
    else:
        succeeded += 1
        total += 1

    print(f"check-all: {succeeded}/{total} checks OK")
    return 0 if succeeded == total else 1
