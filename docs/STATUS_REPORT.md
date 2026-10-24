# AI University — Status Report

**Date:** 2026-10-24
**Prepared by:** DeepSeek Flash 4.1 (implementer)
**Architect:** Claude Opus 5.5 via OpenRouter
**Repository:** https://github.com/quirps/AIUniversity
**Stage:** Foundation built (T-001..T-005); curriculum harness not started
**Bottom line:** The design is complete and documented, and the Python foundation now builds and tests. No lab is runnable yet, so the design has not been validated end-to-end. No Opus rerun is needed. Total design spend is **5.290876 USD**; lab spend is **0.00 USD**.

---

## 1. Executive summary

- **What this is.** AI University is a lab-first course for working engineers on building *reliable* LLM applications. The core thesis is that most production failures are context, task-definition, or evaluation failures, not model-capability failures.
- **What was delivered.** A complete v1 architecture: 38 ordered implementation tickets, JSON schemas, a lab specification, 3 exemplar knowledge cards, a 20-check acceptance suite, governance rules, and a public learning record.
- **What is not done.** No runnable labs, no live experiments, and only 3 of 75 cards. The foundation now exists: repo, Python 3.12 via `uv`, CLI, secrets scan, journal check, schema validation, generated status, config/models, hardware probe, metrics, cost guard, clients, prediction gate, lab runner, post-mortem check, and 118 passing tests.
- **Design quality.** Opus produced a coherent, unusually detailed build plan. Every ticket has exact files, interfaces, commands, acceptance tests, definition of done, and scope limits. The plan is designed so a literal implementer cannot silently invent behavior.
- **Cost.** 5.290876 USD on architecture calls, of which 2.607784 USD was wasted on two empty reasoning-only responses. Lab spend is 0.00 USD. The proposed operating budget is 1 USD/day soft, 2 USD/run hard, and a 5 USD smoke-suite cap.
- **What failed.** Opus did not lose any deliverable. It hit reasoning-budget exhaustion, output truncation, OpenRouter in-flight budget rejections, and transport encoding issues. Each was recovered; the failures are logged rather than hidden.
- **What I need from you.** No blocking decisions remain. OD-02 is resolved at 5.00 USD, OD-05 is resolved to require a committed prediction, and OD-09 is deferred. The only operational choice left is when to push the repo.

---

## 2. What we are building, in plain language

The course teaches engineers how to make LLM systems dependable. It is not a collection of prompt tricks.

Every unit follows the same loop:

> **concept → written prediction → reproducible experiment → measured result → post-mortem → updated personal rule**

The learner does not just read that a technique works. They predict the outcome, run a small experiment, measure it, and record what they now trust. Negative results are first-class.

**v1 scope**

Exception: the learner-facing module layer is an interactive HTML workbench with a lesson-scoped DeepSeek shell (ADR-024). The CLI remains the source of truth.

| In scope | Out of scope |
|---|---|
| Content repo + Python lab harness | Web UI for the core harness, auth, payments, video |
| Working engineers, Python-literate | Beginners |
| API-only via OpenRouter | Local model serving, GPU training, LLM fine-tuning |
| Five runnable labs, twelve specified | All 17 labs runnable |
| Deterministic + human-reviewed assessment | LLM-judged learner grading |
| Public learning record | Polished marketing site |

---

## 3. What was actually done in this session

1. **Reviewed the source.** A 10-page concept map covering mental models, decision design, evaluation, pipeline architecture, the adaptation ladder, training intuition, failure modes, a debugging playbook, and 13 experiment backlogs.
2. **Wrote the architecture contract.** Added measured hardware limits, a local-model policy, and transparency requirements so the design could not quietly assume a cloud GPU or hide costs.
3. **Called Opus 5.5 via OpenRouter.** Fifteen logged attempts, plus three direct diagnostic probes. Every logged attempt has its raw response, repaired markdown, and usage metadata under `ops/opus/`.
4. **Extracted the specifications.** 38 tickets, two JSON schemas, three exemplar cards, lab spec, traceability matrix, acceptance criteria, governance, decision records, and transparency templates.
5. **Repaired the handoff.** Completed truncated sections, fixed encoding loss, removed a malformed template, and reconciled inconsistent decision numbers.
6. **Consolidated decisions.** Replaced eight ambiguous open decisions with a canonical register of twelve (OD-01..OD-12), each with a status and rationale.
7. **Wrote this report.** A manager-level view that explains the work without requiring the reader to know the jargon.

