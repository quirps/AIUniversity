from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

ROLE_NAMES = ("cheap_a", "cheap_b", "cheap_c", "strong", "judge_a", "judge_b")


class ConfigError(Exception):
    pass


class RoleConfig(BaseModel):
    model_id: str
    family: str


class ModelsConfig(BaseModel):
    roles: dict[
        Literal["cheap_a", "cheap_b", "cheap_c", "strong", "judge_a", "judge_b"],
        RoleConfig,
    ]


class Price(BaseModel):
    input_per_mtok: float = Field(ge=0)
    output_per_mtok: float = Field(ge=0)


class PricingConfig(BaseModel):
    retrieved_at: date | None
    fixture_defaults: Price
    models: dict[str, Price]


class CapsConfig(BaseModel):
    per_lab_usd: float = Field(gt=0, le=2.0)
    smoke_total_usd: float = Field(gt=0, le=5.0)


class Config(BaseModel):
    models: ModelsConfig
    pricing: PricingConfig
    caps: CapsConfig


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_config(root: Path) -> Config:
    try:
        models = ModelsConfig.model_validate(_load_yaml(root / "config" / "models.yaml"))
        pricing = PricingConfig.model_validate(_load_yaml(root / "config" / "pricing.yaml"))
        caps = CapsConfig.model_validate(_load_yaml(root / "config" / "caps.yaml"))
    except Exception as exc:
        raise ConfigError(f"config load failed: {exc}") from exc

    return Config(models=models, pricing=pricing, caps=caps)


def resolve_role(
    cfg: Config,
    role: str,
    mode: Literal["fixture", "live"],
) -> RoleConfig:
    if role not in cfg.models.roles:
        raise ConfigError(f"unknown role: {role}")

    role_config = cfg.models.roles[role]
    if mode == "live":
        if role_config.model_id == "UNPINNED":
            raise ConfigError(f"role {role} is UNPINNED")
        if role_config.model_id not in cfg.pricing.models:
            raise ConfigError(f"role {role} model has no pinned price: {role_config.model_id}")

    return role_config
