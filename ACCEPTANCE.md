# ACCEPTANCE.md - AI University v1 Definition of Done

## How to run

Run every command from the repo root in Windows PowerShell 5.1+.

**Preconditions:**
- `ops\bootstrap.ps1` has completed.
- Unless an AC says otherwise, provider keys are unset:
  ```powershell
  Remove-Item Env:OPENROUTER_API_KEY -ErrorAction SilentlyContinue
  Remove-Item Env:DEEPSEEK_API_KEY -ErrorAction SilentlyContinue
  ```

**Checking exit codes:**
- "Exit 0" means `$LASTEXITCODE -eq 0` immediately after the command.
- For pure PowerShell checks that use `if (...) { exit 1 }`, run them in a child shell to read the exit code.

**Live API calls:** No AC makes a live call. Live evidence is checked from committed artifacts only.

**Single gate:** `uv run aiu check-all` (AC-20) runs the offline checks and the full pytest suite. AC-19 is the clean-checkout procedure.

---

### AC-01 - Python 3.12 via uv
- **Requirement:** The project runs on Python 3.12, provisioned by uv, not the system Python 3.7.4.
- **Command:**
  ```powershell
  uv run python -c "import sys; raise SystemExit(0 if sys.version_info[:2]==(3,12) else 1)"; (Get-Content .python-version).Trim()
  ```
- **Expected:** Exit 0. Second line prints `3.12`.
- **Ticket:** T-002

### AC-02 - Locked, reproducible dependencies
- **Requirement:** `uv.lock` is committed and consistent with `pyproject.toml`.
- **Command:**
  ```powershell
  uv lock --check; uv sync --frozen
  ```
- **Expected:** Both commands exit 0.
- **Ticket:** T-002

### AC-03 - Zero-network pytest
- **Requirement:** The full test suite passes with no provider keys present and no network access. Socket creation is blocked in `tests/conftest.py`.
- **Command:**
  ```powershell
  Remove-Item Env:OPENROUTER_API_KEY -ErrorAction SilentlyContinue; Remove-Item Env:DEEPSEEK_API_KEY -ErrorAction SilentlyContinue; uv run pytest -q
  ```
- **Expected:** Exit 0. Summary contains `passed` and no `failed` or `error`.
- **Ticket:** T-002, T-012, T-013

### AC-04 - JSON Schema validation
- **Requirement:** Every card, module, lab manifest, and the trust table validate against `schemas/curriculum.schema.json`.
- **Command:**
  ```powershell
  uv run aiu validate
  ```
- **Expected:** Exit 0. Output ends with `0 errors`.
- **Ticket:** T-006

### AC-05 - No secrets or forbidden files
- **Requirement:** No provider keys, `.env` files, or other forbidden files are tracked; the pre-commit hook is installed.
- **Command:**
  ```powershell
  uv run aiu secrets-scan; git config core.hooksPath
  ```
- **Expected:** First command exits 0 and prints `0 findings`. Second prints `.githooks`.
- **Ticket:** T-003, T-004

### AC-06 - JOURNAL.md is append-only
- **Requirement:** The working `JOURNAL.md` is append-only relative to `HEAD`; existing entries are never edited.
- **Command:**
  ```powershell
  uv run aiu journal check
  ```
- **Expected:** Exit 0 and `journal: append-only OK`.
- **Ticket:** T-005

### AC-07 - status.json and README consistency
- **Requirement:** `status.json` validates, equals freshly generated state, and the README STATUS block matches it.
- **Command:**
  ```powershell
  uv run aiu status --check
  ```
- **Expected:** Exit 0 and `status: OK`.
- **Ticket:** T-007

### AC-08 - Provenance ledger
- **Requirement:** Every claim cited by a card resolves to a ledger row, and the card's status agrees with the ledger. The ledger has eight columns.
- **Command:**
  ```powershell
  uv run aiu provenance check
  ```
