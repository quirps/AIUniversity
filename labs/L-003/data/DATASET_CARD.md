# L-003 — Eval statistics workbench dataset card

## Purpose

A hand-checkable dataset for practising evaluation statistics: raw agreement,
Cohen's kappa, TPR/TNR, observed versus corrected prevalence, and pass@k /
pass^k estimators. There are no model calls in this lab.

## Generator

- Module: `aiu.generators.l003`
- Seed: `1337`
- Command: `uv run aiu dataset build L-003`

The generator shuffles the label pairs with `random.Random(1337)` before
assigning IDs, then sorts the final items by ID.

## Counts

The 200 judge/human label items use the positive label `fail`:

| Cell | Count |
|---|---:|
| True positive (judge fail, human fail) | 24 |
| False negative (judge pass, human fail) | 6 |
| False positive (judge fail, human pass) | 14 |
| True negative (judge pass, human pass) | 156 |

Human positive prevalence is 30/200 = 0.15. Judge TPR is 24/30 = 0.80 and
TNR is 156/170.

The 20 agent items (`t00`..`t19`) each carry `successes` in `{0..5}` and
`trials: 5`:

```text
5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 0, 0, 5, 4, 3
```

## License

Synthetic data is released under CC0 1.0 Universal, per OD-10 and
`LICENSE-DATA`.

## Known biases

Rates were chosen for teaching, not observed in any real system.
