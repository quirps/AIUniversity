from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

SCHEMA_PATH = Path("schemas/curriculum.schema.json")


@dataclass(frozen=True)
class ValidationError_:
    path: str
    pointer: str
    message: str


def load_schema(root: Path) -> dict:
    return json.loads((root / SCHEMA_PATH).read_text(encoding="utf-8"))


def iter_yaml(paths: list[Path]) -> Iterator[Path]:
    seen: set[Path] = set()
    for path in paths:
        if path.is_file():
            candidates = [path] if path.suffix.lower() in {".yaml", ".yml"} else []
        elif path.is_dir():
            candidates = []
            for suffix in ("*.yaml", "*.yml"):
                candidates.extend(sorted(path.rglob(suffix)))
        else:
            candidates = []

        for candidate in candidates:
            if "tests" in candidate.parts:
                continue
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            yield candidate


def _flatten(error: ValidationError) -> Iterator[ValidationError]:
    if error.context:
        for sub_error in error.context:
            yield from _flatten(sub_error)
    else:
        yield error


def validate_file(path: Path, schema: dict) -> list[ValidationError_]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [ValidationError_(path.as_posix(), "", f"YAML error: {exc}")]

    validator = Draft202012Validator(schema)
    errors: list[ValidationError_] = []
    for top_error in validator.iter_errors(data):
        for error in _flatten(top_error):
            pointer = "/" + "/".join(str(part) for part in error.absolute_path)
            if pointer == "/":
                pointer = ""
            errors.append(ValidationError_(path.as_posix(), pointer, error.message))
    return sorted(errors, key=lambda item: (item.path, item.pointer, item.message))


def validate_ids(paths: list[Path]) -> list[ValidationError_]:
    errors: list[ValidationError_] = []
    seen: dict[tuple[str, str], Path] = {}

    for path in paths:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue

        kind = data.get("kind")
        if kind not in {"card", "lab", "module"}:
            continue

        item_id = data.get("id")
        if not isinstance(item_id, str):
            continue

        if path.stem != item_id:
            errors.append(
                ValidationError_(
                    path.as_posix(),
                    "",
                    f"filename stem '{path.stem}' != id '{item_id}'",
                )
            )

        if kind == "card":
            level = data.get("level")
            parent = path.parent.name
            if level and parent != level:
                errors.append(
                    ValidationError_(
                        path.as_posix(),
                        "",
                        f"card {item_id} is under {parent}/, expected {level}/",
                    )
                )
        elif kind == "lab":
            if path.name != "manifest.yaml" or path.parent.name != item_id:
                errors.append(
                    ValidationError_(
                        path.as_posix(),
                        "",
                        f"lab {item_id} must be labs/{item_id}/manifest.yaml",
                    )
                )

        key = (kind, item_id)
        if key in seen:
            errors.append(
                ValidationError_(
                    path.as_posix(),
                    "",
                    f"duplicate {kind} id {item_id} in {seen[key].as_posix()} and {path.as_posix()}",
                )
            )
        else:
            seen[key] = path

    return errors


def validate_paths(root: Path, paths: list[Path]) -> tuple[list[Path], list[ValidationError_]]:
    schema = load_schema(root)
    files = list(iter_yaml(paths))
    errors: list[ValidationError_] = []
    for path in files:
        errors.extend(validate_file(path, schema))
    errors.extend(validate_ids(files))
    return files, errors
