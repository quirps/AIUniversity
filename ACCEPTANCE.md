# ACCEPTANCE.md - AI University v1 Definition of Done

## How to run

Run every command from the repo root in Windows PowerShell 5.1+.

**Preconditions:**
- `ops\bootstrap.ps1` has completed.
- Unless an AC says otherwise, `OPENROUTER_API_KEY` is unset. To unset it:
  ```powershell
  Remove-Item Env:OPENROUTER_API_KEY -ErrorAction SilentlyContinue
  ```

**Checking exit codes:**
- "Exit 0" means `$LASTEXITCODE -eq 0` immediately after the command.
- For pure PowerShell checks that use `if (...) { exit 1 }`, run them in a child shell to read the exit code:
  ```powershell
  powershell -NoProfile -Command "<check>"; $LASTEXITCODE
  ```

**Live API calls:** No AC makes a live call. Live evidence is checked from committed artifacts only.

**Single gate:** `uv run aiu check-all` (AC-20) runs AC-01..AC-18 programmatically. AC-19 is the clean-checkout procedure, which runs everything else.

---

### AC-01 - Python 3.12 via uv
- **Requirement:** The project runs on Python 3.12, provisioned by uv. It does not depend on the system Python 3.7.4.
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
- **Requirement:** The full test suite passes with no API key present and no network access.
- **Network blocking:** Socket creation is blocked in `tests/conftest.py`. Any attempted connection fails the test.
- **Command:**
  ```powershell
  Remove-Item Env:OPENROUTER_API_KEY -ErrorAction SilentlyContinue; uv run pytest -q
  ```
- **Expected:**
  - Exit 0.
  - Summary line contains `passed`.
  - Summary contains no `failed` and no `error`.
- **Ticket:** T-002, T-012, T-013

### AC-04 - JSON Schema validation
- **Requirement:** Every YAML file conforms to `schemas/curriculum.schema.json`. This covers:
  - every card in `curriculum/A..F`;
  - every module in `curriculum/modules`;
  - every `labs/*/manifest.yaml`;
  - `learner/trust_table.yaml`.
- **Command:**
  ```powershell
  uv run aiu validate
  ```
- **Expected:**
  - Exit 0.
  - Output ends with `0 errors`.
- **Ticket:** T-006

### AC-05 - No secrets or forbidden files
- **Requirement:** No API keys, `.env` files or other forbidden files are tracked. The pre-commit hook is installed.
- **Command:**
  ```powershell
  uv run aiu scan-secrets --tracked; git config core.hooksPath
  ```
- **Expected:**
  - First command exits 0 and prints `0 findings`.
  - Second command prints `.githooks`.
- **Ticket:** T-003, T-004

### AC-06 - JOURNAL.md is append-only
- **Requirement:** No commit in history modifies or deletes existing JOURNAL.md lines.
- **Command:**
  ```powershell
  uv run aiu journal-check --history
  ```
- **Expected:** Exit 0.
- **Ticket:** T-005

### AC-07 - status.json and README consistency
- **Requirement:**
  - status.json validates against `schemas/status.schema.json`.
  - status.json equals freshly generated state.
  - The README STATUS block matches status.json.
- **Command:**
  ```powershell
  uv run aiu status --check
  ```
- **Expected:** Exit 0. No diff is printed.
- **Ticket:** T-007

### AC-08 - Provenance ledger
- **Requirement:** Every public number or claim in README, RESULTS, learnings and cards cites a P-### entry. Each P-### entry is one of two kinds:
  - **Verified:** it resolves to an existing `experiments/<lab_id>/<run_id>/` with `cost.json`.
  - **Unverified:** it is labeled `unverified` and never presented as fact.
- **Command:**
  ```powershell
  uv run aiu provenance-check
  ```
- **Expected:**
  - Exit 0.
  - Output reports `0 dangling, 0 untraced, 0 unlabeled`.
- **Ticket:** T-026

