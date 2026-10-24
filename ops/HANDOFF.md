# AI University — Session Handoff

**Repo:** `C:\Users\Joe\Documents\Playground\AIUniversity`
**Remote:** https://github.com/quirps/AIUniversity.git
**Branch:** `main`
**Stage:** `building`
**Tests:** 192 passing
**Live runs:** none
**Next ticket:** **T-033**
**Handoff written:** 2026-10-24, after T-032

This is the operational handoff. A fresh session should be able to continue from
this file without reading the prior conversation.

---

## 1. Current state

T-001 through T-032 are complete, committed, and pushed.

| Area | State |
|---|---|
| Repository, licenses, source PDF | Done |
| Python 3.12 via `uv`, CLI | Done |
| Secrets scan, journal check, pre-commit hooks | Done |
| JSON Schema validation | Done |
| Generated `status.json` + README status block | Done |
| Config, pricing, caps, Pydantic models | Done |
| Hardware probe and tier checks | Done |
| Metrics library | Done |
| Cost estimator and guard | Done |
| Fixture and OpenRouter clients | Done |
| Run IDs, `lab new-run`, committed-prediction gate | Done |
| Lab registry, runner, estimator | Done |
| Post-mortem check | Done |
| 17 lab manifests, `labs list`, `labs check-tiers` | Done |
| Dataset build + synthetic fixture framework | Done |
| L-003, E9, E2, E4, E5 datasets and implementations | Done |
| Fixture smoke suite + total cap | Done |
| Module checkpoint grader | Done |
| Provenance and traceability checks | Done |
| 13 module YAML files | Done |
| Level-A cards (A-001..A-010) | Done |
| Level-B cards (B-001..B-014) | Done |
| Level-C cards (C-001..C-019) | Done |
| Level-D/E cards (D-001..D-015, E-001..E-007) | Done |
| Level-F cards | **In progress: T-033** |
| Learner guide, M-A1 walkthrough, final acceptance | **Not started** |
| Learner HTML workbench / DeepSeek shell | **Not started (ADR-024)** |

Current generated counts:

- Cards: 65 total, by level A=10, B=14, C=19, D=15, E=7, F=0.
- Modules: 13 authored.
- Labs: 17 manifests, 5 runnable implementations (L-003, E9, E2, E4, E5).
- Ledger: 71 claims, all `unverified`.
- Traceability: 79 rows, 65 cards.
- `status.json` reports 6 open gaps.

All 65 authored cards remain `status: draft`. Human content review was
requested in JOURNAL entries 29 through 32 and has not happened yet.

---

## 2. Working commands

Run from the repo root. On this machine `uv` lives at
`%USERPROFILE%\.local\bin\uv.exe`; the pre-commit hook adds that directory to
PATH. If `uv` is not on PATH, use the full path.

```powershell
uv run pytest
uv run aiu --version
uv run aiu validate
uv run aiu status --write
uv run aiu status --check
uv run aiu secrets-scan
uv run aiu journal check
uv run aiu hwcheck --json

uv run aiu labs list
uv run aiu labs check-tiers
uv run aiu labs check-tiers tests/fixtures/invalid_lab_local_bad_fallback.yaml

uv run aiu dataset build <LAB_ID> [--check]
uv run aiu fixtures synth <LAB_ID> [--check]

uv run aiu lab new-run <LAB_ID> --mode fixture
uv run aiu lab estimate <LAB_ID>
uv run aiu lab run <LAB_ID> --run-id <id> --mode fixture [--limit N]
uv run aiu lab postmortem-check <LAB_ID> --run-id <id>

uv run aiu smoke --mode fixture
uv run aiu smoke --mode fixture --cap 6
uv run aiu checkpoint grade M-A1 --answers tests/fixtures/M-A1.answers.yaml
uv run aiu provenance check
uv run aiu traceability check
uv run aiu traceability check --require-all
```

`L-999` is the toy lab in `tests/conftest.py`. All five real runnable labs are
now implemented. `--require-all` on traceability is expected to fail until
T-033 authors the remaining F cards.

---

## 3. Next ticket: T-033

Read `TASKS.md` → `### T-033: Author level F cards and close traceability`.

Deliverables:

