# Draft card review index

All 75 cards are currently `status: draft`. v1.0.0 is tagged without human
verification; a card may move to `reviewed` or `verified` only after a named
human reviews it.

## Timing

- **Not a v1.0.0 blocker:** the release is tagged and the acceptance gate does
  not depend on card review.
- **M-A1 priority:** review A-001, A-007, A-008, and A-010 before the M-A1
  workbench is declared learner-complete.
- **Before claiming curriculum verification:** review all 75 cards and resolve
  the ledger claims they cite.

## Review order

1. M-A1 cards (A-001, A-007, A-008, A-010) for the first workbench.
2. M-A2 and the A-level remainder.
3. B-level decision design and taxonomies.
4. C-level judge validation and eval statistics.
5. D-level pipeline, E-level adaptation, F-level reading.

## Cards by level

### Level A (10)

| Card | Title | Module | File |
|---|---|---|---|
| A-001 | Output is a function of context | M-A1 | [curriculum/A/A-001.yaml](../curriculum/A/A-001.yaml) |
| A-002 | Decision difficulty hierarchy | M-A2 | [curriculum/A/A-002.yaml](../curriculum/A/A-002.yaml) |
| A-003 | Reduce entropy per call | M-A2 | [curriculum/A/A-003.yaml](../curriculum/A/A-003.yaml) |
| A-004 | Autoregressive ordering | M-A2 | [curriculum/A/A-004.yaml](../curriculum/A/A-004.yaml) |
| A-005 | Known judge/model biases | M-A2 | [curriculum/A/A-005.yaml](../curriculum/A/A-005.yaml) |
| A-006 | Verbalized confidence is weak | M-A2 | [curriculum/A/A-006.yaml](../curriculum/A/A-006.yaml) |
| A-007 | Prompt vs capability failure (ceiling test) | M-A1 | [curriculum/A/A-007.yaml](../curriculum/A/A-007.yaml) |
| A-008 | More context is not free | M-A1 | [curriculum/A/A-008.yaml](../curriculum/A/A-008.yaml) |
| A-009 | Ambiguity ceiling | M-A2 | [curriculum/A/A-009.yaml](../curriculum/A/A-009.yaml) |
| A-010 | Silent drift | M-A1 | [curriculum/A/A-010.yaml](../curriculum/A/A-010.yaml) |

### Level B (14)

| Card | Title | Module | File |
|---|---|---|---|
| B-001 | Binary decomposition of judgments | M-B1 | [curriculum/B/B-001.yaml](../curriculum/B/B-001.yaml) |
| B-002 | Evidence-before-verdict schema | M-B2 | [curriculum/B/B-002.yaml](../curriculum/B/B-002.yaml) |
| B-003 | Enums with escape hatch | M-B1 | [curriculum/B/B-003.yaml](../curriculum/B/B-003.yaml) |
| B-004 | MECE categories | M-B1 | [curriculum/B/B-004.yaml](../curriculum/B/B-004.yaml) |
| B-005 | Observable-criteria definitions | M-B1 | [curriculum/B/B-005.yaml](../curriculum/B/B-005.yaml) |
| B-006 | Cardinality limit per call | M-B1 | [curriculum/B/B-006.yaml](../curriculum/B/B-006.yaml) |
| B-007 | Boundary few-shots | M-B1 | [curriculum/B/B-007.yaml](../curriculum/B/B-007.yaml) |
| B-008 | Anchored ordinal scales | M-B2 | [curriculum/B/B-008.yaml](../curriculum/B/B-008.yaml) |
| B-009 | Pairwise vs pointwise; reference-based | M-B2 | [curriculum/B/B-009.yaml](../curriculum/B/B-009.yaml) |
| B-010 | Constrained decoding / structured outputs | M-B2 | [curriculum/B/B-010.yaml](../curriculum/B/B-010.yaml) |
| B-011 | Abstention and escalation paths | M-B2 | [curriculum/B/B-011.yaml](../curriculum/B/B-011.yaml) |
| B-012 | Taxonomy lifecycle (open/axial coding) | M-B3 | [curriculum/B/B-012.yaml](../curriculum/B/B-012.yaml) |
| B-013 | First upstream failure | M-B3 | [curriculum/B/B-013.yaml](../curriculum/B/B-013.yaml) |
| B-014 | Rationale-length smell test | M-B2 | [curriculum/B/B-014.yaml](../curriculum/B/B-014.yaml) |

