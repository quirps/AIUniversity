# E4 — Escape hatch dataset card

## Purpose

A synthetic support-triage dataset for testing whether adding explicit escape
labels reduces forced in-taxonomy errors on out-of-taxonomy messages.

## Generator

- Module: `aiu.generators.e4`
- Seed: `1337`
- Command: `uv run aiu dataset build E4`

The 80 messages are shuffled with `random.Random(1337)` before ID assignment.
All messages are fictional.

## Counts

In-taxonomy, 60 total:

| Label | Count |
|---|---:|
| billing | 12 |
| login | 12 |
| shipping | 12 |
| refund | 12 |
| bug | 12 |

Out-of-taxonomy, 20 total:

| Category | Count |
|---|---:|
| feature_request | 7 |
| partnership | 7 |
| press | 6 |

## Conditions

- `no_escape`: billing, login, shipping, refund, bug.
- `escape`: the same five labels plus `other` and `insufficient_info`.

Output is a single label. A response that does not normalize to an allowed
label parses to `None`.

## Synthetic fixture

`uv run aiu fixtures synth E4` uses these rates:

| Condition | In-taxonomy error rate |
|---|---:|
| no_escape | 0.05 |
| escape | 0.07 |

For out-of-taxonomy messages, `no_escape` always picks a random in-taxonomy
label. `escape` picks `other` with probability 0.85 and otherwise picks a
random in-taxonomy label.

## License

Synthetic data is released under CC0 1.0 Universal, per OD-10 and
`LICENSE-DATA`.

## Known biases

Out-of-taxonomy categories may be obviously distinct. `other` may become a
dumping ground on real data. The message templates repeat across items.