8. **Built the foundation.** Executed T-001 through T-014: repository, Python 3.12 via `uv`, package and CLI, ignore rules, secrets scanner, pre-commit hooks, append-only journal check, schema validation, generated status, config/models, hardware probe, metrics, cost guard, clients, the committed-prediction gate, the lab runner, and the post-mortem check. One hundred eighteen tests pass.

Foundation code was written and committed incrementally and pushed to `origin/main`. No further Opus call was made.

---

## 4. Current state at a glance

| Item | State |
|---|---|
| Architecture spec set | Complete |
| Implementation tickets | 16 executed (T-001..T-016), 22 open |
| Knowledge cards drafted | 3 of 75 |
| Labs defined | 17 total: E1–E13 + L-001..L-004 |
| Labs runnable | 0 of 5 planned runnable labs |
| Modules authored | 0 of 13 |
| Live experiments | 0 |
| Tests | 118 passing |
| Acceptance checks | 20 defined, 0 run |
| Pre-commit hooks | Secrets scan + append-only journal |
| Architecture spend | 5.290876 USD (measured) |
| Lab spend | 0.00 USD |
| Git repository | Local repo initialized; 5 commits; remote set; not pushed |
| Secrets in repo | 0 findings by `aiu secrets-scan` |
| Stage | `building` |

`status.json` still shows the initial architecture snapshot (stage `architecture`, all 38 gaps). T-007 regenerates it from repo state; the table above reflects the actual repo state.

**Interpretation:** The foundation is real and tested, but the course does not run yet. T-001..T-016 are complete; the harness core is done. The next milestone is E9 and M-A1. The first learner-visible proof is M-A1 + lab E9.

---

## 5. What failed from Opus, and whether we need to rerun

**Short answer: no rerun is needed.** Every requested artifact is present and internally consistent. The failures were process failures, not missing content.

| Failure | What happened | Impact | How it was resolved | Rerun? |
|---|---|---|---|---|
| Reasoning-budget exhaustion | Two calls spent 60k/64k tokens on internal reasoning and returned zero visible characters; `finish_reason: length`. Cost: 2.607784 USD. | No deliverable from those calls. | Retried with `reasoning.effort: low`, a larger output budget, and smaller follow-up tasks. | No |
| Output truncation | Several successful calls hit the max-token limit: the first at 64k, the backlog at 32k, later files at 8k and 6k. | Files were cut mid-section (TASKS at T-007, ACCEPTANCE at AC-13, status.json mid-file). | Continued each file in a smaller call using the prior output as context; merged the sections. | No |
| OpenRouter 402 "in-flight budget" | Seven calls were rejected before execution because the pre-authorized max cost exceeded the in-flight ceiling, even with credit remaining. | No output; no cost. | Reduced input and max tokens, waited for the retry window, split into smaller calls. | No |
| UTF-8 / mojibake | PowerShell 5.1 decoded some UTF-8 responses as Latin-1; later an unconditional repair corrupted already-correct characters. | `§`, `→`, `≈`, `≤` were corrupted or lost. | Added a marker-gated repair, then repaired the affected files by context and rescanned. | No |
| Malformed learning template | A trailing code fence survived extraction. | Template was not valid markdown. | Removed the stray fence. | No |
| Opus cannot validate its own design | The model wrote specs but could not run the Python, JSON Schema, or acceptance checks. | Design remains unverified until we build and run it. | This is expected; T-006, T-035, and T-038 are the validation tickets. | No |

**Why a rerun is not recommended:** a rerun would cost roughly 1–2 USD, would not add missing content, and would risk introducing contradictions with the documents already reconciled. A second opinion is only worth it if you want an independent architecture review, which is a different task.

