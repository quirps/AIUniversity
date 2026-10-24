from __future__ import annotations

import importlib
from typing import Protocol

from aiu.config import Config
from aiu.models import CallResult, Item, PlannedCall


class LabImpl(Protocol):
    lab_id: str

    def plan(
        self,
        items: list[Item],
        manifest: dict,
        cfg: Config,
    ) -> list[PlannedCall]: ...

    def score(
        self,
        items: list[Item],
        results: list[CallResult],
        manifest: dict,
    ) -> dict[str, float | None]: ...


REGISTRY: dict[str, type[LabImpl]] = {}


def register(cls: type[LabImpl]) -> type[LabImpl]:
    REGISTRY[cls.lab_id] = cls
    return cls


def load_lab(lab_id: str) -> type[LabImpl] | None:
    if lab_id not in REGISTRY:
        try:
            importlib.import_module(f"aiu.labs.{lab_id.lower().replace('-', '')}")
        except ImportError:
            pass
    return REGISTRY.get(lab_id)
