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
