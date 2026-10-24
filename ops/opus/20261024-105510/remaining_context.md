Emit ONLY the remaining v1 files, in this order, using the exact ## FILE: <path> format. No commentary outside file sections.

1. GOVERNANCE.md - content versioning, verification queue workflow, experiment/results log format, trust-table format, and who may change what.
2. README.md - living front page: what this is, current status, quickstart, what works / what does not yet work, total spend (0.00 at this stage), last verified date, links to journal and artifacts. Do not claim untested things.
3. JOURNAL.md - append-only template plus entry 0: project genesis, measured hardware, architecture call provenance, and current state. Do not invent completed runs.
4. PROVENANCE.md - claim ledger table (P-###, claim, status, source, date, method). Seed P-001, P-011, P-042 from the three exemplar cards, plus the source's main [K] claims; all start unverified unless directly supported by the source text.
5. RESULTS.md - empty experiment index with the required columns and a template row; state that no live runs exist yet.
6. schemas/status.schema.json - JSON Schema for status.json.
7. status.json - initial valid state consistent with the schema: 3 cards drafted, 0 labs runnable, 0 live runs, cumulative_cost_usd 0.0, known_gaps listing the unbuilt tickets.
8. CHANGELOG.md - initial entry for the architecture handoff, newest first.
9. experiments/_template/prediction.md, postmortem.md, config.json, esult.json, metrics.json, cost.json - exact templates with the required fields and placeholder values.
10. docs/learnings/_template.md - narrative learning-post template.
11. ## OPEN DECISIONS - only genuine unresolved decisions.

Constraints: no implementation code; no fabricated results or costs; every claim labeled measured/sourced/assumed; status.json must validate against the emitted schema; do not contradict CONSTITUTION, REPO_LAYOUT, or the ticket list.

CONSTITUTION:
# CONSTITUTION.md

## 1. Audience
Working engineers: fluent Python, have called LLM APIs, basic ML literacy (train/test split, precision/recall). Not researchers; not beginners.

## 2. Outcomes (observable)
After v1 Core (A–E) a learner can:
1. Diagnose a failing LLM call as context, task-definition, evaluation, or capability failure using the §8 playbook on a saved trace.
2. Redesign a decision as binary checks or a ≤7-label MECE enum with an escape hatch, and measure the change.
3. Validate an LLM judge against human labels using kappa, TPR, TNR, and bias checks, and refuse to use one that fails.
4. Build a tiered/cascaded pipeline and report a cost/accuracy curve.
5. Choose the cheapest adaptation rung that passes a held-out set.
6. Keep a "rules of thumb I now trust" table backed by their own runs.

## 3. Non-goals (v1)
Web UI, auth, database, payments, video, local models, GPU training, fine-tuning LLMs, leaderboard benchmarking, LLM-graded learner assessment.

## 4. Pedagogical principles
1. Prediction before observation. The harness enforces it.
2. Every lab ends in a post-mortem. No post-mortem = lab incomplete.
3. Heuristics are defaults with failure conditions, not laws. Every card has `when_it_fails`.
4. Every card has ≥1 misconception.
5. Every module ends in a portfolio artifact.
6. Negative results are first-class.
7. Measure on your own data before trusting a number from anywhere.

## 5. Content standards
- Every card cites `source_section` and carries provenance `S`, `K`, `ADD` (combinations allowed).
- `ADD` cards carry a one-sentence `add_justification`.
- Any number from a `[S]` or `[K]` claim is written as "reported" or "claimed" until its ledger row is `verified`.
- Numbers use the words **measured** (from a live run in `experiments/`, linked), **sourced** (from a cited external source), or **assumed** (configuration estimate or synthetic fixture). No other evidence words.
- No model ID, price, or provider behavior is stated in prose without a date.
- Synthetic datasets use fictional entities only. No PII. No proprietary traces.

## 6. Definition of "verified"
A ledger claim is `verified` only when all hold:
1. A human reviewer set the status.
2. `source` points to a primary source (paper, official doc, or our own run dir) dated within 12 months of the check, or to our own live run.
3. `method` states what was checked (e.g., "read §4.2 of paper; number matches" or "replicated in experiments/E9/<run_id>").
4. `date` is the check date.
`disputed` = credible primary evidence contradicts the claim; the card's `when_it_fails` must cite it.
A claim verified by our own run is verified **for our setup only**; the card must say so.

## 7. Transparency commitments
- `JOURNAL.md` is append-only; corrections are new entries.
- Every live run is committed, including aborted and failed runs.
- Every public number links to a run dir and its `cost.json`.
- Cumulative spend appears in README and `status.json` and is recomputed, not typed.
- README never claims more than `ACCEPTANCE.md` checks prove.
- No secrets, PII, or model weights are committed.


REPO_LAYOUT:
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