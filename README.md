# AI University (v1)

**Repository:** https://github.com/quirps/AIUniversity
**Manager summary:** [docs/STATUS_REPORT.md](docs/STATUS_REPORT.md)
**Definition of done:** [ACCEPTANCE.md](ACCEPTANCE.md)

A hands-on course for working engineers on making LLM systems reliable. It covers:
- diagnosing failures;
- redesigning decisions;
- validating judges;
- building cascades;
- choosing adaptation rungs.

Every live lab requires a written prediction before the run and a post-mortem after it.
The CLI harness is the source of truth for runs, metrics, costs, and artifacts.

See CONSTITUTION.md for audience, outcomes, and standards.

<!-- STATUS:BEGIN -->
| Metric | Value | Basis |
|---|---:|---|
| Cards written | 75 | counted |
| Modules | 13 authored / 13 manifests | counted |
| Labs runnable | 5 of 17 manifests | counted |
| Labs specified | 12 | counted |
| Claims verified | 0 | counted |
| Claims unverified | 84 | counted |
| Claims disputed | 0 | counted |
| Live runs | 15 | measured |
| Cumulative spend (USD) | 0.1704 | measured |
| Last live run | 20261025T001745Z-live-b1c296 | measured |
| Tests | 213 passed / 0 failed (at 2026-10-25T01:27:04Z) | measured |
| Known gaps | 0 | counted |

Known gaps:
- none
<!-- STATUS:END -->

## Current status

The v1 curriculum, harness, learner guide, model pin, and first measured learning
loop are in place. The generated status block above is the authoritative
snapshot; `status.json` is the machine-readable form.

- **Done:** T-001..T-037. Curriculum content is 75 draft cards and 13 modules;
  all 17 lab manifests validate; five labs run in fixture mode; the live smoke
  suite and the E9 learning loop have committed, measured run directories.
- **Gate:** `uv run aiu check-all` runs the offline checks and the full test
  suite. Current result: **19/19 checks OK**, 206 tests passing, 0 failed.
- **Model pin:** `cheap_a`/`judge_a` use DeepSeek direct (`deepseek-flash`);
  `cheap_b`/`judge_b` use OpenRouter `google/gemini-2.5-flash`; `cheap_c` uses
  OpenRouter `qwen/qwen3.7-flash`; `strong` is still `UNPINNED`.
- **First learning loop:** E9 live run `20261025T001745Z-live-b1c296`, actual
  cost $0.0645. Oracle accuracy was 0.7833 and `max_drop` was 0.1833; every miss
  was a partial answer, so the result is logged with that measurement caveat.

### v1 acceptance

AC-01..AC-20 passed in a clean clone with no provider keys on the measured
Windows 10 machine. The full evidence, hardware summary, and limitations are in
[docs/learnings/2026-10-25-v1-acceptance.md](docs/learnings/2026-10-25-v1-acceptance.md).
The release tag is `v1.0.0`.

| AC | Result | Scope |
|---|---|---|
| AC-01 | PASS | Python 3.12 via uv |
| AC-02 | PASS | Locked dependencies |
| AC-03 | PASS | Zero-network pytest |
| AC-04 | PASS | Schema validation |
| AC-05 | PASS | Secrets and hooks |
| AC-06 | PASS | Append-only journal |
| AC-07 | PASS | status/README consistency |
| AC-08 | PASS | Provenance ledger |
| AC-09 | PASS | Traceability |
| AC-10 | PASS | Hardware tiers and fallbacks |
| AC-11 | PASS | Offline hardware check |
| AC-12 | PASS | Cost caps and estimate |
| AC-13 | PASS | Fixture/live separation |
| AC-14 | PASS | Source files and traceability |
| AC-15 | PASS | Transparency artifacts |
| AC-16 | PASS | README bounded by ACCEPTANCE |
| AC-17 | PASS | Assessment structure |
| AC-18 | PASS | Live run logging |
| AC-19 | PASS | Clean-checkout reproduction |
| AC-20 | PASS | Final gate |

## What works

- **Curriculum:** 75 cards (levels A-F), 13 modules, and 17 lab manifests
  validate against the schema. [AC-04]
