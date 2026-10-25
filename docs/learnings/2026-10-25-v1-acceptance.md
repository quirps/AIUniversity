---
title: v1 acceptance on the measured Windows 10 machine
author: Maintainer (DeepSeek Flash 4.1)
date: 2026-10-25
lab_id: none
run_ids: []
cards: []
ledger_entries: [P-082, P-083, P-084]
---

# v1 acceptance on the measured Windows 10 machine

## Question

Can a fresh clone with no provider keys and no pre-existing `.venv` or `.runs/`
reproduce the v1 gate on this machine, and do AC-01..AC-20 pass as written?

## Prediction

Expected: all AC-01..AC-20 pass after the clean-checkout LF fix and the ACCEPTANCE
rewrite, with no live API call. This note is written after the clean-clone run,
so the expected result is reported for context, not as a blind prediction.

## Setup

- **Commit under test:** `a51df3e` (the clean clone for AC-01..AC-18 and AC-20).
- **Clean clone for AC-19:** a fresh clone of `a51df3e` in `%TEMP%`.
- **Mode:** offline; `OPENROUTER_API_KEY` and `DEEPSEEK_API_KEY` unset.
- **Bootstrap:** `powershell -NoProfile -ExecutionPolicy Bypass -File ops\bootstrap.ps1`.
- **Gate:** `uv run aiu check-all`.
- **Hardware (measured):** Windows 10, NVIDIA GeForce GTX 1060 6 GB (Pascal),
  15.81 GB RAM total, 41.23 GB free disk, `hwcheck` tier `API_ONLY`, passed.

## Result

| AC | Result | Evidence |
|---|---|---|
| AC-01 | PASS | Python 3.12.9; `.python-version` = 3.12 |
| AC-02 | PASS | `uv lock --check` and `uv sync --frozen` |
| AC-03 | PASS | pytest 206 passed, 0 failed, no keys |
| AC-04 | PASS | `validate: 106 files, 0 errors` |
| AC-05 | PASS | `secrets-scan: 0 findings`; hooks path `.githooks` |
| AC-06 | PASS | `journal: append-only OK` |
| AC-07 | PASS | `status: OK` |
| AC-08 | PASS | `provenance: OK (84 claims)` |
| AC-09 | PASS | `traceability: OK (79 rows, 75 cards)` |
| AC-10 | PASS | `tiers: OK (17 labs)`; list count 17 |
| AC-11 | PASS | `hwcheck --json` has tier, RAM, disk, GPU keys |
| AC-12 | PASS | cost tests pass; E9 estimate 0.1021 <= 2.00 cap |
| AC-13 | PASS | fixture smoke exits 0; live refuses with `DEEPSEEK_API_KEY not set`; `experiments/` clean |
| AC-14 | PASS | source PDF, concept map, and README tracked; traceability OK |
| AC-15 | PASS | status OK; RESULTS run IDs equal run directories |
| AC-16 | PASS | README links ACCEPTANCE and has a planned section |
| AC-17 | PASS | 13 modules validate; module tests pass |
| AC-18 | PASS | all 15 live run dirs have the eight artifacts and cost keys |
| AC-19 | PASS | fresh clone bootstrap + `check-all` 19/19 |
| AC-20 | PASS | `check-all: 19/19 checks OK`; only README/status refreshed |

Cumulative live spend, summed from `RESULTS.md`: **$0.1704**. The usable smoke
suite cost $0.0302 and the M-A1 E9 run cost $0.0645. No live API calls were made
during T-038.

## Interpretation

The clean clone passes the same gate as the working repo after adding
`.gitattributes` for LF JSONL checkouts. The earlier clone failure was a
line-ending mismatch, not a data or metric failure; it is fixed and recorded.
The acceptance document now describes the implemented v1 surface rather than
the original architecture wish-list. The gate is offline, deterministic, and
reproducible with no keys.

## Limits

- v1 is API-only. Local tiers have API fallbacks only; local inference at the
  ~3B Q4 ceiling is **unverified**, and local training is out of scope.
- All 75 cards remain `draft`; no claim is `verified`. The provenance rows are
  `unverified` except where a human review is recorded.
- The OpenRouter-pinned roles were not exercised live; only the DeepSeek roles
  have measured live runs.
- The E9 accuracy drop is confounded with partial-answer exact-match scoring;
  see `docs/learnings/2026-10-25-e9-context-distractors.md`.
- The ADR-024 HTML workbench and lesson-scoped DeepSeek shell are not built, so
  M-A1 is not learner-complete in the UI sense.

## What changed in the trust table

| Claim / ledger entry | Before | After | Reason |
|---|---|---|---|
| P-082 / P-084 | unverified | unverified | Pricing and live smoke evidence; human verification still required. |
| A-008 trust row | replicated_once | replicated_once | No change on v1 acceptance; the validity caveat remains. |

## Links

- Definition of done: [ACCEPTANCE.md](../../ACCEPTANCE.md)
- Run index: [RESULTS.md](../../RESULTS.md)
- Live smoke cost: [experiments/E9/20261024T235846Z-live-6551ed/cost.json](../../experiments/E9/20261024T235846Z-live-6551ed/cost.json)
- M-A1 run cost: [experiments/E9/20261025T001745Z-live-b1c296/cost.json](../../experiments/E9/20261025T001745Z-live-b1c296/cost.json)
- Provenance: [PROVENANCE.md](../../PROVENANCE.md)
