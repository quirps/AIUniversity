This is part 2a of the continuation. Part 1 produced TASKS.md through T-038, but the T-038 block was truncated and ACCEPTANCE.md was not emitted.

Emit ONLY these two files, in this order, using the exact ## FILE: <path> format:

1. T-038.fragment.md - a complete replacement for the T-038 ticket, starting with ### T-038: Run final v1 acceptance and ending with its **Open decisions:** line. Do not include T-037 or a trailing separator.
2. ACCEPTANCE.md - AC-01 through AC-20. For each: ID, requirement, exact runnable command, expected exit code or output, and the implementing ticket ID. Include checks for Python 3.12/uv, zero-network pytest, JSON Schema validation, secrets scan, journal append-only, status.json/README consistency, provenance ledger, traceability, hardware_tier validity and API fallback, cost caps, fixture/live separation, clean-checkout reproduction, source provenance, transparency artifacts, and a final iu check-all gate. Self-contained and runnable from the repo root in Windows PowerShell.

Constraints:
- Do not contradict the existing decisions, schemas, or tickets.
- No implementation code.
- No commentary outside the file sections.
- Do not emit any other file.

The current TASKS.md, CONSTITUTION.md, LAB_SPEC.md, REPO_LAYOUT.md, DECISIONS.md, and TRACEABILITY.md follow.

<tasks>
# TASKS.md — v1 implementation backlog

Working directory for every command: `C:\Users\Joe\Documents\Playground\AIUniversity`, PowerShell.
Every ticket's DoD includes: a new `JOURNAL.md` entry naming the ticket, acceptance results, commands, cost (USD, usually 0.00), failures; and `status.json` refreshed (`uv run aiu status --write` from T-007 on; manual edit of `known_gaps` before T-007).
"Spec docs" = files emitted in the Opus handoff message, copied byte-for-byte.

---

### T-001: Create repository and install spec documents

**Goal:** Repo exists with git initialized and every spec document from the handoff present verbatim.

**Depends on:** none.

**Files:**
- create: `DECISIONS.md`, `CONSTITUTION.md`, `schemas/curriculum.schema.json`, `schemas/status.schema.json`, `REPO_LAYOUT.md`, `LAB_SPEC.md`, `curriculum/A/A-001.yaml`, `curriculum/B/B-001.yaml`, `curriculum/C/C-004.yaml`, `TRACEABILITY.md`, `TASKS.md`, `ACCEPTANCE.md`, `GOVERNANCE.md`, `README.md`, `JOURNAL.md`, `PROVENANCE.md`, `RESULTS.md`, `CHANGELOG.md`, `status.json`, `experiments/_template/prediction.md`, `experiments/_template/postmortem.md`, `experiments/_template/config.json`, `experiments/_template/result.json`, `experiments/_template/metrics.json`, `experiments/_template/cost.json`, `docs/learnings/_template.md`
- create: `source/concept_map.txt` (human-provided text), `source/README.md`

**Interfaces / schemas:** none.

**Steps:**
1. `New-Item -ItemType Directory -Force` the repo root; `cd` into it.
2. `git init -b main`.
3. Write each file above with exact contents from the handoff.
4. Write `source/README.md`: `Extracted text of "AI Engineering Concept Map" (compiled 2026-10-23). The PDF is authoritative; it is not committed pending OD-05.`
5. Place `source/concept_map.txt` as provided by the human.
6. Append JOURNAL entry 1 (T-001). Commit: `git add -A; git commit -m "T-001: install spec documents"`.

**Acceptance tests:**
- `$f=@('DECISIONS.md','CONSTITUTION.md','schemas/curriculum.schema.json','schemas/status.schema.json','REPO_LAYOUT.md','LAB_SPEC.md','curriculum/A/A-001.yaml','curriculum/B/B-001.yaml','curriculum/C/C-004.yaml','TRACEABILITY.md','TASKS.md','ACCEPTANCE.md','GOVERNANCE.md','README.md','JOURNAL.md','PROVENANCE.md','RESULTS.md','CHANGELOG.md','status.json','experiments/_template/prediction.md','experiments/_template/postmortem.md','docs/learnings/_template.md','source/concept_map.txt'); $m=$f|?{-not(Test-Path $_)}; if($m){$m; exit 1}else{exit 0}` → exit 0.
- `git log --oneline -1` → output contains `T-001`.

**Commands:** as in Steps.

**Definition of done:**
- [ ] All files present; one commit.
- [ ] JOURNAL entry 1 appended after entry 0.
- [ ] `status.json` unchanged (initial).

**Out of scope:** Any Python, any edits to spec content.

**Open decisions:** OD-05 (commit PDF?).

---

### T-002: Bootstrap Python 3.12, uv, and package skeleton

**Goal:** `uv run aiu --version` prints `aiu 0.1.0` using Python 3.12.

**Depends on:** T-001.

**Files:**
- create: `pyproject.toml`, `.python-version`, `src/aiu/__init__.py`, `src/aiu/cli.py`, `tests/test_cli.py`, `ops/bootstrap.ps1`, `ops/RUNBOOK.md`
- create (generated): `uv.lock`

**Interfaces / schemas:**
```toml
[project]
name = "aiu"
version = "0.1.0"
requires-python = ">=3.11,<3.13"
dependencies = ["pydantic>=2.7,<3", "pyyaml>=6.0,<7", "jsonschema>=4.21,<5", "httpx>=0.27,<1", "psutil>=5.9,<7"]
[project.scripts]
aiu = "aiu.cli:main"
[dependency-groups]
dev = ["pytest>=8,<9", "pytest-socket>=0.7,<1"]
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/aiu"]
[tool.pytest.ini_options]
addopts = "--disable-socket -q"
testpaths = ["tests"]
```
```python
# src/aiu/__init__.py
__version__ = "0.1.0"
# src/aiu/cli.py
def build_parser() -> argparse.ArgumentParser: ...  # prog="aiu", --version action prints "aiu 0.1.0"
def main(argv: list[str] | None = None) -> int: ...   # returns exit code; `if __name__` not needed
```
Console script must call `sys.exit(main())` semantics: define `main` returning int and register via hatch; wrap with `def _entry(): raise SystemExit(main())` and point script to `aiu.cli:_entry`. (Update `[project.scripts] aiu = "aiu.cli:_entry"`.)

`ops/bootstrap.ps1` content (exact steps): install uv if `Get-Command uv` fails via `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`; `uv python install 3.12`; `uv sync`; `git config core.hooksPath .githooks`; `uv run aiu --version`.
`ops/RUNBOOK.md`: sections `## Live run procedure` (LAB_SPEC §2 commands), `## Key rotation` (revoke at openrouter.ai, update local `.env`, never commit), `## Incident: key committed` (revoke key immediately, rewrite is NOT allowed for JOURNAL; record incident entry), `## Incident: cost overrun` (record in JOURNAL with cost.json link).

**Steps:**
1. Run uv installer (above); open new shell; `uv --version`.
2. `uv python install 3.12`.
3. Create files above. Write `.python-version` = `3.12`.
4. `uv sync`.
5. `tests/test_cli.py::test_version` calls `main(["--version"])` capturing `SystemExit` code 0 and stdout `aiu 0.1.0`.

**Acceptance tests:**
- `uv run python -c "import sys; print(sys.version_info[:2])"` → `(3, 12)`, exit 0.
- `uv run aiu --version` → `aiu 0.1.0`, exit 0.
- `uv run pytest` → exit 0, `1 passed`.

**Commands:** `uv sync; uv run aiu --version; uv run pytest`

**Definition of done:**
- [ ] `uv.lock` committed.
- [ ] JOURNAL entry; `status.json.known_gaps` unchanged.

**Out of scope:** Any subcommands.

**Open decisions:** none.

---

### T-003: Add .gitignore and .env.example

**Goal:** Secrets and local artifacts cannot be accidentally tracked.

**Depends on:** T-002.

**Files:**
- create: `.gitignore`, `.env.example`, `tests/test_hygiene_files.py`

**Interfaces / schemas:**
`.gitignore` exact lines:
```
.env
.env.*
!.env.example
.venv/
__pycache__/
*.pyc
.pytest_cache/
.runs/
*.gguf
*.safetensors
*.pt
*.bin
*.onnx
*.pem
*.key
dist/
build/
```
`.env.example` exact:
```
# Copy to .env and fill in. Never commit .env.
OPENROUTER_API_KEY=
```

**Steps:**
1. Write both files.
2. Test: `.env.example` exists, contains `OPENROUTER_API_KEY=` with empty value; `.gitignore` contains `.env` and `.runs/` lines.
3. Test: `git check-ignore .env` returns 0 (run via `subprocess` with `git`; skip test if git not on PATH—must not be the case on dev machine).

**Acceptance tests:**
- `uv run pytest tests/test_hygiene_files.py` → exit 0.
- `git check-ignore .env` → prints `.env`, exit 0.
- `git check-ignore .env.example` → exit 1.

**Commands:** `uv run pytest tests/test_hygiene_files.py`

**Definition of done:**
- [ ] Files committed; JOURNAL entry.

**Out of scope:** Loading `.env` (harness reads env vars only; learners load via their shell).

**Open decisions:** none.

---

### T-004: Implement secrets and forbidden-file scanner with pre-commit hook

**Goal:** `aiu secrets-scan` exits 1 on any secret or forbidden file and is enforced on commit.

**Depends on:** T-003.

**Files:**
- create: `src/aiu/secrets_scan.py`, `.githooks/pre-commit`, `tests/test_secrets_scan.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
@dataclass(frozen=True)
class Finding: path: str; line: int | None; rule: str; excerpt: str  # excerpt masks all but first 6 chars of match
SECRET_PATTERNS: dict[str, re.Pattern] = {
  "openrouter_key": re.compile(r"sk-or-v1-[A-Za-z0-9]{16,}"),
  "generic_sk_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
  "bearer_token": re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
  "env_assignment": re.compile(r"^\s*OPENROUTER_API_KEY\s*=\s*\S+", re.M),
}
FORBIDDEN_GLOBS = [".env", ".env.*", "*.pem", "*.key", "*.gguf", "*.safetensors", "*.pt", "*.bin", "*.onnx"]
ALLOWED = [".env.example"]
MAX_FILE_BYTES = 5_000_000
def scan_paths(paths: list[Path]) -> list[Finding]
def staged_paths(root: Path) -> list[Path]   # git diff --cached --name-only --diff-filter=ACM
def all_tracked_and_untracked(root: Path) -> list[Path]  # git ls-files -co --exclude-standard
```
CLI: `aiu secrets-scan [--staged] [--root PATH]`. Prints one line per finding `<rule> <path>:<line> <excerpt>`; prints `secrets-scan: 0 findings` on success. Exit 0/1. Binary files (null byte in first 8 KB) skip pattern scan but still get glob/size checks. Files > MAX_FILE_BYTES → rule `oversize`.
`.githooks/pre-commit`:
```
#!/bin/sh
uv run aiu secrets-scan --staged || exit 1
uv run aiu journal check || exit 1
```
(Second line becomes effective after T-005; until then `journal` subcommand missing → commit fails. Therefore write only the first line in this ticket; T-005 adds the second.)

**Steps:**
1. Implement module + CLI.
2. Tests using `tmp_path`: (a) file with `sk-or-v1-` + 20 alnum → 1 finding rule `openrouter_key`; (b) `.env` file → rule `forbidden_file`; (c) `.env.example` with empty `OPENROUTER_API_KEY=` → 0 findings; (d) 6 MB file → `oversize`; (e) clean file → 0; (f) excerpt never contains full key.
3. `git config core.hooksPath .githooks`.

**Acceptance tests:**
- `uv run pytest tests/test_secrets_scan.py` → exit 0.
- `uv run aiu secrets-scan` → `secrets-scan: 0 findings`, exit 0.
- `Set-Content tmp_leak.txt "sk-or-v1-abcdefghijklmnopqrstuvwx"; uv run aiu secrets-scan; $c=$LASTEXITCODE; Remove-Item tmp_leak.txt; exit $c` → exit 1.

**Commands:** `git config core.hooksPath .githooks; uv run pytest tests/test_secrets_scan.py`

**Definition of done:**
- [ ] Hook installed and committed; JOURNAL entry.

**Out of scope:** History scanning; network secret validation.

**Open decisions:** none.

---

### T-005: Implement append-only journal check

**Goal:** `aiu journal check` exits 1 when existing `JOURNAL.md` content in HEAD is modified.

**Depends on:** T-004.

**Files:**
- create: `src/aiu/journal.py`, `tests/test_journal.py`
- modify: `src/aiu/cli.py`, `.githooks/pre-commit` (add line 2)

**Interfaces / schemas:**
```python
def head_content(root: Path, rel: str = "JOURNAL.md") -> str | None  # git show HEAD:JOURNAL.md; None if absent/no HEAD
def check_append_only(old: str | None, new: str) -> bool  # True iff old is None or new.startswith(old) (after normalizing CRLF->LF on both)
```
CLI: `aiu journal check` → prints `journal: append-only OK` exit 0, or `journal: existing entries modified` exit 1.

**Steps:**
1. Implement; tests on pure function: None→True; prefix→True; edited middle→False; CRLF/LF difference only→True.
2. Add hook line 2.

**Acceptance tests:**
- `uv run pytest tests/test_journal.py` → exit 0.
- `uv run aiu journal check` → exit 0.

**Commands:** `uv run pytest tests/test_journal.py; uv run aiu journal check`

**Definition of done:**
- [ ] Hook has both lines; JOURNAL entry appended (not edited).

**Out of scope:** Journal entry generation.

**Open decisions:** none.

---

### T-006: Implement YAML schema validation command

**Goal:** `aiu validate` validates all curriculum, lab, module, and trust-table YAML against `schemas/curriculum.schema.json`.

**Depends on:** T-005.

**Files:**
- create: `src/aiu/validate.py`, `tests/test_validate.py`, `tests/fixtures/invalid_card_missing_misconception.yaml`, `tests/fixtures/invalid_lab_local_no_fallback.yaml`, `learner/trust_table.yaml`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
SCHEMA_PATH = Path("schemas/curriculum.schema.json")
@dataclass(frozen=True)
class ValidationError_: path: str; pointer: str; message: str
def load_schema(root: Path) -> dict
def iter_yaml(paths: list[Path]) -> Iterator[Path]  # *.yaml recursively, sorted, excluding files under tests/
def validate_file(path: Path, schema: dict) -> list[ValidationError_]  # Draft202012Validator; yaml.safe_load
def validate_ids(paths: list[Path]) -> list[ValidationError_]  # filename stem == id; card in curriculum/<level>/; lab manifest at labs/<id>/manifest.yaml; no duplicate ids
```
CLI: `aiu validate [PATH ...]` default `curriculum labs learner`. Output per error `<path> <pointer> <message>`; final line `validate: <n_files> files, <n_errors> errors`. Exit 0 if 0 errors else 1. Nonexistent default dirs are skipped silently; nonexistent explicit paths → error.
`learner/trust_table.yaml`:
```yaml
kind: trust_table
schema_version: "1.0"
rows: []
```

**Steps:**
1. Implement.
2. Tests: three exemplar cards valid; invalid fixtures each produce ≥1 error; card with `provenance: [K]` and `verify: []` invalid; card `experiment_id: null` without `experiment_null_reason` invalid; filename/id mismatch detected.

**Acceptance tests:**
- `uv run aiu validate` → last line `validate: 4 files, 0 errors`, exit 0.
- `uv run aiu validate tests/fixtures/invalid_lab_local_no_fallback.yaml` → exit 1, output contains `api_fallback`.
- `uv run pytest tests/test_validate.py` → exit 0.

**Commands:** `uv run aiu validate; uv run pytest tests/test_validate.py`

**Definition of done:**
- [ ] JOURNAL entry; `status.json.known_gaps` updated manually.

**Out of scope:** Cross-reference checks (T-026, T-027).

**Open decisions:** none.

---

### T-007: Implement status.json generation, README block, and consistency check

**Goal:** `aiu status --write` regenerates `status.json` and the README STATUS block from repo state, and `aiu status --check` exits 1 on any drift.

**Depends on:** T-006.

**Files:**
- create: `src/aiu/status.py`, `tests/test_status.py`, `tests/fixtures/status_repo/` (minimal fake repo tree used by tests)
- modify: `src/aiu/cli.py`, `status.json`, `README.md` (only the text between the markers)

**Interfaces / schemas:** Output must validate against `schemas/status.schema.json` (handoff file).
```python
STATUS_BEGIN = "<!-- STATUS:BEGIN -->"
STATUS_END = "<!-- STATUS:END -->"
IGNORED_KEYS = ("generated_at", "tests")

def compute_status(root: Path, previous: dict | None) -> dict
  # cards: count files matching curriculum/[A-F]/[A-F]-[0-9][0-9][0-9].yaml, grouped by level and by `status` field
  # modules: count curriculum/modules/M-*.yaml
  # labs: count labs/*/manifest.yaml grouped by `status`
  # provenance: count PROVENANCE.md rows starting "| P-", grouped by status column
  # live_runs: every dir experiments/<lab_id>/<run_id>/ containing cost.json, excluding experiments/_template
  # cumulative_cost_usd: round(sum(cost.json.actual_usd over live_runs), 4)
  # last_live_run: run_id with the greatest lexical value, or null
  # tests: copied from previous["tests"] (written only by `aiu check-all`, T-035); null if previous is None
  # known_gaps: copied from previous["known_gaps"]; [] if previous is None
  # generated_at: UTC ISO-8601 "YYYY-MM-DDTHH:MM:SSZ"
