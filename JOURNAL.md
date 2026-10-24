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
