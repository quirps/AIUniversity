from __future__ import annotations

import json
import math
import random
import shutil
from pathlib import Path

from aiu.cli import main
from aiu.fixtures_synth import SYNTH, register_synth, synth
from aiu.generators.base import GENERATORS, SEED, build, register_generator, serialize
from aiu.labs.base import register
from aiu.models import CallResult, Item, Message, PlannedCall

ROOT = Path(__file__).resolve().parents[1]
LAB_ID = "L-997"


@register_generator(LAB_ID)
def _toy_generator(rng):
    words = ["beta", "alpha"]
    rng.shuffle(words)
    return [
        Item(
            id=f"i{index}",
            input={"prompt": word},
            expected={"answer": word},
            meta={"index": index},
        )
        for index, word in enumerate(words)
    ]


class _ToyLab:
    lab_id = LAB_ID

    def plan(self, items, manifest, cfg):
        return [
            PlannedCall(
                call_key=f"{item.id}|base|cheap_a|0",
                item_id=item.id,
                condition="base",
                role="cheap_a",
                sample=0,
                messages=[Message(role="user", content=item.input["prompt"])],
                temperature=0.0,
                max_tokens=16,
                seed=None,
            )
            for item in items
        ]

    def score(self, items, results, manifest):
        return {}


register(_ToyLab)


@register_synth(LAB_ID)
def _toy_synth(items, calls, rng):
    return [
        CallResult(
            call_key=call.call_key,
            model_id="placeholder",
            text=f"answer-{call.item_id}",
            prompt_tokens=0,
            completion_tokens=0,
            provider_reported_usd=1.0,
            latency_ms=99,
            source="live",
            request_sha256="",
            timestamp="",
        )
        for call in calls
    ]


def _dataset_path(root: Path) -> Path:
    return root / "labs" / LAB_ID / "data" / "items.jsonl"


def _fixture_path(root: Path) -> Path:
    return root / "labs" / LAB_ID / "fixtures" / "responses.jsonl"


def _prepare_synth_root(root: Path) -> None:
    shutil.copytree(ROOT / "config", root / "config")
    assert build(root, LAB_ID, False) == 0
    manifest = root / "labs" / LAB_ID / "manifest.yaml"
    manifest.write_text(
        "\n".join(
            [
                "kind: lab",
                "id: L-997",
                f"dataset:\n  path: labs/{LAB_ID}/data/items.jsonl",
                f"fixtures:\n  path: labs/{LAB_ID}/fixtures/responses.jsonl",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_toy_registrations_exist() -> None:
    assert LAB_ID in GENERATORS
    assert LAB_ID in SYNTH


def test_serialize_sorts_and_uses_compact_json() -> None:
    items = [
        Item(id="b", input={"x": "é"}, expected={}, meta={}),
        Item(id="a", input={"x": "one"}, expected={}, meta={}),
    ]

    payload = serialize(items)
    lines = payload.decode("utf-8").splitlines()

    assert [json.loads(line)["id"] for line in lines] == ["a", "b"]
    assert payload.endswith(b"\n")
    assert "é" in payload.decode("utf-8")


def test_build_is_deterministic(tmp_path: Path) -> None:
    assert build(tmp_path, LAB_ID, False) == 0
    first = _dataset_path(tmp_path).read_bytes()
    assert build(tmp_path, LAB_ID, False) == 0

    assert _dataset_path(tmp_path).read_bytes() == first
    ids = [json.loads(line)["id"] for line in first.decode("utf-8").splitlines()]
    assert ids == ["i0", "i1"]


def test_build_check_ok_and_diff(tmp_path: Path) -> None:
    assert build(tmp_path, LAB_ID, False) == 0
    assert build(tmp_path, LAB_ID, True) == 0

    path = _dataset_path(tmp_path)
    path.write_bytes(path.read_bytes() + b" ")

    assert build(tmp_path, LAB_ID, True) == 1


def test_unknown_lab_returns_6(tmp_path: Path) -> None:
    assert build(tmp_path, "E1", False) == 6
    assert not (tmp_path / "labs" / "E1").exists()


def test_synth_normalizes_results_and_is_deterministic(tmp_path: Path) -> None:
    _prepare_synth_root(tmp_path)

    assert synth(tmp_path, LAB_ID, False) == 0
    first = _fixture_path(tmp_path).read_bytes()

    rows = [json.loads(line) for line in first.decode("utf-8").splitlines()]
    assert len(rows) == 2
    prompts = {
        item.id: item.input["prompt"]
        for item in _toy_generator(random.Random(SEED))
    }
    for row in rows:
        item_id = row["call_key"].split("|")[0]
        prompt = prompts[item_id]
        assert row["source"] == "fixture_synthetic"
        assert row["model_id"] == "fixture"
        assert row["provider_reported_usd"] is None
        assert row["latency_ms"] == 0
        assert row["timestamp"] == "1970-01-01T00:00:00Z"
        assert len(row["request_sha256"]) == 64
        assert row["prompt_tokens"] == math.ceil(len(prompt.encode("utf-8")) / 3)
        assert row["completion_tokens"] == len(row["text"]) // 4 + 1

    assert synth(tmp_path, LAB_ID, True) == 0
    assert synth(tmp_path, LAB_ID, False) == 0
    assert _fixture_path(tmp_path).read_bytes() == first

    fixture = _fixture_path(tmp_path)
    fixture.write_bytes(fixture.read_bytes() + b" ")
    assert synth(tmp_path, LAB_ID, True) == 1


def test_unknown_lab_synth_returns_6(tmp_path: Path) -> None:
    assert synth(tmp_path, "E1", False) == 6


def test_dataset_build_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)

    assert main(["dataset", "build", LAB_ID]) == 0
    assert "WRITTEN" in capsys.readouterr().out

    assert main(["dataset", "build", LAB_ID, "--check"]) == 0
    assert "OK" in capsys.readouterr().out

    path = _dataset_path(tmp_path)
    path.write_bytes(path.read_bytes() + b" ")

    assert main(["dataset", "build", LAB_ID, "--check"]) == 1
    assert "DIFF" in capsys.readouterr().out


def test_fixtures_synth_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    _prepare_synth_root(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(["fixtures", "synth", LAB_ID]) == 0
    assert "WRITTEN" in capsys.readouterr().out

    assert main(["fixtures", "synth", LAB_ID, "--check"]) == 0
    assert "OK" in capsys.readouterr().out

    fixture = _fixture_path(tmp_path)
    fixture.write_bytes(fixture.read_bytes() + b" ")

    assert main(["fixtures", "synth", LAB_ID, "--check"]) == 1
    assert "DIFF" in capsys.readouterr().out
