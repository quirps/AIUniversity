# JOURNAL.md

Append-only. Never edit or delete a past entry. To correct an entry, add a new one that references it. Enforcement: pre-commit check (T-005, not yet built).

## Entry template

```
## Entry <n> - YYYY-MM-DD - <title>
- Author:
- Context:
- What I did:
- What I observed (measured / sourced / assumed - label each):
- Runs: experiments/<lab>/<run_id> | none
- Spend this session (USD, from cost.json): 
- Cumulative spend (USD, recomputed): 
- Decisions / open questions:
- Next:
```

---

## Entry 0 - date of architecture handoff (fill in at commit) - Project genesis

- Author: Maintainer
- Context: AI University v1 starts from a source concept map (`source/concept_map.txt`; the PDF is authoritative). The goal is to build a lab-first curriculum for working engineers.
- Architecture call provenance:
  - The spec set was produced in an architecture session with an LLM assistant acting as architect.
  - The spec set comprises CONSTITUTION, REPO_LAYOUT, GOVERNANCE, TASKS T-001..T-038, ACCEPTANCE, LAB_SPEC, and the ledger seeds.
  - These are proposals, not evidence (assumed).
  - The maintainer has accepted them as the v1 baseline. Changes go through DECISIONS.md.
- Measured hardware: **none yet**. The hardware check (`aiu hwcheck`, T-009) is not built, so no hardware numbers are recorded. The only fact here is the target platform from REPO_LAYOUT: Windows path, Python 3.12 (sourced from the spec, not measured).
- What I observed: nothing measured in labs. No live or fixture runs exist. The architecture calls are measured separately in Entry 1.
- Runs: none
- Lab spend this session (USD): 0.00
- Architecture spend (USD): 5.290876 (measured from each response's `usage.cost`; see Entry 1 and `ops/OPUS_RUN_LOG.md`)
- Cumulative spend (USD): 5.290876
- Current state:
  - Spec documents exist.
  - 3 exemplar cards drafted.
  - 0 labs runnable.
  - 0 live runs.
  - All ledger rows are `unverified`.
- Next: T-001 → T-007 (repo, bootstrap, ignore rules, secrets hook, journal check, validate, status).

---

## Entry 1 - 2026-10-24 - Architecture handoff via OpenRouter

- Author: Maintainer (Opus 5.5 as architect; DeepSeek Flash 4.1 as implementer)
- Context: Convert the source concept map into a v1 architecture: content schema, lab harness spec, backlog, acceptance, and governance.
- What I did:
  - Ran 15 OpenRouter calls to `anthropic/claude-opus-5.5` at temperature 0.2.
  - Saved every raw response, repaired markdown, and usage metadata under `ops/opus/<timestamp>/`.
  - Extracted the spec set into the repo. The call-by-call record is `ops/OPUS_RUN_LOG.md`.
- What I observed (measured):
  - Total architecture spend: **5.290876 USD**, from each response's `usage.cost`.
  - 2 calls returned empty content after spending **2.607784 USD** on reasoning (`finish_reason=length`).
  - 7 calls were rejected with `402 in_flight_budget_exhausted` before any completion.
  - 6 calls produced usable content. The first usable call still truncated at 64k tokens; the backlog was finished in smaller calls.
  - The key was loaded from an existing local `.env`; it was never printed, copied into the repo, or committed.
- What I observed (assumed):
  - The design is coherent but unvalidated. Every card claim remains `unverified` until a lab or a primary-source check says otherwise.
- Runs: none (no lab runs)
- Spend this session (USD): 5.290876 (architecture only)
- Cumulative spend (USD): 5.290876
- Decisions / open questions: `DECISIONS.md` → "Decision register" (OD-01..OD-12).
- Next: T-001, then T-002. Keep architecture spend and lab spend separate in `status.json` and the README.

---

## Entry 2 - 2026-10-24 - Decision review and manager report

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Management review of the architecture handoff. The owner asked for an explicit failure report, a canonical decision set, and a high-level status report.
- What I did:
  - Consolidated OD-01..OD-12 into one canonical register. Resolved eight, deferred one, proposed one, and opened one.
  - Corrected inconsistent OD references across `LAB_SPEC.md`, `TASKS.md`, `README.md`, `REPO_LAYOUT.md`, and `source/README.md`.
  - Added `docs/STATUS_REPORT.md` and linked it from the README.
  - Updated T-001 to commit the source PDF and the three license files.
  - No Opus calls. No git commit or push.
- What I observed (measured): 0.00 USD this session. Cumulative remains 5.290876 USD (architecture only).
- What I observed (assumed): the design is coherent; validation still requires T-006, T-035, and T-038.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: OD-02 deferred, OD-05 proposed, OD-09 open. Everything else is resolved in `DECISIONS.md`.
- Next: owner confirms OD-02, OD-05, OD-09, the budget, and git initialization; then T-001.

---

## Entry 3 - 2026-10-24 - T-001: repository installed and initial commit

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: The owner approved the remaining decisions and asked to begin. T-001 installs the spec set, licenses, source PDF, git repo, and remote.
- Owner approvals recorded: OD-02 = 5.00 USD smoke cap; OD-05 = committed prediction required; OD-03 = 1.00 USD/day soft and 2.00 USD/run hard; OD-09 deferred; commit at T-001 approved.
- What I did:
  - Added the MIT, CC BY 4.0, and CC0 license files.
  - Recorded OD-02 and OD-05 as resolved and OD-09 as deferred in `DECISIONS.md`.
  - Updated T-014 to implement the committed-prediction gate.
  - Initialized git, added the GitHub remote, and committed the spec set.
  - No Opus calls.
- What I observed (measured): spend this session 0.00 USD; cumulative 5.290876 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: no blocking decisions; OD-09 deferred.
- Next: T-002 (uv + Python 3.12), then T-003..T-007.

---

## Entry 4 - 2026-10-24 - T-002 and T-003: Python toolchain and hygiene

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Bootstrap the Python toolchain, then add ignore and environment hygiene before any secret-bearing work.
- What I did:
  - Installed `uv 0.13.5` and Python `3.12.9`.
  - Created `pyproject.toml`, `.python-version`, `src/aiu/`, `tests/`, `ops/bootstrap.ps1`, and `ops/RUNBOOK.md`.
  - Ran `uv sync`: 26 packages resolved; `uv run aiu --version` printed `aiu 0.1.0`; the CLI test passed.
  - Added `.gitignore`, `.env.example`, and hygiene tests.
  - Removed `__pycache__` artifacts that the first T-002 commit picked up before `.gitignore` existed.
  - No Opus calls.
- What I observed (measured): Python 3.12.9; `aiu 0.1.0`; tests pass; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: none.
- Next: T-004 (secrets scan and pre-commit hook), then T-005..T-007.

---

## Entry 5 - 2026-10-24 - T-004: secrets scanner and pre-commit hook

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Prevent credentials and forbidden model artifacts from entering the repo.
- What I did:
  - Implemented `src/aiu/secrets_scan.py` with OpenRouter, generic `sk-`, bearer-token, and env-assignment patterns; forbidden globs; binary and oversize handling; and a documented-dummy allowlist.
  - Added `aiu secrets-scan [--staged] [--root PATH]`.
  - Added `.githooks/pre-commit` and configured `core.hooksPath`.
  - Added 6 scanner tests.
  - No Opus calls.
- What I observed (measured): 10 tests pass; `aiu secrets-scan` reports `0 findings`; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: the dummy `sk-or-v1-abcdefghijklmnopqrstuvwx` is allowlisted because it appears in the project's own test and spec text.
- Next: T-005 (append-only journal check).

---

## Entry 6 - 2026-10-24 - T-005: append-only journal check

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Enforce that past journal entries are never rewritten.
- What I did:
  - Implemented `src/aiu/journal.py` with `head_content` and `check_append_only`.
  - Added `aiu journal check`.
  - Added 4 unit tests for no-HEAD, append, edited-middle, and CRLF/LF normalization.
  - Added the journal check as the second pre-commit hook line.
  - No Opus calls.
- What I observed (measured): tests pass; `aiu journal check` prints `journal: append-only OK`; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: none.
- Next: T-006 (YAML/JSON Schema validation command).
---

## Entry 7 - 2026-10-24 - T-006: schema validation

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Make the curriculum content machine-checkable before adding more cards or labs.
- What I did:
  - Implemented `src/aiu/validate.py` with JSON Schema validation and ID/path checks.
  - Added `aiu validate [PATH ...]`.
  - Added `learner/trust_table.yaml` and two invalid fixtures.
  - Added 8 validator tests.
  - Updated `status.json` to stage `building` and removed T-001..T-006 from `known_gaps`.
  - No Opus calls.
- What I observed (measured): `aiu validate` reports `validate: 4 files, 0 errors`; 22 tests pass; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: none.
- Next: T-007 (status generation and README consistency).
---

## Entry 8 - 2026-10-24 - T-007: generated status and README block

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Replace the hand-maintained status snapshot with a generated one and add a drift check.
- What I did:
  - Implemented `src/aiu/status.py` and `aiu status --write|--check`.
  - Extended `schemas/status.schema.json` with `last_live_run` and `tests`, which the status generator requires.
  - Added a fixture repo and 7 status tests.
  - Regenerated `status.json` and the README STATUS block; removed T-007 from `known_gaps`.
  - No Opus calls.
- What I observed (measured): `aiu status --write` prints `status: written`; `aiu status --check` prints `status: OK`; 29 tests pass; 31 gaps remain; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: the status schema omitted `last_live_run` and `tests`; corrected in this ticket.
- Next: T-008 (config loading and Pydantic models).
---

## Entry 9 - 2026-10-24 - T-008: config and core models

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Add the role, pricing, and cap configuration plus the shared request/response models.
- What I did:
  - Created `config/models.yaml` (all roles `UNPINNED`), `config/pricing.yaml` (assumed defaults), and `config/caps.yaml` ($2.00/$5.00).
  - Implemented `src/aiu/config.py` and `src/aiu/models.py`.
  - Added 7 tests, including stable request hashing and live-mode UNPINNED rejection.
  - Updated `known_gaps`: removed T-008; T-036 now notes `models UNPINNED (OD-01)`.
  - No Opus calls.
- What I observed (measured): 36 tests pass; `aiu status --write` and `--check` pass; 30 gaps remain; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: model IDs and prices remain unpinned until T-036.
- Next: T-009 (hardware check).
---

## Entry 10 - 2026-10-24 - T-009: hardware probe

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Measure the actual machine and enforce the ADR-014 tier thresholds.
- What I did:
  - Implemented `src/aiu/hardware.py` with `psutil` and `nvidia-smi` probing.
  - Added `aiu hwcheck [--tier T] [--json]`.
  - Added 10 hardware tests.
  - Removed T-009 from `known_gaps`; regenerated status.
  - No Opus calls.
- Measured hardware probe (2026-10-24, tier `API_ONLY`), pasted verbatim:

```json
{
  "disk_free_gb": 33.64,
  "failures": [],
  "gpu": {
    "name": "NVIDIA GeForce GTX 1060 6GB",
    "vram_free_gb": 3.6,
    "vram_total_gb": 6.0
  },
  "passed": true,
  "ram_available_gb": 0.43,
  "ram_total_gb": 15.81,
  "tier": "API_ONLY",
  "warnings": []
}
```

- Interpretation: `API_ONLY` passes. Available RAM is 0.43 GB and free VRAM is 3.6 GB under current load, so local inference is not viable and remains out of scope. The 3B Q4 ceiling is theoretical, not available on this machine right now.
- Acceptance: `aiu hwcheck --tier LOCAL_SMALL_GPU_6GB` exits 5 with `missing local_requirements`.
- What I observed (measured): 46 tests pass; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: none.
- Next: T-010 (metrics library).
---

## Entry 11 - 2026-10-24 - T-010: metrics library

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Implement every ADR-011 metric before any lab runner depends on them.
- What I did:
  - Implemented `src/aiu/metrics.py`: accuracy, parse rate, kappa, TPR/TNR, Wilson CI, flip rate, first-slot rate, Rogan-Gladen, pass@k, pass^k, ECE, compound, normalization, exact match, and proportion.
  - Added 21 exact-value tests.
  - Removed T-010 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 67 tests pass; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: none.
- Next: T-011 (cost estimator and CostGuard).
---

## Entry 12 - 2026-10-24 - T-011: cost estimator and CostGuard

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Enforce ADR-008 before and during every paid call.
- What I did:
  - Implemented `src/aiu/cost.py`: estimate, actual cost, role pricing, effective caps, `CostGuard`, and the cost.json record.
  - Added 11 tests, including preflight and mid-run cap breaches.
  - Removed T-011 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 78 tests pass; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: none.
- Next: T-012 (fixture client).
---

## Entry 13 - 2026-10-24 - T-012..T-014: clients and prediction gate

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Add the fixture and live clients, then the run directory and committed-prediction gate.
- What I did:
  - T-012: `FixtureClient` keyed by `call_key`, with duplicate detection and recorded-hash verification.
  - T-013: `OpenRouterClient` with bounded retries, mock-transport tests, key-safe errors, and `api_key_from_env`.
  - T-014: run IDs, `lab new-run`, prediction front matter, commit-time gate, and prediction freezing.
  - Updated `experiments/_template/prediction.md` to YAML front matter so the gate has machine-readable fields.
  - Removed T-012..T-014 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 104 tests pass; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: YAML turns unquoted ISO timestamps into `datetime`; the gate accepts both strings and datetimes.
- Next: T-015 (lab registry and runner).
---

## Entry 14 - 2026-10-24 - T-015: lab registry and runner

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Execute a planned lab end-to-end with deterministic artifacts and exact exit codes.
- What I did:
  - Implemented `src/aiu/runner.py` and `src/aiu/labs/base.py` with the lab registry, planning, scoring, evaluation, cost guard, artifact writes, and fixture recording.
  - Added `aiu lab run` and `aiu lab estimate`.
  - Added a toy lab fixture and 10 runner tests.
  - Removed T-015 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 114 tests pass; spend 0.00 USD.
- Runs: fixture-only toy runs under pytest temp directories.
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: fixture runs report `actual_usd: 0.0`; live runs will use pinned prices once T-036 pins them.
- Next: T-016 (post-mortem check).
---

## Entry 15 - 2026-10-24 - T-016: post-mortem check

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: A lab is incomplete until its post-mortem is filled and its prediction is unchanged.
- What I did:
  - Aligned `experiments/_template/postmortem.md` with the five required headings and YAML front matter.
  - Implemented `src/aiu/postmortem.py` and `aiu lab postmortem-check`.
  - Added 4 tests: untouched template, complete post-mortem, edited prediction, CLI.
  - Removed T-016 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 118 tests pass; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: the handoff template used different headings than T-016; the template now matches the ticket.
- Next: T-017 (author lab manifests, starting with E9).
---

## Entry 16 - 2026-10-24 - Session handoff

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: The live session is large; a fresh session needs a self-contained handoff.
- What I did:
  - Added `ops/HANDOFF.md` with current state, commands, rules, and the T-017 path.
  - Added `ops/NEXT_SESSION_PROMPT.md` as a paste-ready prompt.
  - Linked both from the README.
  - No API calls.
- What I observed (measured): 118 tests pass; T-001..T-016 complete; next ticket T-017.
- Runs: none
- Spend this session (USD): 0.00
- Decisions / open questions: see the handoff.
- Next: T-017 (E9 manifest first, then the other 16; implement labs list/check-tiers).

## Entry 17 - 2026-10-24 - T-017: lab manifests and tier checks

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Every lab in LAB_SPEC section 6 needs a schema-valid manifest, and the hardware-tier policy must be mechanically checked.
- What I did:
  - Authored 17 lab manifests at `labs/E1` through `labs/E13` and `labs/L-001` through `labs/L-004`, starting with E9.
  - Expanded every metric name that contains `<cond>` into explicit per-condition entries.
  - Implemented `src/aiu/labs/tiers.py` with `check_tiers`, `list_labs`, and `manifest_paths`.
  - Added `aiu labs list` and `aiu labs check-tiers [PATH]`.
  - Added `tests/test_tiers.py` and `tests/fixtures/invalid_lab_local_bad_fallback.yaml`.
  - Fixed `validate_ids` so lab manifests validate by their parent directory instead of their filename stem.
  - Removed T-017 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 126 tests pass; `validate` reports 21 files and 0 errors; `labs check-tiers` reports OK for 17 labs; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: lab listing uses lexicographic id order, so E10-E13 appear before E2.
- Next: T-018 (dataset build and synthetic fixture framework).

## Entry 18 - 2026-10-24 - T-018: dataset build and synthetic fixtures

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Labs need deterministic, byte-checkable datasets and synthetic fixtures before lab implementations can land.
- What I did:
  - Added `src/aiu/generators/base.py` with `SEED`, `GENERATORS`, `register_generator`, `serialize`, and `build`.
  - Added `src/aiu/generators/__init__.py` re-exports.
  - Added `src/aiu/fixtures_synth.py` with `SYNTH`, `register_synth`, normalization, and `synth`.
  - Added `aiu dataset build LAB_ID [--check]` and `aiu fixtures synth LAB_ID [--check]`.
  - Generator and lab modules are loaded dynamically by lab id when not already registered.
  - Added 9 tests with toy generator, toy lab, and toy synthetic fixture.
  - Removed T-018 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 135 tests pass; `dataset build E1` exits 6 as expected; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: synthetic prompt tokens count the UTF-8 bytes of the concatenated message contents, divided by three and rounded up.
- Next: T-019 (L-003 statistics workbench).

## Entry 19 - 2026-10-24 - T-019: L-003 eval statistics workbench

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: L-003 must run with zero model calls and reproduce exact, hand-checkable statistics.
- What I did:
  - Added `src/aiu/generators/l003.py` with the fixed label counts and agent success counts, shuffled by `random.Random(1337)` before ID assignment.
  - Added `src/aiu/labs/l003.py` with `plan() == []` and the eleven statistics metrics.
  - Added `labs/L-003/data/items.jsonl` (220 items), `DATASET_CARD.md`, and an empty `fixtures/responses.jsonl`.
  - Added dynamic lab loading (`aiu.labs.base.load_lab`) so CLI runs import a lab module on demand.
  - Added `tests/test_lab_l003.py` with generator, metric, and end-to-end fixture-run coverage.
  - Removed T-019 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 139 tests pass; `dataset build L-003 --check` is OK; `lab estimate L-003` reports 0 calls and 0.0000 USD; spend 0.00 USD.
- Runs: none committed (fixture acceptance ran under pytest in a temporary repo).
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions:
  - T-019's table lists kappa 0.6732 and corrected_fail_rate 0.1504, but the fixed counts plus `aiu.metrics` give 0.646643 and 0.1500. Tests assert the recomputed values, as the ticket also instructs.
  - The literal root-repo PowerShell sequence in T-019 cannot pass the committed-prediction gate because fixture predictions live under the gitignored `.runs/`. The equivalent sequence passes in a temporary git repo and is covered by `tests/test_lab_l003.py`.
- Next: T-020 (E9 context distractors and position).

## Entry 20 - 2026-10-24 - T-020: E9 context distractors and position

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: E9 is the first learner-facing lab. It needed a deterministic dataset, synthetic fixtures, and an end-to-end fixture run.
- What I did:
  - Added `src/aiu/generators/e9.py` with 60 fictional items, five attributes, 20 similar-name distractors per item, and 60–90 word passages.
  - Added `src/aiu/labs/e9.py` with the five ordered conditions, verbatim prompts, metrics, and the seeded synthetic fixture.
  - Stored `meta.distractor_order` in the generator so plan-time ordering is deterministic.
  - Added `labs/E9/data/items.jsonl`, `DATASET_CARD.md`, and `fixtures/responses.jsonl` (300 responses).
  - Added `tests/helpers.py` and refactored the L-003 test to use it.
  - Added `tests/test_lab_e9.py`.
  - Removed T-020 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 144 tests pass; `dataset build E9 --check` and `fixtures synth E9 --check` are OK; `lab estimate E9` reports 300 calls, 0.1678 USD assumed; spend 0.00 USD.
- Runs: none committed (fixture acceptance ran under pytest in a temporary repo).
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: the E9 assumed estimate is 0.1678 USD at fixture-default pricing; T-036 will recompute after pinning.
- Next: T-021 (E2 schema field order).

## Entry 21 - 2026-10-24 - T-021: E2 schema field order

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: E2 checks whether JSON field order changes entailment accuracy, parse rate, and rationale length.
- What I did:
  - Added `src/aiu/generators/e2.py` with 80 balanced items, 80–120 word fictional passages, and one changed attribute per not-entailed claim in `meta.changed_attr`.
  - Added `src/aiu/labs/e2.py` with the three key orders, the brace-to-brace JSON parser, metrics, and the synthetic fixture.
  - Added `labs/E2/data/items.jsonl`, `DATASET_CARD.md`, and `fixtures/responses.jsonl` (240 responses).
  - Added `tests/test_lab_e2.py` covering the single-attribute change, leading-prose parsing, and an end-to-end fixture run.
  - Removed T-021 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 148 tests pass; `dataset build E2 --check` and `fixtures synth E2 --check` are OK; `lab estimate E2` reports 240 calls and 0.1361 USD assumed; spend 0.00 USD.
- Runs: none committed (fixture acceptance ran under pytest in a temporary repo).
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: the seeded E2 fixture produced equal evidence-first and verdict-first accuracy, so `hypothesis_supported` was false for this fixture set; the run still completed and passed validity. The manifest's assumed expected cost remains 0.25 USD until T-036.
- Next: T-022 (E4 escape hatch).

## Entry 22 - 2026-10-24 - T-022: E4 escape hatch

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: E4 checks whether explicit escape labels reduce forced in-taxonomy errors on out-of-taxonomy messages.
- What I did:
  - Added `src/aiu/generators/e4.py` with 60 in-taxonomy messages (12 per label) and 20 out-of-taxonomy messages (7 feature_request, 7 partnership, 6 press).
  - Added `src/aiu/labs/e4.py` with label-only parsing, the two conditions, metrics, and the synthetic fixture.
  - Added `labs/E4/data/items.jsonl`, `DATASET_CARD.md`, and `fixtures/responses.jsonl` (160 responses).
  - Added `tests/test_lab_e4.py` covering exact counts, escape-label parsing, and an end-to-end fixture run.
  - Removed T-022 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 152 tests pass; `dataset build E4 --check` and `fixtures synth E4 --check` are OK; `lab estimate E4` reports 160 calls and 0.0074 USD assumed; spend 0.00 USD.
- Runs: none committed (fixture acceptance ran under pytest in a temporary repo).
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: the escape fixture's remaining 15% of OOT messages choose a random in-taxonomy label, matching the spec's stated drop; the manifest's assumed expected cost remains 0.10 USD until T-036.
- Next: T-023 (E5 position and verbosity bias).

## Entry 23 - 2026-10-24 - T-023: E5 position and verbosity bias

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: E5 tests whether a pairwise judge changes its preference under slot swaps and padding.
- What I did:
  - Added `src/aiu/generators/e5.py` with 40 fictional-domain items, one-fact wrong answers, and 2–3 sentence padding.
  - Added `src/aiu/labs/e5.py` with the four conditions, slot-to-identity mapping, A/B parser, metrics, and synthetic fixture.
  - Added `parse_rate` to `labs/E5/manifest.yaml`.
  - Added `labs/E5/data/items.jsonl`, `DATASET_CARD.md`, and `fixtures/responses.jsonl` (160 responses).
  - Added `tests/test_lab_e5.py` covering the parser, hand-built flip/first-slot values, and an end-to-end fixture run.
  - Removed T-023 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 157 tests pass; `dataset build E5 --check` and `fixtures synth E5 --check` are OK; `validate labs` reports 17 files and 0 errors; `lab estimate E5` reports 160 calls and 0.0072 USD assumed; spend 0.00 USD.
- Runs: none committed (fixture acceptance ran under pytest in a temporary repo).
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: parse_rate is computed over the responses present, so a partial hand-built result set reports the rate for those responses. The manifest's assumed expected cost remains 0.15 USD until T-036.
- Next: T-024 (smoke suite with total cost cap).

## Entry 24 - 2026-10-24 - T-024: smoke suite

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: A single command must exercise every runnable lab offline and bound any live smoke run with the total cap.
- What I did:
  - Added `src/aiu/smoke.py` with `SMOKE_PLAN`, preflight estimation, per-lab run creation, summary JSON, and final status line.
  - Added `aiu smoke --mode fixture|live [--cap USD]`.
  - Amended `runs.check_prediction`: `smoke: true` predictions may contain null metric values, and they skip the commit-time gate because fixture run dirs live under the gitignored `.runs/`.
  - Added `tests/test_smoke.py` for the five-lab fixture run, cap-above-default exit 6, live preflight exit 4 with zero calls, and smoke/null prediction handling.
  - Removed T-024 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 162 tests pass; no network calls; spend 0.00 USD.
- Smoke output (`uv run aiu smoke --mode fixture`):
  ```text
  run_id=20261024T212904Z-fixture-bfd4d2 status=completed cost_usd=0.0000
  L-003 completed cost_usd=0.0000
  run_id=20261024T212904Z-fixture-df7a64 status=completed cost_usd=0.0000
  E9 completed cost_usd=0.0000
  run_id=20261024T212904Z-fixture-cc9a61 status=completed cost_usd=0.0000
  E2 completed cost_usd=0.0000
  run_id=20261024T212904Z-fixture-e5987d status=completed cost_usd=0.0000
  E4 completed cost_usd=0.0000
  run_id=20261024T212904Z-fixture-afcad8 status=completed cost_usd=0.0000
  E5 completed cost_usd=0.0000
  smoke: fixture total_cost_usd=0.0000 cap_usd=5.00 OK
  ```
- Runs: fixture-only smoke runs under `.runs/`; removed after observation and not committed.
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: smoke predictions are machine-generated, so `smoke: true` bypasses the commit-time gate. Live smoke remains out of scope until T-036 pins models and prices.
- Next: T-025 (module checkpoint grader).

## Entry 25 - 2026-10-24 - T-025: module checkpoint grader

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Module completion needs deterministic grading before any module can be declared learner-complete.
- What I did:
  - Added `src/aiu/checkpoint.py` with `grade`, module/answers loaders, and result writing.
  - Added `aiu checkpoint grade MODULE_ID --answers PATH`.
  - Added `learner/checkpoints/.gitkeep` and a schema-valid fixture module at `tests/fixtures/module_test.yaml`.
  - Added `tests/test_checkpoint.py` covering all three item types, tolerance, missing answers, and CLI exit codes.
  - Removed T-025 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 168 tests pass; fixture module validates with 0 schema errors; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: checkpoint result files are written under `learner/checkpoints/`; T-028 will delete the temporary M-A1 result after acceptance, as the ticket specifies.
- Next: T-026 (provenance ledger check).

## Entry 26 - 2026-10-24 - T-026: provenance ledger check

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Cards cite ledger claims, and the ledger must agree with them without any model or URL fetching.
- What I did:
  - Added `src/aiu/provenance.py` with `Claim`, `parse_ledger`, and `check`.
  - Migrated `PROVENANCE.md` to the specified columns `ID | Claim | Tag | Status | Source | Date | Method | Cards`, filling the three existing card citations (A-001, B-001, C-004).
  - Updated `status._provenance_counts` to read both the new eight-column ledger and the legacy six-column fixture format.
  - Added `aiu provenance check`.
  - Added `tests/test_provenance.py` for matching data, missing claims, status mismatch, verified-row requirements, Cards mismatches, duplicate IDs, and CLI behavior.
  - Removed T-026 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 177 tests pass; `aiu provenance check` reports `OK (13 claims)`; `validate` reports 21 files and 0 errors; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: the ledger now carries explicit `Tag` and `Cards` columns. The checker validates citations and verified-row metadata only; it does not fetch sources or change any status.
- Next: T-027 (traceability check).

## Entry 27 - 2026-10-24 - T-027: traceability check

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: Card files must stay aligned with the source-to-card table, and the table must be ready for the full card set.
- What I did:
  - Added `src/aiu/traceability.py` with `Row`, `parse_rows`, `card_files`, and `check`.
  - Added `aiu traceability check [--require-all]`.
  - Supported the actual table rows (`| §...` and `| none`) plus the dash forms used for null experiments and the `E1–E13` range row.
  - Added `tests/test_traceability.py` for matching rows, source/experiment mismatches, absent cards, missing manifests, require-all behavior, and CLI output.
  - Removed T-027 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 186 tests pass; `aiu traceability check` reports `OK (79 rows, 3 cards)`; `--require-all` exits 1 with 72 missing-card problems, as expected before T-033; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: the T-027 interface text says rows start with `| P-`, but the real table uses `| §...`; the parser accepts `§`, `none`, and `P-` prefixes.
- Next: T-028 (author the 13 module YAML files).

## Entry 28 - 2026-10-24 - T-028: 13 module YAML files

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: The curriculum needs the full module layer, and M-A1 must be gradeable.
- What I did:
  - Authored `curriculum/modules/M-A1.yaml` through `M-F2.yaml` (13 files) from LAB_SPEC §7.
  - Added the required M-A1 numeric, mcq, and exact checkpoint items and `tests/fixtures/M-A1.answers.yaml`.
  - Added `tests/test_modules.py` for schema validation, one-module-per-card coverage, TRACEABILITY parity, lab manifest existence, metadata, and M-A1 grading.
  - Updated the old default-scope validation test to count all 17 curriculum files.
  - Removed T-028 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 192 tests pass; `validate curriculum/modules` reports 13 files and 0 errors; `checkpoint grade M-A1` reports 3/3; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Decisions / open questions: the temporary `learner/checkpoints/M-A1.result.json` was deleted after acceptance, as the ticket requires.
- Next: T-029 (author level-A cards A-002..A-010).

## Entry 29 - 2026-10-24 - T-029: level-A cards A-002..A-010

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: The level-A curriculum needs its remaining nine cards, with provenance and traceability intact.
- What I did:
  - Authored `curriculum/A/A-002.yaml` through `A-010.yaml` in the A-001 style.
  - Used existing claims P-002, P-003, P-004, P-006, and P-007 where they fit; appended P-013..P-018 for new claims and updated the reserved-ID note.
  - Left all cards at `status: draft`, `version: 1.0.0`.
  - Updated the default-scope validation count from 17 to 26 files.
  - Removed T-029 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 192 tests pass; `validate curriculum/A` reports 10 files and 0 errors; `provenance` reports `OK (19 claims)`; `traceability` reports `OK (79 rows, 12 cards)`; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Human review requested: the nine new draft cards need a human content review before any is marked reviewed or verified. Existing ledger `Cards` cells were not edited, per the ticket's append-only instruction; new P-013..P-018 rows list their cards.
- Next: T-030 (author level-B cards B-002..B-014).

## Entry 30 - 2026-10-24 - T-030: level-B cards B-002..B-014

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: The level-B decision-design and taxonomy cards complete the middle of the curriculum.
- What I did:
  - Authored `curriculum/B/B-002.yaml` through `B-014.yaml` (13 files) in the exemplar style.
  - Reused P-005 for B-003 and appended P-019..P-030 for the other claims; updated the reserved-ID note.
  - Set B-004 and B-005 to `experiment_id: null` with their TRACEABILITY null reasons.
  - Made B-006's `when_it_fails` state that the `≤7 labels` default is untested `[K]` and that E3 is the measurement.
  - Left every card at `status: draft`, `version: 1.0.0`.
  - Updated the default-scope validation count from 26 to 39 files.
  - Removed T-030 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 192 tests pass; `validate curriculum/B` reports 14 files and 0 errors; `provenance` reports `OK (31 claims)`; `traceability` reports `OK (79 rows, 25 cards)`; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Human review requested: the 13 new draft cards need a human content review before any is marked reviewed or verified.
- Next: T-031 (author level-C cards C-005..C-019).

## Entry 31 - 2026-10-24 - T-031: level-C cards C-001..C-019

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: The level-C evaluation and judge cards complete the measurement half of the curriculum and close the C-level traceability rows.
- What I did:
  - Authored `curriculum/C/C-001.yaml`, `C-002.yaml`, `C-003.yaml`, and `C-005.yaml` through `C-019.yaml` (18 files) in the exemplar style; `C-004.yaml` was already present.
  - Appended P-031..P-041 and P-043..P-049 for the new claims; updated the reserved-ID note. Existing rows were not edited.
  - Set C-019 to `provenance: [ADD]`, `source_section: none`, and copied its TRACEABILITY justification; set the three null-experiment cards to their TRACEABILITY reasons.
  - Wrote the 33-41 point gap in C-005 as reported in one 2026 study (sourced, unverified), and listed the section 7 failure catalog in C-018.
  - Left every card at `status: draft`, `version: 1.0.0`.
  - Updated the default-scope validation count from 39 to 57 files.
  - Removed T-031 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 192 tests pass; `validate curriculum/C` reports 19 files and 0 errors; `provenance` reports `OK (49 claims)`; `traceability` reports `OK (79 rows, 43 cards)`; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Human review requested: the 18 new draft cards need a human content review before any is marked reviewed or verified.
- Next: T-032 (author level-D and level-E cards).

## Entry 32 - 2026-10-24 - T-032: level-D and level-E cards

- Author: Maintainer (DeepSeek Flash 4.1)
- Context: The pipeline, architecture, and adaptation-ladder cards complete levels D and E and leave only level F for T-033.
- What I did:
  - Authored `curriculum/D/D-001.yaml` through `D-015.yaml` (15 files) and `curriculum/E/E-001.yaml` through `E-007.yaml` (7 files) in the exemplar style.
  - Appended P-050..P-071 for the new claims; existing rows were not edited.
  - Stated the five-steps-at-95% result in D-004 as computed arithmetic and kept its other claims unverified K.
  - Set D-012's null reason to reference `src/aiu/clients/openrouter.py`, and noted read-only-in-v1 status in E-006.
  - Set every null-experiment card to its TRACEABILITY reason and used the exact `source_section` for all 22 cards.
  - Left every card at `status: draft`, `version: 1.0.0`.
  - Updated the default-scope validation count from 57 to 79 files.
  - Removed T-032 from `known_gaps`; regenerated status.
  - No Opus calls.
- What I observed (measured): 192 tests pass; `validate curriculum/D curriculum/E` reports 22 files and 0 errors; `provenance` reports `OK (71 claims)`; `traceability` reports `OK (79 rows, 65 cards)`; spend 0.00 USD.
- Runs: none
- Spend this session (USD): 0.00
- Cumulative spend (USD): 5.290876
- Human review requested: the 22 new draft cards need a human content review before any is marked reviewed or verified.
- Next: T-033 (author level-F cards and make `traceability check --require-all` pass).