**What does need to run later:** the implementation and acceptance tests. Those are not Opus calls. They are local commands in T-001 onward, and they cost 0 USD until a live lab runs.

The full call-by-call record is in `ops/OPUS_RUN_LOG.md`.

---

## 6. Cost report

| Category | USD | Notes |
|---|---:|---|
| Empty reasoning-only calls | 2.607784 | Two calls, zero visible output |
| Useful or partial architecture output | 2.683092 | Includes truncation and continuation calls |
| Rejected 402 calls | 0.000000 | Rejected before execution |
| **Architecture total** | **5.290876** | Measured from each response's `usage.cost` |
| Lab runs | 0.000000 | No live runs |
| **Project total** | **5.290876** | |

**Budget policy (proposed):**

- Soft daily target: **1.00 USD**.
- Hard per-run cap: **2.00 USD**.
- Smoke-suite cap: **5.00 USD**, deferred until T-024/T-036.
- Any run above the daily target requires a JOURNAL entry naming the test, its expected learning value, and the spend.
- The key is shared with other projects; the figure above is this project's measured share, not the key's total usage.

The architecture session is a deliberate one-time exception to the 1 USD/day target: 5.29 USD in one day, of which 2.61 USD was wasted on empty reasoning-only calls. The daily target applies to ongoing lab work, not to the initial design investment.

**Credit situation:** at the last check the key had about 1.57 USD remaining, but OpenRouter's in-flight ceiling blocked calls that requested a large max-token reserve. No live labs are planned until after T-036, so no top-up is needed today. Before the first live smoke run, fund the key with at least the 5 USD smoke cap plus headroom.

---

## 7. How the repository is organized

The repo is designed as a paper trail, not a code dump. A reader can start at the source and follow the evidence chain.

| Path | Purpose |
|---|---|
| `README.md` | Living front page: state, quickstart, costs, links |
| `CONSTITUTION.md` | Audience, outcomes, non-goals, evidence standards |
| `DECISIONS.md` | Architecture decision records + canonical OD register |
| `GOVERNANCE.md` | Who may change content, claims, runs, and trust entries |
| `TASKS.md` | 38 ordered tickets with exact acceptance tests |
| `ACCEPTANCE.md` | 20 executable checks that define v1 "done" |
| `LAB_SPEC.md` | Lab kit: datasets, metrics, tiers, costs, lab index |
| `TRACEABILITY.md` | Source concept → card → experiment mapping |
| `PROVENANCE.md` | Claim ledger; every claim starts `unverified` |
| `RESULTS.md` | Index of every live run (empty until T-036) |
| `JOURNAL.md` | Append-only session log, including failures |
| `CHANGELOG.md` | User-visible changes |
| `status.json` | Machine-readable project state |
| `curriculum/` | Concept cards and modules |
| `labs/` | Lab manifests, data, fixtures (created by T-017+) |
| `schemas/` | JSON Schemas for curriculum and status |
| `experiments/` | Per-run artifacts: prediction, config, result, metrics, cost, post-mortem |
| `docs/` | Status report, learner guide, learning posts |
| `learner/` | Trust table, checkpoints, portfolio (learner-owned) |
| `source/` | Original PDF, extracted text, provenance |
| `ops/` | Architecture contract, call logs, scripts, run records |

**The evidence chain:**

```
source PDF/text
  → concept card (claim + provenance + verification status)
  → lab manifest (hypothesis + metric + pass/fail)
  → source run (prediction → config → result → metrics → cost → post-mortem)
  → RESULTS.md row
  → trust-table entry
  → README claim
```

A public number is only allowed if it traces to a run directory and a cost. That is the central transparency rule.

---

## 8. Key design decisions

### 8.1 Hardware-aware by default

Measured machine: Intel i7-10700K, 16 GB RAM, NVIDIA GTX 1060 6 GB (Pascal, about 4 GB free VRAM), 41.6 GB free disk, Windows 10, Python 3.7.4 currently installed.

