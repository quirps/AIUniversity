from __future__ import annotations

from pathlib import Path

import pytest

from aiu.config import ConfigError, Price, load_config
from aiu.cost import (
    CostCapExceeded,
    CostGuard,
    actual_cost,
    cost_record,
    effective_cap,
    estimate_call,
    price_for,
)
from aiu.models import Message, PlannedCall

ROOT = Path(__file__).resolve().parents[1]


def _call(content: str = "x" * 300) -> PlannedCall:
    return PlannedCall(
        call_key="k",
        item_id="i1",
        condition="base",
        role="cheap_a",
        sample=0,
        messages=[Message(role="user", content=content)],
        temperature=0.0,
        max_tokens=16,
        seed=None,
    )


def test_estimate_call_uses_utf8_bytes_and_max_tokens() -> None:
    price = Price(input_per_mtok=0.5, output_per_mtok=1.5)
    expected = (100 * 0.5 + 16 * 1.5) / 1_000_000

    assert estimate_call(_call(), price) == pytest.approx(expected, abs=1e-15)


def test_actual_cost() -> None:
    price = Price(input_per_mtok=0.5, output_per_mtok=1.5)
    assert actual_cost(100, 16, price) == pytest.approx(
        (100 * 0.5 + 16 * 1.5) / 1_000_000,
        abs=1e-15,
    )


def test_preflight_over_cap_raises() -> None:
    guard = CostGuard(2.0)
    with pytest.raises(CostCapExceeded):
        guard.preflight([1.0, 1.01])


def test_mid_run_over_cap_raises() -> None:
    guard = CostGuard(2.0)
    guard.record(1.99)
    with pytest.raises(CostCapExceeded):
        guard.before_call(0.02)


def test_guard_records_calls_and_actuals() -> None:
    guard = CostGuard(2.0)
    guard.record(0.5)
    guard.record(0.25)

    assert guard.actual_so_far == 0.75
    assert guard.calls == 2


def test_effective_cap_rejects_request_above_default() -> None:
    cfg = load_config(ROOT)
    with pytest.raises(ConfigError):
        effective_cap(cfg, 3.0, "lab")


def test_effective_cap_accepts_lower_request() -> None:
    cfg = load_config(ROOT)
    assert effective_cap(cfg, 0.5, "lab") == 0.5


def test_effective_cap_uses_defaults() -> None:
    cfg = load_config(ROOT)
    assert effective_cap(cfg, None, "lab") == 2.0
    assert effective_cap(cfg, None, "smoke") == 5.0


def test_fixture_price_uses_defaults() -> None:
    cfg = load_config(ROOT)
    price = price_for(cfg, "cheap_a", "fixture")
    assert price.input_per_mtok == 0.5
    assert price.output_per_mtok == 1.5


def test_live_price_requires_pinned_model() -> None:
    cfg = load_config(ROOT)
    with pytest.raises(ConfigError):
        price_for(cfg, "cheap_a", "live")


def test_cost_record_has_exact_keys() -> None:
    record = cost_record(
        estimated_usd=0.1,
        actual_usd=0.09,
        provider_reported_usd=None,
        calls=3,
        prompt_tokens=100,
        completion_tokens=20,
        cap_usd=2.0,
        aborted=False,
        pricing_retrieved_at=None,
        mode="fixture",
    )
    assert set(record) == {
        "estimated_usd",
        "actual_usd",
        "provider_reported_usd",
        "calls",
        "prompt_tokens",
        "completion_tokens",
        "cap_usd",
        "aborted",
        "pricing_retrieved_at",
        "mode",
    }
