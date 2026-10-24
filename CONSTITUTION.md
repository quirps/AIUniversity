# CONSTITUTION.md

## 1. Audience
Working engineers: fluent Python, have called LLM APIs, basic ML literacy (train/test split, precision/recall). Not researchers; not beginners.

## 2. Outcomes (observable)
After v1 Core (A–E) a learner can:
1. Diagnose a failing LLM call as context, task-definition, evaluation, or capability failure using the §8 playbook on a saved trace.
2. Redesign a decision as binary checks or a ≤7-label MECE enum with an escape hatch, and measure the change.
3. Validate an LLM judge against human labels using kappa, TPR, TNR, and bias checks, and refuse to use one that fails.
4. Build a tiered/cascaded pipeline and report a cost/accuracy curve.
5. Choose the cheapest adaptation rung that passes a held-out set.
6. Keep a "rules of thumb I now trust" table backed by their own runs.

## 3. Non-goals (v1)
Web UI, auth, database, payments, video, local models, GPU training, fine-tuning LLMs, leaderboard benchmarking, LLM-graded learner assessment.

## 4. Pedagogical principles
1. Prediction before observation. The harness enforces it.
2. Every lab ends in a post-mortem. No post-mortem = lab incomplete.
3. Heuristics are defaults with failure conditions, not laws. Every card has `when_it_fails`.
4. Every card has ≥1 misconception.
5. Every module ends in a portfolio artifact.
6. Negative results are first-class.
7. Measure on your own data before trusting a number from anywhere.

## 5. Content standards
- Every card cites `source_section` and carries provenance `S`, `K`, `ADD` (combinations allowed).
- `ADD` cards carry a one-sentence `add_justification`.
- Any number from a `[S]` or `[K]` claim is written as "reported" or "claimed" until its ledger row is `verified`.
- Numbers use the words **measured** (from a live run in `experiments/`, linked), **sourced** (from a cited external source), or **assumed** (configuration estimate or synthetic fixture). No other evidence words.
- No model ID, price, or provider behavior is stated in prose without a date.
- Synthetic datasets use fictional entities only. No PII. No proprietary traces.

## 6. Definition of "verified"
A ledger claim is `verified` only when all hold:
1. A human reviewer set the status.
2. `source` points to a primary source (paper, official doc, or our own run dir) dated within 12 months of the check, or to our own live run.
3. `method` states what was checked (e.g., "read §4.2 of paper; number matches" or "replicated in experiments/E9/<run_id>").
4. `date` is the check date.
`disputed` = credible primary evidence contradicts the claim; the card's `when_it_fails` must cite it.
A claim verified by our own run is verified **for our setup only**; the card must say so.

## 7. Transparency commitments
- `JOURNAL.md` is append-only; corrections are new entries.
- Every live run is committed, including aborted and failed runs.
- Every public number links to a run dir and its `cost.json`.
- Cumulative spend appears in README and `status.json` and is recomputed, not typed.
- README never claims more than `ACCEPTANCE.md` checks prove.
- No secrets, PII, or model weights are committed.