Consequences:

- v1 is **API-only**. No local training, no LLM fine-tuning.
- Practical local-inference ceiling is about a **3B model at Q4**, short context, batch 1. A 7B Q4 model is not promised.
- Every lab declares a hardware tier: `API_ONLY`, `LOCAL_SMALL_GPU_6GB`, or `LOCAL_CPU_TINY`.
- Local tiers must ship an API fallback.
- Bootstrap targets Python 3.12 via `uv`; the system Python 3.7.4 is never used.

### 8.2 Cheap-first model policy

Model choice is a **role**, not a constant:

- `cheap_a`, `cheap_b`, `cheap_c` for bulk work, from different families.
- `strong` for ceiling tests, cascades, and expensive comparisons.
- `judge_a`, `judge_b` for judge studies, from different families where possible.

Bulk work defaults to inexpensive models such as Gemini 2.5 Flash and DeepSeek Flash 4.1. Exact IDs are pinned per run in `config/models.yaml`, with a retrieval date. Model choice is itself a lab variable (E6, E7, E10, E12), not a hidden assumption.

### 8.3 Evidence before trust

- Deterministic checks first, then cheap model gates, then an LLM judge on a sample, then humans on disagreements.
- Judges are measured against human labels with kappa and per-class TPR/TNR.
- No LLM grades a learner. Checkpoints are deterministic or human-reviewed.
- Every card has a `when_it_fails` section; heuristics are defaults, not laws.
- Every source claim starts `unverified` and moves only with a primary source or a committed replication.

### 8.4 Cost control

- Estimate before running; abort before exceeding the cap.
- Every run records prompt, completion, reasoning, and total tokens, plus USD and the cap.
- Fixture mode is free and offline; live mode requires an explicit key and a pinned model.
- Reasoning tokens are billed and count against the cap.

### 8.5 Transparency

- Append-only journal; corrections are new entries.
- Failed and aborted runs are committed, not deleted.
- Every public number links to its run and cost.
- The architecture process itself is logged, including the 2.61 USD wasted on empty reasoning calls.

---

## 9. Decision register summary

The full rationale is in `DECISIONS.md`. This is the management view.

| ID | Decision | Status | What it means / next |
|---|---|---|---|
| OD-01 | Model selection and price pinning | RESOLVED | Roles, cheap-first; exact IDs pinned per run in T-036. Model choice is a lab variable. |
| OD-02 | Smoke-suite total cap | RESOLVED | 5.00 USD for the live smoke suite; revisit only if T-036's estimate is unrealistic. |
| OD-03 | Per-run cap and daily budget | RESOLVED | 2.00 USD hard per run; 1.00 USD soft daily; exceptions logged. |
| OD-04 | Confidence-interval method | RESOLVED | Wilson for proportions; bootstrap (10k, seed 1337) for paired/continuous quantities. |
| OD-05 | Prediction-gate timing | RESOLVED | Prediction must be committed; `written_at` ≤ commit time < run start. Uncommitted predictions refuse to run. |
| OD-06 | Ledger verification authority | RESOLVED | Named human reviewer; primary source or committed replication; no LLM may set status. |
| OD-07 | Reasoning-token accounting | RESOLVED | Record as reported; `null` if unreported; include in cost and cap. |
| OD-08 | Fixture runs in status | RESOLVED | Never count as live; never appear in RESULTS or README numbers. |
| OD-09 | Human-labeled datasets (E1, E7, E13) | DEFERRED | Revisit when E1/E7/E13 becomes runnable; those labs stay specified in v1. |
| OD-10 | Content license | RESOLVED | MIT code; CC BY 4.0 prose; CC0 synthetic data. |
| OD-11 | Commit the source PDF | RESOLVED | Commit the 288 KB PDF under `source/` in T-001; keep the text copy. |
| OD-12 | Who authors prediction/post-mortem | RESOLVED | The learner writes both; the harness only validates. |

### 9.1 Plain-language explanations of the less obvious decisions

