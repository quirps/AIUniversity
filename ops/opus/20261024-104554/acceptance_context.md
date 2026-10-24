This is part 2a of the continuation. Emit ONLY these two files, in this order:

1. ## FILE: T-038.fragment.md - a complete replacement for T-038, starting with ### T-038: Run final v1 acceptance and ending with its **Open decisions:** line. Do not include T-037 or a trailing separator.
2. ## FILE: ACCEPTANCE.md - AC-01 through AC-20. For each: ID, requirement, exact runnable command, expected exit code or output, and implementing ticket ID. Include Python 3.12/uv, zero-network pytest, JSON Schema validation, secrets scan, journal append-only, status.json/README consistency, provenance ledger, traceability, hardware_tier validity and API fallback, cost caps, fixture/live separation, clean-checkout reproduction, source provenance, transparency artifacts, and a final iu check-all gate. Self-contained and runnable from the repo root in Windows PowerShell.

Constraints: do not contradict existing decisions; no implementation code; no commentary outside file sections; no other files.

Measured hardware: i7-10700K, 16 GB RAM, GTX 1060 6 GB (Pascal, ~4 GB free), 41.6 GB free disk, Windows 10, Python 3.7.4 today (target 3.12 via uv). Local inference ceiling about 3B at Q4, short context; no local training. v1 is API-only via OpenRouter.

Quality bars: clean checkout passes fixture tests with zero network; every lab declares hardware_tier with API fallback for local tiers; README/JOURNAL/PROVENANCE/RESULTS/status.json agree with test state; every public number traces to a run directory and cost; no secrets; no unverified claim presented as fact; no unvalidated judge used for grading.

Ticket titles:
### T-001: Create repository and install spec documents
### T-002: Bootstrap Python 3.12, uv, and package skeleton
### T-003: Add .gitignore and .env.example
### T-004: Implement secrets and forbidden-file scanner with pre-commit hook
### T-005: Implement append-only journal check
### T-006: Implement YAML schema validation command
### T-007: Implement status.json generation, README block, and consistency check
### T-008: Implement config loading and core pydantic models
### T-009: Implement hardware check
### T-010: Implement metrics library
### T-011: Implement cost estimator and CostGuard
### T-012: Implement client interface and FixtureClient
### T-013: Implement OpenRouterClient with retries and mock-transport tests
### T-014: Implement run IDs, `lab new-run`, and the prediction gate
### T-015: Implement the lab registry, runner engine, and `lab run` / `lab estimate`
### T-016: Implement post-mortem check
### T-017: Author all 17 lab manifests and implement `labs list` / `labs check-tiers`
### T-018: Implement dataset build and synthetic fixture framework
### T-019: Implement lab L-003 (eval statistics workbench)
### T-020: Implement lab E9 (context distractors and position)
### T-021: Implement lab E2 (schema field order)
### T-022: Implement lab E4 (escape hatch)
### T-023: Implement lab E5 (position and verbosity bias)
### T-024: Implement smoke suite with total cost cap
### T-025: Implement module checkpoint grader
### T-026: Implement provenance ledger check
### T-027: Implement traceability check
### T-028: Author the 13 module YAML files
### T-029: Author level A cards A-002..A-010
### T-030: Author level B cards B-002..B-014
### T-031: Author level C cards (18 remaining)
### T-032: Author level D and E cards
### T-033: Author level F cards and close traceability
### T-034: Write learner guide and M-A1 walkthrough
### T-035: Implement repo-layout test and `aiu check-all`
### T-036: Pin models and prices, recompute expected costs, and run live smoke
### T-037: Complete module M-A1 end-to-end with a live E9 run
### T-038: Run final v1 acceptance

Repo layout:
# REPO_LAYOUT.md

Root: `C:\Users\Joe\Documents\Playground\AIUniversity`. No other top-level entries are allowed. `aiu validate` does not check layout; T-035 does.