- `curriculum/F/F-001.yaml` through `F-010.yaml` (10 files).
- Append ledger rows only for new claims; do not rewrite existing rows.

Ticket-specific requirements:

- The rules of T-029 apply: source section and experiment from TRACEABILITY,
  every S/K claim gets an `unverified` verify item, cards stay `status: draft`,
  `version: 1.0.0`.
- `F-007` `when_it_fails` and `why_it_matters` reference the measured
  dev-machine profile: GTX 1060 6 GB, Pascal, no tensor cores, no bf16. Use it
  to illustrate memory-bandwidth-bound decoding without requiring any run.
- `F-010` states that local nanochat training is out of scope per the
  local-model policy.
- Use the next free ledger IDs from `P-072` onward.

Acceptance:

```powershell
uv run aiu validate curriculum                  # 88 files, 0 errors
uv run aiu traceability check --require-all     # exit 0
uv run aiu provenance check
uv run pytest tests/test_modules.py
```

DoD:

- Request human content review in the JOURNAL.
- Remove T-033 from `status.json.known_gaps`.
- `uv run aiu status --write` and `uv run aiu status --check`.
- Commit and push.

When adding cards, also update the hardcoded file count in
`tests/test_validate.py::test_default_scope_counts_all_curriculum_files`.
It is currently 79 (65 cards + 13 modules + 1 trust table); after T-033 it
should be 89 (75 cards + 13 modules + 1 trust table).

---

## 4. Remaining path after T-033

1. **T-034** — learner guide + M-A1 walkthrough in `docs/LEARNER_GUIDE.md`.
2. **T-035** — `aiu check-all` and repo-layout checks.
3. **T-036** — human supplies model IDs and prices; pin `config/models.yaml`
   and `config/pricing.yaml`; recompute manifest costs; live smoke under $5.
4. **T-037** — one full live E9 learning loop (estimated $0.40).
5. **T-038** — final v1 acceptance from a clean checkout.
6. **ADR-024** — HTML workbench + lesson-scoped DeepSeek shell. Required
   before M-A1 is learner-complete.

T-036 needs human input for OD-01 and spend approval for OD-02. Do not
fabricate model IDs, prices, or live results.

---

## 5. Project rules that are easy to get wrong

- **Append-only JOURNAL.** Never edit an old entry. The pre-commit hook
  enforces the prefix check.
- **Generated state.** Remove the completed ticket from
  `status.json.known_gaps`, then run `status --write`, then `status --check`.
  Do not hand-edit the README STATUS block.
- **Use `uv run`.** System Python is 3.7.4; the project uses Python 3.12.
- **No secrets in the repo.** Use `OPENROUTER_API_KEY` from the environment.
  The hook runs `aiu secrets-scan --staged`.
- **No network in tests.** `pytest-socket` is active; use
  `httpx.MockTransport`.
- **API-only v1.** No local models or GPU training.
- **Roles are still `UNPINNED`.** Live mode exits 6 until T-036 pins IDs and
  prices. Fixture mode uses `config/pricing.yaml` fixture defaults.
- **Caps:** $2.00 per lab run, $5.00 smoke suite, $1.00/day soft target.
  Do not raise without a DECISIONS entry.
- **Prediction gate (normal runs):** prediction must be committed;
  `written_at <= commit time < run start`. `runs.py` accepts string or YAML
  datetime.
- **Prediction gate (smoke):** `smoke: true` predictions may contain null
  metric values and skip the commit-time gate, because fixture run dirs live
  under the gitignored `.runs/`. This amendment was required by T-024.
- **Fixtures:** `fixture_recorded` hash mismatch is an error;
  `fixture_synthetic` ignores the hash. Fixture runs report
  `actual_usd: 0.0`.
- **Fixture vs live dirs:** fixture runs go to `.runs/` and are never
  committed. Live runs go to `experiments/<lab>/<run_id>/` and are write-once.
- **Smoke output:** fixture smoke writes
  `.runs/smoke-<stamp>.json` and removes nothing automatically. Live smoke
  runs must be indexed in `RESULTS.md` with
  `smoke run; no learner prediction`.