- **Expected:** Exit 0 and `provenance: OK`.
- **Ticket:** T-026

### AC-09 - Traceability
- **Requirement:** Every card maps to exactly one TRACEABILITY row, its `source_section` and `experiment_id` match, and every traceability row has a card file.
- **Command:**
  ```powershell
  uv run aiu traceability check --require-all
  ```
- **Expected:** Exit 0 and `traceability: OK`.
- **Ticket:** T-027, T-033

### AC-10 - Hardware-tier validity and API fallback
- **Requirement:** All 17 labs declare a valid hardware tier; every local-tier lab declares an API fallback; no lab requires local training.
- **Command:**
  ```powershell
  uv run aiu labs check-tiers; (uv run aiu labs list | Measure-Object -Line).Lines
  ```
- **Expected:** First command exits 0 and prints `tiers: OK (17 labs)`. Second line prints `17`.
- **Ticket:** T-017

### AC-11 - Hardware check runs offline
- **Requirement:** `hwcheck` reports tier, RAM, GPU/VRAM, and free disk without network access.
- **Command:**
  ```powershell
  uv run aiu hwcheck --json | uv run python -c "import json,sys; d=json.load(sys.stdin); raise SystemExit(0 if {'tier','passed','ram_total_gb','disk_free_gb','gpu'} <= d.keys() else 1)"
  ```
- **Expected:** Exit 0. The `gpu` value may be null.
- **Ticket:** T-009

### AC-12 - Cost caps enforced
- **Requirement:** Caps are loaded and enforced; every pinned role has a price; the E9 live estimate is below the per-lab cap.
- **Command:**
  ```powershell
  uv run pytest -q tests/test_cost.py; uv run aiu lab estimate E9
  ```
- **Expected:** pytest exits 0. The estimate exits 0 and prints an `estimate_usd` at or below `cap_usd=2.00`.
- **Ticket:** T-011, T-036

### AC-13 - Fixture/live separation
- **Requirement:** Fixture outputs go only to the gitignored `.runs/`; `experiments/` contains only committed live runs; live mode refuses to start without the provider key and makes no network call.
- **Command:**
  ```powershell
  git check-ignore -q .runs/x; uv run aiu smoke --mode fixture; uv run aiu lab run E9 --run-id 20261025T001745Z-live-b1c296 --mode live; git status --porcelain experiments
  ```
- **Expected:**
  - The first command exits 0.
  - Fixture smoke exits 0.
  - The live run command exits non-zero and prints `DEEPSEEK_API_KEY not set`; the key check happens before any run directory is written.
  - `git status --porcelain experiments` prints nothing.
- **Ticket:** T-015, T-024

### AC-14 - Source files and traceability integrity
- **Requirement:** The source PDF, concept map, and source README are tracked, and traceability covers the whole concept map.
- **Command:**
  ```powershell
  git ls-files --error-unmatch "source/AI Engineering Concept Map Raw Material for a Training Schema.pdf" source/concept_map.txt source/README.md; uv run aiu traceability check --require-all
  ```
- **Expected:** Exit 0 and `traceability: OK`.
- **Ticket:** T-001, T-027

### AC-15 - Transparency artifacts agree
- **Requirement:** Every committed live run appears in RESULTS.md, every run ID cited in RESULTS exists under `experiments/`, and status counts/cost match the run directories.
- **Command:**
  ```powershell
  uv run aiu status --check; uv run python -c "import pathlib,re; t=pathlib.Path('RESULTS.md').read_text(encoding='utf-8'); ids=set(re.findall(r'2026\d{4}T\d{6}Z-live-[0-9a-f]{6}',t)); runs={p.name for p in pathlib.Path('experiments').glob('*/*') if p.is_dir()}; raise SystemExit(0 if ids==runs else 1)"
  ```
- **Expected:** Both commands exit 0; status is OK and the run-ID sets match.
- **Ticket:** T-005, T-007, T-024, T-026

