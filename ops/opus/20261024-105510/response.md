## FILE: ACCEPTANCE.part2.md
```markdown
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
```
