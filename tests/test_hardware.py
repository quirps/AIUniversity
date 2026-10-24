from __future__ import annotations

from pathlib import Path

from aiu.hardware import GpuInfo, Probe, check, probe

ROOT = Path(__file__).resolve().parents[1]
DEV = Probe(
    ram_total_gb=16.0,
    ram_available_gb=8.0,
    disk_free_gb=41.6,
    gpu=GpuInfo(name="GTX 1060", vram_total_gb=6.0, vram_free_gb=4.0),
)


def test_api_only_passes() -> None:
    assert check("API_ONLY", DEV)["passed"] is True


def test_local_small_gpu_with_two_gb_passes() -> None:
    result = check("LOCAL_SMALL_GPU_6GB", DEV, {"weights_gb": 2.0})
    assert result["passed"] is True


def test_local_small_gpu_with_three_and_a_half_gb_fails() -> None:
    result = check("LOCAL_SMALL_GPU_6GB", DEV, {"weights_gb": 3.5})
    assert result["passed"] is False
    assert any("vram_free_gb" in failure for failure in result["failures"])


def test_gpu_tier_without_gpu_fails() -> None:
    result = check(
        "LOCAL_SMALL_GPU_6GB",
        Probe(16.0, 8.0, 41.6, None),
        {"weights_gb": 2.0},
    )
    assert result["passed"] is False


def test_cpu_tiny_with_too_many_params_fails() -> None:
    result = check("LOCAL_CPU_TINY", DEV, {"params_b": 1.5})
    assert result["passed"] is False
    assert any("params_b" in failure for failure in result["failures"])


def test_cpu_tiny_at_one_billion_passes() -> None:
    result = check("LOCAL_CPU_TINY", DEV, {"params_b": 1.0})
    assert result["passed"] is True


def test_api_only_low_disk_passes_with_warning() -> None:
    result = check("API_ONLY", Probe(16.0, 8.0, 8.0, None))
    assert result["passed"] is True
    assert result["warnings"] == ["disk_free_gb < 10"]


def test_local_tier_without_requirements_fails() -> None:
    result = check("LOCAL_SMALL_GPU_6GB", DEV)
    assert result["passed"] is False
    assert "missing local_requirements" in result["failures"]


def test_nonexistent_nvidia_smi_gives_no_gpu() -> None:
    result = probe(ROOT, run_cmd=lambda command: None)
    assert result.gpu is None


def test_nvidia_smi_output_is_parsed() -> None:
    result = probe(
        ROOT,
        run_cmd=lambda command: "NVIDIA GeForce GTX 1060 6GB, 6144, 4096\n",
    )
    assert result.gpu is not None
    assert result.gpu.name == "NVIDIA GeForce GTX 1060 6GB"
    assert result.gpu.vram_total_gb == 6.0
    assert result.gpu.vram_free_gb == 4.0
