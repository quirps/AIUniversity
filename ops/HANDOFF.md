# AI University — Session Handoff

**Repo:** `C:\Users\Joe\Documents\Playground\AIUniversity`
**Remote:** https://github.com/quirps/AIUniversity.git
**Branch:** `main`
**Stage:** `v1-accepted`
**Tests:** 213 passing
**Live runs:** 15 completed
**Next work:** **ADR-024 workbench polish + human card review** (no T-ticket remains)
**Handoff written:** 2026-10-25, after the ADR-024 first slice

This is the operational handoff. A fresh session should be able to continue from
this file without reading the prior conversation.

---

## 1. Current state

T-001 through T-038 are complete, committed, and pushed. v1.0.0 is tagged.

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
| Live E9 learning loop | Done (T-037) |
| Final v1 acceptance | Done (T-038, tag `v1.0.0`) |
| Learner HTML workbench / DeepSeek shell | First slice done (ADR-026); polish pending |

Current generated counts:

- Cards: 75 total, by level A=10, B=14, C=19, D=15, E=7, F=10.
- Modules: 13 authored.
- Labs: 17 manifests, 5 runnable implementations (L-003, E9, E2, E4, E5).
- Ledger: 84 claims, all `unverified`.
- Traceability: 79 rows, 75 cards; `--require-all` passes.
- `status.json` reports 0 open gaps and stage `v1-accepted`.
- Tests: 213 passing.
- ADR-024 first slice: `aiu workbench serve M-A1` and
  `aiu workbench render M-A1 --out <path>` exist. The local page shows cards,
  latest live runs, metrics, prediction, post-mortem, trust rows, a checkpoint
  form, and a lesson-scoped DeepSeek chat. ADR-026 records the shell scope:
  direct DeepSeek, no tools, no arbitrary file access.
- v1 acceptance: AC-01..AC-20 pass in a clean clone with no provider keys.
  Commit under test `a51df3e`; final release tag `v1.0.0`.
- The clean-clone failure was a CRLF/LF mismatch in generated JSONL; `.gitattributes`
  now forces LF and AC-19 passes.
- Live runs: 15 completed; lab-run spend $0.1704. T-037 is the full E9
  learning run at $0.0645; the usable smoke suite cost $0.0302. Two earlier
  smoke attempts ran with DeepSeek thinking mode enabled and produced degenerate
  short-answer metrics; their run dirs are committed and marked in `RESULTS.md`.
- T-037 outcome: oracle 0.7833, max_drop 0.1833, hypothesis supported, validity
  check failed because oracle < 0.80. Every miss was a partial answer, so the
  accuracy drop is confounded with exact-match formatting.

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
uv run aiu workbench serve M-A1
uv run aiu workbench render M-A1 --out docs/workbench-M-A1.html
```

`L-999` is the toy lab in `tests/conftest.py`. All five real runnable labs are
now implemented. `--require-all` on traceability now passes with all 75 cards.

---

## 3. Next work: ADR-024 workbench polish + human card review

No T-ticket remains. The ADR-024 first slice is implemented:

- `uv run aiu workbench serve M-A1` serves a local page at
  `http://127.0.0.1:8765/`; `render` writes a static HTML file.
- The page renders module YAML, cards, latest live runs, metrics, prediction,
  post-mortem, trust rows, the checkpoint form, and the lesson shell.
- ADR-026 records the shell scope: chat REPL, DeepSeek direct, lesson context
  only, no tools or arbitrary file access.

Remaining ADR-024 work:

- Human UI/content pass: layout, accessibility, and whether the page needs
  in-page prediction/post-mortem authoring or trust-table editing. The first
  slice displays these artifacts but keeps authoring in the CLI/markdown flow.
- Decide whether the workbench needs a static export path in the repo or only
  the local server.
- Review the M-A1 cards and content for learner-completeness.

Other tracked post-v1 work:

- Draft card review queue: `docs/DRAFT_CARD_REVIEW.md` (75 links). Review M-A1
  cards first; all-card review is required before claiming verified content.
- `strong` role requirements: `docs/STRONG_ROLE.md`. It needs an exact model ID,
  family, provider, price, and key before it can be pinned.

---

## 4. Remaining path after v1

1. **ADR-024 polish** — human UI/content pass and any in-page authoring the
   owner wants.
2. **Human card review** — 75 draft cards, M-A1 first.
3. **`strong` pin** — optional until E7/E10/E12 live work; needs an exact
   frontier model ID and price.

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
- T-037 added `learner/checkpoints/M-A1.answers.yaml`, which is not a curriculum
  schema document. `validate.py` now skips paths containing `checkpoints` so
  `uv run aiu validate learner` still validates only the trust table.
- T-037's E9 validity check failed because exact-match scoring treated partial
  answer phrases as misses. The learning note records this as a measurement
  confound; do not present the E9 drop as a wrong-entity result.
- T-038 found a Windows clean-clone failure: Git's `core.autocrlf` rewrote JSONL
  files to CRLF, so dataset/fixture byte checks and five tests failed. A
  `.gitattributes` rule now forces LF for `*.jsonl`; AC-19 passes.
- T-038 rewrote ACCEPTANCE.md because the original architecture-era commands and
  artifacts (`scan-secrets`, `journal-check --history`, `source-check`,
  `run.json`, and others) did not match the implemented v1 surface. The rewritten
  ACs cover the actual CLI and gates; this is recorded as a spec reconciliation,
  not a waived failure.
- The final version commit is `v1.0.0`; `src/aiu/__init__.py`, `pyproject.toml`,
  `uv.lock`, status.json, and CHANGELOG agree.

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
| `src/aiu/workbench.py` | ADR-024 local workbench and lesson shell |
| `src/aiu/labs/l003.py`, `e9.py`, `e2.py`, `e4.py`, `e5.py` | Runnable lab implementations |
| `curriculum/modules/` | 13 module YAML files |
| `curriculum/A/` through `curriculum/F/` | Authored cards |
| `docs/LEARNER_GUIDE.md` | Learner path through M-A1 |
| `docs/WORKBENCH.md` | Workbench usage and shell scope |
| `docs/DRAFT_CARD_REVIEW.md` | 75-card review queue with links |
| `docs/STRONG_ROLE.md` | Strong-role requirements |
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
- **ADR-024 UI clarification:** resolved by ADR-026 for the first slice: chat
  REPL, DeepSeek direct, lesson context only, no tools or arbitrary file access.
  Remaining: human UI/content pass and any in-page authoring the owner wants.
- **Human content review** of all 75 draft cards is outstanding; see
  `docs/DRAFT_CARD_REVIEW.md` and review the M-A1 cards first.
- **`strong`:** still `UNPINNED`; see `docs/STRONG_ROLE.md`.

No Opus calls should be made unless the user explicitly asks.
