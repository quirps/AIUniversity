# PROVENANCE.md - Claim ledger

Statuses: `unverified` | `verified` | `disputed`. Status rules are in CONSTITUTION §6 and the workflow is in GOVERNANCE §3.

Until a row is `verified`, any number in its claim is "reported" or "claimed".

## Notes on the seed rows

- `date` for seed rows is the date the row was added (fill in at commit). It is not a check date.
- `source` points to the concept map. Exact section anchors are added when T-026 parses the source. Rows without an exact section anchor stay `unverified`.
- Rows P-001, P-011, and P-042 are seeded from the three exemplar cards. Their claim text must match the card text verbatim at commit; see OPEN DECISIONS.
- The other rows (P-002..P-010, P-012) are the source's main [K] claims, paraphrased.
- `Tag` records the provenance tag for the claim (`S`, `K`, or `ADD`).
- `Cards` lists comma-separated card IDs that cite the claim, or `-` for none.

| ID | Claim | Tag | Status | Source | Date | Method | Cards |
|---|---|---|---|---|---|---|---|
| P-001 | (Exemplar card 1, level A) Many LLM failures are context failures - missing, distracting, or badly positioned information - rather than capability failures (claimed) | K | unverified | source/concept_map.txt [K], section TBD | TBD | - | A-001 |
| P-002 | Irrelevant distractor content in context degrades answer accuracy (claimed) | K | unverified | source/concept_map.txt [K], section TBD | TBD | - | - |
| P-003 | Information position within a long context affects recall (middle-of-context weaker) (claimed) | K | unverified | source/concept_map.txt [K], section TBD | TBD | - | - |
| P-004 | In structured output, placing a reasoning field before the answer field changes accuracy (claimed) | K | unverified | source/concept_map.txt [K], section TBD | TBD | - | - |
| P-005 | Adding an explicit escape-hatch label (e.g., "unknown/other") reduces forced misclassification (claimed) | K | unverified | source/concept_map.txt [K], section TBD | TBD | - | - |
| P-006 | LLM judges exhibit position bias in pairwise comparison (claimed) | K | unverified | source/concept_map.txt [K], section TBD | TBD | - | - |
| P-007 | LLM judges exhibit verbosity bias, favoring longer answers (claimed) | K | unverified | source/concept_map.txt [K], section TBD | TBD | - | - |
| P-008 | An LLM judge should be validated against human labels (kappa, TPR, TNR) before use (claimed) | K | unverified | source/concept_map.txt [K], section TBD | TBD | - | - |
| P-009 | Tiered/cascaded pipelines can cut cost at small accuracy loss (claimed) | K | unverified | source/concept_map.txt [K], section TBD | TBD | - | - |
| P-010 | Prefer the cheapest adaptation rung (prompting → retrieval → fine-tuning) that passes a held-out set (claimed) | K | unverified | source/concept_map.txt [K], section TBD | TBD | - | - |
| P-011 | (Exemplar card 2, level B) Binary checks or a ≤7-label MECE enum with an escape hatch are more reliable than open-ended or large-label decisions (claimed) | S | unverified | source/concept_map.txt [K], section TBD | TBD | - | B-001 |
| P-012 | Small, fixed label sets improve labeling consistency (claimed) | K | unverified | source/concept_map.txt [K], section TBD | TBD | - | - |
| P-042 | (Exemplar card 3, level C) Judge agreement measured as kappa against human labels is a better acceptance criterion than raw accuracy under class imbalance (claimed) | S | unverified | source/concept_map.txt [K], section TBD | TBD | - | C-004 |
| P-013 | Decision tasks ordered from easiest to hardest: small closed-set classification, extraction, binary check with quoted evidence, pairwise comparison, anchored ordinal rubric, holistic score, counting/bookkeeping, then judging own output or confidence (claimed) | S,K | unverified | source/concept_map.txt [S,K], section 1.2 | TBD | - | A-002 |
| P-014 | Constraining the output space with enums, schemas, and short answers and asking one decision per call reduces compounded error (claimed) | K | unverified | source/concept_map.txt [K], section 1.3 | TBD | - | A-003 |
| P-015 | Verbalized confidence is poorly calibrated; token logprobs, sample agreement, cross-model agreement, and separate verifiers are better signals (claimed) | K | unverified | source/concept_map.txt [K], section 1.6 | TBD | - | A-006 |
| P-016 | A ceiling test with the strongest model and oracle context distinguishes prompt/context failures from capability or label-ambiguity failures (claimed) | K | unverified | source/concept_map.txt [K], section 1.7 | TBD | - | A-007 |
| P-017 | If two expert humans disagree on a label, no model can exceed that agreement ceiling; the task definition is the bottleneck (claimed) | K | unverified | source/concept_map.txt [K], section 1.9 | TBD | - | A-009 |
| P-018 | Model versions, providers, and default parameters change over time; pin them, log them, and rerun regression suites on change (claimed) | S,K | unverified | source/concept_map.txt [S,K], section 1.10 | TBD | - | A-010 |

P-019..P-041 remain reserved for claims added by T-030..T-033.