### AC-09 - Traceability
- **Requirement:** Every concept in `source/concept_map.txt` maps to at least one card. Every card that references an experiment references an existing lab. TRACEABILITY.md matches the computed map.
- **Command:**
  ```powershell
  uv run aiu traceability-check
  ```
- **Expected:**
  - Exit 0.
  - Output reports `0 unmapped concepts, 0 broken links`.
- **Ticket:** T-027, T-033

### AC-10 - hardware_tier validity and API fallback
- **Requirement:**
  - All 17 labs (E1..E13, L-001..L-004) declare a valid `hardware_tier`.
  - Every local-tier lab declares an API fallback.
  - No lab requires local training.
- **Command:**
  ```powershell
  uv run aiu labs check-tiers; (uv run aiu labs list --json | ConvertFrom-Json).Count
  ```
- **Expected:**
  - First command exits 0.
  - Second command prints `17`.
- **Ticket:** T-017

### AC-11 - Hardware check runs offline
- **Requirement:** `hwcheck` reports CPU, RAM, GPU/VRAM and free disk without network access.
- **Command:**
  ```powershell
  uv run aiu hwcheck --json | uv run python -c "import json,sys; d=json.load(sys.stdin); raise SystemExit(0 if {'cpu','ram_gb','gpu','disk_free_gb'}<=d.keys() else 1)"
  ```
- **Expected:** Exit 0.
- **Ticket:** T-009

### AC-12 - Cost caps enforced
- **Requirement:**
  - `config/caps.yaml` caps are loaded.
  - CostGuard refuses any estimate or run that exceeds a per-run or cumulative cap.
  - Pinned prices exist for every model role.
- **Command:**
  ```powershell
  uv run pytest -q tests/test_cost.py; uv run aiu lab estimate E9 --mode live
  ```
- **Expected:**
  - pytest exits 0.
  - The estimate exits 0 and prints a USD figure that is less than or equal to the printed cap.
- **Ticket:** T-011, T-036

### AC-13 - Fixture/live separation
- **Requirement:**
  - Fixture-mode outputs go only to the gitignored `.runs/`.
  - `experiments/` contains only live runs, and each one is listed in RESULTS.md.
  - Live mode refuses to start without a key.
- **Command:**
  ```powershell
  git check-ignore -q .runs/x; uv run aiu lab run E9 --mode fixture; uv run aiu results-check; uv run aiu lab run E9 --mode live --yes
  ```
- **Expected:**
  - Each of the first three commands exits 0.
  - The last command (no key set) exits non-zero and prints `OPENROUTER_API_KEY not set`. It makes no network call.
  - `git status --porcelain experiments` is empty afterward.
- **Ticket:** T-015, T-024

### AC-14 - Source provenance and concept-map integrity
- **Requirement:**
  - Every file in `source/` is listed in `source/MANIFEST.yaml` with its SHA-256, origin and license or permission note.
  - Recomputed hashes match the manifest.
  - Every concept in `source/concept_map.txt` cites a source file and location that exist.
  - Concept IDs in `source/concept_map.txt` are unique.
- **Command:**
  ```powershell
  uv run aiu source-check
  ```
- **Expected:**
  - Exit 0.
  - Output reports `0 hash mismatches, 0 unlisted files, 0 unresolved citations, 0 duplicate concepts`.
- **Ticket:** T-001, T-027

### AC-15 - Transparency artifacts agree
- **Requirement:**
  - Every `experiments/<lab_id>/<run_id>/` appears in RESULTS.md, has a P-### entry in PROVENANCE.md and has a JOURNAL.md entry.
  - Every run ID cited in RESULTS.md, PROVENANCE.md, JOURNAL.md or status.json exists under `experiments/`.
  - Run counts and cumulative cost in status.json equal the sums over `experiments/*/*/cost.json`.
- **Command:**
  ```powershell
  uv run aiu transparency-check
  ```
- **Expected:**
  - Exit 0.
  - Output reports `0 orphan runs, 0 missing references, 0 count mismatches, 0 cost mismatches`.
- **Ticket:** T-005, T-007, T-024, T-026

