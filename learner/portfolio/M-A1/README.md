# M-A1 portfolio - context is the program

## Run

- Lab: E9, context distractors and position
- Run: `20261025T001745Z-live-b1c296`
- Post-mortem: [`experiments/E9/20261025T001745Z-live-b1c296/postmortem.md`](../../experiments/E9/20261025T001745Z-live-b1c296/postmortem.md)
- Cost: $0.0645 actual of a $2.00 cap
- Evidence class: measured; hypothesis supported, validity check failed

## Diagnostic note

Oracle accuracy was 0.7833 (47/60, 95% CI 0.6638-0.8688), below the E9
validity threshold of 0.80. The four distractor/position conditions all scored
0.60, giving a maximum drop of 0.1833 (95% CI 0.1056-0.2992) against the oracle.
The pass threshold was `max_drop >= 0.05`, so the hypothesis was supported.

The important failure analysis is that every miss in every condition was a
partial answer that named the same entity as the gold answer, for example
`Tarn` for `the Tarn river` or `Sable` for `the city of Sable`. There were no
wrong-entity answers and no `UNKNOWN` answers. The measured drop therefore
reflects answer formatting and exact-match scoring as much as it reflects
distractor use. The run does not establish that distractors cause wrong facts;
it does show that the current E9 scoring treats a correct short answer as a miss.

## What this means for A-001..A-010

- A-008's context warning is not disproved, but this run cannot separate
  distractor harm from answer-format harm.
- A-001's smart-stranger framing still helps: the model had the information and
  produced the right entity in shorthand.
- The next check is a ceiling test (E12) on the failed items plus an E9 scoring
  decision for partial answers before another accuracy comparison.

## Artifacts

- [Prediction](../../experiments/E9/20261025T001745Z-live-b1c296/prediction.md)
- [Metrics](../../experiments/E9/20261025T001745Z-live-b1c296/metrics.json)
- [Result](../../experiments/E9/20261025T001745Z-live-b1c296/result.json)
- [Cost](../../experiments/E9/20261025T001745Z-live-b1c296/cost.json)
- [Learning write-up](../../docs/learnings/2026-10-25-e9-context-distractors.md)
