from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import yaml

from aiu import __version__
from aiu.clients.base import LLMClient, MissingFixture
from aiu.clients.deepseek import api_key_from_env as deepseek_api_key_from_env
from aiu.clients.fixture import FixtureClient
from aiu.clients.live import LiveClient
from aiu.clients.openrouter import (
    AuthError,
    ProviderError,
    api_key_from_env,
)
from aiu.config import Config, ConfigError, load_config, resolve_role
from aiu.cost import (
    CostCapExceeded,
    CostGuard,
    actual_cost,
    cost_record,
    effective_cap,
    estimate_call,
    price_for,
)
from aiu.hardware import check as check_hardware
from aiu.hardware import probe
from aiu.labs.base import load_lab
from aiu.metrics import proportion
from aiu.models import CallResult, Item
from aiu.runs import (
    PredictionGateError,
    check_prediction,
    default_out_dir,
    freeze_prediction,
    run_dir,
)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return _as_utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def load_manifest(root: Path, lab_id: str) -> dict:
    path = root / "labs" / lab_id / "manifest.yaml"
    if not path.is_file():
        raise ConfigError(f"missing manifest for lab {lab_id}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigError(f"invalid manifest for lab {lab_id}")
    return data


def load_items(path: Path, limit: int | None) -> list[Item]:
    if not path.is_file():
        raise ConfigError(f"missing dataset: {path}")
    if limit is not None and limit < 0:
        raise ConfigError("limit must not be negative")

    items = [
        Item.model_validate(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    items.sort(key=lambda item: item.id)
    if limit is not None:
        items = items[:limit]
    return items


def evaluate(conds: list[dict], metrics: dict, rule: str) -> bool | None:
    if not conds:
        return None

    outcomes: list[bool] = []
    for condition in conds:
        name = condition["metric"]
        if name not in metrics or metrics[name] is None:
            return None
        actual = metrics[name]
        target = condition["value"]
        op = condition["op"]
        if op == ">=":
            outcomes.append(actual >= target)
        elif op == "<=":
            outcomes.append(actual <= target)
        elif op == ">":
            outcomes.append(actual > target)
        elif op == "<":
            outcomes.append(actual < target)
        elif op == "==":
            outcomes.append(actual == target)
        else:
            raise ConfigError(f"unknown condition operator: {op}")

    return all(outcomes) if rule == "all" else any(outcomes)


def _prepare(
    root: Path,
    lab_id: str,
    limit: int | None,
):
    manifest = load_manifest(root, lab_id)
    cfg = load_config(root)
    items = load_items(root / manifest["dataset"]["path"], limit)
    impl_cls = load_lab(lab_id)
    if impl_cls is None:
        raise ConfigError(f"lab not registered: {lab_id}")
    impl = impl_cls()
    calls = impl.plan(items, manifest, cfg)
    return manifest, cfg, items, impl, calls


def _write_config(
    rdir: Path,
    root: Path,
    lab_id: str,
    run_id: str,
    mode: str,
    cfg: Config,
    manifest: dict,
    roles: list[str],
    limit: int | None,
    hw: dict,
    now: datetime,
) -> None:
    manifest_path = root / "labs" / lab_id / "manifest.yaml"
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    role_config = {}
    for role in roles:
        resolved = resolve_role(cfg, role, mode)
        role_config[role] = {
            "model_id": resolved.model_id,
            "family": resolved.family,
            "provider": resolved.provider,
        }

    procedure = manifest["procedure"]
    _write_json(
        rdir / "config.json",
        {
            "lab_id": lab_id,
            "run_id": run_id,
            "mode": mode,
            "manifest_sha256": manifest_sha,
            "roles": role_config,
            "temperature": procedure["temperature"],
            "seed": procedure["seed"],
            "max_tokens": procedure["max_tokens"],
            "samples_per_call": procedure["samples_per_call"],
            "limit": limit,
            "started_at": _iso(now),
            "aiu_version": __version__,
            "hw": hw,
        },
    )


def _write_cost(
    rdir: Path,
    cfg: Config,
    mode: str,
    estimated_usd: float,
    actual_usd: float,
    provider_reported_usd: float | None,
    calls: int,
    prompt_tokens: int,
    completion_tokens: int,
    cap_usd: float,
    aborted: bool,
) -> None:
    record = cost_record(
        estimated_usd=estimated_usd,
        actual_usd=actual_usd,
        provider_reported_usd=provider_reported_usd,
        calls=calls,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cap_usd=cap_usd,
        aborted=aborted,
        pricing_retrieved_at=cfg.pricing.retrieved_at,
        mode=mode,
    )
    record["pricing_retrieved_at"] = (
        cfg.pricing.retrieved_at.isoformat() if cfg.pricing.retrieved_at else None
    )
    _write_json(rdir / "cost.json", record)


def _write_result(
    rdir: Path,
    status: str,
    hypothesis_supported: bool | None,
    validity_passed: bool | None,
    evidence_class: str,
    n_calls: int,
    error: str | None,
    now: datetime,
) -> None:
    _write_json(
        rdir / "result.json",
        {
            "status": status,
            "hypothesis_supported": hypothesis_supported,
            "validity_passed": validity_passed,
            "evidence_class": evidence_class,
            "finished_at": _iso(now),
            "n_calls": n_calls,
            "error": error,
        },
    )


def _write_postmortem(rdir: Path, root: Path, manifest: dict, lab_id: str, run_id: str) -> None:
    template = root / manifest["post_mortem_template"]
    if not template.is_file():
        raise ConfigError("missing post-mortem template")
    text = (
        template.read_text(encoding="utf-8")
        .replace("<run_id>", run_id)
        .replace("<lab_id>", lab_id)
    )
    (rdir / "postmortem.md").write_text(text, encoding="utf-8")


def _write_aborted(
    rdir: Path,
    cfg: Config,
    mode: str,
    estimated: float,
    actual: float,
    calls: int,
    prompt_tokens: int,
    completion_tokens: int,
    provider: float | None,
    cap: float,
    now: datetime,
    error: str,
) -> None:
    responses = rdir / "responses.jsonl"
    if not responses.exists():
        responses.write_text("", encoding="utf-8")
    _write_cost(
        rdir, cfg, mode, estimated, actual, provider, calls,
        prompt_tokens, completion_tokens, cap, aborted=True,
    )
    _write_result(rdir, "aborted_cost", None, None, "assumed", calls, error, now)


def _write_failed(
    rdir: Path,
    cfg: Config,
    mode: str,
    estimated: float,
    actual: float,
    calls: int,
    prompt_tokens: int,
    completion_tokens: int,
    provider: float | None,
    cap: float,
    now: datetime,
    error: str,
) -> None:
    _write_cost(
        rdir, cfg, mode, estimated, actual, provider, calls,
        prompt_tokens, completion_tokens, cap, aborted=False,
    )
    _write_result(rdir, "failed", None, None, "assumed", calls, error, now)


def _run_lab(
    root: Path,
    lab_id: str,
    run_id: str,
    mode: str,
    cap: float | None,
    limit: int | None,
    record: bool,
    out: Path | None,
    client_factory: Callable[[str], LLMClient] | None,
    now: datetime | None,
) -> int:
    if mode not in ("fixture", "live"):
        raise ConfigError(f"unknown mode: {mode}")
    if record and mode != "live":
        raise ConfigError("--record is only valid in live mode")

    manifest = load_manifest(root, lab_id)
    if manifest.get("status") != "runnable":
        raise ConfigError(f"lab is not runnable: {lab_id}")

    cfg = load_config(root)
    items = load_items(root / manifest["dataset"]["path"], limit)
    impl_cls = load_lab(lab_id)
    if impl_cls is None:
        raise ConfigError(f"lab not registered: {lab_id}")
    impl = impl_cls()
    calls = impl.plan(items, manifest, cfg)
    roles = sorted({call.role for call in calls})

    if mode == "live":
        providers = set()
        for role in roles:
            resolved = resolve_role(cfg, role, "live")
            price_for(cfg, role, "live")
            providers.add(resolved.provider)
        if "openrouter" in providers:
            api_key_from_env()
        if "deepseek" in providers:
            deepseek_api_key_from_env()

    out_dir = root / (out if out is not None else default_out_dir(mode))
    rdir = run_dir(out_dir, lab_id, run_id)
    prediction_path = rdir / "prediction.md"
    if not prediction_path.is_file():
        raise PredictionGateError("missing prediction.md")

    now_utc = _as_utc(now or datetime.now(timezone.utc))
    metric_names = {metric["name"] for metric in manifest.get("metric", [])}
    check_prediction(prediction_path, metric_names, now_utc)
    freeze_prediction(rdir)

    hw = check_hardware(
        manifest["hardware_tier"],
        probe(root),
        manifest.get("local_requirements"),
    )
    if not hw["passed"]:
        return 5

    cap_usd = effective_cap(cfg, cap, "lab")
    prices = {role: price_for(cfg, role, mode) for role in roles}
    estimates = [estimate_call(call, prices[call.role]) for call in calls]
    guard = CostGuard(cap_usd)

    try:
        guard.preflight(estimates)
    except CostCapExceeded as exc:
        _write_aborted(rdir, cfg, mode, sum(estimates), 0.0, 0, 0, 0, None, cap_usd, now_utc, str(exc))
        return 4

    _write_config(rdir, root, lab_id, run_id, mode, cfg, manifest, roles, limit, hw, now_utc)

    if client_factory is not None:
        client = client_factory(mode)
    elif mode == "fixture":
        fixture_path = manifest.get("fixtures", {}).get("path")
        if not fixture_path:
            raise ConfigError("missing fixture path")
        client = FixtureClient(root / fixture_path)
    else:
        client = LiveClient(cfg)

    results: list[CallResult] = []
    prompt_tokens = 0
    completion_tokens = 0
    provider_total: float | None = None
    actual_total = 0.0

    responses_path = rdir / "responses.jsonl"
    with responses_path.open("w", encoding="utf-8") as responses:
        for call, estimate in zip(calls, estimates):
            try:
                guard.before_call(estimate)
            except CostCapExceeded as exc:
                _write_aborted(
                    rdir, cfg, mode, sum(estimates), actual_total, len(results),
                    prompt_tokens, completion_tokens, provider_total, cap_usd,
                    _as_utc(datetime.now(timezone.utc)), str(exc),
                )
                return 4

            model_id = resolve_role(cfg, call.role, mode).model_id
            try:
                result = client.complete(call, model_id)
            except MissingFixture as exc:
                _write_failed(
                    rdir, cfg, mode, sum(estimates), actual_total, len(results),
                    prompt_tokens, completion_tokens, provider_total, cap_usd,
                    _as_utc(datetime.now(timezone.utc)), str(exc),
                )
                return 3
            except AuthError as exc:
                _write_failed(
                    rdir, cfg, mode, sum(estimates), actual_total, len(results),
                    prompt_tokens, completion_tokens, provider_total, cap_usd,
                    _as_utc(datetime.now(timezone.utc)), str(exc),
                )
                return 6
            except ProviderError as exc:
                _write_failed(
                    rdir, cfg, mode, sum(estimates), actual_total, len(results),
                    prompt_tokens, completion_tokens, provider_total, cap_usd,
                    _as_utc(datetime.now(timezone.utc)), str(exc),
                )
                return 1

            responses.write(result.model_dump_json() + "\n")
            results.append(result)
            prompt_tokens += result.prompt_tokens
            completion_tokens += result.completion_tokens
            if result.provider_reported_usd is not None:
                provider_total = (provider_total or 0.0) + result.provider_reported_usd
            call_cost = (
                0.0
                if mode == "fixture"
                else actual_cost(result.prompt_tokens, result.completion_tokens, prices[call.role])
            )
            actual_total += call_cost
            guard.record(call_cost)

    metrics = impl.score(items, results, manifest)
    hypothesis_supported = evaluate(
        manifest["pass_fail"]["conditions"],
        metrics,
        manifest["pass_fail"]["rule"],
    )
    validity_passed = evaluate(manifest.get("validity_checks", []), metrics, "all")
    evidence_class = (
        "measured"
        if mode == "live" and results and all(result.source == "live" for result in results)
        else "assumed"
    )

    proportions = {
        name: proportion(round(value * len(items)), len(items))
        for name, value in metrics.items()
        if isinstance(value, (int, float)) and 0 <= value <= 1 and items
    }
    _write_json(
        rdir / "metrics.json",
        {
            "metrics": metrics,
            "proportions": proportions,
            "evidence_class": evidence_class,
        },
    )
    _write_cost(
        rdir, cfg, mode, sum(estimates), actual_total, provider_total,
        len(results), prompt_tokens, completion_tokens, cap_usd, aborted=False,
    )
    _write_result(
        rdir, "completed", hypothesis_supported, validity_passed,
        evidence_class, len(results), None, _as_utc(datetime.now(timezone.utc)),
    )
    _write_postmortem(rdir, root, manifest, lab_id, run_id)

    if record:
        fixture_path = root / manifest["fixtures"]["path"]
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        with fixture_path.open("w", encoding="utf-8") as fixtures:
            for result in results:
                recorded = result.model_copy(update={"source": "fixture_recorded"})
                fixtures.write(recorded.model_dump_json() + "\n")

    print(f"run_id={run_id} status=completed cost_usd={actual_total:.4f}")
    return 0


def run_lab(
    root: Path,
    lab_id: str,
    run_id: str,
    mode: str,
    cap: float | None,
    limit: int | None,
    record: bool,
    out: Path | None,
    client_factory: Callable[[str], LLMClient] | None = None,
    now: datetime | None = None,
) -> int:
    try:
        return _run_lab(
            root, lab_id, run_id, mode, cap, limit, record, out,
            client_factory, now,
        )
    except ConfigError as exc:
        print(f"lab run: {exc}")
        return 6
    except PredictionGateError as exc:
        print(f"lab run: {exc}")
        return 7


def estimate_summary(
    root: Path,
    lab_id: str,
    limit: int | None,
    mode: str = "live",
) -> dict:
    manifest = load_manifest(root, lab_id)
    cfg = load_config(root)
    items = load_items(root / manifest["dataset"]["path"], limit)
    impl_cls = load_lab(lab_id)
    if impl_cls is None:
        raise ConfigError(f"lab not registered: {lab_id}")
    calls = impl_cls().plan(items, manifest, cfg)

    total = 0.0
    all_pinned = True
    for call in calls:
        if mode == "live":
            try:
                price = price_for(cfg, call.role, "live")
            except ConfigError:
                price = cfg.pricing.fixture_defaults
                all_pinned = False
        else:
            price = cfg.pricing.fixture_defaults
            all_pinned = False
        total += estimate_call(call, price)

    return {
        "usd": total,
        "calls": len(calls),
        "cap_usd": cfg.caps.per_lab_usd,
        "basis": "pinned" if all_pinned else "assumed",
    }


def estimate_lab(
    root: Path,
    lab_id: str,
    limit: int | None,
    mode: str = "live",
) -> float:
    return estimate_summary(root, lab_id, limit, mode)["usd"]
