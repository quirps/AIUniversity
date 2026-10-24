from __future__ import annotations

import hashlib
import re
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

from aiu.config import ConfigError

RUN_ID_RE = re.compile(r"^[0-9]{8}T[0-9]{6}Z-(fixture|live)-[0-9a-f]{6}$")


class PredictionGateError(Exception):
    pass


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def new_run_id(
    mode: str,
    now: datetime | None = None,
    rand_hex: str | None = None,
) -> str:
    if mode not in ("fixture", "live"):
        raise ValueError(f"unknown mode: {mode}")
    moment = _as_utc(now or datetime.now(timezone.utc))
    suffix = rand_hex or secrets.token_hex(3)
    return f"{moment.strftime('%Y%m%dT%H%M%SZ')}-{mode}-{suffix}"


def default_out_dir(mode: str) -> Path:
    if mode == "fixture":
        return Path(".runs")
    if mode == "live":
        return Path("experiments")
    raise ValueError(f"unknown mode: {mode}")


def run_dir(out: Path, lab_id: str, run_id: str) -> Path:
    return out / lab_id / run_id


def create_run(
    root: Path,
    lab_id: str,
    mode: str,
    out: Path | None,
) -> tuple[str, Path]:
    manifest = root / "labs" / lab_id / "manifest.yaml"
    if not manifest.is_file():
        raise ConfigError(f"missing manifest for lab {lab_id}")

    template_path = root / "experiments" / "_template" / "prediction.md"
    if not template_path.is_file():
        raise ConfigError("missing prediction template")

    run_id = new_run_id(mode)
    out_dir = root / (out if out is not None else default_out_dir(mode))
    rdir = run_dir(out_dir, lab_id, run_id)
    rdir.mkdir(parents=True, exist_ok=False)

    template = template_path.read_text(encoding="utf-8")
    text = (
        template.replace("<run_id>", run_id)
        .replace("<lab_id>", lab_id)
        .replace("<fixture|live>", mode)
    )
    (rdir / "prediction.md").write_text(text, encoding="utf-8")
    return run_id, rdir


def _git_root(path: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=path.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    root = result.stdout.strip()
    if result.returncode != 0 or not root:
        raise ConfigError("prediction is not in a git repository")
    return Path(root).resolve()


def prediction_commit_time(path: Path) -> datetime:
    path = path.resolve()
    root = _git_root(path)
    rel = path.relative_to(root).as_posix()

    result = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", rel],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    stamp = result.stdout.strip()
    if result.returncode != 0 or not stamp:
        raise ConfigError("prediction is not committed")

    status = subprocess.run(
        ["git", "status", "--porcelain", "--", rel],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if status.stdout.strip():
        raise ConfigError("prediction has uncommitted changes")

    try:
        return _as_utc(datetime.fromisoformat(stamp))
    except ValueError as exc:
        raise ConfigError("invalid prediction commit timestamp") from exc


def check_prediction(
    path: Path,
    metric_names: set[str],
    now: datetime,
) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise PredictionGateError("missing prediction front matter")

    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise PredictionGateError("unterminated prediction front matter") from exc

    try:
        data = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as exc:
        raise PredictionGateError(f"invalid prediction front matter: {exc}") from exc
    if not isinstance(data, dict):
        raise PredictionGateError("prediction front matter must be a mapping")

    written_raw = data.get("written_at")
    if isinstance(written_raw, datetime):
        written_at = _as_utc(written_raw)
    elif isinstance(written_raw, str) and written_raw.strip():
        try:
            written_at = _as_utc(
                datetime.fromisoformat(written_raw.replace("Z", "+00:00"))
            )
        except ValueError as exc:
            raise PredictionGateError(
                "written_at is not a valid ISO-8601 timestamp"
            ) from exc
    else:
        raise PredictionGateError("written_at is required")

    now_utc = _as_utc(now)
    if written_at > now_utc:
        raise PredictionGateError("written_at is in the future")

    predicted = data.get("predicted_metrics")
    if not isinstance(predicted, dict) or not predicted:
        raise PredictionGateError("predicted_metrics must be a non-empty mapping")
    unknown = set(predicted) - set(metric_names)
    if unknown:
        raise PredictionGateError(f"unknown metrics: {sorted(unknown)}")

    commit_time = prediction_commit_time(path)
    if written_at > commit_time:
        raise PredictionGateError("written_at is after the prediction commit")
    if commit_time >= now_utc:
        raise PredictionGateError("prediction was committed at or after run start")

    return data


def freeze_prediction(rdir: Path) -> str:
    digest = hashlib.sha256((rdir / "prediction.md").read_bytes()).hexdigest()
    (rdir / "prediction.sha256").write_text(digest + "\n", encoding="utf-8")
    return digest


def prediction_unchanged(rdir: Path) -> bool:
    hash_path = rdir / "prediction.sha256"
    if not hash_path.is_file():
        return False
    expected = hash_path.read_text(encoding="utf-8").strip()
    actual = hashlib.sha256((rdir / "prediction.md").read_bytes()).hexdigest()
    return actual == expected