- **Post-mortem:** five required headings and front-matter
  `trust_table_row` are enforced by `src/aiu/postmortem.py`.
- **`--record`** is live-only and overwrites the lab fixture file.
- **Ledger format:** `PROVENANCE.md` now has eight columns:
  `ID | Claim | Tag | Status | Source | Date | Method | Cards`.
  `status.py` supports both this and the old six-column test fixture.
- **Traceability rows** start with `| §`, `| none`, or `| P-`; the T-027
  ticket text incorrectly said only `| P-` and `| none`.
- **Existing ledger rows are append-only.** T-029 through T-032 did not add
  cards to existing `Cards` cells; only new P-013..P-041, P-043..P-049, and
  P-050..P-071 rows list their cards.
- **Human review.** Do not mark cards `reviewed` or `verified`; only a human
  reviewer may do that.
- **Windows/PowerShell.** Quote paths with spaces. Use `git` and `uv` as
  shown.

### Known spec discrepancies already handled

- T-019's table lists kappa `0.6732` and corrected fail rate `0.1504`, but
  the fixed counts plus `aiu.metrics` produce `0.646643` and `0.1500`.
  `tests/test_lab_l003.py` asserts the recomputed values.
- T-019's literal root-repo fixture sequence cannot pass the commit gate
  because `.runs/` is gitignored. The equivalent run passes in a temporary
  git repo via `tests/helpers.py::run_fixture`.
- T-024 required smoke predictions to bypass the commit gate for the same
  reason.
- T-027's row-prefix description was wrong; see above.
- Lab expected costs remain `assumed` in manifests until T-036.

---

## 6. Key files

| File | Why |
|---|---|
| `TASKS.md` | Authoritative ticket list and acceptance tests |
| `LAB_SPEC.md` | Lab index, specs, metrics, modules, cost basis |
| `schemas/curriculum.schema.json` | Strict schema for cards, modules, labs |
| `DECISIONS.md` | ADRs and canonical OD register |
| `JOURNAL.md` | Append-only history; read latest 2–3 entries |
| `status.json` | Current generated state |
| `PROVENANCE.md` | Claim ledger (8-column format) |
| `TRACEABILITY.md` | Source → card → experiment table |
| `src/aiu/cli.py` | All CLI commands |
| `src/aiu/runner.py` | Runner algorithm, estimates, exit mapping |
| `src/aiu/runs.py` | Run IDs, prediction gate, freezing |
| `src/aiu/postmortem.py` | Post-mortem checks |
| `src/aiu/checkpoint.py` | Module checkpoint grading |
| `src/aiu/provenance.py` | Ledger parser and checker |
| `src/aiu/traceability.py` | Traceability parser and checker |
| `src/aiu/smoke.py` | Smoke suite and summary artifact |
| `src/aiu/labs/base.py` | Lab registry and dynamic `load_lab` |
| `src/aiu/labs/tiers.py` | Lab inventory and tier checks |
| `src/aiu/generators/base.py` | Generator registry, serialization, build |
| `src/aiu/fixtures_synth.py` | Synthetic fixture registry and normalization |
| `src/aiu/labs/l003.py`, `e9.py`, `e2.py`, `e4.py`, `e5.py` | Runnable lab implementations |
| `curriculum/modules/` | 13 module YAML files |
| `curriculum/A/`, `curriculum/B/`, `curriculum/C/` | Authored cards |
| `tests/helpers.py` | Temporary-repo fixture runner |
| `tests/conftest.py` | Toy lab L-999 registration |
| `ops/NEXT_SESSION_PROMPT.md` | Paste-ready prompt for a fresh session |

---

## 7. Open decisions / clarifications

- **OD-01:** model IDs and prices are intentionally unpinned until T-036.
- **OD-02:** live spend approval is still needed for T-036/T-037.
- **OD-09:** human-labeled datasets for E1/E7/E13 are deferred until those
  labs become runnable.
- **ADR-024 UI clarification:** before the workbench starts, decide whether
  the lesson shell is a chat REPL, a sandboxed terminal, or both; whether it
  uses DeepSeek through OpenRouter or the direct API; and what it may touch.
- **Human content review** of all 65 draft cards is outstanding.

No Opus calls should be made unless the user explicitly asks.
