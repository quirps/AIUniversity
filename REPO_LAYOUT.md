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
├── .env.example                              Template for OPENROUTER_API_KEY.
├── LICENSE                  Repository license.
├── LICENSE-CONTENT          Content license (OD-10).
├── LICENSE-DATA             Dataset license.
├── .githooks/
│   └── pre-commit            Secrets scan + journal append-only check.
├── source/
│   ├── concept_map.txt       Source ontology text (PDF authoritative).
│   ├── *.pdf                 Original source PDF (committed, OD-11).
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
│   ├── RUNBOOK.md            Live-run procedure, key rotation, incident steps.
│   ├── OPUS_KICKOFF.md       Architecture contract sent to Opus.
│   ├── OPUS_RUN_LOG.md       Call-by-call architecture spend and failures.
│   ├── call_opus.ps1         Auditable OpenRouter caller (no key inside).
│   ├── extract_opus.ps1      Response-to-files extractor.
│   ├── MINIMAL_SYSTEM.md     Small system prompt for follow-up calls.
│   └── opus/                 Raw responses, repaired markdown, meta.json.
└── .runs/                    (gitignored) fixture-mode run outputs.
```