def render_readme_block(status: dict) -> str
  # Markdown table. Rows, in order: Cards written, Modules, Labs runnable, Labs specified,
  # Claims verified/unverified/disputed, Live runs, Cumulative spend (USD, measured), Last live run,
  # Tests (passed/failed/at), Known gaps (bullet list).
  # Every number is labeled "measured" (from runs or tests) or "counted" (file counts).
def write_status(root: Path) -> None
  # write status.json with indent=2, sort_keys=True, trailing "\n"; replace README text between markers
def check_status(root: Path) -> list[str]
  # returns human-readable mismatch strings; empty list means OK. Checks:
  # 1. compute_status(root, committed) equals committed status.json, ignoring IGNORED_KEYS
  # 2. README text between markers equals render_readme_block(committed)
  # 3. every live run_id appears as a substring of RESULTS.md
  # 4. committed cumulative_cost_usd equals recomputed sum
  # 5. status.json validates against schemas/status.schema.json
```
CLI: `aiu status --write | --check` (mutually exclusive, one required). `--write` prints `status: written`, exit 0. `--check` prints each mismatch on its own line, then `status: OK` (exit 0) or `status: <n> mismatches` (exit 1). If either marker is missing from README, `--write` and `--check` both exit 6 and print `status: README markers missing`.

**Steps:**
1. Implement `status.py` and wire the CLI.
2. Build `tests/fixtures/status_repo/` containing 1 card, 1 lab manifest, a 2-row PROVENANCE.md, a README with markers, a RESULTS.md, and one live run dir with `cost.json` (`actual_usd: 0.1234`).
3. Tests (each copies the fixture repo into `tmp_path`): (a) write then check ? `[]`; (b) delete the run_id from RESULTS.md ? 1 mismatch; (c) edit README block ? 1 mismatch; (d) edit `cumulative_cost_usd` ? mismatch; (e) `tests` key change alone ? no mismatch; (f) missing markers ? exit 6 via `main()`.
4. Run `uv run aiu status --write` on the real repo and commit.

**Acceptance tests:**
- `uv run pytest tests/test_status.py` ? exit 0.
- `uv run aiu status --write` ? `status: written`, exit 0.
- `uv run aiu status --check` ? last line `status: OK`, exit 0.
- `uv run python -c "import json,jsonschema;jsonschema.validate(json.load(open('status.json')),json.load(open('schemas/status.schema.json')))"` ? exit 0.

**Commands:** `uv run pytest tests/test_status.py; uv run aiu status --write; uv run aiu status --check`

**Definition of done:**
- [ ] `status.json` and the README block are regenerated and committed.
- [ ] A JOURNAL entry has been appended.
- [ ] From this ticket onward, every ticket's DoD runs `uv run aiu status --write` followed by `uv run aiu status --check`.

**Out of scope:** Populating the `tests` key (T-035); editing README outside the markers.

**Open decisions:** none.

---

### T-008: Implement config loading and core pydantic models

**Goal:** `config/models.yaml`, `config/pricing.yaml`, and `config/caps.yaml` exist and load into validated pydantic models.

**Depends on:** T-007.

**Files:**
- create: `config/models.yaml`, `config/pricing.yaml`, `config/caps.yaml`, `src/aiu/config.py`, `src/aiu/models.py`, `tests/test_config.py`

**Interfaces / schemas:**

`config/models.yaml` (exact contents):
```yaml
roles:
  cheap_a:  {model_id: UNPINNED, family: unknown}
  cheap_b:  {model_id: UNPINNED, family: unknown}
  cheap_c:  {model_id: UNPINNED, family: unknown}
  strong:   {model_id: UNPINNED, family: unknown}
  judge_a:  {model_id: UNPINNED, family: unknown}
  judge_b:  {model_id: UNPINNED, family: unknown}
```

`config/pricing.yaml` (exact contents; these numbers are **assumed**, per ADR-022):
```yaml
retrieved_at: null
fixture_defaults: {input_per_mtok: 0.50, output_per_mtok: 1.50}
models: {}
```

`config/caps.yaml` (exact contents):
```yaml
per_lab_usd: 2.00
smoke_total_usd: 5.00
```

```python
class RoleConfig(BaseModel): model_id: str; family: str
class ModelsConfig(BaseModel): roles: dict[Literal["cheap_a","cheap_b","cheap_c","strong","judge_a","judge_b"], RoleConfig]
class Price(BaseModel): input_per_mtok: float = Field(ge=0); output_per_mtok: float = Field(ge=0)
class PricingConfig(BaseModel): retrieved_at: date | None; fixture_defaults: Price; models: dict[str, Price]
class CapsConfig(BaseModel): per_lab_usd: float = Field(gt=0, le=2.0); smoke_total_usd: float = Field(gt=0, le=5.0)
class Config(BaseModel): models: ModelsConfig; pricing: PricingConfig; caps: CapsConfig
class ConfigError(Exception): ...   # the CLI maps this to exit 6
def load_config(root: Path) -> Config
def resolve_role(cfg: Config, role: str, mode: Literal["fixture","live"]) -> RoleConfig
  # live mode raises ConfigError if model_id == "UNPINNED" or model_id is missing from pricing.models
class Message(BaseModel): role: Literal["system","user","assistant"]; content: str
class PlannedCall(BaseModel):
  call_key: str; item_id: str; condition: str; role: str; sample: int
  messages: list[Message]; temperature: float; max_tokens: int; seed: int | None
  response_format: dict | None = None; logprobs: bool = False
  def request_sha256(self) -> str  # sha256 of json.dumps(model_dump(exclude={"call_key"}), sort_keys=True, separators=(",",":"))
class CallResult(BaseModel):
  call_key: str; model_id: str; text: str; prompt_tokens: int; completion_tokens: int
  provider_reported_usd: float | None; latency_ms: int; source: Literal["fixture_synthetic","fixture_recorded","live"]
  request_sha256: str; timestamp: str; logprobs: list | None = None
class Item(BaseModel): id: str; input: dict; expected: dict; meta: dict
```

**Steps:**
1. Write the three config files and both modules.
2. Tests: (a) the real configs load; (b) `resolve_role(..., "live")` on UNPINNED raises ConfigError; (c) fixture mode returns the RoleConfig; (d) `per_lab_usd: 3.0` fails validation; (e) `request_sha256` is stable across two identical PlannedCall instances and changes when the temperature changes.

**Acceptance tests:**
- `uv run pytest tests/test_config.py` ? exit 0.
- `uv run python -c "from aiu.config import load_config; from pathlib import Path; print(load_config(Path('.')).caps.per_lab_usd)"` ? `2.0`, exit 0.

**Commands:** `uv run pytest tests/test_config.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `aiu status --write` and `aiu status --check` both exit 0.
- [ ] `known_gaps` includes `models UNPINNED (OD-01)`.

**Out of scope:** Choosing model IDs or prices (OD-01, T-036).

**Open decisions:** OD-01.

---

### T-009: Implement hardware check

**Goal:** `aiu hwcheck --tier <T> --json` reports measured RAM, disk, and GPU and applies the ADR-014 thresholds.

**Depends on:** T-008.

**Files:**
- create: `src/aiu/hardware.py`, `tests/test_hardware.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
@dataclass(frozen=True)
class GpuInfo: name: str; vram_total_gb: float; vram_free_gb: float
@dataclass(frozen=True)
class Probe: ram_total_gb: float; ram_available_gb: float; disk_free_gb: float; gpu: GpuInfo | None
def probe(root: Path, run_cmd: Callable[[list[str]], str | None] = default_run) -> Probe
  # psutil.virtual_memory(); psutil.disk_usage(str(root)); GPU via
  # nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits (MiB/1024).
  # FileNotFoundError or nonzero exit -> gpu=None. GB = bytes / 1024**3, rounded to 2 decimals.
def check(tier: str, p: Probe, local_requirements: dict | None = None) -> dict
  # returns the LAB_SPEC �4 JSON object
```
Thresholds (ADR-014):
- `API_ONLY`: always passes; adds the warning `disk_free_gb < 10` when that condition holds.
- `LOCAL_SMALL_GPU_6GB`: requires `gpu` not null, `vram_free_gb >= weights_gb + 1.0`, `disk_free_gb >= 10 + weights_gb`, and `ram_total_gb >= 15.5`.
- `LOCAL_CPU_TINY`: requires `params_b <= 1.0` and `ram_available_gb >= 4`.

A local tier with `local_requirements=None` fails with `missing local_requirements`.

CLI: `aiu hwcheck [--tier T] [--json]`, default tier `API_ONLY`. Without `--json`, prints `hwcheck: <tier> PASS|FAIL` followed by the failures. Exit 0 on pass, 5 on fail.

**Steps:**
1. Implement with an injectable `run_cmd`.
2. Tests use fake probes. The dev-machine profile (measured): ram_total 16, avail 8, disk 41.6, GPU GTX 1060 vram_total 6.0, free 4.0. Expected results:
   - API_ONLY passes.
   - LOCAL_SMALL_GPU_6GB with weights 2.0 passes.
   - LOCAL_SMALL_GPU_6GB with weights 3.5 fails, because 4.0 < 4.5.
   - gpu=None plus a GPU tier fails.
   - LOCAL_CPU_TINY with params 1.5 fails.
   - Disk 8 on API_ONLY passes with a warning.
   - A nonexistent nvidia-smi binary gives gpu None.

**Acceptance tests:**
- `uv run pytest tests/test_hardware.py` ? exit 0.
- `uv run aiu hwcheck --json` ? valid JSON with `"passed": true`, exit 0.
- `uv run aiu hwcheck --tier LOCAL_SMALL_GPU_6GB` ? exit 5. No local_requirements are given, so the output contains `missing local_requirements`.

**Commands:** `uv run pytest tests/test_hardware.py; uv run aiu hwcheck --json`

**Definition of done:**
- [ ] The actual `hwcheck --json` output from the dev machine is pasted into the JOURNAL entry, labeled measured.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Downloading weights; benchmarking tokens/sec.

**Open decisions:** none.

---

### T-010: Implement metrics library

**Goal:** Every ADR-011 metric is implemented in `src/aiu/metrics.py` and verified against hand-computed values.

**Depends on:** T-008.

**Files:**
- create: `src/aiu/metrics.py`, `tests/test_metrics.py`

**Interfaces / schemas:**
```python
def accuracy(pred: Sequence[object|None], gold: Sequence[object]) -> float
def parse_rate(pred: Sequence[object|None]) -> float
def cohen_kappa(a: Sequence[str], b: Sequence[str]) -> float | None
def tpr(pred: Sequence[str], gold: Sequence[str], positive: str) -> float | None
def tnr(pred: Sequence[str], gold: Sequence[str], positive: str) -> float | None
def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]   # n==0 -> (0.0, 1.0)
def flip_rate(ab: Sequence[str], ba: Sequence[str]) -> float            # inputs are chosen answer identities
def first_slot_rate(choices: Sequence[str]) -> float                    # choices in {"A","B"}
def rogan_gladen(p_obs: float, tpr_: float, tnr_: float) -> float | None
def pass_at_k(n: int, c: int, k: int) -> float
def pass_hat_k(n: int, c: int, k: int) -> float
def ece(conf: Sequence[float], correct: Sequence[bool], bins: int = 10) -> float
def compound(p: float, steps: int) -> float
def normalize_answer(s: str) -> str
def exact_match(pred: str | None, gold: str) -> bool                   # None -> False
def proportion(k: int, n: int) -> dict  # {"value": k/n or None, "n": n, "k": k, "ci95": [lo, hi]}
```

**Steps:**
1. Implement the formulas exactly as written in ADR-011.
2. Tests, all with exact or 1e-9 tolerance unless stated:
   - `cohen_kappa(["p","p","f","f"],["p","f","f","f"]) == 0.5`
   - kappa returns None when p_e == 1
   - `wilson_ci(24,30)` lo ? 0.6269, hi ? 0.9049 (tolerance 1e-3)
   - `rogan_gladen(0.19, 0.8, 0.92) ? 0.15`
   - rogan_gladen returns None when tpr+tnr ? 1
   - `pass_at_k(5,3,3) == 1.0`
   - `pass_hat_k(5,3,3) == 0.1`
   - `compound(0.95,5) ? 0.7738` (tolerance 1e-4)
   - ece is 0 for perfectly calibrated bins
   - a confidence of exactly 1.0 lands in the last bin
   - `normalize_answer("  The, River! ") == "the river"`
   - `flip_rate(["c","c"],["c","w"]) == 0.5`

**Acceptance tests:**
- `uv run pytest tests/test_metrics.py` ? exit 0.

**Commands:** `uv run pytest tests/test_metrics.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Plotting; macro_f1 and confusion matrices (needed only by specified lab E3, v2).

**Open decisions:** none.

---

### T-011: Implement cost estimator and CostGuard

**Goal:** Pre-run and mid-run cost guards behave as ADR-008 specifies and are proven by tests.

**Depends on:** T-008.

**Files:**
- create: `src/aiu/cost.py`, `tests/test_cost.py`

**Interfaces / schemas:**
```python
def estimate_call(call: PlannedCall, price: Price) -> float
  # est_in = ceil(total utf-8 bytes of all message contents / 3); est_out = max_tokens
def actual_cost(prompt_tokens: int, completion_tokens: int, price: Price) -> float
def price_for(cfg: Config, role: str, mode: str) -> Price
  # fixture -> pricing.fixture_defaults; live -> pricing.models[model_id] (ConfigError if missing)
def effective_cap(cfg: Config, requested: float | None, kind: Literal["lab","smoke"]) -> float
  # None -> config default; requested > default -> ConfigError (exit 6)
class CostCapExceeded(Exception): ...   # the CLI maps this to exit 4
class CostGuard:
  def __init__(self, cap_usd: float): ...
  def preflight(self, estimates: list[float]) -> None   # raises CostCapExceeded if sum > cap
  def before_call(self, est_next: float) -> None        # raises if actual_so_far + est_next > cap
  def record(self, usd: float) -> None
  actual_so_far: float; calls: int
def cost_record(...) -> dict   # the exact LAB_SPEC �5 cost.json keys
```

**Steps:**
1. Implement the module.
2. Tests:
   - A message of 300 ASCII bytes with max_tokens 16 at 0.5/1.5 gives `(100*0.5 + 16*1.5)/1e6`.
   - A preflight sum of 2.01 against cap 2.00 raises.
   - A mid-run actual of 1.99 plus an estimate of 0.02 raises.
   - `effective_cap(cfg, 3.0, "lab")` raises ConfigError.
   - `effective_cap(cfg, 0.5, "lab") == 0.5`.

**Acceptance tests:**
- `uv run pytest tests/test_cost.py` ? exit 0.

**Commands:** `uv run pytest tests/test_cost.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Fetching live prices.

**Open decisions:** none.

---

### T-012: Implement client interface and FixtureClient

**Goal:** Planned calls resolve to fixture records deterministically, with exit 3 on a missing or mismatched fixture.

**Depends on:** T-011.

**Files:**
- create: `src/aiu/clients/__init__.py`, `src/aiu/clients/base.py`, `src/aiu/clients/fixture.py`, `tests/test_fixture_client.py`

**Interfaces / schemas:**
```python
class LLMClient(Protocol):
  def complete(self, call: PlannedCall, model_id: str) -> CallResult: ...
class MissingFixture(Exception): ...   # the CLI maps this to exit 3
class FixtureClient:
  def __init__(self, path: Path): ...   # loads JSONL keyed by call_key; duplicate key -> ValueError
  def complete(self, call, model_id) -> CallResult
    # absent key -> MissingFixture
    # record.source == "fixture_recorded" and request_sha256 != call.request_sha256() -> MissingFixture
    # returns the stored CallResult with latency_ms=0
```
Fixture JSONL line = `CallResult.model_dump()` as JSON.

**Steps:**
1. Implement.
2. Tests:
   - A hit returns the stored text.
   - A miss raises.
   - A recorded record with a hash mismatch raises.
   - A synthetic record with a hash mismatch returns.
   - Duplicate keys raise ValueError.

**Acceptance tests:**
- `uv run pytest tests/test_fixture_client.py` ? exit 0.

