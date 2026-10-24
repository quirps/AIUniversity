from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import yaml

from aiu.config import ConfigError, load_config
from aiu.cost import effective_cap
from aiu.runner import estimate_lab, load_manifest, run_lab
from aiu.runs import create_run, default_out_dir

SMOKE_PLAN: list[tuple[str, int | None]] = [
    ("L-003", None),
    ("E9", 20),
    ("E2", 20),
    ("E4", 20),
    ("E5", 20),
]


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return _as_utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_prediction(
    rdir: Path,
    lab_id: str,
    run_id: str,
    mode: str,
    metric_name: str,
    now: datetime,
) -> None:
    front = {
        "run_id": run_id,
        "lab_id": lab_id,
        "mode": mode,
        "author": "smoke",
        "written_at": _iso(now - timedelta(seconds=60)),
        "smoke": True,
        "predicted_metrics": {metric_name: None},
    }
    text = (
        "---\n"
        + yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
        + "---\n\n"
        + f"# Smoke run - {run_id}\n\n"
        + "Machine-generated smoke prediction. No learner prediction is implied.\n"
    )
    (rdir / "prediction.md").write_text(text, encoding="utf-8")


def _read_run(rdir: Path) -> tuple[str, float]:
    result_path = rdir / "result.json"
    cost_path = rdir / "cost.json"
    status = "failed"
    cost = 0.0
    if result_path.is_file():
        status = json.loads(result_path.read_text(encoding="utf-8")).get(
            "status", "failed"
        )
    if cost_path.is_file():
        cost = float(
            json.loads(cost_path.read_text(encoding="utf-8")).get("actual_usd", 0.0)
            or 0.0
        )
    return status, cost


def _write_summary(
    out: Path,
    now: datetime,
    mode: str,
    labs: list[dict],
    total_cost: float,
    cap: float,
) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"smoke-{now.strftime('%Y%m%dT%H%M%SZ')}.json"
    payload = {
        "mode": mode,
        "labs": labs,
        "total_cost_usd": round(total_cost, 4),
        "cap_usd": cap,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def run_smoke(
    root: Path,
    mode: str,
    cap: float | None,
    now: datetime | None = None,
    client_factory: Callable[[str], object] | None = None,
) -> int:
    cfg = load_config(root)
    total_cap = effective_cap(cfg, cap, "smoke")
    moment = _as_utc(now or datetime.now(timezone.utc))
    out = root / default_out_dir(mode)

    estimates = [
        estimate_lab(root, lab_id, limit, mode)
        for lab_id, limit in SMOKE_PLAN
    ]
    if sum(estimates) > total_cap:
        print(
            f"smoke: {mode} total_cost_usd=0.0000 cap_usd={total_cap:.2f} FAIL"
        )
        return 4

    labs: list[dict] = []
    spent = 0.0
    code = 0

    for lab_id, limit in SMOKE_PLAN:
        manifest = load_manifest(root, lab_id)
        metric_name = manifest["metric"][0]["name"]
        run_id, rdir = create_run(root, lab_id, mode, None)
        _write_prediction(rdir, lab_id, run_id, mode, metric_name, moment)

        lab_cap = min(cfg.caps.per_lab_usd, total_cap - spent)
        code = run_lab(
            root,
            lab_id,
            run_id,
            mode,
            lab_cap,
            limit,
            False,
            None,
            client_factory=client_factory,
            now=moment,
        )
        status, cost = _read_run(rdir)
        labs.append(
            {
                "lab_id": lab_id,
                "run_id": run_id,
                "status": status,
                "cost_usd": round(cost, 4),
            }
        )
        spent += cost
        print(f"{lab_id} {status} cost_usd={cost:.4f}")
        if code != 0:
            break

    _write_summary(out, moment, mode, labs, spent, total_cap)
    verdict = "OK" if code == 0 else "FAIL"
    print(
        f"smoke: {mode} total_cost_usd={spent:.4f} cap_usd={total_cap:.2f} {verdict}"
    )
    return code