### Level C (19)

| Card | Title | Module | File |
|---|---|---|---|
| C-001 | Error analysis first, metrics second | M-B3 | [curriculum/C/C-001.yaml](../curriculum/C/C-001.yaml) |
| C-002 | One evaluator per failure category | M-B3 | [curriculum/C/C-002.yaml](../curriculum/C/C-002.yaml) |
| C-003 | Gold set from real traffic | M-C1 | [curriculum/C/C-003.yaml](../curriculum/C/C-003.yaml) |
| C-004 | Measure the judge, not just the app | M-C1 | [curriculum/C/C-004.yaml](../curriculum/C/C-004.yaml) |
| C-005 | Raw agreement overstates judge quality | M-C1 | [curriculum/C/C-005.yaml](../curriculum/C/C-005.yaml) |
| C-006 | Consistency is not validity | M-C2 | [curriculum/C/C-006.yaml](../curriculum/C/C-006.yaml) |
| C-007 | Judge rankings do not transfer | M-C2 | [curriculum/C/C-007.yaml](../curriculum/C/C-007.yaml) |
| C-008 | Stack cheap judge mitigations | M-C2 | [curriculum/C/C-008.yaml](../curriculum/C/C-008.yaml) |
| C-009 | Freeze the judge | M-C1 | [curriculum/C/C-009.yaml](../curriculum/C/C-009.yaml) |
| C-010 | Split gold labels for judge-prompt tuning | M-C1 | [curriculum/C/C-010.yaml](../curriculum/C/C-010.yaml) |
| C-011 | A perfect pass rate means the eval is too easy | M-C3 | [curriculum/C/C-011.yaml](../curriculum/C/C-011.yaml) |
| C-012 | Correct prevalence for judge error | M-C3 | [curriculum/C/C-012.yaml](../curriculum/C/C-012.yaml) |
| C-013 | Offline and online evals answer different questions | M-C3 | [curriculum/C/C-013.yaml](../curriculum/C/C-013.yaml) |
| C-014 | Agent evals: outcomes and trajectories | M-C3 | [curriculum/C/C-014.yaml](../curriculum/C/C-014.yaml) |
| C-015 | Eval the evals | M-C3 | [curriculum/C/C-015.yaml](../curriculum/C/C-015.yaml) |
| C-016 | Benchmark contamination | M-C3 | [curriculum/C/C-016.yaml](../curriculum/C/C-016.yaml) |
| C-017 | Report per-category metrics | M-C3 | [curriculum/C/C-017.yaml](../curriculum/C/C-017.yaml) |
| C-018 | Failure-mode catalog for taxonomies | M-B3 | [curriculum/C/C-018.yaml](../curriculum/C/C-018.yaml) |
| C-019 | Small-sample confidence intervals | M-C1 | [curriculum/C/C-019.yaml](../curriculum/C/C-019.yaml) |

### Level D (15)