- **Offline harness:** `aiu validate`, `aiu secrets-scan`, `aiu journal check`,
  `aiu status --write|--check`, `aiu hwcheck`, `aiu labs list`,
  `aiu labs check-tiers`, `aiu provenance check`, and
  `aiu traceability check --require-all`. [AC-05..AC-10]
- **Labs and fixtures:** dataset build and fixture synthesis for E2, E4, E5, E9,
  and L-003; fixture smoke suite. [AC-12, AC-13]
- **Live runs:** 15 committed live run directories with prediction, post-mortem,
  metrics, result, and cost artifacts; the usable smoke suite and the full E9
  learning loop. [AC-18]
- **Learner path:** `docs/LEARNER_GUIDE.md`, the M-A1 checkpoint (3/3), the
  M-A1 portfolio note, and the E9 learning write-up. [AC-15, AC-16]
- **Workbench (ADR-024 first slice, post-v1):** `uv run aiu workbench serve M-A1`
  serves a local lesson page with cards, latest run artifacts, trust rows, the
  checkpoint form, and a lesson-scoped DeepSeek shell. See
  [docs/WORKBENCH.md](docs/WORKBENCH.md).
- **Generated state:** `status.json` and the README STATUS block are consistent;
  `aiu check-all` records the pytest result. [AC-07, AC-20]

## Planned / not yet verified

- **ADR-024 workbench polish:** the first local workbench slice exists (ADR-026),
  but a human pass on layout, content, and shell boundaries is still needed
  before M-A1 is called learner-complete in the UI sense.
- **Draft card review:** all 75 cards are still `draft`; the review queue and
  links are in [docs/DRAFT_CARD_REVIEW.md](docs/DRAFT_CARD_REVIEW.md).
- **`strong` role:** still `UNPINNED`; requirements and the current DeepSeek
  candidate are in [docs/STRONG_ROLE.md](docs/STRONG_ROLE.md).
- **Unimplemented labs:** E1, E3, E6, E7, E8, E10, E11, E12, E13, L-001, L-002,
  and L-004 are specified but not runnable in v1.
- **Local tiers:** local GPU/CPU tiers have API fallbacks only. Local inference
  at the ~3B Q4 ceiling and local training have not been verified; v1 is API-only.
- **Human content review:** all 75 cards are still `draft`; 0 claims are
  `verified`. Only a human reviewer may change those statuses.
- **OpenRouter live roles:** the OpenRouter-pinned roles were not exercised live
  in T-036 because no OpenRouter key was available.
- **E9 scoring:** the first E9 run's partial-answer scoring issue is recorded in
  the post-mortem and learning note; it is not yet fixed.

## Quickstart

```powershell
./ops/bootstrap.ps1
uv run aiu --version
uv run aiu secrets-scan
uv run aiu journal check
uv run aiu validate
uv run aiu labs list
uv run aiu check-all
uv run aiu workbench serve M-A1
```

Live mode needs the relevant provider key in the shell:
`DEEPSEEK_API_KEY` for the DeepSeek roles and `OPENROUTER_API_KEY` for the
OpenRouter roles. Never commit either key.

## Links

- Definition of done: [ACCEPTANCE.md](ACCEPTANCE.md)
- Manager status report: [docs/STATUS_REPORT.md](docs/STATUS_REPORT.md)
- Decisions: [DECISIONS.md](DECISIONS.md)
- Journal: [JOURNAL.md](JOURNAL.md)
- Claim ledger: [PROVENANCE.md](PROVENANCE.md)
- Run index: [RESULTS.md](RESULTS.md)
- Changes: [CHANGELOG.md](CHANGELOG.md)
- Learnings: [docs/learnings/](docs/learnings/)
- Learner guide: [docs/LEARNER_GUIDE.md](docs/LEARNER_GUIDE.md)
- Workbench: [docs/WORKBENCH.md](docs/WORKBENCH.md)
- Draft card review queue: [docs/DRAFT_CARD_REVIEW.md](docs/DRAFT_CARD_REVIEW.md)
- Strong role: [docs/STRONG_ROLE.md](docs/STRONG_ROLE.md)
- Session handoff: [ops/HANDOFF.md](ops/HANDOFF.md)
- Next-session prompt: [ops/NEXT_SESSION_PROMPT.md](ops/NEXT_SESSION_PROMPT.md)
