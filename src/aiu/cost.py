from __future__ import annotations

import math
from datetime import date
from typing import Literal

from aiu.config import Config, ConfigError, Price, resolve_role
from aiu.models import PlannedCall


class CostCapExceeded(Exception):
    pass


def estimate_call(call: PlannedCall, price: Price) -> float:
    input_bytes = sum(len(message.content.encode("utf-8")) for message in call.messages)
    estimated_input_tokens = math.ceil(input_bytes / 3)
    estimated_output_tokens = call.max_tokens
    return (
        estimated_input_tokens * price.input_per_mtok
        + estimated_output_tokens * price.output_per_mtok
    ) / 1_000_000


def actual_cost(prompt_tokens: int, completion_tokens: int, price: Price) -> float:
    return (
        prompt_tokens * price.input_per_mtok
        + completion_tokens * price.output_per_mtok
    ) / 1_000_000


def price_for(cfg: Config, role: str, mode: str) -> Price:
    if mode == "fixture":
        return cfg.pricing.fixture_defaults
    if mode != "live":
        raise ConfigError(f"unknown mode: {mode}")

    role_config = resolve_role(cfg, role, "live")
    price = cfg.pricing.models.get(role_config.model_id)
    if price is None:
        raise ConfigError(f"no pinned price for model: {role_config.model_id}")
    return price


def effective_cap(
    cfg: Config,
    requested: float | None,
    kind: Literal["lab", "smoke"],
) -> float:
    if kind == "lab":
        default = cfg.caps.per_lab_usd
    elif kind == "smoke":
        default = cfg.caps.smoke_total_usd
    else:
        raise ConfigError(f"unknown cap kind: {kind}")

    if requested is None:
        return default
    if requested < 0:
        raise ConfigError("cap must not be negative")
    if requested > default:
        raise ConfigError(f"requested cap {requested} exceeds default {default}")
    return float(requested)


class CostGuard:
    def __init__(self, cap_usd: float):
        self.cap_usd = cap_usd
        self.actual_so_far = 0.0
        self.calls = 0

    def preflight(self, estimates: list[float]) -> None:
        if sum(estimates) > self.cap_usd:
            raise CostCapExceeded(
                f"estimated {sum(estimates):.6f} exceeds cap {self.cap_usd:.6f}"
            )

    def before_call(self, est_next: float) -> None:
        if self.actual_so_far + est_next > self.cap_usd:
            raise CostCapExceeded(
                f"actual {self.actual_so_far:.6f} + estimate {est_next:.6f} "
                f"exceeds cap {self.cap_usd:.6f}"
            )

    def record(self, usd: float) -> None:
        self.actual_so_far += usd
        self.calls += 1


def cost_record(
    *,
    estimated_usd: float,
    actual_usd: float,
    provider_reported_usd: float | None,
    calls: int,
    prompt_tokens: int,
    completion_tokens: int,
    cap_usd: float,
    aborted: bool,
    pricing_retrieved_at: date | None,
    mode: Literal["fixture", "live"],
) -> dict:
    return {
        "estimated_usd": estimated_usd,
        "actual_usd": actual_usd,
        "provider_reported_usd": provider_reported_usd,
        "calls": calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cap_usd": cap_usd,
        "aborted": aborted,
        "pricing_retrieved_at": pricing_retrieved_at,
        "mode": mode,
    }