**Commands:** `uv run pytest tests/test_fixture_client.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** HTTP.

**Open decisions:** none.

---

### T-013: Implement OpenRouterClient with retries and mock-transport tests

**Goal:** A live HTTP client implements ADR-005 exactly and is tested with zero sockets.

**Depends on:** T-012.

**Files:**
- create: `src/aiu/clients/openrouter.py`, `tests/test_openrouter_client.py`

**Interfaces / schemas:**
```python
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
RETRY_STATUS = {408, 429, 500, 502, 503, 504}
class AuthError(Exception): ...        # HTTP 401 -> the CLI exits 6
class ProviderError(Exception): ...    # retries exhausted or non-retryable 4xx
class OpenRouterClient:
  def __init__(self, api_key: str, transport: httpx.BaseTransport | None = None,
               sleep: Callable[[float], None] = time.sleep, timeout: float = 60.0): ...
  def complete(self, call: PlannedCall, model_id: str) -> CallResult
    # body keys per ADR-005; omit seed if None, response_format if None, logprobs if False
    # text = choices[0].message.content (None -> "")
    # tokens from usage.prompt_tokens / completion_tokens (missing -> 0, record warning)
    # provider_reported_usd = usage.cost if present else None
    # source="live"; timestamp = UTC ISO-8601
def api_key_from_env() -> str   # ConfigError if OPENROUTER_API_KEY is unset or empty
```
Retry rule: at most 3 retries, sleeping `2**attempt` for attempt 0, 1, 2. The key never appears in logs, exceptions, or artifacts.

**Steps:**
1. Implement.
2. Tests use `httpx.MockTransport`:
   - (a) The request body and headers match the spec, `Authorization` included, and `X-Title: AI University` is present.
   - (b) 429, 429, then 200 succeeds, with sleep called with [1, 2].
   - (c) Four consecutive 503s raise ProviderError after 3 retries.
   - (d) 401 raises AuthError without retrying.
   - (e) 400 raises ProviderError without retrying.
   - (f) A missing usage block gives tokens 0.
   - (g) `repr` and `str` of exceptions do not contain the key.

**Acceptance tests:**
- `uv run pytest tests/test_openrouter_client.py` ? exit 0, with zero socket errors (pytest-socket is active).

**Commands:** `uv run pytest tests/test_openrouter_client.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Streaming, async, provider fallback routing.

**Open decisions:** none.

---

### T-014: Implement run IDs, `lab new-run`, and the prediction gate

**Goal:** A run directory with a prediction template can be created, and `check_prediction` enforces ADR-016.

**Depends on:** T-007.

**Files:**
- create: `src/aiu/runs.py`, `tests/test_runs.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
RUN_ID_RE = re.compile(r"^[0-9]{8}T[0-9]{6}Z-(fixture|live)-[0-9a-f]{6}$")
def new_run_id(mode: str, now: datetime | None = None, rand_hex: str | None = None) -> str
def default_out_dir(mode: str) -> Path        # fixture -> ".runs", live -> "experiments"
def run_dir(out: Path, lab_id: str, run_id: str) -> Path
def create_run(root: Path, lab_id: str, mode: str, out: Path | None) -> tuple[str, Path]
  # copies experiments/_template/prediction.md and fills front matter lab_id, run_id, mode;
  # leaves written_at empty and predicted_metrics as {}
class PredictionGateError(Exception): ...     # the CLI maps this to exit 7
def check_prediction(path: Path, metric_names: set[str], now: datetime) -> dict
  # YAML front matter between the first two '---' lines; requires written_at (ISO-8601 UTC) < now;
  # predicted_metrics is a non-empty mapping with keys ? metric_names
def freeze_prediction(rdir: Path) -> str      # writes prediction.sha256 (hex of file bytes) and returns it
def prediction_unchanged(rdir: Path) -> bool
```
CLI: `aiu lab new-run LAB_ID --mode fixture|live [--out-dir PATH]` prints `run_id=<id> dir=<path>`, exit 0. It exits 6 if `labs/<LAB_ID>/manifest.yaml` is absent; until T-017 lands, tests use a tmp manifest.

**Steps:**
1. Implement.
2. Tests:
   - The regex matches the generated ID.
   - An empty predicted_metrics raises.
   - An unknown metric key raises.
   - A future written_at raises.
   - A valid prediction passes.
   - The hash changes after an edit.

**Acceptance tests:**
- `uv run pytest tests/test_runs.py` ? exit 0.

**Commands:** `uv run pytest tests/test_runs.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Executing labs.

**Open decisions:** none.

---

### T-015: Implement the lab registry, runner engine, and `lab run` / `lab estimate`

**Goal:** `aiu.runner.run_lab` executes the LAB_SPEC �3 algorithm for any registered lab, with exact exit codes.

**Depends on:** T-009, T-010, T-012, T-013, T-014.

**Files:**
- create: `src/aiu/runner.py`, `src/aiu/labs/__init__.py`, `src/aiu/labs/base.py`, `tests/test_runner.py`, `tests/fixtures/toy_lab/` (manifest.yaml, data/items.jsonl with 4 items, fixtures/responses.jsonl)
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
class LabImpl(Protocol):
  lab_id: str
  def plan(self, items: list[Item], manifest: dict, cfg: Config) -> list[PlannedCall]
  def score(self, items: list[Item], results: list[CallResult], manifest: dict) -> dict[str, float | None]
REGISTRY: dict[str, type[LabImpl]]  # filled by T-019..T-023
def register(cls): ...               # decorator
def load_manifest(root: Path, lab_id: str) -> dict
def load_items(path: Path, limit: int | None) -> list[Item]   # sorted by id; first N
def evaluate(conds: list[dict], metrics: dict, rule: str) -> bool | None  # None if any referenced metric is None or missing
def run_lab(root: Path, lab_id: str, run_id: str, mode: str, cap: float | None,
            limit: int | None, record: bool, out: Path | None,
            client_factory: Callable[[str], LLMClient] | None = None, now: datetime | None = None) -> int
def estimate_lab(root: Path, lab_id: str, limit: int | None, mode: str = "live") -> float
```
Artifact contents:
- `config.json`: `{lab_id, run_id, mode, manifest_sha256, roles: {role: {model_id, family}}, temperature, seed, max_tokens, samples_per_call, limit, started_at, aiu_version, hw: <hwcheck dict>}`
- `result.json`: `{status: "completed"|"aborted_cost"|"failed", hypothesis_supported: bool|null, validity_passed: bool|null, evidence_class: "measured"|"assumed", finished_at, n_calls, error: str|null}`
- `evidence_class` is `measured` only if `mode == live` and every CallResult.source is `live`.
- `metrics.json`: `{metrics: {...flat...}, proportions: {name: proportion dict}, evidence_class}`
- `responses.jsonl`: one CallResult per line.

`--record` (live only) overwrites `labs/<id>/fixtures/responses.jsonl` with `fixture_recorded` copies. It is an error in fixture mode (exit 6).

Exit mapping:
- `ConfigError` ? 6
- `PredictionGateError` ? 7
- hardware fail ? 5
- `CostCapExceeded` ? 4, after writing `result.json` with `aborted_cost` plus partial `responses.jsonl` and `cost.json`
- `MissingFixture` ? 3
- `AuthError` ? 6
- `ProviderError` ? 1, after writing `result.json` with `failed`

stdout is exactly one line, `run_id=<id> status=<s> cost_usd=<x.xxxx>`. No metric is printed.

CLI:
- `aiu lab run LAB_ID --run-id RUN_ID --mode M [--cap USD] [--limit N] [--record] [--out-dir PATH]`
- `aiu lab estimate LAB_ID [--limit N]` prints `estimate_usd=<x.xxxx> calls=<n> cap_usd=<y>`. It uses live pricing if every role is pinned, otherwise fixture_defaults with the suffix ` basis=assumed`. Exit 0.

**Steps:**
1. Implement the runner and a toy LabImpl registered only in tests (a `conftest.py` registers `toy`). The toy lab uses ID `L-999` under `tmp_path`.
2. Tests:
   - Fixture run ? exit 0 with all 8 artifacts present, `evidence_class == "assumed"`, and stdout matching the regex.
   - Missing prediction ? 7.
   - Cap 0.0000001 ? 4 with `result.json.status == "aborted_cost"`.
   - A removed fixture line ? 3.
   - Live mode with UNPINNED roles ? 6.
   - The prediction edited after the run ? `prediction_unchanged` is False.

**Acceptance tests:**
- `uv run pytest tests/test_runner.py` ? exit 0.

**Commands:** `uv run pytest tests/test_runner.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Real lab implementations; postmortem validation.

**Open decisions:** none.

---

### T-016: Implement post-mortem check

**Goal:** `aiu lab postmortem-check` exits 0 only for a complete post-mortem whose prediction is unchanged.

**Depends on:** T-015.

**Files:**
- create: `src/aiu/postmortem.py`, `tests/test_postmortem.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:** Required headings in `postmortem.md` are those of `experiments/_template/postmortem.md`:
- `## Prediction vs outcome`
- `## What surprised me`
- `## Confounds observed`
- `## Rule-of-thumb update`
- `## Next experiment`

```python
REQUIRED_HEADINGS: tuple[str, ...]  # exactly the five above
def check_postmortem(rdir: Path) -> list[str]
  # problems: missing file; missing heading; a section body shorter than 20 non-whitespace chars
  # or still containing the template placeholder "TODO";
  # front matter `trust_table_row` absent or not a rule text present in learner/trust_table.yaml;
  # prediction.sha256 missing or mismatched
```
CLI: `aiu lab postmortem-check LAB_ID --run-id RUN_ID [--out-dir PATH]` prints each problem, then `postmortem: OK` (exit 0) or `postmortem: <n> problems` (exit 1). The out-dir default follows the mode encoded in run_id.

**Steps:**
1. Implement.
2. Tests:
   - The untouched template ? ?5 problems.
   - A complete post-mortem with a matching trust row ? OK.
   - An edited prediction ? problem `prediction modified after run`.

**Acceptance tests:**
- `uv run pytest tests/test_postmortem.py` ? exit 0.

**Commands:** `uv run pytest tests/test_postmortem.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Judging post-mortem quality (human rubric, GOVERNANCE).

**Open decisions:** none.

---

### T-017: Author all 17 lab manifests and implement `labs list` / `labs check-tiers`

**Goal:** Every lab in LAB_SPEC �6 has a schema-valid manifest, and the tier policy is mechanically checked.

**Depends on:** T-006, T-015.

**Files:**
- create: `labs/<ID>/manifest.yaml` for E1-E13 and L-001-L-004 (17 files), `src/aiu/labs/tiers.py`, `tests/test_tiers.py`, `tests/fixtures/invalid_lab_local_bad_fallback.yaml`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:** Each manifest follows the `lab` schema with these values:
- **From LAB_SPEC �6:** `id`, `title`, `status`, `hardware_tier: API_ONLY`, `concept_ids`, `cost_cap_usd: 2.00`, `cost_basis: assumed`, `expected_cost_usd`, and `post_mortem_template`.
- **From �8/�9:** dataset, conditions, metrics, pass_fail, validity_checks, and confounds.

Metric `name`s with `<cond>` are expanded to one entry per condition. Example: E9 has `accuracy:oracle` . `accuracy:d20_middle`, then `accuracy_drop:d5_start` . `accuracy_drop:d20_middle`, then `max_drop` and `unknown_rate:<cond>`. Every `impl` names a function path such as `aiu.labs.e9.score`.

Field values by lab group:
- **Runnable labs:** `fixtures.path = labs/<ID>/fixtures/responses.jsonl`, `provenance: synthetic`, and `n_calls` equal to the �6 call count (0 for L-003).
- **Specified labs:** `fixtures: {path: null, provenance: none, n_calls: 0}`; `dataset.n_items` as given in �9; `generator: null` where human labels are needed.
- **Lab roles:** `model_roles` copied from �6, with `[]` for "none".
- **`expected_runtime_minutes` (assumed):** runnable labs use `ceil(calls * 1.5 s / 60)`; L-003 uses 1.

```python
def check_tiers(root: Path) -> list[str]
  # each manifest: tier in enum; local tier => api_fallback.lab_id exists, its manifest
  # hardware_tier == API_ONLY, and its fixtures.provenance != "none"; local_requirements present
def list_labs(root: Path) -> list[tuple[str, str, str, str]]   # id, status, tier, title
```
CLI:
- `aiu labs list` prints `<id>\t<status>\t<tier>\t<title>` per lab sorted by id, exit 0.
- `aiu labs check-tiers` prints problems, then `tiers: OK (<n> labs)`; exit 0 or 1. With an explicit file argument (`aiu labs check-tiers PATH`) it checks only that manifest.

**Steps:**
1. Write the 17 manifests.
2. Implement tiers.py and the CLI.
3. Tests:
   - The real repo has 0 problems.
   - A tmp LOCAL_SMALL_GPU_6GB manifest with a fallback to a `specified` lab without fixtures ? problem.
   - A local manifest with weights_gb 4.0 fails schema validation.

**Acceptance tests:**
- `uv run aiu validate labs` ? `validate: 17 files, 0 errors`, exit 0.
- `uv run aiu labs list` ? 17 lines, exit 0.
- `uv run aiu labs check-tiers` ? `tiers: OK (17 labs)`, exit 0.
- `uv run aiu labs check-tiers tests/fixtures/invalid_lab_local_bad_fallback.yaml` ? exit 1.
- `uv run pytest tests/test_tiers.py` ? exit 0.

**Commands:** `uv run aiu validate labs; uv run aiu labs check-tiers; uv run pytest tests/test_tiers.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` shows labs runnable 5 and specified 12.
- [ ] `status --check` passes.

**Out of scope:** Implementing any lab; local-tier labs.

**Open decisions:** none.

---

### T-018: Implement dataset build and synthetic fixture framework

**Goal:** `aiu dataset build` and `aiu fixtures synth` are deterministic and byte-checkable for any lab with a generator.

**Depends on:** T-017.

**Files:**
- create: `src/aiu/generators/__init__.py`, `src/aiu/generators/base.py`, `src/aiu/fixtures_synth.py`, `tests/test_generators_base.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
SEED = 1337
GENERATORS: dict[str, Callable[[random.Random], list[Item]]]   # filled by T-019..T-023
def serialize(items: list[Item]) -> bytes
  # sorted by id; json.dumps(sort_keys=True, ensure_ascii=False, separators=(",",":")); "\n" line endings; trailing "\n"
def build(root: Path, lab_id: str, check: bool) -> int
  # check=True -> compare bytes, exit 1 on diff; else write labs/<id>/data/items.jsonl
SYNTH: dict[str, Callable[[list[Item], list[PlannedCall], random.Random], list[CallResult]]]
def synth(root: Path, lab_id: str, check: bool) -> int
  # plans with fixture mode, no limit; rng = random.Random(SEED); source="fixture_synthetic";
  # model_id="fixture"; prompt_tokens=ceil(bytes/3); completion_tokens=len(text)//4+1;
  # timestamp="1970-01-01T00:00:00Z"
```
CLI: `aiu dataset build LAB_ID [--check]` and `aiu fixtures synth LAB_ID [--check]`. Both print `<cmd>: <lab_id> OK|DIFF|WRITTEN`. Exit codes: 0, 1 on DIFF, 6 if no generator is registered.

**Steps:**
1. Implement.
2. Tests use a toy generator: two builds produce identical bytes; `--check` after a manual edit ? 1; an unknown lab ? 6.

**Acceptance tests:**
- `uv run pytest tests/test_generators_base.py` ? exit 0.
- `uv run aiu dataset build E1` ? exit 6. E1 has no generator, which is expected.

**Commands:** `uv run pytest tests/test_generators_base.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Lab-specific generators.

**Open decisions:** none.

---

### T-019: Implement lab L-003 (eval statistics workbench)

**Goal:** L-003 runs in fixture mode with zero model calls and reproduces exact, hand-checkable statistics.

**Depends on:** T-018.

**Files:**
- create: `src/aiu/generators/l003.py`, `src/aiu/labs/l003.py`, `labs/L-003/data/items.jsonl`, `labs/L-003/data/DATASET_CARD.md`, `labs/L-003/fixtures/responses.jsonl` (empty file), `tests/test_lab_l003.py`

**Interfaces / schemas:** The generator produces 200 label items (IDs `j000`.`j199`) with exact counts from LAB_SPEC �8: 24 TP, 6 FN, 14 FP, 156 TN. The positive label is `fail`. It also produces 20 agent items (`t00`.`t19`) with `expected = {successes: c, trials: 5}`, where c comes from the listed counts. Item order is shuffled by `random.Random(1337)` before ID assignment; ids are then sorted.

`plan()` returns `[]`. `score()` computes the metrics below:

| Metric | Expected value | Tolerance |
|---|---|---|
| `raw_agreement` | 0.90 | exact |
| `tpr` | 0.80 | exact |
| `tnr` | 156/170 | 1e-9 |
| `observed_fail_rate` | 0.19 | exact |
| `true_fail_rate` | 0.15 | exact |
| `corrected_fail_rate` | `rogan_gladen(0.19, 0.8, 156/170)` | 1e-9 |
| `kappa` | 0.6732 | 1e-3 |
| `agreement_minus_kappa` | 0.90 ? kappa | 1e-9 |
| `compound_0.95_5` | 0.7738 | 1e-4 |

`corrected_fail_rate` is approximately 0.1504. Both `kappa` and `corrected_fail_rate` are recomputed in the test from the counts via `aiu.metrics`. `pass_at_3` and `pass_hat_3` are means of `pass_at_k(5,c,3)` and `pass_hat_k(5,c,3)` over the 20 tasks, also recomputed in the test.

The `pass_fail` condition `agreement_minus_kappa >= 0.15` is therefore true by construction.