**Smoke suite (OD-02).** A smoke suite is a small set of live calls across the runnable labs, used to prove the whole pipeline works end-to-end and to measure actual cost. It is not the full evaluation. The provisional cap is 5.00 USD; we confirm it at T-024/T-036, when there is a real estimate to compare against.

**Human labels (OD-09).** Some experiments compare model judgments with human judgments. That requires a person to label a sample. E1 (binary vs scale), E7 (jury vs single judge), and E13 (judge distillation) need this. The five runnable labs do not. The open question is who labels, how many items, and under what written guide.

**Confidence intervals (OD-04).** A single accuracy number from 100 test items is noisy. A 95% confidence interval gives a range that is likely to contain the true value. **Wilson** is a formula that behaves well for proportions, especially small samples and values near 0 or 1. **Bootstrap** resamples the data thousands of times and is better for paired differences or continuous quantities such as latency, where no simple formula exists. We use Wilson for accuracy/TPR/TNR/pass rates and bootstrap for deltas, and every metric records which method was used. This matters because a reported "0.80 vs 0.75" difference may be noise if the intervals overlap.

**The prediction gate (OD-05).** Before a run, the learner writes a prediction. The gate refuses to run without one. The open question is how to prove the prediction was written *before* the result, not after. Option A trusts the typed `written_at` timestamp: simple, but easy to fake. Option B requires the prediction to be committed to git first, then compares its commit time to the run start: stronger, with a little more friction. I propose Option B. It is a process control, not a model decision.

**The claim ledger (OD-06).** `PROVENANCE.md` lists claims with a status. `unverified` means "not checked yet". `verified` means a named human checked a primary source or replicated the claim in a committed run. `disputed` means credible evidence contradicts it. The question was who may change the status. The resolution: only a named human reviewer, never an LLM. A single passing run is not enough unless the reviewer signs off that the run is the primary evidence. This stops the course from teaching a claim merely because one model run agreed with it.

**Reasoning tokens (OD-07).** Some models think before answering. Those thinking tokens are billed and count against the output limit. If the provider reports them, we record them and include them in cost and cap checks. If the provider does not report them, we record `null`, not `0`, because `0` would falsely imply there was no reasoning. This matters: a model with mandatory reasoning can spend the entire budget before writing a single visible word, which is exactly what happened twice during the architecture calls.

**Fixture mode (OD-08).** A fixture is a saved or synthetic model response. Fixture mode runs the full pipeline offline and for free using those responses. It is for automated tests and for teaching the mechanics. It is not evidence about real model behavior. The resolution: fixture runs never count as live runs, never appear in `RESULTS.md`, and never contribute to public numbers. Only live runs do.

**Needs your decision now:** none. OD-09 is deferred until E1, E7, or E13 becomes runnable.

---

## 10. Risks and mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| Model/provider drift | A pinned model can change under you; a judge can silently shift. | Pin exact IDs and retrieval dates; freeze judge model/rubric; re-run regression on change. |
| Judge bias | Position, verbosity, self-preference, sycophancy can make metrics look better than reality. | Cross-family judges, order swaps, kappa/TPR/TNR, human spot-checks. |
| Cost overrun | Live experiments can multiply calls. | Estimate, hard cap, daily target, abort-on-cap, cost.json on every run. |
| Hardware limits | 6 GB VRAM invites unrealistic local-model plans. | API-only v1; explicit tiers; API fallback; no promised 7B local runs. |
| Spec drift | Inconsistent decision numbers already caused confusion. | One canonical OD register; traceability check; acceptance gate. |
| Copyright/licensing | The source PDF and datasets need clear terms. | Resolved licenses (OD-10); PDF committed with a documented fallback. |
| Credit/keys | Shared key, in-flight budget, accidental leakage. | Env-only key, secrets scan, no key in repo, top-up before live smoke. |
| Teaching the wrong lesson | A heuristic can be taught as a law. | `when_it_fails` on every card; unverified claims labeled; own-data replication. |

---

## 11. What happens next

### Immediate (no spend)

