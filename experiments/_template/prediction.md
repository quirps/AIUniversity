---
run_id: <run_id>
lab_id: <lab_id>
mode: <fixture|live>
author: <name or handle>
written_at:
predicted_metrics: {}
---

# Prediction - <run_id>

> Write and commit this file BEFORE the run. The prediction gate rejects runs whose
> prediction is missing, incomplete, uncommitted, or has a `written_at` later than the
> commit time. Do not edit after the run starts; record changes in `postmortem.md`.
>
> Fill `predicted_metrics` with the lab metric names and your predicted values, for example:
> `predicted_metrics: {accuracy: 0.80, max_drop: 0.05}`.

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