**Steps:**
1. Implement the generator and lab; register both.
2. `uv run aiu dataset build L-003`; create the empty fixture file.
3. Write the DATASET_CARD.md: synthetic, seed 1337, counts, license per OD-04, and the bias note "rates chosen for teaching, not observed in any real system".
4. Tests: an end-to-end fixture run via `run_lab` into `tmp_path` with a valid prediction, asserting the values above and `hypothesis_supported is True`.

**Acceptance tests:**
- `uv run aiu dataset build L-003 --check` ? `OK`, exit 0.
- `uv run pytest tests/test_lab_l003.py` ? exit 0.
- The PowerShell sequence below ? final exit 0.
  ```
  $o=(uv run aiu lab new-run L-003 --mode fixture); $id=($o -split ' ')[0] -replace 'run_id=',''
  uv run python -c "import sys,pathlib,datetime;p=pathlib.Path('.runs/L-003/'+sys.argv[1]+'/prediction.md');t=p.read_text();t=t.replace('written_at:','written_at: '+(datetime.datetime.utcnow()-datetime.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),1).replace('predicted_metrics: {}','predicted_metrics: {kappa: 0.8}',1);p.write_text(t)" $id
  uv run aiu lab run L-003 --run-id $id --mode fixture
  ```
  This sequence requires the prediction template to contain the literal lines `written_at:` and `predicted_metrics: {}`. If it does not, the template is a spec defect.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Live mode; L-003 has no model calls.

**Open decisions:** OD-04 (content license).

---

### T-020: Implement lab E9 (context distractors and position)

**Goal:** E9 builds its dataset, synthesizes fixtures, and runs end-to-end in fixture mode exactly per LAB_SPEC �8.

**Depends on:** T-018.

**Files:**
- create: `src/aiu/generators/e9.py`, `src/aiu/labs/e9.py`, `labs/E9/data/items.jsonl`, `labs/E9/data/DATASET_CARD.md`, `labs/E9/fixtures/responses.jsonl`, `tests/test_lab_e9.py`, `tests/helpers.py`

**Interfaces / schemas:**
- **Data and prompts:** LAB_SPEC �8 E9 (60 items, 5 conditions, prompts verbatim, role `cheap_a`, temperature 0, seed 1337, max_tokens 16).
- **Distractor order:** `meta.distractor_order` (fixed in the generator), not random at plan time.
- **call_key:** `"{item_id}|{condition}|cheap_a|0"`.
- **Synthetic fixture:** for each call, `rng.random() < error_rate[cond]` produces distractor 0's value, otherwise the expected answer. Rates are given in LAB_SPEC �8.

`tests/helpers.py`:
```python
def fill_prediction(rdir: Path, metrics: dict) -> None   # sets written_at = now-60s, predicted_metrics = metrics
def run_fixture(root: Path, lab_id: str, tmp: Path, limit: int | None = None) -> tuple[int, Path]
```
T-019's test is refactored to use these helpers.

**Steps:**
1. Implement the generator. Entities are fictional names built from syllable lists in the generator file. Each passage is 60-90 words, enforced by a generator assertion.
2. Run `aiu dataset build E9` and `aiu fixtures synth E9`.
3. Tests:
   - 60 items.
   - Every distractor name is within edit distance ?2 of the key name and not equal to it.
   - 300 planned calls.
   - A fixture run exits 0.
   - `metrics.json` contains every manifest metric name.
   - `validity_passed is True`.
   - `evidence_class == "assumed"`.
   - The planned prompt for `d20_middle` places the key passage at index 10.

**Acceptance tests:**
- `uv run aiu dataset build E9 --check` ? exit 0.
- `uv run aiu fixtures synth E9 --check` ? exit 0.
- `uv run pytest tests/test_lab_e9.py` ? exit 0.
- `uv run aiu lab estimate E9` ? line contains `calls=300` and `basis=assumed`, exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended, recording the assumed estimate.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Live runs (T-037).

**Open decisions:** none.

---

### T-021: Implement lab E2 (schema field order)

**Goal:** E2 runs end-to-end in fixture mode per LAB_SPEC �8.

**Depends on:** T-020.

**Files:**
- create: `src/aiu/generators/e2.py`, `src/aiu/labs/e2.py`, `labs/E2/data/items.jsonl`, `labs/E2/data/DATASET_CARD.md`, `labs/E2/fixtures/responses.jsonl`, `tests/test_lab_e2.py`

**Interfaces / schemas:**
- **Data and conditions:** LAB_SPEC �8 E2 (80 items, 40/40 split; conditions verdict_first, reasoning_first, evidence_first).
- **Parser:** first `{` to last `}`, then `json.loads`; `verdict` must be in the allowed set, otherwise None.
- **Synthetic fixture texts:** JSON with keys in the condition's order.
  - A wrong verdict is the flipped label, at the �8 rate.
  - At rate 0.02 the text is `not json` (a parse failure).
  - `evidence_quote` is an exact sentence from the passage.
- **`mean_rationale_chars`:** mean `len(reasoning)` over parsed items.

**Steps:**
1. Implement, build, and synth.
2. Tests:
   - Exactly one attribute differs between the passage fact and each not_entailed claim (the generator records `meta.changed_attr`).
   - The parser handles a leading prose prefix.
   - The fixture run exits 0 with all metrics present and `validity_passed is True`.

**Acceptance tests:**
- `uv run aiu dataset build E2 --check` ? exit 0.
- `uv run aiu fixtures synth E2 --check` ? exit 0.
- `uv run pytest tests/test_lab_e2.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** `response_format` structured-output variant (v2).

**Open decisions:** none.

---

### T-022: Implement lab E4 (escape hatch)

**Goal:** E4 runs end-to-end in fixture mode per LAB_SPEC �8.

**Depends on:** T-020.

**Files:**
- create: `src/aiu/generators/e4.py`, `src/aiu/labs/e4.py`, `labs/E4/data/items.jsonl`, `labs/E4/data/DATASET_CARD.md`, `labs/E4/fixtures/responses.jsonl`, `tests/test_lab_e4.py`

**Interfaces / schemas:**
- **Data and conditions:** LAB_SPEC �8 E4 (80 items with 60 in-taxonomy and 20 OOT, by the exact per-label counts in �8; 2 conditions; label-only output).
- **Parser:** `normalize_answer(text)` must equal a normalized allowed label for the condition, otherwise None.
- **Synthetic fixture rates:** per �8. Random labels are drawn with the same rng.

**Steps:**
1. Implement, build, and synth.
2. Tests:
   - Label counts match �8 exactly.
   - `other` is not allowed in `no_escape` (parses to None).
   - The fixture run exits 0 with `validity_passed is True` and all metrics present.

**Acceptance tests:**
- `uv run aiu dataset build E4 --check` ? exit 0.
- `uv run aiu fixtures synth E4 --check` ? exit 0.
- `uv run pytest tests/test_lab_e4.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Hierarchical classification.

**Open decisions:** none.

---

### T-023: Implement lab E5 (position and verbosity bias)

**Goal:** E5 runs end-to-end in fixture mode per LAB_SPEC �8.

**Depends on:** T-020.

**Files:**
- create: `src/aiu/generators/e5.py`, `src/aiu/labs/e5.py`, `labs/E5/data/items.jsonl`, `labs/E5/data/DATASET_CARD.md`, `labs/E5/fixtures/responses.jsonl`, `tests/test_lab_e5.py`

**Interfaces / schemas:**
- **Data and conditions:** LAB_SPEC �8 E5 (40 items, 4 conditions, role `judge_a`, output `A` or `B`).
- **Score mapping:** the slot letter maps to identity `correct` or `wrong` per condition.
- **Parser:** first non-space char uppercased, which must be in {A, B}, otherwise None. A None is excluded from flip pairs and counted in a `parse_rate` metric that is added to the manifest metric list in this ticket.
- **`flip_rate_padded`:** computed over the pair (cw_padwrong, wc_padwrong).
- **Synthetic fixture:** per �8.

**Steps:**
1. Implement, build, and synth.
2. Update `labs/E5/manifest.yaml` to add `parse_rate` and bump nothing else.
3. Tests:
   - Hand-built results [A,B] for cw and wc give flip_rate 0 and first_slot 0.5.
   - The fixture run exits 0 with `validity_passed is True`.

**Acceptance tests:**
- `uv run aiu dataset build E5 --check` ? exit 0.
- `uv run aiu fixtures synth E5 --check` ? exit 0.
- `uv run pytest tests/test_lab_e5.py` ? exit 0.
- `uv run aiu validate labs` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Cross-family judging (E6).

**Open decisions:** none.

---

### T-024: Implement smoke suite with total cost cap

**Goal:** `aiu smoke --mode fixture` runs every runnable lab with zero network, and `--mode live` is bounded by `smoke_total_usd`.

**Depends on:** T-019, T-020, T-021, T-022, T-023, T-016.

**Files:**
- create: `src/aiu/smoke.py`, `tests/test_smoke.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
SMOKE_PLAN: list[tuple[str, int | None]] = [("L-003", None), ("E9", 20), ("E2", 20), ("E4", 20), ("E5", 20)]
def run_smoke(root: Path, mode: str, cap: float | None, now: datetime | None = None,
              client_factory=None) -> int
  # total_cap = effective_cap(cfg, cap, "smoke")
  # preflight: total estimate over all labs (estimate_lab with limits) > total_cap -> exit 4, no calls
  # per lab: create_run; write prediction with front matter smoke: true, written_at=now-60s,
  #   predicted_metrics={<first manifest metric>: null}; then run_lab with
  #   cap=min(per_lab_usd, total_cap - spent)
  # any lab exit != 0 -> stop and return that code
  # summary written to <out>/smoke-<run_stamp>.json:
  #   {mode, labs:[{lab_id, run_id, status, cost_usd}], total_cost_usd, cap_usd}
```
The prediction gate accepts `null` values when `smoke: true`. This is a `check_prediction` amendment: values may be null only if `smoke` is true. Smoke run dirs created in live mode are real live runs and must be indexed in RESULTS.md (GOVERNANCE) with lesson `smoke run; no learner prediction`.

CLI: `aiu smoke --mode fixture|live [--cap USD]`. It prints one line per lab, then `smoke: <mode> total_cost_usd=<x.xxxx> cap_usd=<y> OK|FAIL`. Exit 0, or the first failing code.

**Steps:**
1. Implement and amend `runs.check_prediction`.
2. Tests:
   - Fixture smoke into tmp ? exit 0 with 5 labs completed and `total_cost_usd == 0`.
   - `--cap 6` ? exit 6.
   - A live smoke with a mock client and a cap below the estimate ? exit 4 with zero calls made.

**Acceptance tests:**
- `uv run aiu smoke --mode fixture` ? last line ends `OK`, exit 0.
- `uv run aiu smoke --mode fixture --cap 6` ? exit 6.
- `uv run pytest tests/test_smoke.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended, with the smoke output pasted.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Running live smoke (T-036).

**Open decisions:** none.

---

### T-025: Implement module checkpoint grader

**Goal:** `aiu checkpoint grade` deterministically grades the deterministic items of a module's checkpoint.

**Depends on:** T-006.

**Files:**
- create: `src/aiu/checkpoint.py`, `tests/test_checkpoint.py`, `learner/checkpoints/.gitkeep`, `tests/fixtures/module_test.yaml`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:** The answers file is YAML of the form `{module_id: M-A1, answers: {Q01: "B", Q02: 0.77}}`.

Grading rules by item type:
- `mcq`: exact match of the trimmed string against `answer`.
- `exact`: `normalize_answer` equality.
- `numeric`: `abs(given - answer) <= tolerance`.
- A missing answer is incorrect.

```python
def grade(module: dict, answers: dict) -> dict
  # {module_id, total, correct, items: {Q01: {correct: bool, given, expected}}, graded_at}
```
CLI: `aiu checkpoint grade MODULE_ID --answers PATH`. The module is loaded from `curriculum/modules/<ID>.yaml`; a missing module ? exit 6. Writes `learner/checkpoints/<ID>.result.json` and prints `checkpoint: <correct>/<total>`. Exit 0 if every item is correct, otherwise 1.

**Steps:**
1. Implement.
2. Tests use the fixture module (3 items, one of each type): all correct ? exit 0; one wrong ? exit 1; a numeric answer within tolerance ? correct.

**Acceptance tests:**
- `uv run pytest tests/test_checkpoint.py` ? exit 0.

**Commands:** `uv run pytest tests/test_checkpoint.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Grading human-rubric items; LLM grading (forbidden, ADR-019).

**Open decisions:** none.

---

### T-026: Implement provenance ledger check

**Goal:** `aiu provenance check` exits 1 if any card cites a claim missing from `PROVENANCE.md` or disagrees with the ledger status.

**Depends on:** T-006.

**Files:**
- create: `src/aiu/provenance.py`, `tests/test_provenance.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:** Ledger rows are markdown table rows beginning `| P-###`, with columns in this order: `ID | Claim | Tag | Status | Source | Date | Method | Cards`.
```python
@dataclass(frozen=True)
class Claim: id: str; claim: str; tag: str; status: str; source: str; date: str; method: str; cards: list[str]
def parse_ledger(text: str) -> dict[str, Claim]   # duplicate id or status not in enum -> ValueError
def check(root: Path) -> list[str]
  # 1. every card verify[].claim_id exists in the ledger
  # 2. card verify status == ledger status
  # 3. ledger status "verified" requires a non-empty Source, a YYYY-MM-DD Date, and a non-empty Method
  # 4. every card ID listed in a ledger row's Cards column that has a card file cites that claim
```
CLI: `aiu provenance check` prints problems, then `provenance: OK (<n> claims)`; exit 0 or 1.

**Steps:**
1. Implement.
2. Tests:
   - Synthetic ledger and card in tmp: OK.
   - Missing claim ? problem.
   - Status mismatch ? problem.
   - A verified row with an empty source ? problem.

**Acceptance tests:**
- `uv run aiu provenance check` ? exit 0 against the real repo (exemplar cards cite P-001, P-011, and P-042, which exist in the handoff ledger).
- `uv run pytest tests/test_provenance.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Fetching or checking URLs; only humans verify (ADR-018).

**Open decisions:** none.

---

### T-027: Implement traceability check

**Goal:** `aiu traceability check` enforces the TRACEABILITY.md rules against the card files.

**Depends on:** T-006.

**Files:**
- create: `src/aiu/traceability.py`, `tests/test_traceability.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
@dataclass(frozen=True)
class Row: src: str; concept: str; card: str; experiment: str; tag: str; status: str
def parse_rows(text: str) -> list[Row]   # rows starting "| �" or "| none"
def check(root: Path, require_all_cards: bool) -> list[str]
  # 1. each card file appears in exactly one row (match by card id)
  # 2. card.source_section == row.src
  # 3. row.experiment == "-" <=> card.experiment_id is null; else equal
  # 4. each referenced experiment (not "-", not "E1-E13") has labs/<id>/manifest.yaml
  # 5. if require_all_cards: every row card id matching ^[A-F]-\d{3}$ has a file
```
CLI: `aiu traceability check [--require-all]` prints problems, then `traceability: OK (<rows> rows, <cards> cards)`; exit 0 or 1.

**Steps:**
1. Implement.
2. Tests:
   - A tmp repo with a matching card ? OK.
   - A source_section mismatch ? problem.
   - experiment null versus `E9` ? problem.
   - A card absent from the table ? problem.

**Acceptance tests:**
- `uv run aiu traceability check` ? exit 0 (3 exemplar cards).
- `uv run aiu traceability check --require-all` ? exit 1 before T-033. This is expected and is recorded in the JOURNAL.
- `uv run pytest tests/test_traceability.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Editing TRACEABILITY.md content.

**Open decisions:** none.

---

### T-028: Author the 13 module YAML files

**Goal:** Every module in LAB_SPEC �7 exists as a schema-valid YAML file, and M-A1's checkpoint is gradeable.

**Depends on:** T-025, T-017.

**Files:**
- create: `curriculum/modules/M-A1.yaml`, `M-A2.yaml`, `M-B1.yaml`, `M-B2.yaml`, `M-B3.yaml`, `M-C1.yaml`, `M-C2.yaml`, `M-C3.yaml`, `M-D1.yaml`, `M-D2.yaml`, `M-E1.yaml`, `M-F1.yaml`, `M-F2.yaml`, `tests/test_modules.py`, `tests/fixtures/M-A1.answers.yaml`

**Interfaces / schemas:**
- **Source fields:** `card_ids`, `lab_ids`, `conceptual`, and `level` are taken from LAB_SPEC �7.
- **`objective`:** begins `Can ` and names an observable capability.
- **Checkpoint:** ?3 deterministic items whose answers are derivable from the cards or ADR-011 formulas, and ?2 human_rubric lines.
- **`portfolio_artifact.path_pattern`:** `learner/portfolio/<MODULE_ID>/`.

M-A1 must include these items:
- `Q01` (numeric): accuracy drop when oracle=0.95 and d20_middle=0.80; answer 0.15, tolerance 0.001.
- `Q02` (mcq): which playbook step checks whether the information is in context; choices ["Step 1","Step 2","Step 5","Step 7"]; answer "Step 2".
- `Q03` (exact): the term for running the strongest model with oracle context; answer "ceiling test".

