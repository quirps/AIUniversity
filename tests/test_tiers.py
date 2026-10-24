from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from aiu.cli import main
from aiu.labs.tiers import check_tiers, list_labs
from aiu.validate import load_schema, validate_file

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def test_real_repo_has_no_tier_problems() -> None:
    assert check_tiers(ROOT) == []


def test_list_labs_has_17_sorted_rows() -> None:
    labs = list_labs(ROOT)
    assert len(labs) == 17
    assert [row[0] for row in labs] == sorted(row[0] for row in labs)
    assert {row[1] for row in labs} == {"runnable", "specified"}
    assert {row[2] for row in labs} == {"API_ONLY"}


def test_local_lab_with_specified_fallback_without_fixtures_is_a_problem(
    tmp_path: Path,
) -> None:
    local = tmp_path / "labs" / "L-999" / "manifest.yaml"
    local.parent.mkdir(parents=True)
    shutil.copyfile(FIXTURES / "invalid_lab_local_bad_fallback.yaml", local)

    fallback = tmp_path / "labs" / "E1" / "manifest.yaml"
    fallback.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "labs" / "E1" / "manifest.yaml", fallback)

    problems = check_tiers(tmp_path)
    assert problems
    assert any("no fixtures" in problem for problem in problems)


def test_explicit_invalid_manifest_path_is_a_problem() -> None:
    path = FIXTURES / "invalid_lab_local_bad_fallback.yaml"
    problems = check_tiers(ROOT, path)
    assert len(problems) == 1
    assert "no fixtures" in problems[0]


def test_local_manifest_with_oversized_weights_fails_schema(tmp_path: Path) -> None:
    schema = load_schema(ROOT)
    data = yaml.safe_load(
        (FIXTURES / "invalid_lab_local_bad_fallback.yaml").read_text(encoding="utf-8")
    )
    data["local_requirements"]["weights_gb"] = 4.0
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")

    errors = validate_file(path, schema)
    assert any(error.pointer.endswith("/weights_gb") for error in errors)


def test_labs_list_cli(capsys) -> None:
    assert main(["labs", "list"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 17
    assert lines[0].split("\t")[:3] == ["E1", "specified", "API_ONLY"]


def test_labs_check_tiers_cli(capsys) -> None:
    assert main(["labs", "check-tiers"]) == 0
    assert "tiers: OK (17 labs)" in capsys.readouterr().out


def test_labs_check_tiers_cli_with_bad_path(capsys) -> None:
    bad = FIXTURES / "invalid_lab_local_bad_fallback.yaml"
    assert main(["labs", "check-tiers", str(bad)]) == 1
    assert "no fixtures" in capsys.readouterr().out
