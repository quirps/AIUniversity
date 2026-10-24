from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from aiu.config import CapsConfig, ConfigError, load_config, resolve_role
from aiu.models import Message, PlannedCall

ROOT = Path(__file__).resolve().parents[1]


def test_real_configs_load() -> None:
    cfg = load_config(ROOT)

    assert cfg.caps.per_lab_usd == 2.0
    assert cfg.caps.smoke_total_usd == 5.0
    assert set(cfg.models.roles) == {
        "cheap_a",
        "cheap_b",
        "cheap_c",
        "strong",
        "judge_a",
        "judge_b",
    }
    assert cfg.models.roles["cheap_a"].model_id == "UNPINNED"
    assert cfg.pricing.retrieved_at is None


def test_live_unpinned_role_raises() -> None:
    cfg = load_config(ROOT)

    with pytest.raises(ConfigError):
        resolve_role(cfg, "cheap_a", "live")


def test_fixture_mode_returns_unpinned_role() -> None:
    cfg = load_config(ROOT)
    role = resolve_role(cfg, "cheap_a", "fixture")

    assert role.model_id == "UNPINNED"


def test_live_pinned_model_without_price_raises() -> None:
    cfg = load_config(ROOT)
    cfg.models.roles["cheap_a"].model_id = "provider/model"

    with pytest.raises(ConfigError):
        resolve_role(cfg, "cheap_a", "live")


def test_cap_ceiling_is_enforced() -> None:
    with pytest.raises(ValidationError):
        CapsConfig(per_lab_usd=3.0, smoke_total_usd=5.0)


def _call(temperature: float, call_key: str = "a") -> PlannedCall:
    return PlannedCall(
        call_key=call_key,
        item_id="i1",
        condition="base",
        role="cheap_a",
        sample=0,
        messages=[Message(role="user", content="hello")],
        temperature=temperature,
        max_tokens=16,
        seed=1,
    )


def test_request_hash_is_stable_across_call_keys() -> None:
    assert _call(0.0, "a").request_sha256() == _call(0.0, "b").request_sha256()


def test_request_hash_changes_with_temperature() -> None:
    assert _call(0.0).request_sha256() != _call(1.0).request_sha256()