`tests/fixtures/M-A1.answers.yaml` holds the correct answers.

Test requirements:
- Every card appears in exactly one module.
- Module card IDs match TRACEABILITY card IDs (A-001.F-010 and C-019).
- Every `lab_ids` entry has a manifest.

**Steps:**
1. Author the files.
2. Write the tests.

**Acceptance tests:**
- `uv run aiu validate curriculum/modules` ? `validate: 13 files, 0 errors`, exit 0.
- `uv run aiu checkpoint grade M-A1 --answers tests/fixtures/M-A1.answers.yaml` ? `checkpoint: 3/3`, exit 0. Afterwards, delete `learner/checkpoints/M-A1.result.json`; it is not committed by this ticket.
- `uv run pytest tests/test_modules.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Card content.

**Open decisions:** none.

---

### T-029: Author level A cards A-002..A-010

**Goal:** All 10 level-A cards exist, validate, and pass provenance and traceability checks.

**Depends on:** T-026, T-027.

**Files:**
- create: `curriculum/A/A-002.yaml` . `curriculum/A/A-010.yaml` (9 files)
- modify: `PROVENANCE.md` (append rows only, for new P-### IDs if a card needs a claim not already seeded)

**Interfaces / schemas:**
- **Schema:** `card` in `schemas/curriculum.schema.json`.
- **`source_section` and `experiment_id`:** exactly as in the TRACEABILITY row.
- **Provenance:** carried from the source tag. Every S/K claim gets a `verify` item with `status: unverified`.
- **Card content:** each card has ?1 `when_it_fails` item, and any number in the card is written as "reported" or "claimed".
- **Card metadata:** `status: draft`, `version: 1.0.0`.

**Steps:**
1. Write the cards using the A-001 exemplar style.
2. Append any new ledger rows.
3. Run the checks.

**Acceptance tests:**
- `uv run aiu validate curriculum/A` ? `validate: 10 files, 0 errors`, exit 0.
- `uv run aiu provenance check` ? exit 0.
- `uv run aiu traceability check` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] Human content review is requested in the JOURNAL; cards stay `draft` until reviewed.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Marking claims verified.

**Open decisions:** none.

---

### T-030: Author level B cards B-002..B-014

**Goal:** All 14 level-B cards exist and pass all content checks.

**Depends on:** T-029.

**Files:**
- create: `curriculum/B/B-002.yaml` . `curriculum/B/B-014.yaml` (13 files)
- modify: `PROVENANCE.md` (append only)

**Interfaces / schemas:** The rules of T-029 apply. B-004 and B-005 have `experiment_id: null`, with `experiment_null_reason` copied from TRACEABILITY. B-006 `when_it_fails` must state that the "?7 labels" default is untested `[K]`, to be measured by E3.

**Steps:** Author the cards; append ledger rows; run the checks.

**Acceptance tests:**
- `uv run aiu validate curriculum/B` ? `validate: 14 files, 0 errors`, exit 0.
- `uv run aiu provenance check` ? exit 0.
- `uv run aiu traceability check` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Same as T-029.

**Open decisions:** none.

---

### T-031: Author level C cards (18 remaining)

**Goal:** All 19 level-C cards (C-001..C-019, of which C-004 already exists) exist and pass all checks.

**Depends on:** T-030.

**Files:**
- create: `curriculum/C/C-001.yaml`, `C-002`, `C-003`, `C-005` . `C-019` (18 files)
- modify: `PROVENANCE.md` (append only)

**Interfaces / schemas:**
- The rules of T-029 apply.
- C-019 has `provenance: [ADD]`, `source_section: none`, and `add_justification` copied from TRACEABILITY.
- C-005 states the 33-41 point gap as "reported in one 2026 study (sourced, unverified)".
- C-018 lists the �7 failure catalog in `why_it_matters` or `tags`.

**Steps:** Author the cards; append ledger rows; run the checks.

**Acceptance tests:**
- `uv run aiu validate curriculum/C` ? `validate: 19 files, 0 errors`, exit 0.
- `uv run aiu provenance check` ? exit 0.
- `uv run aiu traceability check` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Same as T-029.

**Open decisions:** none.

---

### T-032: Author level D and E cards

**Goal:** All 15 level-D and 7 level-E cards exist and pass all checks.

**Depends on:** T-031.

**Files:**
- create: `curriculum/D/D-001.yaml` . `D-015.yaml` (15 files), `curriculum/E/E-001.yaml` . `E-007.yaml` (7 files)
- modify: `PROVENANCE.md` (append only)

**Interfaces / schemas:**
- The rules of T-029 apply.
- D-004 states "five steps at 95% ? 77%" as arithmetic, which is computed and needs no verification. Its other claims remain unverified K.
- D-012 `experiment_null_reason` references `src/aiu/clients/openrouter.py`.
- E-006 notes "read-only in v1".

**Steps:** Author the cards; append ledger rows; run the checks.

**Acceptance tests:**
- `uv run aiu validate curriculum/D curriculum/E` ? `validate: 22 files, 0 errors`, exit 0.
- `uv run aiu provenance check` ? exit 0.
- `uv run aiu traceability check` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Same as T-029.

**Open decisions:** none.

---

### T-033: Author level F cards and close traceability

**Goal:** All 75 cards exist, and `aiu traceability check --require-all` exits 0.

**Depends on:** T-032, T-028.

**Files:**
- create: `curriculum/F/F-001.yaml` . `F-010.yaml` (10 files)
- modify: `PROVENANCE.md` (append only)

**Interfaces / schemas:**
- The rules of T-029 apply.
- F-007 `when_it_fails` and `why_it_matters` reference the measured dev-machine profile: GTX 1060 6 GB, Pascal, no tensor cores, no bf16. This illustrates memory-bandwidth-bound decoding without requiring any run.
- F-010 states that local nanochat training is out of scope per the local-model policy.

**Steps:** Author the cards; run all checks.

**Acceptance tests:**
- `uv run aiu validate curriculum` ? `validate: 88 files, 0 errors`, exit 0. The count is 75 cards plus 13 modules.
- `uv run aiu traceability check --require-all` ? exit 0.
- `uv run aiu provenance check` ? exit 0.
- `uv run pytest tests/test_modules.py` ? exit 0.

**Commands:** as in the acceptance tests.

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` shows 75 cards; `status --check` passes.

**Out of scope:** Same as T-029.

**Open decisions:** none.

---

### T-034: Write learner guide and M-A1 walkthrough

**Goal:** A learner can follow `docs/LEARNER_GUIDE.md` through module M-A1 using only repo commands.

**Depends on:** T-028, T-020, T-016.

**Files:**
- create: `docs/LEARNER_GUIDE.md`, `tests/test_learner_guide.py`

**Interfaces / schemas:** The guide has these sections, in order:
1. `## Setup`, covering `ops/bootstrap.ps1` and `.env`.
2. `## The learning loop`, covering prediction ? run ? post-mortem ? trust table.
3. `## Module M-A1 walkthrough`, with the exact LAB_SPEC �2 commands for E9, then `aiu checkpoint grade M-A1 --answers learner/checkpoints/M-A1.answers.yaml`, then the portfolio artifact path.
4. `## Fixture mode practice`, the same loop with `--mode fixture`, clearly labeled "results are assumed, not measured".
5. `## Costs`, listing the assumed estimate and the $2 cap.
6. `## What the harness will refuse to do`, mapping exit codes 3-7.

Test requirement: every line in the guide's fenced code blocks that starts with `uv run aiu` must name a subcommand registered in `build_parser()`.

**Steps:** Write the guide and the test.

**Acceptance tests:**
- `uv run pytest tests/test_learner_guide.py` ? exit 0.

**Commands:** `uv run pytest tests/test_learner_guide.py`

**Definition of done:**
- [ ] JOURNAL entry appended.
- [ ] `status --write` and `status --check` pass.

**Out of scope:** Guides for other modules.

**Open decisions:** none.

---

### T-035: Implement repo-layout test and `aiu check-all`

**Goal:** One command runs every offline check, records test results in `status.json`, and enforces REPO_LAYOUT.md.

**Depends on:** T-024, T-026, T-027, T-033, T-034.

**Files:**
- create: `tests/test_layout.py`, `src/aiu/checkall.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**

`tests/test_layout.py` asserts four things:
1. The tracked top-level entries (`git ls-files` first path segment, plus `.runs` if present) are a subset of the REPO_LAYOUT.md tree.
2. Every directory under `labs/` matches the lab_id pattern.
3. `experiments/` contains only `_template` and lab_id dirs, and each run dir matches RUN_ID_RE with mode `live`.
4. `.runs/` is not tracked.

```python
CHECKS = [
  ["secrets-scan"], ["journal", "check"], ["validate"], ["labs", "check-tiers"],
  ["provenance", "check"], ["traceability", "check", "--require-all"],
  ["dataset", "build", "<each generator lab>", "--check"], ["fixtures", "synth", "<each runnable lab>", "--check"],
  ["smoke", "--mode", "fixture"],
]
def check_all(root: Path) -> int
  # runs CHECKS in-process via main(); then subprocess `uv run pytest` (inherits --disable-socket);
  # parses "N passed" / "M failed" from the pytest summary;
  # writes status.json.tests = {passed, failed, ran_at}; then status --write; then status --check;
  # prints "check-all: <k>/<total> checks OK"; returns 0 iff all are 0
```
CLI: `aiu check-all`.

**Steps:**
1. Implement.
2. Run it and fix any finding in the offending ticket's scope, recording each fix in the JOURNAL.

**Acceptance tests:**
- `uv run pytest tests/test_layout.py` ? exit 0.
- `uv run aiu check-all` ? last line `check-all: <n>/<n> checks OK`, exit 0.
- `uv run python -c "import json;t=json.load(open('status.json'))['tests'];assert t['failed']==0 and t['passed']>0"` ? exit 0.

**Commands:** `uv run aiu check-all`

**Definition of done:**
- [ ] JOURNAL entry appended, with the check-all output.
- [ ] `status.json.tests` is populated; README block is regenerated.

**Out of scope:** Live checks.

**Open decisions:** none.

---

### T-036: Pin models and prices, recompute expected costs, and run live smoke

**Goal:** Models and prices are pinned with dates, manifests carry pinned-pricing estimates, and one live smoke run completes under $5.00 (measured).

**Depends on:** T-035. Also blocked on human input: OD-01 and OD-02.

**Files:**
- modify: `config/models.yaml`, `config/pricing.yaml`, `labs/E2/manifest.yaml`, `labs/E4/manifest.yaml`, `labs/E5/manifest.yaml`, `labs/E9/manifest.yaml`, `labs/L-003/manifest.yaml`, `DECISIONS.md` (append ADR-024 recording the pinned IDs, prices, and date), `RESULTS.md`, `PROVENANCE.md` (append rows for pricing and OpenRouter usage, seed, and logprob behavior observed)
- create: `experiments/<lab_id>/<run_id>/.` for each smoke lab (committed, including failures)

**Interfaces / schemas:**
- **models.yaml:** the human-supplied IDs. judge_a.family must differ from judge_b.family, and cheap_a/b/c must be three distinct families. Add a test in `tests/test_config.py` asserting distinct families when nothing is UNPINNED.
- **pricing.yaml:** `retrieved_at` is the pinning date, and `models` holds one entry per pinned ID. Prices are sourced from the OpenRouter model page on that date.
- **Runnable manifests:** `expected_cost_usd` = the `aiu lab estimate` value; `cost_basis: estimated_from_pinned_pricing`.

**Steps:**
1. The human supplies IDs and prices. The implementer edits the configs and appends ADR-024.
2. `uv run aiu lab estimate <ID>` for each runnable lab; write the values into the manifests.
3. Set `$env:OPENROUTER_API_KEY` in the shell only.
4. `uv run aiu smoke --mode live`.
5. Add one RESULTS.md row per live run dir, with lesson `smoke run; no learner prediction`, and append the observed behavior to PROVENANCE as `unverified` or measured-for-our-setup rows.
6. `uv run aiu secrets-scan`, then `uv run aiu check-all`.

**Acceptance tests:**
- `uv run aiu lab estimate E9` ? no `basis=assumed`, exit 0.
- `uv run aiu smoke --mode live` ? last line ends `OK`, with `total_cost_usd` < 5.00, exit 0. If it exits 4 or 1, the run dirs are still committed and the ticket is returned as a spec defect with the JOURNAL entry.
- `uv run aiu status --check` ? exit 0. Every live run_id appears in RESULTS.md and the cumulative cost matches.
- `uv run aiu secrets-scan` ? exit 0.

**Commands:** as in Steps.

**Definition of done:**
- [ ] JOURNAL entry appended, with per-lab measured cost, total, and model IDs with date.
- [ ] README spend is updated via `status --write`.
- [ ] CHANGELOG entry added.

**Out of scope:** Learner-prediction runs (T-037); changing prompts to make tests pass.

**Open decisions:** OD-01 (model IDs), OD-02 (approval to spend up to $5.00 on live smoke).

---

### T-037: Complete module M-A1 end-to-end with a live E9 run

**Goal:** One full learning loop (prediction ? live E9 ? post-mortem ? trust-table row ? checkpoint ? portfolio ? learning write-up) exists in the repo with measured numbers.

**Depends on:** T-036, T-034.

**Files:**
- create: `experiments/E9/<run_id>/` (all 8 artifacts plus a filled `postmortem.md`), `learner/portfolio/M-A1/README.md`, `learner/checkpoints/M-A1.answers.yaml`, `learner/checkpoints/M-A1.result.json`, `docs/learnings/YYYY-MM-DD-e9-context-distractors.md`
- modify: `learner/trust_table.yaml` (one row for A-008 or A-001), `RESULTS.md`, `CHANGELOG.md`

**Interfaces / schemas:**
- **Trust row:** follows the `trust_row` schema. `my_replication` is set from `result.json.hypothesis_supported`: true ? `replicated`, false ? `failed_to_replicate`, null ? `inconclusive`. `run_ids` holds `[<run_id>]`.
- **Learning write-up:** follows `docs/learnings/_template.md`. Every number links to `experiments/E9/<run_id>/metrics.json` and `cost.json`.
- **Outcome logging:** negative or inconclusive outcomes are logged exactly as observed.

**Steps:** Follow docs/LEARNER_GUIDE.md "Module M-A1 walkthrough" verbatim. The human writes the prediction and post-mortem content, or explicitly delegates them and records the delegation in the JOURNAL.

**Acceptance tests:**
- `uv run aiu lab postmortem-check E9 --run-id <run_id>` ? `postmortem: OK`, exit 0.
- `uv run aiu checkpoint grade M-A1 --answers learner/checkpoints/M-A1.answers.yaml` ? exit 0.
- `uv run aiu validate learner` ? exit 0.
- `uv run aiu status --check` ? exit 0.
- `uv run python -c "import json;assert json.load(open('experiments/E9/<run_id>/result.json'))['evidence_class']=='measured'"` ? exit 0.

**Commands:** LAB_SPEC �2 sequence with `E9`, then the commands above.

**Definition of done:**
- [ ] JOURNAL entry appended, with measured cost.
- [ ] RESULTS row added; CHANGELOG entry added.
- [ ] `status --write` done; `check-all` exits 0.

**Out of scope:** Other modules; editing the prediction after the run (forbidden).

**Open decisions:** OD-06 (whether the human or the implementer authors the learner prediction and post-mortem).

---

### T-038: Run final v1 acceptance

**Goal:** Every check in ACCEPTANCE.md passes from a clean checkout, and the result is recorded publicly.

**Depends on:** T-037.

**Files:**
- create: `docs/learnings/YYYY-MM-DD-v1-acceptance.md`
- modify: `README.md` (non-generated sections: the "what works / what doesn't" table must match ACCEPTANCE results), `CHANGELOG.md` (`v1.0.0`), `JOURNAL.md`, `status.json`

**Interfaces / schemas:** ACCEPTANCE.md AC-01..AC-20.

**Steps:**
1. `git clone` the repo into `C:\Users\Joe\Documents\Playground\aiu-accept`.
2. `

</tasks>

<constitution>
# CONSTITUTION.md

## 1. Audience
Working engineers: fluent Python, have called LLM APIs, basic ML literacy (train/test split, precision/recall). Not researchers; not beginners.

## 2. Outcomes (observable)
After v1 Core (A–E) a learner can:
1. Diagnose a failing LLM call as context, task-definition, evaluation, or capability failure using the §8 playbook on a saved trace.
2. Redesign a decision as binary checks or a ≤7-label MECE enum with an escape hatch, and measure the change.
3. Validate an LLM judge against human labels using kappa, TPR, TNR, and bias checks, and refuse to use one that fails.
4. Build a tiered/cascaded pipeline and report a cost/accuracy curve.
5. Choose the cheapest adaptation rung that passes a held-out set.
6. Keep a "rules of thumb I now trust" table backed by their own runs.

## 3. Non-goals (v1)
Web UI, auth, database, payments, video, local models, GPU training, fine-tuning LLMs, leaderboard benchmarking, LLM-graded learner assessment.

