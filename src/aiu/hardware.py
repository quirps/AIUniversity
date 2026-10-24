from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import psutil

RunCommand = Callable[[list[str]], str | None]


@dataclass(frozen=True)
class GpuInfo:
    name: str
    vram_total_gb: float
    vram_free_gb: float


@dataclass(frozen=True)
class Probe:
    ram_total_gb: float
    ram_available_gb: float
    disk_free_gb: float
    gpu: GpuInfo | None


def default_run(command: list[str]) -> str | None:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def probe(root: Path, run_cmd: RunCommand = default_run) -> Probe:
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(str(root))

    gpu: GpuInfo | None = None
    output = run_cmd(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,memory.free",
            "--format=csv,noheader,nounits",
        ]
    )
    if output and output.strip():
        first_line = output.strip().splitlines()[0]
        parts = [part.strip() for part in first_line.split(",")]
        if len(parts) >= 3:
            try:
                gpu = GpuInfo(
                    name=parts[0],
                    vram_total_gb=round(float(parts[1]) / 1024, 2),
                    vram_free_gb=round(float(parts[2]) / 1024, 2),
                )
            except ValueError:
                gpu = None

    return Probe(
        ram_total_gb=round(memory.total / 1024**3, 2),
        ram_available_gb=round(memory.available / 1024**3, 2),
        disk_free_gb=round(disk.free / 1024**3, 2),
        gpu=gpu,
    )


def check(tier: str, p: Probe, local_requirements: dict | None = None) -> dict:
    warnings: list[str] = []
    failures: list[str] = []

    if tier == "API_ONLY":
        if p.disk_free_gb < 10:
            warnings.append("disk_free_gb < 10")
    elif tier == "LOCAL_SMALL_GPU_6GB":
        if local_requirements is None:
            failures.append("missing local_requirements")
        else:
            weights_gb = float(local_requirements.get("weights_gb", 0.0))
            if p.gpu is None:
                failures.append("gpu is required for this tier")
            else:
                if p.gpu.vram_free_gb < weights_gb + 1.0:
                    failures.append(
                        f"vram_free_gb {p.gpu.vram_free_gb} < {weights_gb + 1.0}"
                    )
            if p.disk_free_gb < 10 + weights_gb:
                failures.append(
                    f"disk_free_gb {p.disk_free_gb} < {10 + weights_gb}"
                )
            if p.ram_total_gb < 15.5:
                failures.append(f"ram_total_gb {p.ram_total_gb} < 15.5")
    elif tier == "LOCAL_CPU_TINY":
        if local_requirements is None:
            failures.append("missing local_requirements")
        else:
            params_b = float(local_requirements.get("params_b", 0.0))
            if params_b > 1.0:
                failures.append(f"params_b {params_b} > 1.0")
            if p.ram_available_gb < 4:
                failures.append(f"ram_available_gb {p.ram_available_gb} < 4")
    else:
        failures.append(f"unknown tier: {tier}")

    gpu = None
    if p.gpu is not None:
        gpu = {
            "name": p.gpu.name,
            "vram_total_gb": p.gpu.vram_total_gb,
            "vram_free_gb": p.gpu.vram_free_gb,
        }

    return {
        "tier": tier,
        "passed": not failures,
        "ram_total_gb": p.ram_total_gb,
        "ram_available_gb": p.ram_available_gb,
        "disk_free_gb": p.disk_free_gb,
        "gpu": gpu,
        "warnings": warnings,
        "failures": failures,
    }
