---
run_id: 20261025T001745Z-live-b1c296
lab_id: E9
author: Maintainer (DeepSeek Flash 4.1), delegated by owner
written_at: 2026-10-25T00:26:00Z
result_status: completed
actual_cost_usd: 0.0645243
trust_table_row: On the synthetic E9 setup, distractor and position conditions reduced exact-match accuracy by about 18 percentage points, but every miss was a partial answer rather than a wrong-entity fact.
---

# Post-mortem - 20261025T001745Z-live-b1c296

## Prediction vs outcome

The prediction was that oracle accuracy would be about 0.85 and that the maximum drop across the four non-oracle conditions would be about 0.20, with a pass threshold of max_drop >= 0.05. The observed max_drop was 0.1833 (95% CI 0.1056-0.2992), so the hypothesis was supported and the pass threshold was cleared. The per-condition drops were 0.1667 for d5_start and 0.1833 for d5_middle, d5_end, and d20_middle. Oracle accuracy was 0.7833 (95% CI 0.6638-0.8688), below the E9 validity threshold of 0.80, so `validity_passed` is false and the result should be treated as provisional even though `hypothesis_supported` is true. A manual review of the misses found that all 13 oracle misses and all non-oracle misses were partial forms of the gold answer (for example `Tarn` for `the Tarn river`), not wrong entities.

## What surprised me

I expected the distractor and position conditions to spread out around the predicted drops, but d5_middle, d5_end, and d20_middle all landed at exactly 0.60. That is evidence that this setup is dominated by the presence of similar-name distractors rather than by where the key passage sits. The oracle result also came in below the validity threshold, which I did not predict. Most surprising was the failure analysis: every miss, in every condition, was a partial answer such as `Tarn` or `Sable` rather than a wrong entity. That means the exact-match metric is measuring answer format as much as context use. The equal condition rates and the partial-answer pattern are measured; the explanation that the prompt encourages short names is a plausible interpretation, not a separately tested claim.

## Confounds observed

Synthetic facts and short passages may not represent real retrieval tasks; the dataset is controlled across conditions but remains synthetic. Similar-name distractors may test name matching rather than attention, and the uniform non-oracle rates are consistent with that confound. The d20_middle condition is the direct position check, but it did not separate from the shorter distractor conditions. The run used one model (`deepseek-flash`) at temperature 0 and seed 1337, so it says nothing about other models. The prediction was informed by the T-036 smoke run on the first 20 items, so it was not blind. The oracle validity failure is itself a confound: it caps how strongly this run can support a general rule.

## Rule-of-thumb update

I now trust this narrower rule for the synthetic E9 setup only: distractor and position conditions reduced exact-match accuracy by about 18 percentage points, but every miss was a partial answer rather than a wrong-entity fact. It touches A-008 and the unverified ledger claims P-002 and P-003. I have not marked any ledger claim verified, which requires human review. The practical lesson is that E9's exact-match scoring needs a partial-answer or normalization fix before its accuracy drops can be read as context failures.

## Next experiment

Run E12 as a ceiling test on the failed E9 items with oracle context and the strongest available model, to separate context/distractor failures from capability failures. Before another E9 accuracy run, add a scoring decision for partial answers (accept a normalized substring when it names the same entity) or change the prompt to require the full gold phrase; the current exact-match rule conflates format with context use. Then rerun E9 with the same seed and check whether the position effect appears once the oracle validity threshold is met. These are concrete follow-up runs, not changes to this prediction.