1. **T-001: DONE.** Git initialized, remote set, spec set/licences/PDF committed.
2. **T-002: DONE.** `uv`, Python 3.12, package skeleton, CLI, and tests.
3. **T-003: DONE.** Ignore rules and `.env.example`.
4. **T-004: DONE.** Secrets scanner and pre-commit hook.
5. **T-005: DONE.** Append-only journal check.
6. **T-006: DONE.** YAML/JSON Schema validation command.
7. **T-007: DONE.** Generated status and README consistency check.
8. **T-008: DONE.** Config loading and core models.

### Harness core (no spend until the live run)

9. **T-009 (next)-T-016:** hardware check, metrics, cost guard, fixture/live clients, run IDs and prediction gate, runner, post-mortem check.
10. **T-017, T-018, T-020:** E9 manifest, synthetic dataset and fixtures, E9 lab.
11. **T-025, T-028, T-029, T-034:** checkpoint grader, M-A1 module, level-A cards, learner guide.
12. **T-037:** one full learning loop with a live E9 run (estimated 0.40 USD).

### Then

13. **T-024/T-036:** pin models and prices, run the live smoke suite under the 5.00 USD cap.
14. Author the remaining cards and modules (T-028-T-033) and the final acceptance run (T-038).

### What I need from you

1. **No blocking decisions.** OD-02, OD-05, and the budget policy are approved; OD-09 is deferred.
2. **Git:** the local repo is pushed to `origin/main`; future pushes happen at ticket checkpoints.

No Opus calls will be made without your explicit approval.

---

## Appendix A — Glossary for a non-specialist

- **LLM:** large language model; the thing that generates text.
- **Prompt:** the instructions and context sent to the model.
- **Context window:** the finite text the model can see for one call.
- **RAG (retrieval-augmented generation):** fetching relevant documents and putting them in the context.
- **Tool / agent:** a tool is a function the model can call; an agent is a loop that decides which tools to call.
- **LLM judge:** using a model to score another model's output.
- **Kappa:** agreement between two labelers after correcting for chance. 0 is chance; 1 is perfect.
- **TPR / TNR:** true-positive rate and true-negative rate; how often a judge catches failures and clears successes.
- **Fixture:** a recorded or synthetic response used to run tests offline and for free.
- **Fine-tuning / SFT / DPO / RLVR:** ways to change a model's weights. v1 does not do these.
- **Token:** a piece of text the model reads or writes; billing and limits are in tokens.
- **Temperature / seed:** randomness controls. Low temperature and a fixed seed make runs more repeatable.
- **OpenRouter:** a gateway that exposes many models behind one API.
- **In-flight budget:** OpenRouter's limit on how much a request may pre-authorize at once, separate from your remaining balance.

---

## Appendix B — Architecture call summary

| Outcome | Calls | Cost (USD) |
|---|---:|---:|
| Empty content, reasoning-only | 2 | 2.607784 |
| Partial or complete content | 6 | 2.683092 |
| Rejected before execution (402) | 7 | 0.000000 |
| Direct diagnostic probe (not a run dir) | 1 | 0.000128 |
| **Total** | **16** | **5.290876** |

Full detail, including max tokens and finish reasons, is in `ops/OPUS_RUN_LOG.md`. Two further direct probes were rejected with 402 at zero cost.

---

## Appendix C — What "v1 done" means

The 20 acceptance checks cover:

- Python 3.12 and locked dependencies.
- Zero-network tests.
- JSON Schema validation.
- No secrets or forbidden files.
- Append-only journal.
- `status.json` and README consistency.
- Provenance ledger integrity.
- Traceability from source to card to experiment.
- Hardware-tier validity and API fallback.
- Cost caps.
- Fixture/live separation.
- Source provenance.
- Transparency artifacts agreeing with test state.
- README claims bounded by what acceptance proves.
- Assessment not dominated by a single unvalidated LLM judge.
- Complete logging for every live run.
- Clean-checkout reproduction.
- A final `aiu check-all` gate.

The exact commands are in `ACCEPTANCE.md`.
