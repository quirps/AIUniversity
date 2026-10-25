---
run_id: 20261025T001745Z-live-b1c296
lab_id: E9
mode: live
author: Maintainer (DeepSeek Flash 4.1), delegated by owner
written_at: 2026-10-25T00:17:00Z
predicted_metrics: {accuracy:oracle: 0.85, accuracy:d5_start: 0.78, accuracy:d5_middle: 0.72, accuracy:d5_end: 0.75, accuracy:d20_middle: 0.65, max_drop: 0.20}
---

# Prediction - 20261025T001745Z-live-b1c296

> Write and commit this file BEFORE the run. The prediction gate rejects runs whose
> prediction is missing, incomplete, uncommitted, or has a `written_at` later than the
> commit time. Do not edit after the run starts; record changes in `postmortem.md`.

## Hypothesis

Under E9's distractor and position conditions, compared with the oracle-context condition, exact-match accuracy will decrease, and the maximum drop across the four non-oracle conditions will be at least 0.05.

## Expected direction

decrease; expected maximum drop about 0.15-0.25.

## Metric

- **name:** max_drop
- **definition:** maximum of accuracy:oracle minus accuracy for each non-oracle condition (d5_start, d5_middle, d5_end, d20_middle); range 0-1, higher means more degradation.
- **n (planned):** 60 items per condition, 300 calls total.

## Pass/fail threshold

- **pass if:** max_drop >= 0.05, and validity check accuracy:oracle >= 0.80.
- **fail if:** max_drop < 0.05 with accuracy:oracle >= 0.80.
- **inconclusive if:** accuracy:oracle < 0.80 (task broken) or a required metric is null.

## Confounds

1. Synthetic facts may be easier than real retrieval tasks - controlled only by keeping the same synthetic dataset across conditions.
2. Similar-name distractors may test name matching rather than attention - uncontrolled; the post-mortem will inspect wrong answers.
3. Short contexts may show no lost-in-the-middle effect - the d20_middle condition is the direct check.
4. The T-036 smoke run used the first 20 items and informed the predicted values - the prediction is not blind.

## Budget

- **estimated cost (from `lab estimate`):** 0.1021
- **cap_usd:** 2.00
