# PROVENANCE.md - Claim ledger

Statuses: `unverified` | `verified` | `disputed`. Status rules are in CONSTITUTION §6 and the workflow is in GOVERNANCE §3.

Until a row is `verified`, any number in its claim is "reported" or "claimed".

## Notes on the seed rows

- `date` for seed rows is the date the row was added (fill in at commit). It is not a check date.
- `source` points to the concept map. Exact section anchors are added when T-026 parses the source. Rows without an exact section anchor stay `unverified`.
- Rows P-001, P-011, and P-042 are seeded from the three exemplar cards. Their claim text must match the card text verbatim at commit; see OPEN DECISIONS.
- The other rows (P-002..P-010, P-012) are the source's main [K] claims, paraphrased.

| ID | Claim | Status | Source | Date | Method |
|---|---|---|---|---|---|
| P-001 | (Exemplar card 1, level A) Many LLM failures are context failures - missing, distracting, or badly positioned information - rather than capability failures (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-002 | Irrelevant distractor content in context degrades answer accuracy (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-003 | Information position within a long context affects recall (middle-of-context weaker) (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-004 | In structured output, placing a reasoning field before the answer field changes accuracy (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-005 | Adding an explicit escape-hatch label (e.g., "unknown/other") reduces forced misclassification (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-006 | LLM judges exhibit position bias in pairwise comparison (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-007 | LLM judges exhibit verbosity bias, favoring longer answers (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-008 | An LLM judge should be validated against human labels (kappa, TPR, TNR) before use (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-009 | Tiered/cascaded pipelines can cut cost at small accuracy loss (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-010 | Prefer the cheapest adaptation rung (prompting → retrieval → fine-tuning) that passes a held-out set (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-011 | (Exemplar card 2, level B) Binary checks or a ≤7-label MECE enum with an escape hatch are more reliable than open-ended or large-label decisions (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-012 | Small, fixed label sets improve labeling consistency (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |
| P-042 | (Exemplar card 3, level C) Judge agreement measured as kappa against human labels is a better acceptance criterion than raw accuracy under class imbalance (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | - |

P-013..P-041 are reserved for claims added by T-029..T-033.
