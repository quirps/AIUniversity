# AI University — Session Handoff

**Repo:** `C:\Users\Joe\Documents\Playground\AIUniversity`
**Remote:** https://github.com/quirps/AIUniversity.git
**Branch:** `main`
**Stage:** `building`
**Tests:** 205 passing
**Live runs:** 14 completed
**Next ticket:** **T-037** (human prediction/post-mortem or explicit delegation needed)
**Handoff written:** 2026-10-24, after T-036

This is the operational handoff. A fresh session should be able to continue from
this file without reading the prior conversation.

---

## 1. Current state

T-001 through T-036 are complete, committed, and pushed.

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
| Pin models/prices, live smoke | Done (ADR-025) |
| Live E9 learning loop | **Next: T-037** |
| Final v1 acceptance | **Not started** |
| Learner HTML workbench / DeepSeek shell | **Not started (ADR-024)** |

Current generated counts:

- Cards: 75 total, by level A=10, B=14, C=19, D=15, E=7, F=10.
- Modules: 13 authored.
- Labs: 17 manifests, 5 runnable implementations (L-003, E9, E2, E4, E5).
- Ledger: 84 claims, all `unverified`.
- Traceability: 79 rows, 75 cards; `--require-all` passes.
- `status.json` reports 2 open gaps.
- Tests: 205 passing.
- Live runs: 14 completed; lab-run spend $0.1058. The usable smoke suite cost
  $0.0302. Two earlier smoke attempts ran with DeepSeek thinking mode enabled
  and produced degenerate short-answer metrics; their run dirs are committed and
  marked in `RESULTS.md`.

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
uv run aiu smoke --mode live
uv run aiu checkpoint grade M-A1 --answers tests/fixtures/M-A1.answers.yaml
uv run aiu provenance check
uv run aiu traceability check
uv run aiu traceability check --require-all
uv run aiu check-all
```

`L-999` is the toy lab in `tests/conftest.py`. All five real runnable labs are
now implemented. `--require-all` on traceability now passes with all 75 cards.

---

## 3. Next ticket: T-037

Read `TASKS.md` → `### T-037: Complete module M-A1 end-to-end with a live E9
run`.

This ticket needs a learner-authored prediction and post-mortem, or an explicit
human delegation recorded in the JOURNAL. Do not invent the learner's prediction
or post-mortem content.

Deliverables:

- Create `experiments/E9/<run_id>/` with all eight artifacts and a filled
  `postmortem.md`.
- Create `learner/portfolio/M-A1/README.md`,
  `learner/checkpoints/M-A1.answers.yaml`,
  `learner/checkpoints/M-A1.result.json`, and
  `docs/learnings/YYYY-MM-DD-e9-context-distractors.md`.
- Modify `learner/trust_table.yaml` (one row for A-008 or A-001), `RESULTS.md`,
  and `CHANGELOG.md`.

Requirements:

- Follow `docs/LEARNER_GUIDE.md` → Module M-A1 walkthrough verbatim.
- The trust row follows the `trust_row` schema. Set `my_replication` from
  `result.json.hypothesis_supported`: true → `replicated`, false →
  `failed_to_replicate`, null → `inconclusive`; `run_ids` holds `[<run_id>]`.
- The learning write-up follows `docs/learnings/_template.md`; every number
  links to `experiments/E9/<run_id>/metrics.json` and `cost.json`.
- Log negative or inconclusive outcomes exactly as observed.

Acceptance:

```powershell
uv run aiu lab postmortem-check E9 --run-id <run_id>      # postmortem: OK
uv run aiu checkpoint grade M-A1 --answers learner/checkpoints/M-A1.answers.yaml
uv run aiu validate learner
uv run aiu status --check
uv run python -c "import json;assert json.load(open('experiments/E9/<run_id>/result.json'))['evidence_class']=='measured'"
```

E9 full-run estimate: $0.1021. The per-lab cap is $2.00 and the daily soft
target is $1.00.

DoD:

- Append a JOURNAL entry with the measured cost.
- Add the RESULTS row and CHANGELOG entry.
- Regenerate status; `aiu check-all` exits 0.
- Commit and push.

---

## 4. Remaining path after T-037

1. **T-038** — final v1 acceptance from a clean checkout.
2. **ADR-024** — HTML workbench + lesson-scoped DeepSeek shell. Required
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
- **No secrets in the repo.** Use `OPENROUTER_API_KEY` for OpenRouter roles and
  `DEEPSEEK_API_KEY` for DeepSeek roles from the environment. The hook runs
  `aiu secrets-scan --staged`.
- **No network in tests.** `pytest-socket` is active; use
  `httpx.MockTransport`.
- **API-only v1.** No local models or GPU training.
- **Roles:** `cheap_a`/`judge_a` are DeepSeek direct (`deepseek-flash`);
  `cheap_b`/`judge_b` are OpenRouter `google/gemini-2.5-flash`; `cheap_c` is
  OpenRouter `qwen/qwen3.7-flash`; `strong` remains `UNPINNED`. Live mode exits
  6 for an unpinned role or a missing provider key. Fixture mode uses
  `config/pricing.yaml` fixture defaults.
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
- **Smoke output:** smoke writes `.runs/smoke-<stamp>.json` for both modes and
  removes nothing automatically. Live smoke runs must be indexed in
  `RESULTS.md` with `smoke run; no learner prediction`.
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
  P-050..P-071, and P-072..P-081 rows list their cards. T-036 appended the
  operational rows P-082..P-084 with no cards.
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
- T-036's ticket text says "append ADR-024", but ADR-024 already covers the
  learner workbench; the provider/pin decision is ADR-025.
- T-036 changed the live smoke summary path from `experiments/` to `.runs/` so
  `experiments/` contains only `_template` and live lab run directories.
- DeepSeek thinking mode is enabled by default. The DeepSeek client disables it
  for these short-answer labs; enabling it made max_tokens-limited runs return
  empty content.
- The first two T-036 smoke attempts are committed with degenerate metrics;
  `RESULTS.md` labels them. The usable suite is the third attempt.
- `strong` is deliberately still `UNPINNED`; the OpenRouter-pinned roles were
  not exercised live because no OpenRouter key was available.

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
| `src/aiu/clients/base.py` | Client protocol |
| `src/aiu/clients/deepseek.py` | DeepSeek direct client (thinking disabled) |
| `src/aiu/clients/live.py` | Per-role provider router |
| `src/aiu/clients/openrouter.py` | OpenRouter client |
| `src/aiu/checkall.py` | Offline check runner and test recording |
| `src/aiu/labs/l003.py`, `e9.py`, `e2.py`, `e4.py`, `e5.py` | Runnable lab implementations |
| `curriculum/modules/` | 13 module YAML files |
| `curriculum/A/` through `curriculum/F/` | Authored cards |
| `docs/LEARNER_GUIDE.md` | Learner path through M-A1 |
| `tests/helpers.py` | Temporary-repo fixture runner |
| `tests/conftest.py` | Toy lab L-999 registration |
| `ops/NEXT_SESSION_PROMPT.md` | Paste-ready prompt for a fresh session |

---

## 7. Open decisions / clarifications

- **OD-01:** the smoke set is pinned (ADR-025); `strong` remains `UNPINNED`
  until a later decision. OpenRouter roles are pinned but were not exercised
  live in T-036.
- **OD-02:** smoke cap is $5.00 and resolved; T-036 measured $0.0302 for the
  usable suite. T-037's full E9 estimate is $0.1021, within the $2.00 per-lab
  cap and the $1.00 daily soft target.
- **OD-09:** human-labeled datasets for E1/E7/E13 are deferred until those
  labs become runnable.
- **ADR-024 UI clarification:** before the workbench starts, decide whether
  the lesson shell is a chat REPL, a sandboxed terminal, or both; whether it
  uses DeepSeek through OpenRouter or the direct API; and what it may touch.
- **Human content review** of all 75 draft cards is outstanding.

No Opus calls should be made unless the user explicitly asks.
