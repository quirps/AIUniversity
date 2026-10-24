from __future__ import annotations

from pathlib import Path

import yaml

TIERS = {"API_ONLY", "LOCAL_SMALL_GPU_6GB", "LOCAL_CPU_TINY"}
LOCAL_TIERS = {"LOCAL_SMALL_GPU_6GB", "LOCAL_CPU_TINY"}


def manifest_paths(root: Path, path: Path | None = None) -> list[Path]:
    if path is not None:
        target = path if path.is_absolute() else root / path
        if target.is_dir():
            return sorted(target.glob("*/manifest.yaml"))
        return [target]

    base = root / "labs"
    if not base.is_dir():
        return []
    return sorted(base.glob("*/manifest.yaml"))


def _load(path: Path) -> tuple[dict | None, str | None]:
    if not path.is_file():
        return None, f"{path.as_posix()}: manifest not found"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, f"{path.as_posix()}: YAML error: {exc}"
    if not isinstance(data, dict):
        return None, f"{path.as_posix()}: manifest is not a mapping"
    return data, None


def check_tiers(root: Path, path: Path | None = None) -> list[str]:
    problems: list[str] = []

    for manifest_path in manifest_paths(root, path):
        manifest, error = _load(manifest_path)
        if error is not None:
            problems.append(error)
            continue

        tier = manifest.get("hardware_tier")
        if tier not in TIERS:
            problems.append(
                f"{manifest_path.as_posix()}: unknown hardware_tier {tier!r}"
            )
            continue

        if tier not in LOCAL_TIERS:
            continue

        if not isinstance(manifest.get("local_requirements"), dict):
            problems.append(
                f"{manifest_path.as_posix()}: local tier requires local_requirements"
            )

        fallback = manifest.get("api_fallback")
        if not isinstance(fallback, dict) or not isinstance(
            fallback.get("lab_id"), str
        ):
            problems.append(
                f"{manifest_path.as_posix()}: local tier requires api_fallback.lab_id"
            )
            continue

        lab_id = fallback["lab_id"]
        fallback_path = root / "labs" / lab_id / "manifest.yaml"
        fallback_manifest, fallback_error = _load(fallback_path)
        if fallback_error is not None:
            problems.append(
                f"{manifest_path.as_posix()}: fallback {lab_id}: {fallback_error}"
            )
            continue

        if fallback_manifest.get("hardware_tier") != "API_ONLY":
            problems.append(
                f"{manifest_path.as_posix()}: fallback {lab_id} must be API_ONLY"
            )

        fixtures = fallback_manifest.get("fixtures")
        provenance = fixtures.get("provenance") if isinstance(fixtures, dict) else None
        if provenance == "none" or provenance is None:
            problems.append(
                f"{manifest_path.as_posix()}: fallback {lab_id} has no fixtures"
            )

    return problems


def list_labs(root: Path) -> list[tuple[str, str, str, str]]:
    labs: list[tuple[str, str, str, str]] = []
    for manifest_path in manifest_paths(root):
        manifest, error = _load(manifest_path)
        if error is not None or manifest is None:
            continue
        labs.append(
            (
                str(manifest.get("id", "")),
                str(manifest.get("status", "")),
                str(manifest.get("hardware_tier", "")),
                str(manifest.get("title", "")),
            )
        )
    return sorted(labs, key=lambda row: row[0])