## 4. Pedagogical principles
1. Prediction before observation. The harness enforces it.
2. Every lab ends in a post-mortem. No post-mortem = lab incomplete.
3. Heuristics are defaults with failure conditions, not laws. Every card has `when_it_fails`.
4. Every card has ≥1 misconception.
5. Every module ends in a portfolio artifact.
6. Negative results are first-class.
7. Measure on your own data before trusting a number from anywhere.

## 5. Content standards
- Every card cites `source_section` and carries provenance `S`, `K`, `ADD` (combinations allowed).
- `ADD` cards carry a one-sentence `add_justification`.
- Any number from a `[S]` or `[K]` claim is written as "reported" or "claimed" until its ledger row is `verified`.
- Numbers use the words **measured** (from a live run in `experiments/`, linked), **sourced** (from a cited external source), or **assumed** (configuration estimate or synthetic fixture). No other evidence words.
- No model ID, price, or provider behavior is stated in prose without a date.
- Synthetic datasets use fictional entities only. No PII. No proprietary traces.

## 6. Definition of "verified"
A ledger claim is `verified` only when all hold:
1. A human reviewer set the status.
2. `source` points to a primary source (paper, official doc, or our own run dir) dated within 12 months of the check, or to our own live run.
3. `method` states what was checked (e.g., "read §4.2 of paper; number matches" or "replicated in experiments/E9/<run_id>").
4. `date` is the check date.
`disputed` = credible primary evidence contradicts the claim; the card's `when_it_fails` must cite it.
A claim verified by our own run is verified **for our setup only**; the card must say so.

## 7. Transparency commitments
- `JOURNAL.md` is append-only; corrections are new entries.
- Every live run is committed, including aborted and failed runs.
- Every public number links to a run dir and its `cost.json`.
- Cumulative spend appears in README and `status.json` and is recomputed, not typed.
- README never claims more than `ACCEPTANCE.md` checks prove.
- No secrets, PII, or model weights are committed.

</constitution>

<lab_spec>
# LAB_SPEC.md — Lab kit

## 1. Modes
| Mode | Client | Network | Default out dir | Evidence class | Cost |
|---|---|---|---|---|---|
| `fixture` | FixtureClient | none | `.runs/` | `assumed` if fixtures synthetic, `measured` never | actual 0; estimate via `fixture_defaults` |
| `live` | OpenRouterClient | OpenRouter | `experiments/` | `measured` | pinned pricing |

Live mode preconditions (else exit 6): `OPENROUTER_API_KEY` set and non-empty; all roles used by the lab pinned (not `UNPINNED`); pricing present for each pinned model ID; `--cap` ≤ `caps.per_lab_usd`.

## 2. Learner workflow (exact commands, PowerShell, repo root)
```
uv run aiu lab new-run E9 --mode live          # prints RUN_ID; creates prediction.md
# edit experiments\E9\<RUN_ID>\prediction.md   # fill predicted_metrics BEFORE running
uv run aiu lab estimate E9
uv run aiu lab run E9 --run-id <RUN_ID> --mode live
# edit experiments\E9\<RUN_ID>\postmortem.md   # copied from template at run end
uv run aiu lab postmortem-check E9 --run-id <RUN_ID>
# add/update a row in learner\trust_table.yaml; add a row to RESULTS.md
uv run aiu validate learner
uv run aiu status --write
```

## 3. Runner algorithm (`aiu.runner.run_lab`)
1. Load manifest; require `status == runnable` (else exit 6).
2. Resolve out dir; verify prediction gate (ADR-016) (else exit 7); write `prediction.sha256`.
3. `aiu.hardware.check(tier)`; failure → exit 5.
4. Load dataset (apply `--limit`).
5. `plan()` → list of PlannedCall (deterministic order: item id, condition order in manifest, role order, sample).
6. Pre-run estimate; > cap → write `result.json` status `aborted_cost`, exit 4.
7. Write `config.json`.
8. For each call: guard check; call client; append to `responses.jsonl`; update cost.
9. `score()` → MetricsReport; evaluate `validity_checks` (all must hold) and `pass_fail`; set `evidence_class`.
10. Write `metrics.json`, `cost.json`, `result.json`; copy `experiments/_template/postmortem.md` to run dir with front matter `lab_id`, `run_id` filled.
11. Print exactly: `run_id=<id> status=<status> cost_usd=<actual:.4f>`; exit 0.

`pass_fail` metric names refer to keys in `metrics.json:metrics` (flat, e.g. `accuracy:oracle`). If any referenced metric is `None`, `hypothesis_supported = null`.

## 4. Hardware check
`aiu hwcheck --json` prints `{"tier":..., "passed":bool, "ram_total_gb":float, "ram_available_gb":float, "disk_free_gb":float, "gpu":{"name":str,"vram_total_gb":float,"vram_free_gb":float}|null, "warnings":[...], "failures":[...]}`. Thresholds per ADR-014. GPU via `nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits` (MiB → GB = /1024); missing binary → `gpu: null`.

## 5. Cost accounting
Per ADR-008. `cost.json` schema: `{estimated_usd, actual_usd, provider_reported_usd, calls, prompt_tokens, completion_tokens, cap_usd, aborted, pricing_retrieved_at, mode}`.

## 6. Lab index
| ID | Title | Status v1 | Tier | Roles | Cards | Calls (full) | Expected cost (assumed) |
|---|---|---|---|---|---|---|---|
| E1 | Binary vs scale judging | specified | API_ONLY | judge_a | A-002, B-001, B-008, C-003, C-005, C-010, A-009 | 900 | 0.60 |
| E2 | Schema field order | runnable | API_ONLY | cheap_a | A-004, B-002, B-010, B-014 | 240 | 0.25 |
| E3 | Label cardinality curve | specified | API_ONLY | cheap_a | A-003, B-006, C-017 | 880 | 0.50 |
| E4 | Escape hatch | runnable | API_ONLY | cheap_a | B-003 | 160 | 0.10 |
| E5 | Position and verbosity bias | runnable | API_ONLY | judge_a | A-005, B-009, C-006, C-008 | 160 | 0.15 |
| E6 | Same- vs cross-family judge | specified | API_ONLY | cheap_a, cheap_b, judge_a, judge_b | D-008 | 320 | 0.40 |
| E7 | Jury vs single judge | specified | API_ONLY | cheap_a, cheap_b, cheap_c, strong | C-004, C-007, D-007 | 400 | 1.20 |
| E8 | Few-shot curve | specified | API_ONLY | cheap_a | B-007, E-001 | 960 | 0.80 |
| E9 | Context distractors and position | runnable | API_ONLY | cheap_a | A-001, A-008, D-009, D-010 | 300 | 0.40 |
| E10 | Cascade threshold sweep | specified | API_ONLY | cheap_a, strong | B-011, D-001, D-003, D-013 | 400 | 1.00 |
| E11 | Calibration | specified | API_ONLY | cheap_a | A-006, D-006 | 600 | 0.40 |
| E12 | Ceiling test | specified | API_ONLY | strong | A-007 | ≤100 | 0.80 |
| E13 | Judge distillation | specified | API_ONLY | judge_a | E-005 | 500 | 0.40 |
| L-001 | Pinned replay and drift | specified | API_ONLY | cheap_a | A-010, C-009, E-004 | 240 | 0.25 |
| L-002 | Error analysis on traces | specified | API_ONLY | none | B-012, B-013, C-001, C-002 | 0 | 0.00 |
| L-003 | Eval statistics workbench | runnable | API_ONLY | none | C-012, C-014, C-015, C-019, D-004 | 0 | 0.00 |
| L-004 | Indirect prompt injection | specified | API_ONLY | cheap_a | D-014 | 160 | 0.15 |

Cost basis for all rows: `assumed` (ADR-022). `cost_cap_usd = 2.00` for every lab.
Licenses: all datasets are synthetic and authored for this repo; license = repo content license (OD-04).
`post_mortem_template` for every lab: `experiments/_template/postmortem.md`.

## 7. Modules
| Module | Title | Level | Cards | Labs | Conceptual |
|---|---|---|---|---|---|
| M-A1 | Context is the program | A | A-001, A-007, A-008, A-010 | E9, E12, L-001 | false |
| M-A2 | Difficulty, entropy, order, bias | A | A-002, A-003, A-004, A-005, A-006, A-009 | E2, E11 | false |
| M-B1 | Designing decisions and labels | B | B-001, B-003, B-004, B-005, B-006, B-007 | E3, E4, E8 | false |
| M-B2 | Schemas and scales | B | B-002, B-008, B-009, B-010, B-011, B-014 | E1, E2, E5 | false |
| M-B3 | Taxonomies from traces | B | B-012, B-013, C-001, C-002, C-018 | L-002 | false |
| M-C1 | Gold sets and judge validation | C | C-003, C-004, C-005, C-009, C-010, C-019 | E1, E7 | false |
| M-C2 | Judge bias | C | C-006, C-007, C-008, D-008 | E5, E6 | false |
| M-C3 | Eval statistics and operations | C | C-011, C-012, C-013, C-014, C-015, C-016, C-017 | L-003 | false |
| M-D1 | Tiers, cascades, ensembles | D | D-001, D-003, D-004, D-005, D-006, D-007, D-013 | E10 | false |
| M-D2 | Context, retrieval, tools, safety | D | D-002, D-009, D-010, D-011, D-012, D-014, D-015 | L-004 | false |
| M-E1 | The adaptation ladder | E | E-001, E-002, E-003, E-004, E-005, E-006, E-007 | E8, E13 | false |
| M-F1 | Machine intuition I (reading) | F | F-001, F-002, F-003, F-004, F-005 | — | true |
| M-F2 | Machine intuition II (reading) | F | F-006, F-007, F-008, F-009, F-010 | — | true |

## 8. Runnable lab specifications (exact)

### E9 — Context distractors and position
- Dataset: `labs/E9/data/items.jsonl`, 60 items, generator `aiu.generators.e9`, seed 1337. Each item: fictional entity (e.g. "the town of Varnholt"), attribute ∈ {founding_year, river, mayor, export, twin_city}, value. `input = {question, key_passage, distractors[20]}`; each distractor states the same attribute with a different value for a **similarly named** entity (edit distance ≤ 2 on the name). Each passage 60–90 words. `expected = {answer}`.
- Conditions (order fixed): `oracle` (key passage only), `d5_start` (key first, then 5 distractors), `d5_middle` (key at index 3 of 6), `d5_end` (key last of 6), `d20_middle` (key at index 10 of 21).
- Prompt: system `"Answer using only the passages. Reply with the answer only, no explanation. If the passages do not contain the answer, reply UNKNOWN."`; user `"Passages:\n[1] ...\n[2] ...\n\nQuestion: <question>"`.
- Role `cheap_a`, temperature 0, seed 1337, max_tokens 16, samples 1. Calls 300.
- Metrics: `accuracy:<cond>` = exact_match rate per condition (5 keys); `accuracy_drop:<cond>` = accuracy:oracle − accuracy:<cond> for the 4 non-oracle conditions; `max_drop` = max of the 4 drops; `unknown_rate:<cond>`.
- pass_fail: rule `any`; `max_drop >= 0.05`. Interpretation: "supported = adding distractors or moving the key fact measurably hurts this model at this context length".
- validity_checks: `accuracy:oracle >= 0.80` (else the task itself is broken).
- Synthetic fixture error rates (seed 1337): oracle 0.02, d5_start 0.05, d5_middle 0.10, d5_end 0.07, d20_middle 0.15; wrong answer = the value from distractor 0.
- Confounds: synthetic facts are easy; similar-name distractors may test name matching rather than attention; short contexts (<4k tokens) may show no lost-in-the-middle effect.

### E2 — Schema field order
- Dataset: `labs/E2/data/items.jsonl`, 80 items, generator `aiu.generators.e2`. `input = {passage (80–120 words, fictional), claim}`; `expected = {label ∈ {"entailed","not_entailed"}}`, 40/40. Not-entailed claims change exactly one attribute (number, name, or date) from a passage fact.
- Conditions: `verdict_first` (JSON keys `verdict, reasoning`), `reasoning_first` (`reasoning, verdict`), `evidence_first` (`evidence_quote, reasoning, verdict`).
- Prompt: system describes task and says `"Return a single JSON object with exactly these keys in this order: <keys>. verdict must be \"entailed\" or \"not_entailed\"."`; no `response_format`.
- Parse: first `{` to last `}` → `json.loads`; key `verdict` with valid value else None.
- Role `cheap_a`, temperature 0, seed 1337, max_tokens 300. Calls 240.
- Metrics: `accuracy:<cond>`, `parse_rate:<cond>`, `evidence_valid_rate:evidence_first` (normalized evidence_quote is substring of normalized passage), `mean_rationale_chars:<cond>`, `delta_evidence_vs_verdict` = accuracy:evidence_first − accuracy:verdict_first.
- pass_fail: `all`; `delta_evidence_vs_verdict >= 0.05`.
- validity_checks: `parse_rate:verdict_first >= 0.90`, `parse_rate:reasoning_first >= 0.90`, `parse_rate:evidence_first >= 0.90`.
- Synthetic fixture error rates: verdict_first 0.15, reasoning_first 0.10, evidence_first 0.08; parse failure rate 0.02 all.
- Confounds: models may ignore requested key order; reasoning-native models reason internally regardless; single-attribute swaps may be too easy.

### E4 — Escape hatch
- Dataset: `labs/E4/data/items.jsonl`, 80 items, generator `aiu.generators.e4`: 60 in-taxonomy support messages (12 each: billing, login, shipping, refund, bug) and 20 out-of-taxonomy (feature_request ×7, partnership ×7, press ×6). `expected = {label, in_taxonomy: bool}`.
- Conditions: `no_escape` (labels: billing, login, shipping, refund, bug), `escape` (+ `other`, `insufficient_info`).
- Output: label only. Parse: normalized text must equal one allowed label, else None.
- Role `cheap_a`, temperature 0, seed 1337, max_tokens 8. Calls 160.
- Metrics: `in_tax_accuracy:<cond>`; `oot_error_rate:<cond>` = fraction of OOT items assigned an in-taxonomy label (None counts as not error); `oot_error_drop` = oot_error_rate:no_escape − oot_error_rate:escape; `in_tax_cost` = in_tax_accuracy:no_escape − in_tax_accuracy:escape.
- pass_fail: `all`; `oot_error_drop >= 0.30`, `in_tax_cost <= 0.05`.
- validity_checks: `in_tax_accuracy:no_escape >= 0.80`.
- Synthetic fixture rates: no_escape: in-tax error 0.05, OOT → random in-tax label always; escape: in-tax error 0.07, OOT → `other` with p 0.85.
- Confounds: OOT categories may be obviously distinct; "other" may become a dumping ground on real data.

### E5 — Position and verbosity bias
- Dataset: `labs/E5/data/items.jsonl`, 40 items, generator `aiu.generators.e5`: fictional-domain question, `correct` answer, `wrong` answer (one-fact error), `padding` (2–3 on-topic sentences adding no facts). `expected = {better: "correct"}`.
- Conditions: `cw_plain` (A=correct, B=wrong), `wc_plain` (A=wrong, B=correct), `cw_padwrong` (A=correct, B=wrong+padding), `wc_padwrong` (A=wrong+padding, B=correct).
- Prompt: judge picks better answer; output `A` or `B` only.
- Role `judge_a`, temperature 0, seed 1337, max_tokens 4. Calls 160.
- Metrics: `flip_rate` (plain pair cw/wc per item: chosen identity differs); `first_slot_rate` (over plain conditions); `correct_pref:plain`; `correct_pref:padwrong`; `verbosity_shift` = correct_pref:plain − correct_pref:padwrong; `flip_rate_padded`.
- pass_fail: `any`; `flip_rate >= 0.10`, `verbosity_shift >= 0.10`.
- validity_checks: `correct_pref:plain >= 0.60`.
- Synthetic fixture: prefers first slot with p 0.15 regardless, else correct; with padded wrong, picks padded with p 0.10.
- Confounds: one-fact errors may be trivially detectable; frontier judges may show small verbosity bias (P-005).

### L-003 — Eval statistics workbench
- No model calls. Dataset `labs/L-003/data/items.jsonl`, generator `aiu.generators.l003`: 200 items `{judge_label, human_label}` with human prevalence 0.15 positive (`fail`), judge TPR 0.80, TNR 0.92 (exact counts: 30 positives, 24 TP, 6 FN; 170 negatives, 156 TN, 14 FP), plus `agent_trials`: 20 tasks × 5 trials with success counts fixed in generator (counts: [5,5,5,4,4,4,3,3,3,2,2,2,1,1,1,0,0,5,4,3]).
- Condition: `analysis`.
- Metrics: `raw_agreement`, `kappa`, `tpr`, `tnr`, `observed_fail_rate` (judge), `corrected_fail_rate` (Rogan–Gladen), `true_fail_rate` (human), `agreement_minus_kappa`, `pass_at_3`, `pass_hat_3` (means over tasks), `compound_0.95_5`.
- pass_fail: `all`; `agreement_minus_kappa >= 0.15`. Expected deterministic values are asserted in tests (T-019).
- validity_checks: none.
- fixtures: provenance `none`... (runnable labs require fixtures) → fixtures `{path: "labs/L-003/fixtures/responses.jsonl", provenance: "synthetic", n_calls: 0}` (empty file).

