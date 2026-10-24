## FILE: status.complete.json
```json
{
  "schema_version": 1,
  "aiu_version": "0.1.0",
  "generated_at": "2026-10-24T00:00:00Z",
  "stage": "architecture",
  "cards": { "drafted": 3, "by_level": { "A": 1, "B": 1, "C": 1, "D": 0, "E": 0, "F": 0 } },
  "labs": { "total": 17, "runnable": 0 },
  "modules": { "total": 13, "authored": 0 },
  "live_runs": { "total": 0, "completed": 0, "aborted": 0, "failed": 0 },
  "cumulative_cost_usd": 0.0,
  "ledger": { "total": 13, "unverified": 13, "verified": 0, "disputed": 0 },
  "last_verified": null,
  "known_gaps": [
    { "ticket": "T-001", "title": "Create repository and install spec documents" },
    { "ticket": "T-002", "title": "Bootstrap Python 3.12, uv, and package skeleton" },
    { "ticket": "T-003", "title": "Add .gitignore and .env.example" },
    { "ticket": "T-004", "title": "Implement secrets and forbidden-file scanner with pre-commit hook" },
    { "ticket": "T-005", "title": "Implement append-only journal check" },
    { "ticket": "T-006", "title": "Implement YAML schema validation command" },
    { "ticket": "T-007", "title": "Implement status.json generation, README block, and consistency check" },
    { "ticket": "T-008", "title": "Implement config loading and core pydantic models" },
    { "ticket": "T-009", "title": "Implement hardware check" },
    { "ticket": "T-010", "title": "Implement metrics library" },
    { "ticket": "T-011", "title": "Implement cost estimator and CostGuard" },
    { "ticket": "T-012", "title": "Implement client interface and FixtureClient" },
    { "ticket": "T-013", "title": "Implement OpenRouterClient with retries and mock-transport tests" },
    { "ticket": "T-014", "title": "Implement run IDs, `lab new-run`, and the prediction gate" },
    { "ticket": "T-015", "title": "Implement the lab registry, runner engine, and `lab run` / `lab estimate`" },
    { "ticket": "T-016", "title": "Implement post-mortem check" },
    { "ticket": "T-017", "title": "Author all 17 lab manifests and implement `labs list` / `labs check-tiers`" },
    { "ticket": "T-018", "title": "Implement dataset build and synthetic fixture framework" },
    { "ticket": "T-019", "title": "Implement lab L-003 (eval statistics workbench)" },
    { "ticket": "T-020", "title": "Implement lab E9 (context distractors and position)" },
    { "ticket": "T-021", "title": "Implement lab E2 (schema field order)" },
    { "ticket": "T-022", "title": "Implement lab E4 (escape hatch)" },
    { "ticket": "T-023", "title": "Implement lab E5 (position and verbosity bias)" },
    { "ticket": "T-024", "title": "Implement smoke suite with total cost cap" },
    { "ticket": "T-025", "title": "Implement module checkpoint grader" },
    { "ticket": "T-026", "title": "Implement provenance ledger check" },
    { "ticket": "T-027", "title": "Implement traceability check" },
    { "ticket": "T-028", "title": "Author the 13 module YAML files" },
    { "ticket": "T-029", "title": "Author level A cards A-002..A-010" },
    { "ticket": "T-030", "title": "Author level B cards B-002..B-014" },
    { "ticket": "T-031", "title": "Author level C cards (18 remaining)" },
    { "ticket": "T-032", "title": "Author level D and E cards" },
    { "ticket": "T-033", "title": "Author level F cards and close traceability" },
    { "ticket": "T-034", "title": "Write learner guide and M-A1 walkthrough" },
    { "ticket": "T-035", "title": "Implement repo-layout test and `aiu check-all`" },
    { "ticket": "T-036", "title": "Pin models and prices, recompute expected costs, and run live smoke" },
    { "ticket": "T-037", "title": "Complete module M-A1 end-to-end with a live E9 run" },
    { "ticket": "T-038", "title": "Run final v1 acceptance" }
  ]
}
```