```
AIUniversity/
├── README.md                 Living front page; generated STATUS block.
├── JOURNAL.md                Append-only session log.
├── DECISIONS.md              ADRs.
├── CONSTITUTION.md           Audience, outcomes, standards, "verified".
├── GOVERNANCE.md             Versioning, verification queue, logs, trust table.
├── PROVENANCE.md             Claim ledger (P-###).
├── RESULTS.md                Index of every live run.
├── TRACEABILITY.md           Source concept → card → experiment.
├── TASKS.md                  Implementation backlog.
├── ACCEPTANCE.md             v1 definition of done as commands.
├── LAB_SPEC.md               Lab kit and lab index.
├── REPO_LAYOUT.md            This file.
├── CHANGELOG.md              User-visible changes, newest first.
├── status.json               Generated machine-readable state.
├── pyproject.toml            Package + deps + pytest config.
├── uv.lock                   Pinned dependency lock.
├── .python-version           "3.12".
├── .gitignore                Ignore rules (see T-003).
├── .env.example              Template for OPENROUTER_API_KEY.
├── .githooks/
│   └── pre-commit            Secrets scan + journal append-only check.
├── source/
│   ├── concept_map.txt       Source ontology text (PDF authoritative).
│   └── README.md             Provenance of the source file.
├── schemas/
│   ├── curriculum.schema.json  Cards, labs, modules, trust table.
│   └── status.schema.json      status.json schema.
├── config/
│   ├── models.yaml           Role → pinned model ID.
│   ├── pricing.yaml          Pinned USD/Mtok prices.
│   └── caps.yaml             Cost caps.
├── curriculum/
│   ├── A/ … F/               One YAML card per file: <ID>.yaml.
│   └── modules/              One YAML module per file: M-<L><n>.yaml.
├── labs/
│   └── <lab_id>/             One dir per lab (E1..E13, L-001..L-004).
│       ├── manifest.yaml     Lab manifest (schema: lab).
│       ├── data/             items.jsonl + DATASET_CARD.md (runnable labs).
│       └── fixtures/         responses.jsonl (runnable labs).
├── src/aiu/
│   ├── __init__.py           __version__.
│   ├── cli.py                argparse entry point.
│   ├── validate.py           YAML → JSON Schema validation.
│   ├── models.py             Pydantic models (data, calls, artifacts).
│   ├── config.py             Load models/pricing/caps.
│   ├── cost.py               Estimator + CostGuard.
│   ├── clients/              base.py, fixture.py, openrouter.py.
│   ├── hardware.py           hwcheck.
│   ├── metrics.py            ADR-011 metrics.
│   ├── runs.py               run_id, run dirs, prediction gate.
│   ├── runner.py             Lab execution engine.
│   ├── postmortem.py         Post-mortem checks.
│   ├── labs/                 Lab implementations + registry.
│   ├── generators/           Deterministic dataset generators.
│   ├── status.py             status.json + README block + consistency.
│   ├── journal.py            Append-only check.
│   ├── secrets_scan.py       Secret/forbidden-file scan.
│   ├── provenance.py         Ledger parsing + check.
│   ├── traceability.py       Traceability check.
│   ├── checkpoint.py         Module checkpoint grader.
│   └── smoke.py              Smoke suite.
├── tests/                    pytest; zero network.
├── experiments/
│   ├── _template/            Per-run artifact templates.
│   └── <lab_id>/<run_id>/    Committed live runs only.
├── docs/
│   ├── LEARNER_GUIDE.md      How to complete a module.
│   └── learnings/            YYYY-MM-DD-<slug>.md + _template.md.
├── learner/
│   ├── trust_table.yaml      "Rules of thumb I now trust".
│   ├── checkpoints/          <module>.answers.yaml, <module>.result.json.
│   └── portfolio/            Module portfolio artifacts.
├── ops/
│   ├── bootstrap.ps1         Windows bootstrap (uv, Python, sync, hooks).
│   └── RUNBOOK.md            Live-run procedure, key rotation, incident steps.
└── .runs/                    (gitignored) fixture-mode run outputs.
```


Current T-038 (truncated):
### T-038: Run final v1 acceptance

**Goal:** Every check in ACCEPTANCE.md passes from a clean checkout, and the result is recorded publicly.

**Depends on:** T-037.

**Files:**
- create: `docs/learnings/YYYY-MM-DD-v1-acceptance.md`
- modify: `README.md` (non-generated sections: the "what works / what doesn't" table must match ACCEPTANCE results), `CHANGELOG.md` (`v1.0.0`), `JOURNAL.md`, `status.json`

**Interfaces / schemas:** ACCEPTANCE.md AC-01..AC-20.

**Steps:**
1. `git clone` the repo into `C:\Users\Joe\Documents\Playground\aiu-accept`.
2. `