## 9. Specified labs (manifest content; not implemented in v1)
For each: dataset path `labs/<ID>/data/items.jsonl`, `n_items` as stated, temperature 0 unless stated, seed 1337, `fixtures: {path: null, provenance: "none", n_calls: 0}`.

- **E1** Binary vs scale. 100 items, `human_labeled` (OD-03). Conditions `binary`, `scale5`, `anchored5`; 3 repeats each (samples_per_call 3, temp 0). Metrics: `kappa_vs_human:<cond>` (scales binarized at ≥4 = pass), `run_variance:<cond>` = mean per-item variance of normalized score across repeats. pass `all`: `kappa_vs_human:binary - kappa_vs_human:scale5 >= 0.10` (metric name `kappa_gap_binary_scale5`). Confound: binarization threshold choice.
- **E3** Label cardinality. 200 items, 20 leaf categories in 4 coarse groups, 10/leaf. Conditions `k3, k5, k8, k12, k20, hier20`. Metrics `accuracy:<cond>`, `macro_f1:<cond>`, confusion matrix file. pass `all`: `accuracy:k3 - accuracy:k20 >= 0.10`. Confound: subsets differ in intrinsic difficulty.
- **E6** Self-preference. 40 questions; `cheap_a` and `cheap_b` generate answers; gold marks both correct; `judge_a` (family = cheap_a's) and `judge_b` (family = cheap_b's) compare both orders. Metric `self_pref:<judge>` = P(choose same-family answer). pass `any`: `self_pref:judge_a >= 0.60`, `self_pref:judge_b >= 0.60`. Requires judge_a.family == cheap_a.family (config check).
- **E7** Jury vs single. E1 dataset. `cheap_a/b/c` majority vote vs `strong`. Metrics `kappa:jury`, `kappa:strong`, `cost:jury`, `cost:strong`. pass `all`: `kappa:jury - kappa:strong >= -0.02`, `cost_ratio_jury_strong <= 0.5`.
- **E8** Few-shot curve. E3 k12 task, 80 test items. Conditions `shots{0,2,5,10}_{prototype,boundary}` (0-shot once). Metric `accuracy:<cond>`. pass: `accuracy:shots5_boundary - accuracy:shots5_prototype >= 0.05`.
- **E10** Cascade. E2 task, 80 items. `cheap_a` 3 samples temp 0.7 seed 1337; escalate to `strong` if agreement < t, t ∈ {3/3, 2/3, never}; plus `strong_only`. Metrics `accuracy:<policy>`, `cost_per_item:<policy>`. pass `any` over policies: accuracy ≥ accuracy:strong_only − 0.02 and cost ≤ 0.5× strong_only (metric `frontier_dominates` ∈ {0,1}, condition `>= 1`).
- **E11** Calibration. 100 fictional-QA items. Methods: verbalized confidence; first-token logprob (if supported, P-076); 5-sample agreement temp 0.7. Metrics `ece:<method>`. pass: `ece:verbalized - ece:sample_agreement >= 0.05`.
- **E12** Ceiling test. Input: failed items from a prior E2 or E9 live run (run_id parameter). `strong` + oracle context. Metric `prompt_fraction` = fraction now correct. pass: `prompt_fraction >= 0.50`.
- **E13** Judge distillation. 500 items; judge_a labels; 100 human-clean labels (OD-03); student TF-IDF+LR (ADR-020). Metrics `student_vs_judge`, `student_vs_human`, `judge_vs_human`. pass: `student_vs_judge >= 0.85`.
- **L-001** Pinned replay. E2 dataset; run twice with same pin ≥24 h apart, once with an alternate pin. Metrics `change_rate:same_pin`, `change_rate:alt_pin`, `accuracy_delta:alt_pin`. pass `all`: `change_rate:same_pin <= 0.02`.
- **L-002** Error analysis. 60 synthetic support-bot traces with seeded failures and seeded first-upstream step. Learner writes `learner/portfolio/L-002/notes.yaml` and `taxonomy.yaml`. Metric `first_upstream_agreement`, `coverage`. pass `all`: `coverage >= 1.0`, `first_upstream_agreement >= 0.70`. No model calls.
- **L-004** Indirect injection. 40 QA items over 4 retrieved docs, one doc contains an injected instruction. Conditions `naive_concat`, `delimited_untrusted`. Metric `attack_success_rate:<cond>`. pass: `asr_drop >= 0.20`.

## 10. Capstone CAP-001 (specified)
Build a support-ticket triage app: deterministic checks → `cheap_a` classifier with escape hatch → cascade to `strong` on `unsure`; a 40-item regression set; a judge validated against ≥50 human labels with kappa reported with Wilson CI; a cost/accuracy curve over ≥3 thresholds. Deliverable dir: `learner/portfolio/CAP-001/`. Human-reviewed rubric in GOVERNANCE §6.

</lab_spec>

<repo_layout>
# REPO_LAYOUT.md

Root: `C:\Users\Joe\Documents\Playground\AIUniversity`. No other top-level entries are allowed. `aiu validate` does not check layout; T-035 does.

```
AIUniversity/
├── README.md                 Living front page; generated STATUS block.
├── JOURNAL.md                Append-only session log.
├── DECISIONS.md              ADRs.
├── CONSTITUTION.md           Audience, outcomes, standards, "verified".
├── GOVERNANCE.md             Versioning, verification queue, logs, trust table.
├── PROVENANCE.md             Claim ledger (P-###).
├── RESULTS.md                Index of every live run.
├── TRACEABILITY.md           Source concept → card → experiment.
├── TASKS.md                  Implementation backlog.
├── ACCEPTANCE.md             v1 definition of done as commands.
├── LAB_SPEC.md               Lab kit and lab index.
├── REPO_LAYOUT.md            This file.
├── CHANGELOG.md              User-visible changes, newest first.
├── status.json               Generated machine-readable state.
├── pyproject.toml            Package + deps + pytest config.
├── uv.lock                   Pinned dependency lock.
├── .python-version           "3.12".
├── .gitignore                Ignore rules (see T-003).
├── .env.example              Template for OPENROUTER_API_KEY.
├── .githooks/
│   └── pre-commit            Secrets scan + journal append-only check.
├── source/
│   ├── concept_map.txt       Source ontology text (PDF authoritative).
│   └── README.md             Provenance of the source file.
├── schemas/
│   ├── curriculum.schema.json  Cards, labs, modules, trust table.
│   └── status.schema.json      status.json schema.
├── config/
│   ├── models.yaml           Role → pinned model ID.
│   ├── pricing.yaml          Pinned USD/Mtok prices.
│   └── caps.yaml             Cost caps.
├── curriculum/
│   ├── A/ … F/               One YAML card per file: <ID>.yaml.
│   └── modules/              One YAML module per file: M-<L><n>.yaml.
├── labs/
│   └── <lab_id>/             One dir per lab (E1..E13, L-001..L-004).
│       ├── manifest.yaml     Lab manifest (schema: lab).
│       ├── data/             items.jsonl + DATASET_CARD.md (runnable labs).
│       └── fixtures/         responses.jsonl (runnable labs).
├── src/aiu/
│   ├── __init__.py           __version__.
│   ├── cli.py                argparse entry point.
│   ├── validate.py           YAML → JSON Schema validation.
│   ├── models.py             Pydantic models (data, calls, artifacts).
│   ├── config.py             Load models/pricing/caps.
│   ├── cost.py               Estimator + CostGuard.
│   ├── clients/              base.py, fixture.py, openrouter.py.
│   ├── hardware.py           hwcheck.
│   ├── metrics.py            ADR-011 metrics.
│   ├── runs.py               run_id, run dirs, prediction gate.
│   ├── runner.py             Lab execution engine.
│   ├── postmortem.py         Post-mortem checks.
│   ├── labs/                 Lab implementations + registry.
│   ├── generators/           Deterministic dataset generators.
│   ├── status.py             status.json + README block + consistency.
│   ├── journal.py            Append-only check.
│   ├── secrets_scan.py       Secret/forbidden-file scan.
│   ├── provenance.py         Ledger parsing + check.
│   ├── traceability.py       Traceability check.
│   ├── checkpoint.py         Module checkpoint grader.
│   └── smoke.py              Smoke suite.
├── tests/                    pytest; zero network.
├── experiments/
│   ├── _template/            Per-run artifact templates.
│   └── <lab_id>/<run_id>/    Committed live runs only.
├── docs/
│   ├── LEARNER_GUIDE.md      How to complete a module.
│   └── learnings/            YYYY-MM-DD-<slug>.md + _template.md.
├── learner/
│   ├── trust_table.yaml      "Rules of thumb I now trust".
│   ├── checkpoints/          <module>.answers.yaml, <module>.result.json.
│   └── portfolio/            Module portfolio artifacts.
├── ops/
│   ├── bootstrap.ps1         Windows bootstrap (uv, Python, sync, hooks).
│   └── RUNBOOK.md            Live-run procedure, key rotation, incident steps.
└── .runs/                    (gitignored) fixture-mode run outputs.
```

</repo_layout>

<decisions>
# DECISIONS.md — Architecture Decision Records

Format per entry: Context / Decision / Alternatives rejected / Consequences / Date.
All entries dated 2026-10-23 are **assumed** dates (source compilation date). The human confirms or corrects them in JOURNAL entry 1.
New decisions are appended. Superseded decisions are marked `SUPERSEDED BY ADR-xxx` and are never deleted.

---

## ADR-001: Repository layout
- Context: Content, harness, and public learning record must coexist without confusion.
- Decision: Single repo. Layout is fixed by `REPO_LAYOUT.md`. Python package lives in `src/aiu/`. Content lives in `curriculum/`. Lab assets live in `labs/<lab_id>/`. Live run artifacts live in `experiments/<lab_id>/<run_id>/`. Fixture-mode runs write to `.runs/` (gitignored) by default.
- Alternatives rejected: separate content and harness repos (traceability breaks); writing fixture runs into `experiments/` (pollutes the public record with non-evidence).
- Consequences: Every directory has a single purpose. `aiu status --check` can scan `experiments/` and trust that every run dir there is live.
- Date: 2026-10-23

## ADR-002: CLI shape
- Context: Implementer needs an exact, testable command surface.
- Decision: One entry point `aiu` (console script `aiu = aiu.cli:main`), built on stdlib `argparse`. Subcommands:
  - `aiu --version`
  - `aiu validate [PATH ...]` (default paths: `curriculum labs learner`)
  - `aiu status --write | --check`
  - `aiu journal check`
  - `aiu secrets-scan [--staged] [--root PATH]`
  - `aiu hwcheck [--tier API_ONLY|LOCAL_SMALL_GPU_6GB|LOCAL_CPU_TINY] [--json]`
  - `aiu labs list`
  - `aiu labs check-tiers`
  - `aiu dataset build LAB_ID [--check]`
  - `aiu fixtures synth LAB_ID [--check]`
  - `aiu lab new-run LAB_ID --mode fixture|live [--out-dir PATH]`
  - `aiu lab estimate LAB_ID [--limit N]`
  - `aiu lab run LAB_ID --run-id RUN_ID --mode fixture|live [--cap USD] [--limit N] [--record] [--out-dir PATH]`
  - `aiu lab postmortem-check LAB_ID --run-id RUN_ID [--out-dir PATH]`
  - `aiu smoke --mode fixture|live [--cap USD]`
  - `aiu checkpoint grade MODULE_ID --answers PATH`
  - `aiu provenance check`
  - `aiu traceability check`
  - `aiu check-all`
- Alternatives rejected: click/typer (extra dependency, no benefit); multiple scripts (harder to document).
- Consequences: argparse usage errors exit 2 (argparse default).
- Date: 2026-10-23

## ADR-003: Exit codes
- Decision (all `aiu` commands):
  - 0 success
  - 1 check failed (validation finding, secrets found, test/consistency mismatch, checkpoint not fully correct)
  - 2 CLI usage error (argparse)
  - 3 missing fixture for a planned call in fixture mode
  - 4 cost cap would be exceeded (pre-run or mid-run)
  - 5 hardware check failed for declared tier
  - 6 configuration error (missing key, UNPINNED model in live mode, malformed config, HTTP 401)
  - 7 prediction gate failed (missing/invalid/edited `prediction.md`)
- Consequences: Acceptance tests assert these codes exactly.
- Date: 2026-10-23

## ADR-004: Python and tooling
- Decision: Python 3.12 installed via `uv python install 3.12`; `.python-version` = `3.12`; `requires-python = ">=3.11,<3.13"`. Dependencies: `pydantic>=2.7,<3`, `pyyaml>=6.0,<7`, `jsonschema>=4.21,<5`, `httpx>=0.27,<1`, `psutil>=5.9,<7`. Dev group: `pytest>=8,<9`, `pytest-socket>=0.7,<1`. Build backend: hatchling. Exact versions are pinned by committed `uv.lock`.
- Alternatives rejected: system Python 3.7.4 (below target); `openai` SDK (extra surface; OpenRouter is plain HTTP); `requests` (no built-in mock transport).
- Consequences: Never invoke the system `python`; always `uv run`.
- Date: 2026-10-23

## ADR-005: HTTP client for OpenRouter
- Decision: `httpx.Client` POST to `https://openrouter.ai/api/v1/chat/completions`. Headers: `Authorization: Bearer $OPENROUTER_API_KEY`, `Content-Type: application/json`, `X-Title: AI University`. Body: `model`, `messages`, `temperature`, `max_tokens`, `seed` (if not null), `response_format` (if not null), `logprobs` (if true), `usage: {"include": true}`. Timeout 60 s. Retries: max 3 retries on HTTP 408/429/500/502/503/504 and `httpx.TransportError`, sleep `2**attempt` seconds (attempt = 0,1,2), sleep function injectable. No retry on other 4xx. HTTP 401 → exit 6.
- Alternatives rejected: SDK; async client (no throughput need).
- Consequences: Tests use `httpx.MockTransport`; no sockets.
- Verify: OpenRouter usage/cost field, seed support, logprob support → PROVENANCE P-075..P-077.
- Date: 2026-10-23

## ADR-006: Offline/fixture mode
- Decision: Two client implementations behind one interface: `FixtureClient` and `OpenRouterClient`. Fixture records are JSONL at `labs/<lab_id>/fixtures/responses.jsonl`, keyed by `call_key = "{item_id}|{condition}|{role}|{sample}"`. Each record stores `request_sha256` and `source` (`fixture_synthetic` or `fixture_recorded`). For `fixture_recorded`, a `request_sha256` mismatch with the planned call is an error (exit 3). For `fixture_synthetic`, the hash is not checked.
- Initial fixtures are **synthetic**, generated deterministically by `aiu fixtures synth LAB_ID` from dataset ground truth with a lab-defined error-injection rate and seed 1337. Synthetic fixture metrics are labeled `evidence_class: "assumed"` and never appear in `RESULTS.md` or README numbers.
- `aiu lab run --mode live --record` overwrites the fixture file with `fixture_recorded` records.
- Alternatives rejected: keying by request hash only (prompt edits would orphan every synthetic fixture); VCR-style HTTP cassettes (couples tests to HTTP shape).
- Date: 2026-10-23

## ADR-007: Network isolation in tests
- Decision: `pytest-socket` with `addopts = "--disable-socket -q"` in `pyproject.toml`. Any socket creation during tests fails the test.
- Consequences: "Zero network calls in fixture mode" is enforced mechanically.
- Date: 2026-10-23

## ADR-008: Cost accounting
- Decision:
  - Prices come only from `config/pricing.yaml` (USD per million tokens, manually pinned with `retrieved_at` date).
  - Pre-call estimate per call: `est_in = ceil(utf8_bytes(all message contents) / 3)`; `est_out = max_tokens`; `est_usd = (est_in*in_price + est_out*out_price) / 1e6`. Multiply by `samples` already expanded as separate calls.
  - Pre-run: if `sum(est_usd) > cap` → exit 4, no calls made, run dir gets `result.json` with `status: "aborted_cost"`.
  - Mid-run: before each call, if `actual_so_far + est_usd(next) > cap` → stop, write partial artifacts, `status: "aborted_cost"`, exit 4.
  - Actual cost = `(prompt_tokens*in_price + completion_tokens*out_price)/1e6` from response usage. Provider-reported cost (if present) is stored as `provider_reported_usd` but does not drive the guard.
  - Fixture mode: actual cost = 0; estimate uses `pricing.yaml: fixture_defaults` so the guard is exercised.
  - Default caps in `config/caps.yaml`: `per_lab_usd: 2.00`, `smoke_total_usd: 5.00`. `--cap` may lower but never raise above `per_lab_usd` for `lab run`, or above `smoke_total_usd` for `smoke` (exit 6 if raised).
- Alternatives rejected: trusting provider-reported cost only (not always present; verify P-075).
- Date: 2026-10-23

