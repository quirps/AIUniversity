# E5 — Position and verbosity bias dataset card

## Purpose

A synthetic pairwise-judging dataset for testing whether a judge changes its
preference when two answers swap slots or when the wrong answer is padded with
irrelevant prose.

## Generator

- Module: `aiu.generators.e5`
- Seed: `1337`
- Command: `uv run aiu dataset build E5`

The 40 fictional-domain questions are shuffled with `random.Random(1337)`
before ID assignment.

## Counts

- 40 items, IDs `e5000`..`e5039`.
- Each item has a question, a correct answer, a one-fact wrong answer, and two
  or three sentences of on-topic padding that add no facts.
- 160 planned calls: 40 items × 4 conditions.

## Conditions

- `cw_plain`: A = correct, B = wrong.
- `wc_plain`: A = wrong, B = correct.
- `cw_padwrong`: A = correct, B = wrong plus padding.
- `wc_padwrong`: A = wrong plus padding, B = correct.

Output is `A` or `B` only. A response whose first non-space character is not
`A` or `B` parses to `None`.

## Synthetic fixture

`uv run aiu fixtures synth E5` prefers the first slot with probability 0.15
regardless of which answer is there. Otherwise it chooses the correct answer.
In padded conditions it chooses the padded wrong answer with an additional
probability of 0.10.

## License

Synthetic data is released under CC0 1.0 Universal, per OD-10 and
`LICENSE-DATA`.

## Known biases

One-fact errors may be trivially detectable. Frontier judges may show small
verbosity bias. The padding sentences are generic and may be easy to ignore.
