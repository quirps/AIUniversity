# Post-mortem - <run_id>

- **run_id:** <run_id>
- **lab_id:** <lab_id>
- **author:** <name or handle>
- **written_at:** <YYYY-MM-DDTHH:MM:SSZ>
- **result status:** <completed | aborted | failed> (from result.json)
- **actual cost (usd):** <from cost.json>

## Prediction vs result
| | Prediction | Result |
|---|---|---|
| Direction | <from prediction.md> | <observed> |
| Metric value | <expected> | <value [ci_low, ci_high], n> |
| Threshold verdict | - | <pass | fail | inconclusive> |

## Observed
<What actually happened, facts only. Cite metrics.json and specific items/artifacts.
Include anything surprising or anomalous, including errors and aborted items.>

## Why
<Your best explanation. Separate evidence-backed reasons from speculation; label speculation.
Address each confound listed in prediction.md.>

## What I now trust
<Claims you now hold, with confidence (low | medium | high) and their scope limits.
Note any provenance ledger entry or card this supports or disputes.>

## What I will change
<Changes to method, prompts, datasets, thresholds, or your mental model.>

## Next
<The next concrete experiment or action, with its own falsifiable question.>
