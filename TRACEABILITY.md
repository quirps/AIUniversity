# TRACEABILITY.md

One row per source bullet. `aiu traceability check` parses rows beginning `| §` and verifies: every non-`OOS` card ID has a file `curriculum/<L>/<ID>.yaml` (after T-033), every card file appears exactly once here, card `source_section` matches the row, and `experiment_id` matches the row's Experiment (`—` ⇔ null).

| Src | Concept | Card | Experiment | Tag | Status |
|---|---|---|---|---|---|
| §1.1 | Output is a function of context | A-001 | E9 | K | in scope |
| §1.2 | Decision difficulty hierarchy | A-002 | E1 | S,K | in scope |
| §1.3 | Reduce entropy per call | A-003 | E3 | K | in scope |
| §1.4 | Autoregressive ordering | A-004 | E2 | K | in scope |
| §1.5 | Known judge/model biases | A-005 | E5 | S,K | in scope |
| §1.6 | Verbalized confidence is weak | A-006 | E11 | K | in scope |
| §1.7 | Prompt vs capability failure (ceiling test) | A-007 | E12 | K | in scope |
| §1.8 | More context is not free | A-008 | E9 | K | in scope |
| §1.9 | Ambiguity ceiling | A-009 | E1 | K | in scope |
| §1.10 | Silent drift | A-010 | L-001 | S,K | in scope |
| §2.1 | Binary decomposition | B-001 | E1 | S | in scope |
| §2.2 | Evidence-before-verdict schema | B-002 | E2 | S | in scope |
| §2.3 | Enums with escape hatch | B-003 | E4 | K | in scope |
| §2.4 | MECE categories | B-004 | — | K | in scope (null: exercised inside E3/L-002 taxonomy design; no isolated lab) |
| §2.5 | Observable-criteria definitions | B-005 | — | K | in scope (null: assessed by human-reviewed rewrite exercise) |
| §2.6 | Cardinality limit per call | B-006 | E3 | K | in scope |
| §2.7 | Boundary few-shots | B-007 | E8 | K | in scope |
| §2.8 | Anchored ordinal scales | B-008 | E1 | S | in scope |
| §2.9 | Pairwise vs pointwise; reference-based | B-009 | E5 | S,K | in scope |
| §2.10 | Constrained decoding / structured outputs | B-010 | E2 | K | in scope |
| §2.11 | Abstention and escalation paths | B-011 | E10 | K | in scope |
| §2.12 | Taxonomy lifecycle (open/axial coding) | B-012 | L-002 | S | in scope |
| §2.13 | First upstream failure | B-013 | L-002 | S | in scope |
| §2.14 | Rationale-length smell test | B-014 | E2 | S | in scope |
| §3.1 | Tiered checking | D-001 | E10 | S,K | in scope |
| §3.2 | Workflows vs agents | D-002 | — | K | in scope (null: no agent runtime in v1; conceptual) |
| §3.3 | Routing and cascades | D-003 | E10 | K | in scope |
| §3.4 | Error compounding | D-004 | L-003 | K | in scope |
| §3.5 | Verifier/generator asymmetry | D-005 | — | K | in scope (null: best-of-N lab deferred to v2) |
| §3.6 | Self-consistency / majority vote | D-006 | E11 | K | in scope |
| §3.7 | Jury of small diverse models | D-007 | E7 | S | in scope |
| §3.8 | Independent judge | D-008 | E6 | S | in scope |
| §3.9 | Retrieval (RAG) evaluation | D-009 | E9 | K | in scope |
| §3.10 | Context engineering | D-010 | E9 | K | in scope |
| §3.11 | Tool design (ACI) | D-011 | — | K | in scope (null: no tool-use runtime in v1) |
| §3.12 | Reliability plumbing | D-012 | — | K | in scope (null: studied via harness source `src/aiu/clients/openrouter.py`) |
| §3.13 | Cost and latency levers | D-013 | E10 | K | in scope |
| §3.14 | Guardrails / untrusted content | D-014 | L-004 | K | in scope |
| §4.1 | Error analysis first | C-001 | L-002 | S | in scope |
| §4.2 | Failure-category evaluators | C-002 | L-002 | S | in scope |
| §4.3 | Gold set | C-003 | E1 | S | in scope |
| §4.4 | Measure the judge (kappa, TPR/TNR) | C-004 | E1 | S | in scope |
| §4.5 | Kappa deflation | C-005 | E1 | S | in scope |
| §4.6 | Consistency is not validity | C-006 | E5 | S | in scope |
| §4.7 | Judge rankings don't transfer | C-007 | E7 | S | in scope |
| §4.8 | Stack cheap mitigations | C-008 | E5 | S | in scope |
| §4.9 | Freeze the judge | C-009 | L-001 | S | in scope |
| §4.10 | Dev/test split for judge prompts | C-010 | E1 | K | in scope |
| §4.11 | 100% pass rate means eval too easy | C-011 | — | S | in scope (null: assessed via checkpoint and capstone regression set) |
| §4.12 | Correct for judge error (prevalence) | C-012 | L-003 | K | in scope |
| §4.13 | Offline vs online | C-013 | — | K | in scope (null: no production traffic in v1) |
| §4.14 | Agent evals (pass@k, pass^k) | C-014 | L-003 | K | in scope |
| §4.15 | Eval the evals | C-015 | L-003 | K | in scope |
| §4.16 | Contamination | C-016 | — | K | in scope (null: conceptual; no benchmark training data access) |
| §4.17 | Per-category reporting | C-017 | E3 | K | in scope |
| §5 | Adaptation ladder ordering | E-001 | E8 | K | in scope |
| §5.1 | Prompt optimization (DSPy/GEPA) | E-002 | — | K | in scope (null: optimizer frameworks out of v1 scope) |
| §5.2 | Reasoning models | E-003 | — | K | in scope (null: depends on OD-01 model choice; v2 lab) |
| §5.3 | Prompt versioning and regression | E-004 | L-001 | K | in scope |
| §5.4 | Fine-tuning / distillation | E-005 | E13 | K | in scope |
| §5.5 | Preference and RL methods | E-006 | — | K | in scope (null: training-side, read-only in v1) |
| §5.6 | Synthetic data | E-007 | — | K | in scope (null: practiced via repo generators; no isolated lab) |
| §6.1 | Pretraining data | F-001 | — | K | reading track (null: training-side) |
| §6.2 | Scaling laws | F-002 | — | K | reading track (null: training-side) |
| §6.3 | Tokenization | F-003 | — | K | reading track (null: training-side) |
| §6.4 | What post-training changes | F-004 | — | K | reading track (null: training-side) |
| §6.5 | Label noise and ambiguity | F-005 | — | K | reading track (null: training-side) |
| §6.6 | Data mix interference | F-006 | — | K | reading track (null: training-side) |
| §6.7 | Infrastructure (MFU, KV cache, etc.) | F-007 | — | K | reading track (null: training-side) |
| §6.8 | In-context learning | F-008 | E8 | K | reading track |
| §6.9 | Interpretability as intuition | F-009 | — | K | reading track (null: training-side) |
| §6.10 | Small-model labs (nanochat) | F-010 | — | S | reading track (null: GPU/CPU training out of scope, §3.2 policy) |
| §7 | Failure-mode catalog | C-018 | L-002 | K | in scope |
| §8 | Debugging playbook (8 steps) | D-015 | E12 | K | in scope |
| none | Small-sample confidence intervals | C-019 | L-003 | ADD | in scope (justification: v1 gold sets are 40–200 items; uncertainty must be reported to avoid overclaiming) |
| §9 | Experiment backlog E1–E13 | — | E1–E13 | — | specified in LAB_SPEC.md |
| §9 | Training-side labs | OOS | — | — | out of scope v1: GPU training excluded by §3 locked decisions |
| §10 | Sources list | — | — | — | captured in PROVENANCE.md |
| §11 | Schema instructions | — | — | — | implemented by schemas/curriculum.schema.json + CONSTITUTION.md |
