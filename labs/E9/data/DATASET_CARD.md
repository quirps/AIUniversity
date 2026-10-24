# E9 — Context distractors and position dataset card

## Purpose

A synthetic long-context dataset for testing whether similar-name distractors
and the position of a key passage change exact-match accuracy.

## Generator

- Module: `aiu.generators.e9`
- Seed: `1337`
- Command: `uv run aiu dataset build E9`

All entities and values are fictional. Each item has a key passage and 20
distractor passages. Distractor entity names are one or two edits from the key
entity name.

## Counts

- 60 items, IDs `e000`..`e059`.
- 5 attributes, cycled evenly: `founding_year`, `river`, `mayor`, `export`,
  `twin_city`.
- 21 passages per item: one key and 20 distractors.
- Each passage is 60–90 words.
- 300 planned calls: 60 items × 5 conditions.

## Conditions

`oracle`, `d5_start`, `d5_middle`, `d5_end`, `d20_middle`.

- `oracle`: key passage only.
- `d5_start`: key first, then five distractors.
- `d5_middle`: key at index 3 of six passages.
- `d5_end`: key last of six passages.
- `d20_middle`: key at index 10 of 21 passages.

## Synthetic fixture

`uv run aiu fixtures synth E9` uses the seeded error rates below. A wrong
answer is the value from the first distractor in the item's fixed distractor
order.

| Condition | Error rate |
|---|---:|
| oracle | 0.02 |
| d5_start | 0.05 |
| d5_middle | 0.10 |
| d5_end | 0.07 |
| d20_middle | 0.15 |

## License

Synthetic data is released under CC0 1.0 Universal, per OD-10 and
`LICENSE-DATA`.

## Known biases

Synthetic facts are easy, so absolute accuracy may overstate real-world
performance. Similar-name distractors may test name matching rather than
attention. Contexts are short (under 4k tokens), so they may not reproduce a
lost-in-the-middle effect.
