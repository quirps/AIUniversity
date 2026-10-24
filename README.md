# AI University (v1)

**Repository:** https://github.com/quirps/AIUniversity
**Manager summary:** [docs/STATUS_REPORT.md](docs/STATUS_REPORT.md)

A hands-on course for working engineers on making LLM systems reliable. It covers:
- diagnosing failures;
- redesigning decisions;
- validating judges;
- building cascades;
- choosing adaptation rungs.

Every lab requires a written prediction before the run and a post-mortem after it.

See CONSTITUTION.md for audience, outcomes, and standards.

<!-- STATUS:BEGIN -->
| Metric | Value | Basis |
|---|---:|---|
| Cards written | 3 | counted |
| Modules | 0 authored / 0 manifests | counted |
| Labs runnable | 0 of 0 manifests | counted |
| Labs specified | 0 | counted |
| Claims verified | 0 | counted |
| Claims unverified | 13 | counted |
| Claims disputed | 0 | counted |
| Live runs | 0 | measured |
| Cumulative spend (USD) | 0.0000 | measured |
| Last live run | none | measured |
| Tests | not run | measured |
| Known gaps | 22 | counted |

Known gaps:
- T-017: Author all 17 lab manifests and implement `labs list` / `labs check-tiers`
- T-018: Implement dataset build and synthetic fixture framework
- T-019: Implement lab L-003 (eval statistics workbench)
- T-020: Implement lab E9 (context distractors and position)
- T-021: Implement lab E2 (schema field order)
- T-022: Implement lab E4 (escape hatch)
- T-023: Implement lab E5 (position and verbosity bias)
- T-024: Implement smoke suite with total cost cap
- T-025: Implement module checkpoint grader
- T-026: Implement provenance ledger check
- T-027: Implement traceability check
- T-028: Author the 13 module YAML files
- T-029: Author level A cards A-002..A-010
- T-030: Author level B cards B-002..B-014
- T-031: Author level C cards (18 remaining)
- T-032: Author level D and E cards
- T-033: Author level F cards and close traceability
- T-034: Write learner guide and M-A1 walkthrough
- T-035: Implement repo-layout test and `aiu check-all`
- T-036: Pin models and prices; models UNPINNED (OD-01)
- T-037: Complete module M-A1 end-to-end with a live E9 run
- T-038: Run final v1 acceptance
<!-- STATUS:END -->

## Current status

The repo contains the specification set, three drafted cards, and a working Python foundation. The curriculum harness is partial.

The architecture handoff itself cost **5.290876 USD** across 15 Opus calls. Two reasoning-only failures and seven pre-authorization rejections are logged in `ops/OPUS_RUN_LOG.md` rather than hidden.

The canonical decision register is in `DECISIONS.md` (OD-01..OD-12). All blocking decisions are resolved: $5.00 smoke cap, $2.00/run hard cap, $1.00/day soft target, and committed predictions. OD-09 (human labels) is deferred until E1, E7, or E13 becomes runnable.

## Implementation progress

- **Done:** T-001..T-016. Repository, Python 3.12 via `uv`, package and CLI, ignore rules, secrets scanner, pre-commit hooks, append-only journal check, schema validation, generated status, config/models, hardware probe, metrics, cost guard, fixture/live clients, committed-prediction gate, lab runner, and post-mortem check. 118 tests pass.
- **Working commands:** `uv run aiu --version`, `uv run aiu secrets-scan`, `uv run aiu journal check`, `uv run aiu validate`, `uv run aiu status --write|--check`, `uv run aiu hwcheck --json`.
- **Next:** T-017 (author lab manifests, starting with E9).
- `status.json` and the STATUS block are generated. Run `uv run aiu status --write` after state changes; `--check` detects drift.

## Quickstart

Bootstrap (already run on this machine):

```powershell
./ops/bootstrap.ps1
uv run aiu --version        # aiu 0.1.0
uv run aiu secrets-scan     # secrets-scan: 0 findings
uv run aiu journal check    # journal: append-only OK
uv run aiu validate         # validate: 4 files, 0 errors
```

Planned, not yet working:

```powershell
uv run aiu labs list
```

## What works

- Reading the specs:
  - CONSTITUTION.md
  - REPO_LAYOUT.md
  - GOVERNANCE.md
  - TASKS.md
  - ACCEPTANCE.md
  - LAB_SPEC.md
- Reading the 3 drafted cards. Their claims are **unverified** (see PROVENANCE.md).
- Python 3.12 via `uv`; `aiu --version`; `aiu secrets-scan`; `aiu journal check`; `aiu validate`.
- Pre-commit hooks for secrets and journal append-only checks.

## What does not work yet

- Status generation (T-007)
- Cost guard and clients (T-011-T-013)
- All labs (T-015-T-023)
- Smoke suite (T-024)
- Checkpoints (T-025)
- Provenance and traceability checks (T-026, T-027)
- Modules and remaining cards (T-028-T-033)
- Learner guide (T-034)
- Live runs (T-036, T-037)
- Acceptance (T-038)

## Links

- Manager status report: [docs/STATUS_REPORT.md](docs/STATUS_REPORT.md)
- Decisions: [DECISIONS.md](DECISIONS.md)
- Journal: [JOURNAL.md](JOURNAL.md)
- Claim ledger: [PROVENANCE.md](PROVENANCE.md)
- Run index: [RESULTS.md](RESULTS.md) (empty)
- Changes: [CHANGELOG.md](CHANGELOG.md)
- Learnings: [docs/learnings/](docs/learnings/)
- Architecture call log: [ops/OPUS_RUN_LOG.md](ops/OPUS_RUN_LOG.md)
- Session handoff: [ops/HANDOFF.md](ops/HANDOFF.md)
- Next-session prompt: [ops/NEXT_SESSION_PROMPT.md](ops/NEXT_SESSION_PROMPT.md)
