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
| P-019 | Require a quoted evidence span or citation before a verdict; reject verdicts without evidence (claimed) | S | unverified | source/concept_map.txt [S], section 2.2 | TBD | - | B-002 |
| P-020 | Categories should be mutually exclusive and collectively exhaustive; overlapping categories cause inconsistent classification (claimed) | K | unverified | source/concept_map.txt [K], section 2.4 | TBD | - | B-004 |
| P-021 | Define labels by observable text or output properties rather than subjective impressions (claimed) | K | unverified | source/concept_map.txt [K], section 2.5 | TBD | - | B-005 |
| P-022 | Accuracy usually falls as label count rises; keep roughly seven or fewer labels per decision and go hierarchical beyond that (claimed) | K | unverified | source/concept_map.txt [K], section 2.6 | TBD | - | B-006 |
| P-023 | Boundary examples near the decision boundary teach classification better than prototypical examples alone (claimed) | K | unverified | source/concept_map.txt [K], section 2.7 | TBD | - | B-007 |
| P-024 | Anchored ordinal scales with concrete level definitions are more reliable than unanchored scales (claimed) | S | unverified | source/concept_map.txt [S], section 2.8 | TBD | - | B-008 |
| P-025 | Pairwise comparison is easier for models than absolute scoring, and reference-based comparison beats reference-free when a gold answer exists (claimed) | S,K | unverified | source/concept_map.txt [S,K], section 2.9 | TBD | - | B-009 |
| P-026 | Constrained decoding guarantees syntax but not correctness; field order and enum descriptions still affect accuracy (claimed) | K | unverified | source/concept_map.txt [K], section 2.10 | TBD | - | B-010 |
| P-027 | Design an explicit abstention and escalation path for unsure outputs (claimed) | K | unverified | source/concept_map.txt [K], section 2.11 | TBD | - | B-011 |
| P-028 | Taxonomy lifecycle: open coding of real traces, axial coding into named categories, and iteration until saturation (claimed) | S | unverified | source/concept_map.txt [S], section 2.12 | TBD | - | B-012 |
| P-029 | In a multi-step trace, label the earliest step that went wrong; downstream errors are usually consequences (claimed) | S | unverified | source/concept_map.txt [S], section 2.13 | TBD | - | B-013 |
| P-030 | If a judge's rationale is regularly longer than the rubric, the rubric is under-specified (claimed) | S | unverified | source/concept_map.txt [S], section 2.14 | TBD | - | B-014 |
| P-031 | Error analysis should come before metric design; reported guidance puts 60-80% of development time on error analysis and evaluation, starting from real traces rather than dashboards (reported) | S | unverified | source/concept_map.txt [S], section 4.1 | 2026-10-24 | - | C-001 |
| P-032 | Each named failure category should get one evaluator, a code check when possible and a binary LLM judge when semantic and persistent; one-off bugs should not get judges (claimed) | S | unverified | source/concept_map.txt [S], section 4.2 | 2026-10-24 | - | C-002 |
| P-033 | A gold set should be 200-500 human-labeled traces drawn from real traffic, labeled binary with a short note (reported) | S | unverified | source/concept_map.txt [S], section 4.3 | 2026-10-24 | - | C-003 |
| P-034 | Raw agreement overstates judge quality; one 2026 large-scale study reported a 33-41 point gap between exact match and Cohen's kappa on MT-Bench (sourced, unverified) | S | unverified | source/concept_map.txt [S], section 4.5 | 2026-10-24 | - | C-005 |
| P-035 | A judge can have test-retest reliability above 0.95 and still show severe position bias; stability and bias must be checked separately (reported) | S | unverified | source/concept_map.txt [S], section 4.6 | 2026-10-24 | - | C-006 |
| P-036 | Judge-model rankings shifted by up to 14 positions across benchmarks; choose the judge on your own gold set (reported) | S | unverified | source/concept_map.txt [S], section 4.7 | 2026-10-24 | - | C-007 |
| P-037 | Position-swapping plus chain-of-thought plus an explicit rubric gave the largest gain in one April 2026 benchmark, and chain-of-thought alone helped universally (reported) | S | unverified | source/concept_map.txt [S], section 4.8 | 2026-10-24 | - | C-008 |
| P-038 | Freeze the judge's model, rubric version, and low temperature, and re-validate whenever any of them changes (claimed) | S | unverified | source/concept_map.txt [S], section 4.9 | 2026-10-24 | - | C-009 |
| P-039 | Split gold labels into a dev set for judge-prompt tuning and a held-out test set for reporting agreement, to avoid overfitting (claimed) | K | unverified | source/concept_map.txt [K], section 4.10 | 2026-10-24 | - | C-010 |
| P-040 | A 100% pass rate means the eval is too easy; add harder cases from production failures (reported) | S | unverified | source/concept_map.txt [S], section 4.11 | 2026-10-24 | - | C-011 |
| P-041 | Correct for judge error when estimating prevalence: the observed pass rate is biased when the judge has known TPR and TNR, and simple corrections exist (claimed) | K | unverified | source/concept_map.txt [K], section 4.12 | 2026-10-24 | - | C-012 |
| P-043 | Offline evals use fixed datasets and regression suites before deploy; online evals sample production traces, monitor drift, and feed new failures back into the dataset (claimed) | K | unverified | source/concept_map.txt [K], section 4.13 | 2026-10-24 | - | C-013 |
| P-044 | Agent evals should grade outcomes and trajectories separately, using pass@k for capability and pass^k for reliability (claimed) | K | unverified | source/concept_map.txt [K], section 4.14 | 2026-10-24 | - | C-014 |
| P-045 | Eval the evals by seeding known-bad and known-good items and using synthetic perturbations such as typos and reordered lists to test robustness (claimed) | K | unverified | source/concept_map.txt [K], section 4.15 | 2026-10-24 | - | C-015 |
| P-046 | Public benchmarks can leak into training data; trust private, product-specific evaluation sets more (claimed) | K | unverified | source/concept_map.txt [K], section 4.16 | 2026-10-24 | - | C-016 |
| P-047 | Report precision and recall per failure category and a confusion matrix rather than one blended score (claimed) | K | unverified | source/concept_map.txt [K], section 4.17 | 2026-10-24 | - | C-017 |
| P-048 | The section 7 failure-mode catalog for building taxonomies includes hallucinated facts, ungrounded claims, instruction conflicts, format drift, truncation, wrong tool use, tool loops, context overflow, sycophancy, refusal errors, prompt injection, reward hacking, stale knowledge, persona drift, silent model changes, and judge failures (claimed) | K | unverified | source/concept_map.txt [K], section 7 | 2026-10-24 | - | C-018 |
| P-049 | Small gold sets of 40-200 items require confidence intervals for kappa, TPR, and TNR; point estimates alone overclaim precision (claimed) | ADD | unverified | TRACEABILITY.md [ADD] | 2026-10-24 | - | C-019 |

P-050 onward remains available for claims added by T-032..T-033.