### AC-16 - README bounded by ACCEPTANCE
- **Requirement:** README links to ACCEPTANCE.md and has an explicit `Planned / not yet verified` section for work outside v1. It must not claim v1 acceptance before AC-01..AC-20 pass.
- **Command:**
  ```powershell
  uv run python -c "import pathlib; t=pathlib.Path('README.md').read_text(encoding='utf-8'); ok=('ACCEPTANCE.md' in t and 'Planned / not yet verified' in t); print('readme: OK' if ok else 'readme: MISSING'); raise SystemExit(0 if ok else 1)"
  ```
- **Expected:** Exit 0 and `readme: OK`.
- **Ticket:** T-007, T-026, T-034

### AC-17 - Assessment structure
- **Requirement:** Every card and module declares an assessment; every module checkpoint has deterministic items and a human rubric; no module is graded only by an LLM judge.
- **Command:**
  ```powershell
  uv run aiu validate curriculum; uv run pytest -q tests/test_modules.py
  ```
- **Expected:** Both commands exit 0. Module tests confirm 13 modules, all cards assigned once, and deterministic plus human-rubric items.
- **Ticket:** T-019, T-020, T-021

### AC-18 - Live run logging completeness
- **Requirement:** Every committed live run directory has the eight required artifacts, and `cost.json` records token counts and USD cost.
- **Command:**
  ```powershell
  uv run python -c "import json,pathlib; req={'prediction.md','prediction.sha256','config.json','responses.jsonl','postmortem.md','metrics.json','cost.json','result.json'}; keys={'prompt_tokens','completion_tokens','actual_usd'}; ok=all(req <= {p.name for p in d.iterdir()} and keys <= set(json.loads((d/'cost.json').read_text())) for d in pathlib.Path('experiments').glob('*/*') if d.is_dir()); print('runs: OK' if ok else 'runs: MISSING'); raise SystemExit(0 if ok else 1)"
  ```
- **Expected:** Exit 0 and `runs: OK`.
- **Ticket:** T-014, T-015, T-024

### AC-19 - Clean-checkout reproduction
- **Requirement:** A fresh clone with only git and uv, no provider keys, and no pre-existing `.venv` or `.runs/` reaches a passing gate.
- **Command:**
  ```powershell
  $d = Join-Path $env:TEMP ("aiu-clean-" + [guid]::NewGuid()); git clone (git rev-parse --show-toplevel) $d; Push-Location $d; Remove-Item Env:OPENROUTER_API_KEY -ErrorAction SilentlyContinue; Remove-Item Env:DEEPSEEK_API_KEY -ErrorAction SilentlyContinue; powershell -NoProfile -ExecutionPolicy Bypass -File ops\bootstrap.ps1; uv run aiu check-all; $rc = $LASTEXITCODE; Pop-Location; Remove-Item -Recurse -Force $d; exit $rc
  ```
- **Expected:** Bootstrap exits 0. `check-all` exits 0. Final exit code is 0.
- **Ticket:** T-002, T-008, T-035, T-038

### AC-20 - Final gate
- **Requirement:** `aiu check-all` runs every offline check and the full test suite, prints one OK/FAIL line per check, and exits non-zero if any check fails. It may refresh the generated `status.json` and README Tests row.
- **Command:**
  ```powershell
  Remove-Item Env:OPENROUTER_API_KEY -ErrorAction SilentlyContinue; Remove-Item Env:DEEPSEEK_API_KEY -ErrorAction SilentlyContinue; uv run aiu check-all; $rc = $LASTEXITCODE; git status --porcelain; exit $rc
  ```
- **Expected:**
  - Exit 0.
  - Output ends with `check-all: 19/19 checks OK`.
  - `git status --porcelain` shows no changes other than the generated `README.md` and `status.json` Tests row.
- **Ticket:** T-035