## ADR-009: Model configuration
- Decision: `config/models.yaml` maps **roles** to pinned model IDs: `cheap_a`, `cheap_b`, `cheap_c` (three different families), `strong`, `judge_a`, `judge_b` (different family from `judge_a`). Each role: `model_id`, `family`. The literal value `UNPINNED` is allowed in the repo; live mode refuses to run any lab whose roles resolve to `UNPINNED` (exit 6). Fixture mode ignores model IDs and records `model_id` from the fixture file.
- Labs reference roles, never model IDs. No model ID string appears in `src/`.
- Alternatives rejected: choosing models now (pricing and availability on OpenRouter must be checked by the human on the day of pinning).
- Open: concrete IDs are OD-01.
- Date: 2026-10-23

## ADR-010: Dataset format and provenance
- Decision: Datasets are JSONL at `labs/<lab_id>/data/items.jsonl`, one object per line: `{"id": str, "input": object, "expected": object, "meta": object}`, sorted by `id`. v1 runnable datasets are **synthetic**, generated by deterministic generators in `src/aiu/generators/<lab_id_lower>.py` with `seed=1337`, using fictional entities only. Generated files are committed; `aiu dataset build LAB_ID --check` regenerates in memory and exits 1 if bytes differ. Each dataset dir has `DATASET_CARD.md` (purpose, generator, seed, counts, license, known biases).
- Datasets needing human labels (E1, E7, E13) are `specified`, not runnable, until the human supplies labels (OD-03).
- `--limit N` takes the first N items by `id` order.
- Alternatives rejected: public benchmarks (contamination, license); LLM-generated datasets (unverifiable labels).
- Date: 2026-10-23

## ADR-011: Metric definitions (implemented in `src/aiu/metrics.py`)
- `accuracy(pred, gold) = (#i: pred_i == gold_i) / n`; parse failures are `pred_i = None` and count as incorrect.
- `parse_rate = (#parsed) / n`.
- `cohen_kappa(a, b) = (p_o - p_e) / (1 - p_e)`; `p_e = Σ_k p_a(k) p_b(k)`; returns `None` if `p_e == 1`.
- `tpr = TP/(TP+FN)`, `tnr = TN/(TN+FP)`; `None` on zero denominator. Positive class is declared per lab.
- `wilson_ci(k, n, z=1.96) -> (lo, hi)`: `center = (p + z²/2n)/(1+z²/n)`, `half = z*sqrt(p(1-p)/n + z²/4n²)/(1+z²/n)`.
- `flip_rate = (#pairs whose chosen answer identity differs between AB and BA orders) / #pairs`.
- `first_slot_rate = (#choices of the first-presented answer) / #judgments`.
- `rogan_gladen(p_obs, tpr, tnr) = clip((p_obs + tnr - 1)/(tpr + tnr - 1), 0, 1)`; `None` if `tpr + tnr - 1 <= 0`.
- `pass_at_k(n, c, k) = 1 - C(n-c, k)/C(n, k)` (unbiased; 1.0 if n-c < k).
- `pass_hat_k(n, c, k) = C(c, k)/C(n, k)`.
- `ece(conf, correct, bins=10)`: equal-width bins on [0,1], last bin inclusive of 1.0; `Σ_b |B_b|/n * |acc(B_b) - mean_conf(B_b)|`.
- `compound(p, steps) = p**steps`.
- `normalize_answer(s) = collapse_whitespace(strip_punctuation(lower(s))).strip()`; punctuation = `string.punctuation`.
- `exact_match(pred, gold) = normalize_answer(pred) == normalize_answer(gold)`.
- Every proportion reported in `metrics.json` includes `n` and a Wilson 95% CI.
- Date: 2026-10-23

## ADR-012: Card-count targets
- Decision: 75 cards total. A: 10, B: 14, C: 19 (17 from §4, C-018 from §7 failure catalog, C-019 `[ADD]`), D: 15 (14 from §3, D-015 from §8 playbook), E: 7, F: 10. IDs are fixed in `TRACEABILITY.md`.
- Card ID format `^[A-F]-\d{3}$`. Experiment IDs are `E1`–`E13` (no hyphen) and `L-\d{3}`. The level-E card `E-001` and experiment `E1` are distinct by format; the validator enforces patterns.
- Date: 2026-10-23

## ADR-013: Module structure
- Decision: 13 modules, fixed in `LAB_SPEC.md §7` and authored as `curriculum/modules/M-<level><n>.yaml`. Each module has 3–8 cards. Cards belong to exactly one module.
- `M-A1` is the reference module that a learner can complete end-to-end in v1 (lab E9 runnable).
- Date: 2026-10-23

## ADR-014: Hardware-tier policy
- Decision: Every lab manifest declares exactly one `hardware_tier` ∈ {`API_ONLY`, `LOCAL_SMALL_GPU_6GB`, `LOCAL_CPU_TINY`}. Local tiers require `api_fallback.lab_id` pointing to an existing `API_ONLY` manifest with fixtures, and `local_requirements`. All 17 v1 labs are `API_ONLY`. `aiu hwcheck` measures RAM, disk, GPU (via `nvidia-smi` if present) and checks thresholds:
  - `API_ONLY`: always passes; reports a warning (not failure) if free disk < 10 GB.
  - `LOCAL_SMALL_GPU_6GB`: free VRAM ≥ `local_requirements.weights_gb + 1.0`, free disk ≥ 10 GB + weights_gb, RAM total ≥ 16 GB minus 0.5 tolerance.
  - `LOCAL_CPU_TINY`: `local_requirements.params_b ≤ 1.0`, RAM available ≥ 4 GB.
- No weights are downloaded by any command in v1.
- Date: 2026-10-23

## ADR-015: Lab status in v1
- Decision: `runnable` labs (end-to-end, fixture + live): **E2, E4, E5, E9, L-003**. `specified` (manifest complete, no implementation): E1, E3, E6, E7, E8, E10, E11, E12, E13, L-001, L-002, L-004. Capstone `CAP-001` is specified in `LAB_SPEC.md` without a manifest.
- Rationale: these five need no human labels and have ground truth by construction; together they cover levels A, B, C.
- Date: 2026-10-23

## ADR-016: Prediction gate and run artifacts
- Decision: `aiu lab new-run` creates `<out>/<lab_id>/<run_id>/prediction.md` from template. `run_id = YYYYMMDDTHHMMSSZ-<mode>-<6 lowercase hex>` (UTC). `aiu lab run` refuses (exit 7) unless `prediction.md` front matter parses, `predicted_metrics` is non-empty with keys ⊆ manifest metric names, and `written_at` < now. At run start the harness writes `prediction.sha256`. `postmortem-check` fails if the hash changed.
- Default out dirs: fixture → `.runs/`, live → `experiments/`.
- Run artifacts: `prediction.md`, `prediction.sha256`, `config.json`, `responses.jsonl`, `result.json`, `metrics.json`, `cost.json`, `postmortem.md`. The harness prints only `run_id`, status, and cost to stdout; metrics are written to file, never printed before `prediction.sha256` exists.
- Date: 2026-10-23

## ADR-017: Public state consistency
- Decision: `status.json` is generated by `aiu status --write` from repo state. `README.md` contains a generated block between `<!-- STATUS:BEGIN -->` and `<!-- STATUS:END -->`. `aiu status --check` exits 1 if: recomputed status ≠ committed status (ignoring `generated_at`, `tests`), README block ≠ render, any `experiments/*/*/` run dir is not referenced by run_id in `RESULTS.md`, or cumulative cost ≠ sum of `cost.json:actual_usd`.
- Date: 2026-10-23

## ADR-018: Provenance ledger
- Decision: `PROVENANCE.md` is a markdown table; rows begin `| P-###`. Card `verify[].claim_id` must exist in the ledger; ledger status must equal card verify status (`aiu provenance check`). Status values: `unverified`, `verified`, `disputed`. Only the human may set `verified` or `disputed` (GOVERNANCE §2).
- Date: 2026-10-23

## ADR-019: Assessment policy
- Decision: Module checkpoints are (a) deterministic items (`mcq`, `numeric` with tolerance, `exact`) graded by `aiu checkpoint grade`, and (b) a human rubric for the postmortem/portfolio artifact. No LLM judge grades learners in v1. LLM judges appear only as objects of study in labs.
- Date: 2026-10-23

## ADR-020: E13 student classifier
- Decision: E13 is `specified` only. When implemented, the student is TF-IDF + logistic regression (scikit-learn, CPU). This is not LLM fine-tuning and is not a training-side lab; tier stays `API_ONLY` (judge labels come from API). scikit-learn is not added in v1.
- Date: 2026-10-23

## ADR-021: Git hooks on Windows
- Decision: `.githooks/pre-commit` is a two-line `sh` script (Git for Windows bundles `sh`) that runs `uv run aiu secrets-scan --staged` and `uv run aiu journal check`. Activated by `git config core.hooksPath .githooks`.
- Alternatives rejected: pre-commit framework (extra dependency).
- Date: 2026-10-23

## ADR-022: Assumed costs
- Decision: `expected_cost_usd` in lab manifests is **assumed** at $0.50/Mtok input and $1.50/Mtok output until OD-01 pins real models and prices; T-036 re-computes from `aiu lab estimate` and updates manifests.
- Date: 2026-10-23

## ADR-023: Journal is append-only
- Decision: `aiu journal check` compares `git show HEAD:JOURNAL.md` with the working copy; exit 1 unless HEAD content is an exact prefix of the working copy. If `JOURNAL.md` is not in HEAD (first commit), exit 0.
- Date: 2026-10-23

</decisions>

<traceability>
# TRACEABILITY.md

One row per source bullet. `aiu traceability check` parses rows beginning `| §` and verifies: every non-`OOS` card ID has a file `curriculum/<L>/<ID>.yaml` (after T-033), every card file appears exactly once here, card `source_section` matches the row, and `experiment_id` matches the row's Experiment (`—` ⇔ null).

| Src | Concept | Card | Experiment | Tag | Status |
|---|---|---|---|---|---|
| §1.1 | Output is a function of context | A-001 | E9 | K | in scope |
| §1.2 | Decision difficulty hierarchy | A-002 | E1 | S,K | in scope |
| §1.3 | Reduce entropy per call | A-003 | E3 | K | in scope |
| §1.4 | Autoregressive ordering | A-004 | E2 | K | in scope |
| §1.5 | Known judge/model biases | A-005 | E5 | S,K | in scope |
| §1.6 | Verbalized confidence is weak | A-006 | E11 | K | in scope |
| §1.7 | Prompt vs capability failure (ceiling test) | A-007 | E12 | K | in scope |
| §1.8 | More context is not free | A-008 | E9 | K | in scope |
| §1.9 | Ambiguity ceiling | A-009 | E1 | K | in scope |
| §1.10 | Silent drift | A-010 | L-001 | S,K | in scope |
| §2.1 | Binary decomposition | B-001 | E1 | S | in scope |
| §2.2 | Evidence-before-verdict schema | B-002 | E2 | S | in scope |
| §2.3 | Enums with escape hatch | B-003 | E4 | K | in scope |
| §2.4 | MECE categories | B-004 | — | K | in scope (null: exercised inside E3/L-002 taxonomy design; no isolated lab) |
| §2.5 | Observable-criteria definitions | B-005 | — | K | in scope (null: assessed by human-reviewed rewrite exercise) |
| §2.6 | Cardinality limit per call | B-006 | E3 | K | in scope |
| §2.7 | Boundary few-shots | B-007 | E8 | K | in scope |
| §2.8 | Anchored ordinal scales | B-008 | E1 | S | in scope |
| §2.9 | Pairwise vs pointwise; reference-based | B-009 | E5 | S,K | in scope |
| §2.10 | Constrained decoding / structured outputs | B-010 | E2 | K | in scope |
| §2.11 | Abstention and escalation paths | B-011 | E10 | K | in scope |
| §2.12 | Taxonomy lifecycle (open/axial coding) | B-012 | L-002 | S | in scope |
| §2.13 | First upstream failure | B-013 | L-002 | S | in scope |
| §2.14 | Rationale-length smell test | B-014 | E2 | S | in scope |
| §3.1 | Tiered checking | D-001 | E10 | S,K | in scope |
| §3.2 | Workflows vs agents | D-002 | — | K | in scope (null: no agent runtime in v1; conceptual) |
| §3.3 | Routing and cascades | D-003 | E10 | K | in scope |
| §3.4 | Error compounding | D-004 | L-003 | K | in scope |
| §3.5 | Verifier/generator asymmetry | D-005 | — | K | in scope (null: best-of-N lab deferred to v2) |
| §3.6 | Self-consistency / majority vote | D-006 | E11 | K | in scope |
| §3.7 | Jury of small diverse models | D-007 | E7 | S | in scope |
| §3.8 | Independent judge | D-008 | E6 | S | in scope |
| §3.9 | Retrieval (RAG) evaluation | D-009 | E9 | K | in scope |
| §3.10 | Context engineering | D-010 | E9 | K | in scope |
| §3.11 | Tool design (ACI) | D-011 | — | K | in scope (null: no tool-use runtime in v1) |
| §3.12 | Reliability plumbing | D-012 | — | K | in scope (null: studied via harness source `src/aiu/clients/openrouter.py`) |
| §3.13 | Cost and latency levers | D-013 | E10 | K | in scope |
| §3.14 | Guardrails / untrusted content | D-014 | L-004 | K | in scope |
| §4.1 | Error analysis first | C-001 | L-002 | S | in scope |
| §4.2 | Failure-category evaluators | C-002 | L-002 | S | in scope |
| §4.3 | Gold set | C-003 | E1 | S | in scope |
| §4.4 | Measure the judge (kappa, TPR/TNR) | C-004 | E1 | S | in scope |
| §4.5 | Kappa deflation | C-005 | E1 | S | in scope |
| §4.6 | Consistency is not validity | C-006 | E5 | S | in scope |
| §4.7 | Judge rankings don't transfer | C-007 | E7 | S | in scope |
| §4.8 | Stack cheap mitigations | C-008 | E5 | S | in scope |
| §4.9 | Freeze the judge | C-009 | L-001 | S | in scope |
| §4.10 | Dev/test split for judge prompts | C-010 | E1 | K | in scope |
| §4.11 | 100% pass rate means eval too easy | C-011 | — | S | in scope (null: assessed via checkpoint and capstone regression set) |
| §4.12 | Correct for judge error (prevalence) | C-012 | L-003 | K | in scope |
| §4.13 | Offline vs online | C-013 | — | K | in scope (null: no production traffic in v1) |
| §4.14 | Agent evals (pass@k, pass^k) | C-014 | L-003 | K | in scope |
| §4.15 | Eval the evals | C-015 | L-003 | K | in scope |
| §4.16 | Contamination | C-016 | — | K | in scope (null: conceptual; no benchmark training data access) |
| §4.17 | Per-category reporting | C-017 | E3 | K | in scope |
| §5 | Adaptation ladder ordering | E-001 | E8 | K | in scope |
| §5.1 | Prompt optimization (DSPy/GEPA) | E-002 | — | K | in scope (null: optimizer frameworks out of v1 scope) |
| §5.2 | Reasoning models | E-003 | — | K | in scope (null: depends on OD-01 model choice; v2 lab) |
| §5.3 | Prompt versioning and regression | E-004 | L-001 | K | in scope |
| §5.4 | Fine-tuning / distillation | E-005 | E13 | K | in scope |
| §5.5 | Preference and RL methods | E-006 | — | K | in scope (null: training-side, read-only in v1) |
| §5.6 | Synthetic data | E-007 | — | K | in scope (null: practiced via repo generators; no isolated lab) |
| §6.1 | Pretraining data | F-001 | — | K | reading track (null: training-side) |
| §6.2 | Scaling laws | F-002 | — | K | reading track (null: training-side) |
| §6.3 | Tokenization | F-003 | — | K | reading track (null: training-side) |
| §6.4 | What post-training changes | F-004 | — | K | reading track (null: training-side) |
| §6.5 | Label noise and ambiguity | F-005 | — | K | reading track (null: training-side) |
| §6.6 | Data mix interference | F-006 | — | K | reading track (null: training-side) |
| §6.7 | Infrastructure (MFU, KV cache, etc.) | F-007 | — | K | reading track (null: training-side) |
| §6.8 | In-context learning | F-008 | E8 | K | reading track |
| §6.9 | Interpretability as intuition | F-009 | — | K | reading track (null: training-side) |
| §6.10 | Small-model labs (nanochat) | F-010 | — | S | reading track (null: GPU/CPU training out of scope, §3.2 policy) |
| §7 | Failure-mode catalog | C-018 | L-002 | K | in scope |
| §8 | Debugging playbook (8 steps) | D-015 | E12 | K | in scope |
| none | Small-sample confidence intervals | C-019 | L-003 | ADD | in scope (justification: v1 gold sets are 40–200 items; uncertainty must be reported to avoid overclaiming) |
| §9 | Experiment backlog E1–E13 | — | E1–E13 | — | specified in LAB_SPEC.md |
| §9 | Training-side labs | OOS | — | — | out of scope v1: GPU training excluded by §3 locked decisions |
| §10 | Sources list | — | — | — | captured in PROVENANCE.md |
| §11 | Schema instructions | — | — | — | implemented by schemas/curriculum.schema.json + CONSTITUTION.md |

</traceability>