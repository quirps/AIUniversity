# E2 — Schema field order dataset card

## Purpose

A synthetic entailment dataset for testing whether the order of JSON output
fields changes verdict accuracy, parse rate, and rationale length.

## Generator

- Module: `aiu.generators.e2`
- Seed: `1337`
- Command: `uv run aiu dataset build E2`

Each item has a fictional 80–120 word passage and a claim. The 80 items are
balanced 40 entailed and 40 not entailed. Each not-entailed claim changes
exactly one passage fact; `meta.changed_attr` records which one.

## Conditions

`verdict_first`, `reasoning_first`, `evidence_first`.

- `verdict_first`: JSON keys `verdict, reasoning`.
- `reasoning_first`: JSON keys `reasoning, verdict`.
- `evidence_first`: JSON keys `evidence_quote, reasoning, verdict`.

The `evidence_quote` must be an exact sentence from the passage.

## Synthetic fixture

`uv run aiu fixtures synth E2` returns JSON with the condition's key order.
Verdict errors use the rates below. Independently, 2% of responses are the
literal text `not json` to exercise parse-failure handling.

| Condition | Wrong-verdict rate |
|---|---:|
| verdict_first | 0.15 |
| reasoning_first | 0.10 |
| evidence_first | 0.08 |

## License

Synthetic data is released under CC0 1.0 Universal, per OD-10 and
`LICENSE-DATA`.

## Known biases

Models may ignore the requested key order. Reasoning-native models may reason
internally regardless of output order. Single-attribute claim changes may be
too easy to detect.