## FILE: CHANGELOG.md
```markdown
# Changelog

All notable changes to AI University are recorded here, newest first.
Versions follow semantic versioning. Dates are ISO 8601 (YYYY-MM-DD).

## 0.1.0 - 2026-10-24 - Architecture handoff

Stage: `architecture`. No implementation code, no live runs, cumulative cost $0.00.

### Added
- Specification documents (architecture, acceptance criteria, ticket plan T-001..T-038).
- `status.schema.json` and `status.json` (stage `architecture`; 3 cards drafted, A/B/C 1 each;
  17 labs defined, 0 runnable; 13 modules planned, 0 authored; 0 live runs;
  provenance ledger: 13 entries, all unverified; `last_verified` null).
- Draft knowledge cards: one each at levels A, B, and C.
- Experiment templates under `experiments/_template/`:
  `prediction.md`, `postmortem.md`, `config.json`, `result.json`, `metrics.json`, `cost.json`.
- Learning post template at `docs/learnings/_template.md`.
- This changelog.

### Known gaps
- All tickets T-001..T-038 are open; see `known_gaps` in `status.json`.
- Model IDs and prices are not pinned; no expected-cost figures are final (T-036).
- `ACCEPTANCE.md` has never been run to passing (T-038).
```

## FILE: experiments/_template/prediction.md
```markdown
# Prediction - <run_id>

> Write and commit this file BEFORE the run. The prediction gate rejects runs whose
> prediction is missing, incomplete, or has a `written_at` later than the run start.
> Do not edit after the run starts; record changes in `postmortem.md` instead.

- **run_id:** <run_id>
- **lab_id:** <lab_id>
- **author:** <name or handle>
- **written_at:** <YYYY-MM-DDTHH:MM:SSZ>

## Hypothesis
<One falsifiable sentence: "Under condition X, compared with Y, metric M will ...">

## Expected direction
<One of: increase | decrease | no change (within threshold)>
<Optional: expected magnitude, e.g. "about 5-15 percentage points">

## Metric
- **name:** <metric name as it will appear in metrics.json>
- **definition:** <how it is computed, unit, higher-is-better or lower-is-better>
- **n (planned):** <number of items / trials>

## Pass/fail threshold
- **pass if:** <precise rule, e.g. "difference >= 5 pp and 95% CI excludes 0">
- **fail if:** <precise rule>
- **inconclusive if:** <precise rule, e.g. "CI includes 0 and width > 10 pp">

## Confounds
<List what else could produce the expected result, and how the setup controls for each.>
1. <confound> - <control or "uncontrolled">
2. <confound> - <control or "uncontrolled">

## Budget
- **estimated cost (from `lab estimate`):** <usd or "fixture: 0">
- **cap_usd:** <usd>
```

## FILE: experiments/_template/postmortem.md
```markdown
# Post-mortem - <run_id>

- **run_id:** <run_id>
- **lab_id:** <lab_id>
- **author:** <name or handle>
- **written_at:** <YYYY-MM-DDTHH:MM:SSZ>
- **result status:** <completed | aborted | failed> (from result.json)
- **actual cost (usd):** <from cost.json>

## Prediction vs result
| | Prediction | Result |
|---|---|---|
| Direction | <from prediction.md> | <observed> |
| Metric value | <expected> | <value [ci_low, ci_high], n> |
| Threshold verdict | - | <pass | fail | inconclusive> |

## Observed
<What actually happened, facts only. Cite metrics.json and specific items/artifacts.
Include anything surprising or anomalous, including errors and aborted items.>

## Why
<Your best explanation. Separate evidence-backed reasons from speculation; label speculation.
Address each confound listed in prediction.md.>

## What I now trust
<Claims you now hold, with confidence (low | medium | high) and their scope limits.
Note any provenance ledger entry or card this supports or disputes.>

## What I will change
<Changes to method, prompts, datasets, thresholds, or your mental model.>

## Next
<The next concrete experiment or action, with its own falsifiable question.>
```

## FILE: experiments/_template/config.json
```json
{
  "run_id": "<run_id>",
  "lab_id": "<lab_id>",
  "mode": "<fixture|live>",
  "model_id": null,
  "temperature": null,
  "seed": null,
  "dataset_path": "<path/to/dataset>",
  "n_items": null,
  "created_at": "<YYYY-MM-DDTHH:MM:SSZ>"
}
```

