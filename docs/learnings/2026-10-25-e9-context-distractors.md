---
title: E9 distractors lowered exact-match accuracy through partial answers, not wrong facts
author: Maintainer (DeepSeek Flash 4.1), delegated by owner
date: 2026-10-25
lab_id: E9
run_ids: [20261025T001745Z-live-b1c296]
cards: [A-008]
ledger_entries: [P-002, P-003]
---

# E9 distractors lowered exact-match accuracy through partial answers, not wrong facts

## Question

Does adding similar-name distractor passages, or moving the key fact away from the
only passage, reduce exact-match accuracy on E9? A-008 claims that more context
is not free; this run tests that claim on the synthetic E9 setup.

## Prediction

The prediction was oracle accuracy about 0.85, a maximum drop of about 0.20, and
a pass threshold of `max_drop >= 0.05`. The prediction also stated that the T-036
smoke run on the first 20 items informed these values, so it was not blind. See
[prediction.md](../../experiments/E9/20261025T001745Z-live-b1c296/prediction.md).

## Setup

- **Mode:** live
- **Model:** `deepseek-flash` (DeepSeek direct, pinned 2026-10-24)
- **Temperature / seed:** 0 / 1337
- **Dataset:** `labs/E9/data/items.jsonl`, n = 60
- **Conditions compared:** oracle vs d5_start, d5_middle, d5_end, d20_middle
- **Config:** [config.json](../../experiments/E9/20261025T001745Z-live-b1c296/config.json)

## Result

| Condition | Accuracy | n | k | 95% CI |
|---|---:|---:|---:|---|
| oracle | 0.7833 | 60 | 47 | 0.6638-0.8688 |
| d5_start | 0.6167 | 60 | 37 | 0.4902-0.7291 |
| d5_middle | 0.6000 | 60 | 36 | 0.4737-0.7143 |
| d5_end | 0.6000 | 60 | 36 | 0.4737-0.7143 |
| d20_middle | 0.6000 | 60 | 36 | 0.4737-0.7143 |

`max_drop` was 0.1833 (95% CI 0.1056-0.2992). The hypothesis threshold passed,
but `accuracy:oracle` was 0.7833, below the 0.80 validity threshold, so
`validity_passed` is false. The threshold verdict is **pass with a failed
validity check**; treat the result as provisional.

## Interpretation

The non-oracle conditions lost 16.7-18.3 percentage points versus oracle, close
to the predicted 0.20. However, every miss in every condition was a partial
answer that named the same entity as the gold answer, such as `Tarn` for
`the Tarn river` or `Sable` for `the city of Sable`. There were no wrong-entity
answers and no `UNKNOWN` answers. That is evidence that the current exact-match
scoring is measuring answer format as well as context use, so the drop cannot be
read as a distractor-induced fact error. The equal rates for d5_middle, d5_end,
and d20_middle are also evidence against a position-specific effect in this
setup.

## Limits

This is one live run, one model, one synthetic dataset, and one seed. The
prediction was informed by the earlier 20-item smoke run, so it was not blind.
The oracle validity check failed, which caps how strongly the run can support
A-008. The partial-answer pattern may be a prompt-format interaction: the prompt
asks for the answer only, and the model returns a short name. A scoring change
or prompt change is required before the next accuracy comparison.

## What changed in the trust table

| Claim / ledger entry | Before | After | Reason |
|---|---|---|---|
| A-008 trust row | absent | `replicated_once` | One live E9 run produced the drop, with the partial-answer caveat recorded in the notes. |
| P-002 / P-003 | unverified | unverified | The run does not establish wrong-entity errors; human review is still required. |

## Links

- Run: [experiments/E9/20261025T001745Z-live-b1c296/](../../experiments/E9/20261025T001745Z-live-b1c296/)
- Post-mortem: [postmortem.md](../../experiments/E9/20261025T001745Z-live-b1c296/postmortem.md)
- Result: [result.json](../../experiments/E9/20261025T001745Z-live-b1c296/result.json)
- Cost: [cost.json](../../experiments/E9/20261025T001745Z-live-b1c296/cost.json) - actual $0.0645 of cap $2.00
