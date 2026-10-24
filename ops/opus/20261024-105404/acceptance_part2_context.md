Here is ACCEPTANCE.md through AC-13. Emit ONLY one file:

## FILE: ACCEPTANCE.part2.md

It must contain AC-14 through AC-20, continuing the exact same format as AC-01..AC-13 (heading, Requirement, Command, Expected, Ticket). Cover:
- AC-14: source provenance and concept-map integrity.
- AC-15: transparency artifacts agree (JOURNAL, PROVENANCE, RESULTS, status.json, experiments).
- AC-16: README claims do not exceed what ACCEPTANCE proves.
- AC-17: learner assessment is not a single unvalidated LLM judge; deterministic or human-reviewed checks dominate.
- AC-18: every live run logs model ID, parameters, seed, cost, timestamp, and artifacts.
- AC-19: clean-checkout reproduction from clone to passing gate.
- AC-20: final iu check-all gate aggregates the required checks and exits 0.

Constraints: runnable from the repo root in Windows PowerShell; reference implementing ticket IDs; no implementation code; no commentary; do not repeat AC-01..AC-13.

Current ACCEPTANCE.md:
<acceptance>
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
</acceptance>