| Card | Title | Module | File |
|---|---|---|---|
| D-001 | Tiered checking before judges | M-D1 | [curriculum/D/D-001.yaml](../curriculum/D/D-001.yaml) |
| D-002 | Workflows before agents | M-D2 | [curriculum/D/D-002.yaml](../curriculum/D/D-002.yaml) |
| D-003 | Routing and cascades | M-D1 | [curriculum/D/D-003.yaml](../curriculum/D/D-003.yaml) |
| D-004 | Error compounding in chains | M-D1 | [curriculum/D/D-004.yaml](../curriculum/D/D-004.yaml) |
| D-005 | Verifier-generator asymmetry | M-D1 | [curriculum/D/D-005.yaml](../curriculum/D/D-005.yaml) |
| D-006 | Self-consistency and majority vote | M-D1 | [curriculum/D/D-006.yaml](../curriculum/D/D-006.yaml) |
| D-007 | Jury of small diverse models | M-D1 | [curriculum/D/D-007.yaml](../curriculum/D/D-007.yaml) |
| D-008 | Independent judge | M-C2 | [curriculum/D/D-008.yaml](../curriculum/D/D-008.yaml) |
| D-009 | Evaluate retrieval and generation separately | M-D2 | [curriculum/D/D-009.yaml](../curriculum/D/D-009.yaml) |
| D-010 | Context engineering | M-D2 | [curriculum/D/D-010.yaml](../curriculum/D/D-010.yaml) |
| D-011 | Tool design for agents | M-D2 | [curriculum/D/D-011.yaml](../curriculum/D/D-011.yaml) |
| D-012 | Reliability plumbing | M-D2 | [curriculum/D/D-012.yaml](../curriculum/D/D-012.yaml) |
| D-013 | Cost and latency levers | M-D1 | [curriculum/D/D-013.yaml](../curriculum/D/D-013.yaml) |
| D-014 | Guardrails for untrusted content | M-D2 | [curriculum/D/D-014.yaml](../curriculum/D/D-014.yaml) |
| D-015 | Debugging playbook | M-D2 | [curriculum/D/D-015.yaml](../curriculum/D/D-015.yaml) |

### Level E (7)

| Card | Title | Module | File |
|---|---|---|---|
| E-001 | The adaptation ladder | M-E1 | [curriculum/E/E-001.yaml](../curriculum/E/E-001.yaml) |
| E-002 | Automated prompt optimization | M-E1 | [curriculum/E/E-002.yaml](../curriculum/E/E-002.yaml) |
| E-003 | Reasoning models | M-E1 | [curriculum/E/E-003.yaml](../curriculum/E/E-003.yaml) |
| E-004 | Prompt versioning and regression | M-E1 | [curriculum/E/E-004.yaml](../curriculum/E/E-004.yaml) |
| E-005 | Fine-tuning and distillation | M-E1 | [curriculum/E/E-005.yaml](../curriculum/E/E-005.yaml) |
| E-006 | Preference tuning and RL | M-E1 | [curriculum/E/E-006.yaml](../curriculum/E/E-006.yaml) |
| E-007 | Synthetic data | M-E1 | [curriculum/E/E-007.yaml](../curriculum/E/E-007.yaml) |

### Level F (10)

| Card | Title | Module | File |
|---|---|---|---|
| F-001 | Pretraining data quality and mixture | M-F1 | [curriculum/F/F-001.yaml](../curriculum/F/F-001.yaml) |
| F-002 | Scaling laws and data-parameter ratio | M-F1 | [curriculum/F/F-002.yaml](../curriculum/F/F-002.yaml) |
| F-003 | Tokenization shapes failure modes | M-F1 | [curriculum/F/F-003.yaml](../curriculum/F/F-003.yaml) |
| F-004 | What post-training changes | M-F1 | [curriculum/F/F-004.yaml](../curriculum/F/F-004.yaml) |
| F-005 | Label noise and ambiguity | M-F1 | [curriculum/F/F-005.yaml](../curriculum/F/F-005.yaml) |
| F-006 | Data mix interference | M-F2 | [curriculum/F/F-006.yaml](../curriculum/F/F-006.yaml) |
| F-007 | Infrastructure limits and decoding | M-F2 | [curriculum/F/F-007.yaml](../curriculum/F/F-007.yaml) |
| F-008 | In-context learning | M-F2 | [curriculum/F/F-008.yaml](../curriculum/F/F-008.yaml) |
| F-009 | Interpretability as intuition | M-F2 | [curriculum/F/F-009.yaml](../curriculum/F/F-009.yaml) |
| F-010 | Small-model labs and v1 scope | M-F2 | [curriculum/F/F-010.yaml](../curriculum/F/F-010.yaml) |