## FILE: experiments/_template/result.json
```json
{
  "status": "<completed|aborted|failed>",
  "started_at": null,
  "ended_at": null,
  "error": null,
  "items_completed": null,
  "artifacts": []
}
```

## FILE: experiments/_template/metrics.json
```json
{
  "metrics": [
    {
      "name": "<metric_name>",
      "value": null,
      "n": null,
      "ci_low": null,
      "ci_high": null
    }
  ],
  "notes": "<CI method, exclusions, anomalies; empty string if none>"
}
```

## FILE: experiments/_template/cost.json
```json
{
  "model_id": null,
  "prompt_tokens": null,
  "completion_tokens": null,
  "reasoning_tokens": null,
  "usd": null,
  "cap_usd": null,
  "within_cap": null
}
```

## FILE: docs/learnings/_template.md
```markdown
---
title: <Short claim-style title>
author: <name or handle>
date: <YYYY-MM-DD>
lab_id: <lab_id>
run_ids: [<run_id>]
cards: [<card ids, e.g. C-001>]
ledger_entries: [<ledger ids affected, or empty>]
---

# <Title>

## Question
<What you wanted to know, and why it matters in practice.>

## Prediction
<What you expected before running, quoted or summarised from
[prediction.md](../../experiments/<run_id>/prediction.md), including the pass/fail threshold.>

## Setup
- **Mode:** <fixture | live>
- **Model:** <model_id, or "n/a (fixture)">
- **Temperature / seed:** <values>
- **Dataset:** <dataset_path>, n = <n_items>
- **Conditions compared:** <condition A vs condition B>
- **Config:** [config.json](../../experiments/<run_id>/config.json)

## Result
<Headline metric with value, n, and confidence interval, copied from
[metrics.json](../../experiments/<run_id>/metrics.json). State the threshold verdict:
pass | fail | inconclusive. Include a table or chart if helpful.>

## Interpretation
<What the result means, and how it compares with the prediction. Distinguish evidence from speculation.>

## Limits
<Sample size, single model, synthetic data, uncontrolled confounds, fixture vs live, and any
reason this may not generalise.>

## What changed in the trust table
| Claim / ledger entry | Before | After | Reason |
|---|---|---|---|
| <claim or ledger id> | <unverified | verified | disputed> | <new state> | <one line> |

<If nothing changed, write "No change" and explain why.>

## Links
- Run: [experiments/<run_id>/](../../experiments/<run_id>/)
- Post-mortem: [postmortem.md](../../experiments/<run_id>/postmortem.md)
- Result: [result.json](../../experiments/<run_id>/result.json)
- Cost: [cost.json](../../experiments/<run_id>/cost.json) - actual $<usd> of cap $<cap_usd>
```

## OPEN DECISIONS

- **OD-01 - Model selection and price pinning:** Decide which OpenRouter model IDs to use for live labs, and how to source and pin prices: a snapshot date or a per-run fetch. This blocks final expected costs (T-036).
- **OD-02 - Smoke suite total cost cap:** Set the USD value of the total cap for the live smoke suite (T-024, T-036).
- **OD-03 - Per-run default cost cap:** Set the default `cap_usd` for a single live run. Also decide whether learners can raise it, and if so, how.
- **OD-04 - Confidence interval method:** Choose the default CI method in the metrics library, either Wilson or bootstrap, and decide whether it varies by metric type (T-010, T-019).
- **OD-05 - Prediction gate timing source:** Decide whether `written_at` is trusted as written by the author or checked against the git commit timestamp of `prediction.md` (T-014).
- **OD-06 - Ledger verification authority:** Decide what evidence moves a ledger entry from unverified to verified or disputed. Options are a single passing live run, replication, or reviewer sign-off (T-026).
- **OD-07 - Reasoning token accounting:** Decide how to record `reasoning_tokens` for models that do not report them: as `null` or as `0`. Also decide whether these tokens count toward the cap estimate (T-011).
- **OD-08 - Fixture runs in status counts:** Decide whether fixture-mode runs count toward `live_runs`. The working assumption is that they do not; this needs confirmation (T-007).