### AC-16 - README claims bounded by ACCEPTANCE
- **Requirement:**
  - Every capability claim in README.md is tagged with the AC-## that proves it.
  - Every tagged AC exists in ACCEPTANCE.md.
  - Untagged capability statements appear only under an explicit "Planned / not yet verified" heading.
  - README contains no claims of outcomes such as "learners will master" or "proven effective" unless they are backed by a verified P-### entry.
- **Command:**
  ```powershell
  uv run aiu readme-claims-check
  ```
- **Expected:**
  - Exit 0.
  - Output reports `0 untagged claims, 0 unknown ACs, 0 unbacked outcome claims`.
- **Ticket:** T-007, T-026, T-034

### AC-17 - Assessment not dominated by a single unvalidated LLM judge
- **Requirement:**
  - Every assessment item in `curriculum/` and `labs/` declares a `grader` of `deterministic`, `human`, or `llm`.
  - In every module, `deterministic` plus `human` items carry at least 70% of the total score weight.
  - No module's pass/fail decision depends on `llm`-graded items alone.
  - Every `llm` grader:
    - references a rubric;
    - uses at least two judges or one judge plus human spot-check;
    - links a validation record in `learner/grader_validation/` showing agreement with human labels.
- **Command:**
  ```powershell
  uv run aiu assessment-check; uv run pytest -q tests/test_assessment.py
  ```
- **Expected:**
  - Both commands exit 0.
  - First output reports `0 modules below threshold, 0 llm-only gates, 0 unvalidated llm graders`.
- **Ticket:** T-019, T-020, T-021

### AC-18 - Live run logging completeness
- **Requirement:** Every `experiments/<lab_id>/<run_id>/` contains `run.json` and `cost.json`, and both validate against `schemas/run.schema.json`.
  - `run.json` records model ID (exact provider slug), all sampling parameters, seed, ISO-8601 UTC start and end timestamps, git commit and the list of artifact files with SHA-256.
  - `cost.json` records token counts and USD cost.
  - Listed artifact hashes match the files on disk.
- **Command:**
  ```powershell
  uv run aiu runs-check
  ```
- **Expected:**
  - Exit 0.
  - Output reports `0 missing fields, 0 schema errors, 0 hash mismatches`.
- **Ticket:** T-014, T-015, T-024

### AC-19 - Clean-checkout reproduction
- **Requirement:** A fresh clone on a Windows machine with only git and uv installed reaches a passing gate with no manual steps beyond those below. This must work with no API key and no pre-existing `.venv` or `.runs/`.
- **Command:**
  ```powershell
  $d = Join-Path $env:TEMP ("aiu-clean-" + [guid]::NewGuid()); git clone (git rev-parse --show-toplevel) $d; Push-Location $d; Remove-Item Env:OPENROUTER_API_KEY -ErrorAction SilentlyContinue; powershell -NoProfile -ExecutionPolicy Bypass -File ops\bootstrap.ps1; uv run aiu check-all; $rc = $LASTEXITCODE; Pop-Location; Remove-Item -Recurse -Force $d; exit $rc
  ```
- **Expected:**
  - Bootstrap exits 0.
  - `uv run aiu check-all` exits 0.
  - Final exit code is 0.
- **Ticket:** T-002, T-008, T-035

### AC-20 - Final gate
- **Requirement:**
  - `aiu check-all` runs the checks for AC-01 through AC-18 in order.
  - It prints one PASS/FAIL line per AC.
  - It exits non-zero if any check fails.
  - It makes no network call.
  - It writes no tracked files.
- **Command:**
  ```powershell
  Remove-Item Env:OPENROUTER_API_KEY -ErrorAction SilentlyContinue; uv run aiu check-all; $rc = $LASTEXITCODE; git status --porcelain; exit $rc
  ```
- **Expected:**
  - Exit 0.
  - Output contains 18 lines `AC-01 PASS` .. `AC-18 PASS`.
  - Output ends with `ALL CHECKS PASSED`.
  - `git status --porcelain` prints nothing.
- **Ticket:** T-035
