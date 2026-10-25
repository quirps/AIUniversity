# Changelog

All notable changes to AI University are recorded here, newest first.
Versions follow semantic versioning. Dates are ISO 8601 (YYYY-MM-DD).

## Unreleased - 2026-10-25 - M-A1 live learning loop

### Added
- Full live E9 run `20261025T001745Z-live-b1c296` with prediction, post-mortem, metrics, cost, and measured `max_drop=0.1833`.
- M-A1 checkpoint answers and result (3/3), portfolio diagnostic note, and E9 learning write-up.
- Trust-table row for A-008 marked `replicated_once` with the partial-answer caveat.

### Changed
- T-037 logged a failed E9 validity check and a scoring artifact: all misses were partial answers, not wrong entities.

## Unreleased - 2026-10-24 - Pinned models and live smoke

### Added
- DeepSeek direct provider support (`DEEPSEEK_API_KEY`, `https://api.deepseek.com/chat/completions`) with thinking mode disabled for short-answer labs.
- Pinned role map and pricing for the v1 smoke set; `strong` remains `UNPINNED` pending a later decision (ADR-025).
- Five committed live smoke run directories and measured smoke cost of $0.0302 for the usable suite.

### Changed
- Runnable lab manifests now use `cost_basis: estimated_from_pinned_pricing` and the recomputed estimates.
- `aiu smoke --mode live` now routes each call by role provider.

## Unreleased - 2026-10-24 - Decision review and manager report

### Changed
- Consolidated OD-01..OD-12 into one canonical register in `DECISIONS.md`.
- Resolved model policy, per-run/daily caps, CI method, ledger authority, reasoning accounting, fixture counting, licenses, PDF commit, and prediction authorship.
- Resolved the smoke cap at $5.00 (OD-02) and the committed-prediction gate (OD-05); deferred human-label ownership (OD-09).
- Corrected OD cross-references in `LAB_SPEC.md`, `TASKS.md`, `README.md`, `REPO_LAYOUT.md`, `source/README.md`, and `JOURNAL.md`.
- T-001 now installs the source PDF and the three license files.

### Added
- `docs/STATUS_REPORT.md`: manager-level overview, failure log, cost report, risks, and next steps.
- Foundation T-001..T-016: Python 3.12 via `uv`, package and CLI, secrets scanner, pre-commit hooks, append-only journal check, schema validation, generated status, config/models, hardware probe, metrics, cost guard, clients, prediction gate, lab runner, and post-mortem check.

## 0.1.0 - 2026-10-24 - Architecture handoff

Stage: `architecture`. No implementation code, no live runs. Lab cost $0.00; architecture cost **$5.290876** (see `ops/OPUS_RUN_LOG.md`).

### Added
- Specification documents (architecture, acceptance criteria, ticket plan T-001..T-038).
- `status.schema.json` and `status.json` (stage `architecture`; 3 cards drafted, A/B/C 1 each;
  17 labs defined, 0 runnable; 13 modules planned, 0 authored; 0 live runs;
  provenance ledger: 13 entries, all unverified; `last_verified` null).
- Draft knowledge cards: one each at levels A, B, and C.
- Experiment templates under `experiments/_template/`:
  `prediction.md`, `postmortem.md`, `config.json`, `result.json`, `metrics.json`, `cost.json`.
- Learning post template at `docs/learnings/_template.md`.
- Architecture call record: `ops/OPUS_KICKOFF.md`, `ops/OPUS_RUN_LOG.md`, and raw responses under `ops/opus/`.
- This changelog.

### Known gaps
- All tickets T-001..T-038 are open; see `known_gaps` in `status.json`.
- Model IDs and prices are not pinned; no expected-cost figures are final (T-036).
- `ACCEPTANCE.md` has never been run to passing (T-038).
