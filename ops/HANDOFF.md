# AI University — Session Handoff

**Repo:** `C:\Users\Joe\Documents\Playground\AIUniversity`
**Remote:** https://github.com/quirps/AIUniversity.git
**Branch:** `main`
**Stage:** `building`
**Tests:** 200 passing
**Live runs:** none
**Next ticket:** **T-036** (blocked on human-supplied model IDs/prices and spend approval)
**Handoff written:** 2026-10-24, after T-035

This is the operational handoff. A fresh session should be able to continue from
this file without reading the prior conversation.

---

## 1. Current state

T-001 through T-035 are complete, committed, and pushed.

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
| Level-F cards (F-001..F-010) | Done |
| Learner guide, M-A1 walkthrough | Done |
| `aiu check-all`, repo-layout checks | Done |
| Pin models/prices, live smoke | **Next: T-036, blocked on human input** |
| Final v1 acceptance | **Not started** |
| Learner HTML workbench / DeepSeek shell | **Not started (ADR-024)** |

Current generated counts:

- Cards: 75 total, by level A=10, B=14, C=19, D=15, E=7, F=10.
- Modules: 13 authored.
- Labs: 17 manifests, 5 runnable implementations (L-003, E9, E2, E4, E5).
- Ledger: 81 claims, all `unverified`.
- Traceability: 79 rows, 75 cards; `--require-all` passes.
- `status.json` reports 3 open gaps.
- Tests: 200 passing; `status.json.tests` and the README Tests row are populated
  by `aiu check-all`.

All 75 authored cards remain `status: draft`. Human content review was
requested in JOURNAL entries 29 through 33 and has not happened yet.

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
uv run aiu check-all
```

`L-999` is the toy lab in `tests/conftest.py`. All five real runnable labs are
now implemented. `--require-all` on traceability now passes with all 75 cards.

---

## 3. Next ticket: T-036 (blocked on human input)

Read `TASKS.md` → `### T-036: Pin models and prices, recompute expected
costs, and run live smoke`.

**Do not start until the human supplies the exact OpenRouter model IDs and
prices, and approves the live spend.** Do not fabricate IDs, prices, or live
results.

Deliverables:

- Modify `config/models.yaml`, `config/pricing.yaml`, the five runnable lab
  manifests, `DECISIONS.md` (append ADR-024), `RESULTS.md`, and
  `PROVENANCE.md` (append pricing and observed-behavior rows).
- Create committed live run dirs under `experiments/<lab_id>/<run_id>/` for
  each smoke lab, including failures.

Requirements:

- `judge_a.family` must differ from `judge_b.family`; cheap_a/b/c must be three
  distinct families. Add the distinct-family test in `tests/test_config.py`.
- `pricing.yaml:retrieved_at` is the pinning date; one entry per pinned model
  ID, sourced from the OpenRouter model page.
- Runnable manifests: `expected_cost_usd` = `aiu lab estimate` value and
  `cost_basis: estimated_from_pinned_pricing`.
- Load `OPENROUTER_API_KEY` into the shell only; never write it to a file.
- One `RESULTS.md` row per live run dir with lesson
  `smoke run; no learner prediction`; append observed pricing/usage/logprob
  behavior to `PROVENANCE.md` as `unverified` or measured-for-our-setup rows.
- Add a CHANGELOG entry.

Acceptance:

```powershell
uv run aiu lab estimate E9              # no basis=assumed
uv run aiu smoke --mode live            # last line OK, total_cost_usd < 5.00
uv run aiu status --check
uv run aiu secrets-scan
uv run aiu check-all
```

If the live smoke exits 4 or 1, commit the run dirs and return the ticket as a
spec defect with a JOURNAL entry.

DoD:

- Append a JOURNAL entry with per-lab measured cost, total, and model IDs plus
  the pin date.
- Regenerate status so README spend is current.
- Commit and push.

---

## 4. Remaining path after T-036

1. **T-037** — one full live E9 learning loop (estimated $0.40).
2. **T-038** — final v1 acceptance from a clean checkout.
3. **ADR-024** — HTML workbench + lesson-scoped DeepSeek shell. Required
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
- **Existing ledger rows are append-only.** T-029 through T-033 did not add
  cards to existing `Cards` cells; only new P-013..P-041, P-043..P-049,
  P-050..P-071, and P-072..P-081 rows list their cards.
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
- T-035's ticket text names `status.json.tests.ran_at`, but
  `schemas/status.schema.json` requires `tests.at`; `check-all` writes `at`.
- T-035 added the tracked `LICENSE*` files to `REPO_LAYOUT.md` and an empty
  `register_synth("L-003")` so the runnable no-call lab passes fixture checks.
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
- **Human content review** of all 75 draft cards is outstanding.

No Opus calls should be made unless the user explicitly asks.
