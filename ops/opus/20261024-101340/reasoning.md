This is a massive deliverable requiring every file complete, with tight prose and no abbreviated schemas or tickets. I'm planning out the repo layout first, deciding on the structure of files like README, JOURNAL, DECISIONS, CONSTITUTION, and REPO_LAYOUT before building everything out.

I'm mapping out the full directory structure â config files, source assets, JSON schemas for curriculum and status, per-module and per-lab YAML manifests, datasets with their own docs, and the core Python package under src/aiu covering CLI, config, models, client, fixtures, cost tracking, running experiments, metrics, hardware, validation, status, and secrets checking, plus tests and experiment/learnings templates.

Now I'm figuring out where learner-specific state lives, like the trust table, and deciding to keep an ops/ directory minimal with just a secrets pattern list, a pre-commit hook script, and a smoke-test budget config rather than overbuilding it.

For the schema files, I'll place them under schemas/ as curriculum.schema.json and status.schema.json, noting the path choice in DECISIONS since it wasn't dictated. I'm designing the curriculum schema as a single JSON Schema (draft 2020-12) using oneOf definitions discriminated by a `kind` field (card/lab/module), validated with the jsonschema library.

Now I'm working through the card's required fields per section 4.4 â things like id, level, title, provenance, verify, misconceptions, experiment_id, and so on â plus metadata like schema_version, status, and module_id. I need a conditional rule requiring an `experiment_null_reason` field when experiment_id is null, and an id pattern like `^[A-F]-[0-9]{3}$`, though cross-checking that the level enum matches the id prefix will need to happen in the validator rather than pure JSON Schema.

I'm also planning semantic checks in validate.py â verifying id prefix matches level, file paths align, prerequisites exist, experiment_id resolves to a real lab, and there are no cycles. For provenance I'm defining an enum array with values S, K, or ADD, and for verify I'm structuring objects with claim, status, source, date, method, and ledger_id, requiring at least one verify entry whenever provenance includes "K" using a contains/if-then schema rule. For source_section I'm sketching an object with a section integer, an item label, and an optional lines field, since exact line numbers aren't available yet.

I'm working out a reference pattern like `^(1[01]|[1-9])\.[0-9]{1,2}$` so each card's source_section can point to a specific concept_map section and heading, and mapping out how many items exist per section â failure catalog items 7.1 through 7.16, section 8 items 8.1 through 8.8, and experiment references E1 through E13 in section 9.

I'm now enumerating every source item across sections 1 and 2 so each card can trace back precisely: section 1 covers the ten core ideas (output as function of context, decision difficulty, entropy, autoregressive ordering, biases, verbalized confidence, prompt vs capability, context cost, ambiguity ceiling, silent drift), while section 2 starts listing its own bullets like binary decomposition and evidence-before-verdict.

I continue counting through section 2's fourteen bullets, then move into section 3's fourteen items on tiered checking, workflows vs agents, routing, error compounding, verifiers, and related reliability concepts, before starting on section 4's items about error analysis, failure-category evaluators, and gold sets.

Rounding out section 4 to seventeen items with provenance, offline/online, agent evals, evaluating the evals, contamination, and per-category reporting. Then I sketch section 5 as a seven-item ladder covering prompt optimization, reasoning models, prompt versioning, fine-tuning/distillation, preference/RL, and synthetic data; section 6 as ten items on pretraining data, scaling, tokenization, post-training, label noise, data mix, infrastructure, ICL, interpretability, and small-model labs like nanochat; and I begin section 7 on failure modes with hallucinated facts, ungrounded claims, and ignored instructions.

I continue listing failure modes through sixteen entries -- format drift, truncation, wrong tool calls, tool loops, context overflow, sycophancy, refusal issues, prompt injection, reward hacking, stale knowledge, persona inconsistency, silent version changes, and judge failures. I map out section 8 as eight steps, section 9 as thirteen E-items plus a training-side list, section 10 as ten sources feeding provenance, and section 11 as meta-instructions, tallying roughly 110 concepts total, which means the traceability table will need about that many rows, one per bullet.

Now I'm working out how the source sections map to the A-F levels, noting that it's not a clean one-to-one mapping -- the failure catalog and debugging playbook from sections 7 and 8 need to become reference artifacts rather than fitting neatly into a single level, so I'm deciding whether to place them as YAML reference files or as cards themselves.

I'll use a "failure_catalog" kind with items array and a "playbook" kind with steps.

For card IDs, I'm numbering section 1 as A-001 through A-010, then section 2's 2.1â2.14 as B-001 through B-014, though a few of those later itemsâtaxonomy lifecycle, first upstream failure, rationale smellâneed special handling.

I'm keeping those three items in B for ontology fidelity, deciding the diagnostic one still belongs there. Then C covers section 4 (C-001âC-017), D covers section 3 (D-001âD-014), E covers section 5 (E-001âE-007), and F covers section 6 (F-001âF-010). I'm flagging that E's card IDs could be confused with the experiment labels since both use "E" but different formats, so I'll note that ambiguity as a decision point while still following the source's naming. Now I'm also thinking through which additional cards might need to be added.

A-011 already covers reproducibility, so no new card needed there. I'm adding C-018 for confidence intervals on small eval sets using the Wilson interval, since small gold sets need uncertainty quantification. I'm also working out where the debugging playbook from section 8 fitsâit spans levels, so rather than forcing it into A, I'll land on D-015 as a dedicated card for the debugging playbook's decision order.

For the failure catalog, I'll make it a reference file plus card C-018 for the failure-mode taxonomy, and keep one real addition, C-019, for uncertainty estimation on small eval setsâtrying to stay minimal on new cards rather than piling on extras like cost accounting.

Now I'm tallying card counts per level (A through F) to hit roughly 75 total, with 65 covering the core AâE concepts for v1, plus three exemplars, and I need to make sure the task list includes tickets for writing whatever's left.

I'm organizing cards into modules, grouping roughly 3-8 per module and assigning one authoring ticket per module, with DeepSeek drafting content and a human reviewer required before anything counts as truth. For level A I'm splitting into two modulesâone on context and decision difficulty, another on biases and failure attributionâand I'm starting to do the same grouping for level B, working through how to cleanly bucket taxonomy-building cards without awkward cross-level overlap.

For level C I've settled on four modules covering error analysis/gold sets, judge validation, judge operations, and production/agent evals, distributing the nineteen cards across them in groups of roughly 3-6. Now I'm moving on to figure out the module breakdown for level D.

D has 15 cards, which I split into four modules: tiered checks and workflows, cascades/verifiers/juries, context and retrieval, and production plumbing. For level E with 7 cards, I'm grouping them into two modules around the adaptation ladder and training-side adaptation, then starting to look at level F's grouping into two modules as well.

Now I'm counting up to 16 modules plus a capstone, and checking each has at least one runnable lab unless it's conceptual. Looking at the E labs specifically, I'm weighing whether E13 (judge distillation) counts as "training" given the locked rule that training-side labs stay conceptual in v1 -- since a TF-IDF logistic regression classifier runs on CPU without local models, it might still qualify as API-only and runnable rather than violate that constraint.

For v1, I'm picking a representative runnable subset so a learner can complete a full module: E1, E2, E4, E5, E9, E12 seem like solid candidates to include.

I need to keep smoke suite costs under $5 total and $2 per lab, using cheap models for quick runs at small sample sizes. I'm also wondering about pinning exact model IDs, since I can't fully verify current OpenRouter IDs given uncertainty about the date and my own knowledge cutoff.

The honest approach is to define roles in config/models.yaml with placeholder IDs the human must confirm, plus a verification ticket checking IDs against OpenRouter's models endpoint and fetching pricing. I'll set up roles like cheap_a, cheap_b, cheap_c for jury diversity, strong for ceiling testing, and judge_default, proposing candidate IDs as an open decision while pricing gets frozen into a dated config file.

Cost estimation should multiply calls by expected prompt and completion token costs, aborting if it exceeds the cap, and I can also track actual cost during runs since OpenRouter can return usage.cost when usage accounting is enabled via the request body. Still, I'll compute cost locally from pinned pricing as the source of truth and just record provider-reported cost when available as a cross-check.

For model IDs, I'm wary of hardcoding specific versions since they may be deprecated by 2026 â better to mark them as placeholders requiring human verification, with the config validator refusing to run in live mode if any ID is left unpinned, while fixture-mode tests remain unaffected by this constraint.

For fixtures themselves, since there's no way to record real outputs before any live run occurs, I'll start with hand-authored synthetic responses labeled as such, then allow re-recording from actual runs later via a `--record` flag that marks them as genuinely recorded rather than synthetic.

Fixture-derived metrics must never be presented as real measurements in RESULTS.md, and fixture runs should write to a gitignored local directory rather than the experiments folder, so only genuine live runs populate the official results. I'm also working out the fixture lookup scheme -- hashing the canonical request into a key and storing responses as JSONL entries keyed by that hash, including token usage and optional logprobs.

For network isolation in tests, I'm leaning toward writing a custom conftest guard rather than relying entirely on the pytest-socket plugin, since that gives more predictable control over blocking outbound connections during fixture-mode test runs.

For the HTTP client I'm settling on httpx hitting OpenRouter's chat completions endpoint, with bearer auth headers and optional referer/title headers, and I need to check which models support logprobs and seed params via the `supported_parameters` field for pin verification. I'm also sketching the CLI surface starting with a `doctor` command that checks Python version, uv, and API key presence.

Now I'm defining the remaining CLI commands: hardware tier checks, content validation, lab listing, prediction creation with a template file, and the run command with fixture/live modes, size options, and budget limits â enforcing that predictions must be filled in before live runs so the harness never leaks results prematurely.

I'm also sketching out cost estimation, postmortem validation, and lab closing logic, weighing whether to auto-edit RESULTS.md or instead generate result rows from a JSONL experiments index to keep things simpler and less error-prone.

I'm also planning `aiu status build/check` to regenerate status.json deterministically from repo state, plus smoke-mode budget caps, secrets scanning, and trust-table validation commands.

I still need `aiu trace check` for traceability coverage and `aiu ledger check` for provenance IDs, along with defining exit codes (0 ok through 6 missing precondition) and the run ID format combining timestamp, mode, size, and a random hex suffix. I'm also thinking through synthetic dataset licensing requirements.

Licensing needs a decision: default to CC-BY-4.0 for content and MIT for code, though that's flagged as open. I'm sketching out the datasets needed â a support tickets set with a 20-category taxonomy plus out-of-taxonomy items for cardinality and escape-hatch tests, and an answer-grading set with reference answers and human labels for comparing binary versus scaled scoring.

Since getting 500 human labels is costly, I'm proposing that synthetic items be built with labels determined by construction â perturbing a reference answer to create known-correct, missing-fact, or wrong-fact variants â tagged as "constructed" ground truth, with a 10% human spot-check required before live runs. I'm also planning a pairwise comparison dataset with deliberately injected factual errors and verbose padding for length-bias tests, and a needle-in-context dataset with key facts buried among distractors at varying positions.

For the ceiling-failures task, I'm designing a setup around a fictional company policy question tested under three conditions â cheap model without the policy context, cheap model with it, and strong model with it â so failures can be classified as context-driven, capability-driven, or genuinely ambiguous based on which condition resolves them.

For calibration (E11), I can reuse the support_tickets 8-label classification task, comparing verbalized confidence against token logprobs and sampling agreement at temperature 0.7, scored with ECE and Brier. For field order (E2) and jury evaluation (E7), the answer_grading_v1 binary task works well, measuring accuracy against constructed labels and cost/kappa respectively. Few-shot testing (E8) can similarly reuse support_tickets with a pool of examples.

For the cascade experiment (E10), I'll use support_tickets with a cheap model sampling three times, escalating on disagreement, sweeping agreement thresholds. E13 reuses answer_grading_v1 judge labels. This converges to roughly 3-4 core datasets: tickets_v1, grading_v1, pairwise_v1, and needle_v1, each stored as JSONL with pydantic models defining the exact fields -- I'm sketching out the schema for a tickets_v1 record now.

I'm designing the taxonomy structure for tickets_v1: a YAML file with 20 leaf labels under 5 coarse categories, plus views collapsing to cardinalities of 3, 5, 8, 12, and 20, where each view maps leaf labels to coarser labels and gold values derive from that mapping, with out-of-taxonomy items getting a null leaf and an "other" gold label when the escape hatch is available.

I swap the overlapping "bug_report_cosmetic" for "how_to_question" to keep the product group cleanly separated from technical, finalizing all 20 leaf names across the five groups. Then I start sketching the k12 view by merging pairs within each group into subcategories, like splitting billing into refund_or_dispute and billing_admin.

For k12 I try full merges but only get 10 categories, so I adjust by keeping technical's four leaves unmerged while merging the rest into pairs, giving exactly 12. For k8 I reduce furtherâbilling 2, account 2, technical down to 1, shipping 2, product 1âand I'm about to work out the coarser k5 and k3 groupings.

I'm deciding to treat out-of-taxonomy items like job applications, spam, and legal threats as gold "other," making up 15% of the test set, with an escape hatch using "other" and "unsure" labels where unsure abstentions get reported separately from correctness. For dataset sizing, I'm planning a test set of 200 items (170 in-taxonomy, 30 out-of-taxonomy), a dev set of 40, and an example pool of 60 split evenly between prototype and boundary cases.

For the smoke subset, I'm settling on a deterministic set of 20 items flagged `smoke: true` that must include at least 3 out-of-taxonomy cases. For the 300 synthetic tickets, I'm deciding these get constructed by writing content targeted at specific leaf labels, with human spot-checks required for quality. I'm also sketching the schema for grading items, including fields for id, question, reference, candidate, pass/fail label, defect type, anchored score, split, and smoke flag.

I want the knowledge base behind these questions to be fully synthetic and fictionalâsomething like a made-up company's internal docsâso there's zero contamination risk from the model's prior knowledge. Each question gets paired with candidate answers spanning different defect types, with label_pass derived directly from whether defect is none. For evaluating agreement across scoring methods, I'm planning to compare kappa scores between binary judgments, 1-5 scales, and anchored 1-5 scales, including how binarizing a 4+ score compares to the constructed binary label, and testing run-to-run variance by repeating each condition three times at temperature 0.7.

For stability measurement I'm leaning toward using temp 0 for the primary kappa calculation, but running the stability check with 3 repeats at temperature 0.7 with distinct seeds, since temp 0 repeats would likely be too uniform to reveal anything interesting about provider-level nondeterminism. That gives me a cost structure of 3 conditions times 4 total runs (1 baseline plus 3 repeats) times sample size.

Scaling up from a smoke test of 20 to a full run of n=120 brings the call count from roughly 240 to about 1440, which stays cheap enough with the lower-cost model (under a dollar). I'm treating these cost figures as assumed estimates pending real pricing confirmation, and defining Cohen's kappa with the standard observed-vs-expected agreement formula, flagging it as undefined if expected agreement hits 1 so I can report null rather than divide by zero. I'm also setting up the pairwise comparison logic for grading_v1, pairing good and defective candidate responses to the same question.

For the swap and verbosity experiments, I'm defining metrics like flip rate under AB/BA order swaps, position bias as deviation from 50% preference for the first answer, and verbosity effect as the accuracy drop when defective responses get padded with filler. I want pairs generated deterministically at run-time from grading_v1 using a seeded builder function, with filler sentences pulled from a fixed file so padding stays reproducible.

For the same-vs-cross-family experiment, I'm designing two generator roles from different model families that each answer a set of questions, then having judges from both families compare the pairs with order swaps to measure self-preference as the gap between how often each judge favors its own family's answers.

Now I'm deciding which labs to mark as fully runnable in v1 versus just specified for later -- settling on seven runnable labs (E1 through E5, E9, E12) while the rest stay specified-only with manifests and non-runnable status, trying to balance a complete backlog against keeping smoke-test costs low.

I'm also mapping each module to its anchor labs, making sure every module has at least one runnable lab unless it's purely conceptual: A1 ties to context/field-order labs, A2 to bias and ceiling tests, B1 to the binary/evidence lab, and so on through the rest of the taxonomy.

For B3, I'm proposing a new lab built around open/axial coding on forty traces â mostly manual work where the learner outputs a taxonomy plus coded traces, and the harness checks a saturation curve of new categories appearing every ten traces. Since this requires no API calls, it fits the zero-cost, human-only hardware tier, and it can double as supporting evidence for the error-analysis module as well.

For C2 on judge measurement, I'm sketching a judge validation lab covering kappa and TPR/TNR on a held-out gold set, reusing the grading pipeline and running judge evaluation across dev then test splits â this overlaps with earlier evaluator-building work, so I can share artifacts. For C3's mitigation stack, I'm noting that the same lab already covers the dev/test overfitting check and prevalence correction as straightforward math, while mitigation stacking itself is partially handled elsewhere.

For the offline/online and contamination module, I'm weighing whether agent evals with pass@k warrant a runnable lab or should stay conceptual, deciding agent environments are out of scope for v1 but offline regression testing could still fit into the capstone project. For the tiered checking module, I'm considering a lab that runs deterministic checks before model-based gates, possibly tied to ticket responses with formatting errors, and linking it to an existing playbook-card exercise.

Now I'm sketching the tiered checking lab in more concrete terms: run grading candidates through tier-1 deterministic checks (empty responses, length, reference-number regex mismatches) that catch a chunk of errors for free, then route the rest through a cheap judge, comparing cost and accuracy against judging everything. For the cascades/verifier/jury module I'm assigning existing exercises and making one of them runnable, and for the RAG/context engineering module I'm figuring out which exercise should serve as its lab.

For plumbing and guardrails, I'm leaning toward a fault-injection fixture that tests retry behavior under timeouts and rate limits, keeping it conceptual since it's cheap and offline. I'm also assigning the few-shot curve exercise as the runnable lab for the prompt optimization module, while marking the remaining modules and the capstone as conceptual, and starting to tally up which exercises count as runnable in version one.

Counting through the candidates, I land on roughly ten to twelve runnable labs, checking the smoke-test budget stays under a few dollars even with a stronger model included, then trimming down to a representative subset covering the core exercises plus a couple of lab tickets, folding one module's lab into an existing exercise to avoid redundancy.

I still need to fully flesh out each lab's procedure, metric, and pass/fail criteria in the lab spec index and corresponding tickets.

Since lab manifests get created from tickets, LAB_SPEC needs enough detail per lab to actually write those YAML files -- covering all 17 labs (E1-E13 plus L-001 through L-003), each with its own spec block.

For pass_fail, I need to separate run validity from hypothesis outcome: a `validity_gate` checks the run itself is sound (parse rate, completion count), while a separate `outcome_rule` determines whether results support or refute the source's claim using a confidence interval. The learner's lab grade isn't tied to whether the hypothesis was confirmed -- they pass based on whether they executed the methodology correctly, not on the scientific outcome.

With small samples, smoke runs will almost always come back inconclusive, so I'm explicitly labeling those "inconclusive (smoke)" since smoke runs exist to validate the pipeline, not generate findings -- full runs are what produce actual results. I'm using a paired bootstrap with 2000 resamples, fixed seed, and a 95% percentile interval, applying one uniform decision rule: supports if the CI excludes zero in the claimed direction, refutes if it excludes zero in the opposite direction, otherwise inconclusive. I'm also laying out the metrics module now, covering accuracy, kappa, sensitivity/specificity, flip rate, calibration error, Brier score, and confidence interval and correction methods.

For parsing model outputs, rather than relying on provider-specific structured output support (which varies and hurts portability), I'll prompt for JSON directly and use a tolerant parser that extracts the first JSON block, validates it, and counts failures separately as a tracked parse-failure rate rather than silently treating them as wrong answers. For classification tasks I'm keeping outputs to a simple normalized label field, stripped and lowercased, even in the reasoning condition.

Invalid labels get tracked separately as their own error category too. Prompts live as plain-text templates using simple variable substitution rather than a full templating engine for determinism, with each prompt version recorded via its content hash â and I'm deciding to keep execution sequential by default for reproducibility, since the full run only takes a few minutes anyway, leaving concurrency as an optional later addition.

For the larger experiment with 1200 calls, a sequential run would take around 40 minutes, so I want to support a configurable concurrency option using a thread pool while preserving result ordering. Before dispatching each call I need a budget guard that accounts for already-spent cost plus in-flight reserved cost plus the estimated max cost of the new call, aborting the run and marking it accordingly if the cap would be exceeded.

For token estimation without a real tokenizer, I'll use a conservative character-based approximation (chars divided by 3, rounded up) combined with per-token pricing from the config, which is already conservative enough that no extra safety multiplier is needed. If the total estimated cost exceeds the budget before the run even starts, I should abort immediately with exit code 4, and the budget flag can only lower the cap, never exceed the hard $2 ceiling.

For retries, I'll cap at 3 attempts on 429s, 5xx errors, or timeouts, using simple exponential backoff of 1, 2, 4 seconds without jitter, with a 60 second timeout per call, and I'll only bill usage from successful responses, not failed retry attempts. For logging, each call writes an entry into calls.jsonl within the run directory, capturing the request hash, role, model id, parameters, and other call details.

Since this is synthetic data with no PII concerns, I'll store full response text plus a sha256 hash of it rather than redacting anything. I also want to capture the model and provider actually returned by OpenRouter, since these can silently drift from what was requested, which ties into the earlier concern about model substitution â plus I should log the harness's git commit hash for reproducibility.

Now I'm working through the hardware check logic: using platform and disk usage utilities, adding psutil for RAM, and querying nvidia-smi via subprocess for GPU specs when available. For tier requirements, API_ONLY should basically always pass with just a disk space reserve check, while GPU tiers need actual hardware probing.

For the small-GPU tier I need to verify nvidia-smi is present, free VRAM covers the model weights plus headroom, total VRAM meets a floor, RAM is sufficient, and disk space remains after loading weights. The tiny CPU tier instead checks RAM against a multiple of weight size and caps parameter count. Since no v1 labs run locally yet, I'll still build out the check and test it with a mocked probe fixture, then move to validating the lab schema -- requiring an api_fallback block and local_requirements object whenever the tier isn't API_ONLY.

I also need to spec out how local runs record measured tokens/sec and peak VRAM/RAM in the result schema, testing this via a synthetic manifest fixture since no local labs exist yet. Then I'm designing a secrets-check command that scans tracked and staged files for API key patterns and forbidden file types (env files, keys, large binaries, model weights), falling back to a full repo walk if git isn't available, plus a pre-commit hook installer script to wire this into git hooks automatically.

For Windows compatibility, I'm noting Git for Windows bundles sh to run hooks, so a simple shebang-based shell script invoking the secrets-check command should work without requiring bash. I still need to decide whether to assume git and uv are pre-installed or add install steps using winget and the official install script, treating missing git as an open decision that should halt and ask a human rather than silently installing.

I'm now pinning the Python version to 3.12, planning to record the exact patch uv resolves to in the journal, and setting the requires-python range to span 3.11 through under 3.13. For dependencies, I'm settling on pydantic, pyyaml, jsonschema, httpx, and stdlib argparse instead of typer to cut down on third-party CLI tooling, plus psutil and python-dotenv for environment loading, with pytest and possibly ruff as dev dependencies.

I'm deciding against pulling in matplotlib for plotting â instead I'll emit a curve.csv and an ASCII table, deferring actual chart rendering to a future version. I'm also finalizing the lockfile approach with uv lock committing uv.lock, and laying out the pyproject structure: the package lives at src/aiu with a CLI entry point and hatchling as the build backend.

Now I'm starting to define the status.json schema, including a version field and a generated timestamp.

Writing status schema fields...

I still need to figure out how the tests field gets populated â whether `aiu status build` actually runs pytest itself or just reads results from a prior run.

So the flow is: run pytest with junit output, then feed that junit file into `aiu status build` to pull in test counts. And `aiu status check` should recompute everything except `generated_at` and `tests`, comparing against the stored file and failing with exit 1 on any mismatch.

For known gaps, I want them read from a manually maintained `ops/known_gaps.yaml` file so they persist across builds. Cumulative cost should sum `actual_usd_computed` across live experiment cost.json files, and the README's status table should be kept in sync by having `aiu status build` rewrite a marked block in README between `<!-- STATUS:BEGIN -->` markers, generated directly from status.json so there's no risk of drift.

For RESULTS.md, I need `aiu results check` to verify that every live run directory with a result.json has a matching row with the correct run_id, lab_id, and cost value. The PROVENANCE ledger needs a structured markdown table with P-00x IDs, claim text, source refs, tags, status, evidence, date, method, and card links, seeded with roughly one row per source bullet across all ~105 sourced claims, with verification checking that every card's ledger_id actually exists in the table.

I'm realizing status should default to "unverified" for everything initially â even [S] claims citing vendor blogs â since verification requires actually reading the source. Given PROVENANCE and TRACEABILITY both run ~110 rows plus ~40 task tickets, this output is going to be massive, so I need to define "verified" precisely: a claim counts as verified only when someone has located a primary source within 18 months of the verification date supporting the claim, or has replicated it directly.

Now I'm thinking through the trust table design â it should live in a committed `trust/rules_of_thumb.yaml` file rather than a personal learner file, with fields like rule_id, rule text, card_ids, source_tag, an evidence_strength enum (assumed/sourced/replicated_once/replicated_multi/refuted), replication_status, and run_ids to track actual experimental outcomes.

I'm also adding review scheduling fields: last_reviewed, next_review following a spaced-repetition cadence of 1/7/30/90 days, plus notes and a flag for failed replications. I'll register this as a `trust_table` kind in the curriculum schema, keep it as YAML without markdown rendering, and work out how spaced review prompts attach at the module level, then define the module schema itself with its id pattern, level, title, objective, and 3â8 card_ids.

For checkpoints I'm distinguishing deterministic versus human-reviewed types, with a description and optional check command, plus a portfolio artifact path pattern. I'm sketching how deterministic checks might work in practice, like a learner submitting a rubric.yaml with yes/no criteria and evidence fields, and deciding I need to implement an `aiu checkpoint` command for one demo module to prove the "complete one full module" acceptance criterion -- settling on M-B2 as that demo module.

I'm settling on M-B2 paired with lab E4 as the end-to-end demo, since it's cheap and clear. The checkpoint design becomes concrete: the learner writes a classifier_spec.yaml with at most seven labels including "other" and "unsure," each with an observable definition of at least ten words avoiding vague terms like "seems" or "good," plus boundary examples for confusable label pairs -- all checkable deterministically via `aiu checkpoint M-B2 --file ...`, alongside a completed postmortem for E4 with an updated trust table.

For other modules, I'll keep checkpoints human-reviewed with a binary rubric stored in the module YAML rather than trying to automate everything in v1, which stays consistent with the deterministic-where-possible philosophy. I'm also setting up the portfolio directory structure and picking card exemplars â A-004 on autoregressive ordering tied to E2, B-003 on escape hatches tied to E4, and C-004 on measuring the judge tied to L-002 â each needing full retrieval questions.

I still need to mark the A-004 claim about verdict-first fields causing post-hoc rationalization as unverified since it's a K-tagged claim lacking a ledger entry, and since the exemplar content is my own authoring it needs a draft review status pending human approval. I'm working out the card schema fields: kind, schema_version, content_version, review_status, module_id, experiment_null_reason, plus an assessment object with type and description, and exactly three retrieval questions as {q, a} pairs, with prerequisites required to point to existing cards.

Since exemplars like A-004 reference cards not yet written (A-001, A-003), I decide the semantic validator should check prerequisite IDs against the full planned card list in TRACEABILITY rather than requiring files to already exist, reserving the stricter existence check for `--strict` mode used at final acceptance. I'm also defining the experiment_id pattern to match either E1-E13 or L-series IDs, and sketching out the lab manifest schema fields including kind, schema_version, status, modes, and size configurations.

Now I'm working through the full experiment spec fields: id, title, hardware tier, hypothesis, concept_ids, dataset metadata, procedure steps, metrics with formulas, pass/fail gates, controls (held constant, varied, randomized), expected runtime and cost estimates, fixtures, and known confounds.

Then I'm moving to the harness architecture itself under src/aiu: a CLI dispatcher, repo-root path detection, config loading for models/pricing/budget via pydantic, and a content-loading module where I need to decide how JSON Schema and pydantic models coexist as sources of truth without duplicating validation logic.

Validation combines schema checks with semantic ones, while the client layer defines a common interface so a live OpenRouter client and a fixture-based client are interchangeable. I'm also sketching out fixture hashing, cost estimation with a budget guard, and a runner module that manages the full lifecycle of a run â setting up the run directory, checking predictions, writing config, executing the lab's run function, and recording metrics.

I'm then laying out the rest of the module structure: a labs package with individual lab files exposing a registry of run functions, plus metrics, dataset loaders with pydantic models, hardware detection, secrets checking, and supporting modules for status, results, tracing, ledgers, trust, checkpoints, and JSON parsing. Now I'm thinking through who actually authors the fixture responses for synthetic test fixtures, since hash-keyed fixtures require the implementer to generate them deliberately.

I'm designing an `aiu fixtures synth` command that dry-runs a lab through the FixtureClient to collect all requests it would make, then fills in responses using a per-lab deterministic synthetic responder that returns the correct answer for a hash-determined fraction of items and wrong answers otherwise. Since the responder needs access to the gold label but the request is hashed on content, I'm adding a `meta` field to ChatRequest that's excluded from the hash so lab modules can pass item identifiers through to the synthesizer.

I'm thinking through the accuracy threshold logic -- hashing the request to get a deterministic percentage, comparing against a configurable accuracy_pct per condition so synthetic fixture results differ across test conditions, which lets tests validate the metrics pipeline without needing real findings. Only smoke-size fixtures get committed to keep the repo small, with full-size fixtures generated on demand, and I'm weighing whether to add a `--record` option for capturing real live responses into a fixture file, though I might defer that to a later version since CI only needs the synthetic path.

Now I'm designing the prediction-locking workflow: `aiu lab predict` generates a prediction.md from a template, the learner fills it in, and `aiu lab run --mode live` validates that every required section has real content (no TODOs, no empty placeholder lines) before recording a SHA-256 hash and lock timestamp. If the file gets edited after locking, the hash check catches it, and critically there's no command exposing results before a prediction exists, preserving the integrity of the prediction-then-reveal structure.

I'm also sketching the post-run closure flow: after a run, a postmortem.md stub gets created, and `aiu lab close` validates it's filled out and references the run's trust-table entries, then writes a separate `closure.json` with closure timestamp, postmortem hash, and trust rule IDs rather than mutating result.json directly. Runs with recorded outcomes must be closed to show up as resolved in `results check`, while unclosed runs remain flagged as "open."

Now I'm outlining the templates: the postmortem needs fields for what happened, prediction-vs-outcome comparison, mechanism hypothesis, confounds, rule-of-thumb updates, cost, and next experiment; the prediction template needs lab, hypothesis, predicted numeric values per condition, confidence, reasoning, and what would change my mind.

With that settled, I'm starting to draft the ticket list for Phase 0 bootstrap, beginning with installing uv and a pinned Python version and verifying git, followed by scaffolding the repo layout and pyproject config.

I'm working through where to place the transparency docs and env/secrets setup -- deciding whether to fold doc materialization into the scaffold ticket or make it its own ticket, and settling on ordering git init, file materialization, and package scaffolding in sequence.

Then I'm sketching out the remaining tickets: a network guard for pytest, schema and semantic validation for content files, a hardware probe with tier checks, model/pricing config verification, a chat client abstraction with fixture support, and OpenRouter live integration.

Continuing the ticket list: cost estimation and budget guarding, a metrics library, parsing utilities, run lifecycle management with artifacts and locking, a fixture synthesizer/recorder, and dataset authoring and validation for tickets, grading, and needle-in-haystack datasets.

Then I'm outlining the remaining lab tasksâE1 through E13 covering various experiments, judge validation, tiered checking, offline error-analysis coding, specified-only manifests for the unbuilt labs, a completeness audit tying all labs to fixtures, and moving into the trust table schema.

From there I map out the check tickets: trust check, status build, results/ledger checks, traceability, plus reference files for the failure catalog and playbook. Then I start breaking down card-authoring work per moduleâroughly 16 modules each needing their own cards and YAML manifest, weighing whether to combine or split them into individual half-day tickets like M-A1, M-A2, M-B1, and so on.

To cut down the ticket count, I decide to group by level instead of per-moduleâso tickets A through F plus a capstone, about 7 tickets total instead of 18, since authoring a handful of cards per level is fast enough to combine. I also note remaining pieces: a checkpoint command, a smoke test suite capped at $5, a CI fixture test for clean checkouts, and something on the human side still to define.

I need a human-gated step for pinning models, a live smoke run requiring an API key and spend approval, a learner walkthrough for acceptance, and a final ticket running the full acceptance checksâbringing the total closer to 48 tickets. Each ticket will need to stay compact but complete, with dependencies only pointing to earlier tickets, and every DoD should require a JOURNAL.md entry plus a status.json update.

Since `aiu status build` only exists starting at T-036, earlier tickets would need fragile manual status.json edits â so I should move status build much earlier, around T-005, implementing it with simple glob-based counts over curriculum YAML and lab status fields before the full loaders exist. That way every ticket from T-005 onward can just run `uv run aiu status build` to update state consistently.

For T-001 through T-004, before status build exists, I'll treat status.json as manually unchanged unless a ticket explicitly touches a field like `known_gaps`, with each ticket's journal entry documenting that no automated status update applies yet.

Thinking about ordering: maybe T-001 should materialize the spec files themselves (including status.json) rather than bootstrap tooling, since writing files doesn't require toolchain setup, so I'm reconsidering which ticket comes first.

Laying out the rest of the ticket sequence: scaffold Python with version check and tests, build the status/README pipeline, add a network guard, create `.env.example` with a doctor command, then secrets scanning and git hooks â while making sure `.gitignore` and the concept map file get covered somewhere in these early tickets.

I realize the human needs to place `source/concept_map.txt` themselves since I can't see the original conversation text, so T-001 should verify the file exists with its expected marker before proceeding, flagging it as an open decision if missing. There's also the open question of whether to commit that text given licensing, and whether the repo should be public â plus I need to work out assumed per-model pricing to estimate costs for each lab.

Running the numbers, cheap classification calls cost roughly $0.01 for 120 calls, while strong calls cost about $0.009 each, making an E12 smoke test with 20 strong calls around $0.18 total â all cheap enough to note as "assumed" estimates in the lab spec. Now I'm defining the common model roles across labs: cheap_a as the default generator/classifier, cheap_b and cheap_c as different model families for diversity, strong as the escalation/ceiling model, and judge defaulting to cheap_b to ensure independence from cheap_a.

For E1, comparing binary versus scale grading, I'm setting up three conditions â plain binary pass/fail, unanchored 1-5 scale, and anchored 1-5 scale with level descriptions â run through the judge role at temp 0 for the primary pass plus three stability repeats at temp 0.7 with different seeds. I'm defining the JSON output formats for each condition, the binarization rule (score â¥4 counts as pass), and the kappa and stability metrics needed to compare them.

The outcome rule hinges on whether binary beats scale on both kappa and stability, validated through paired bootstrap confidence intervals on the kappa differences across items, gated by parse failure rate under 5% and full task completion, while flagging confounds like the fixed binarization threshold and the fact that labels aren't human-derived.

For E2, I'm setting up the field-order test â three JSON schemas (verdict-first, reasoning-first, evidence-first) graded by a cheap judge model at temperature 0, checking key order compliance via ordered parsing and measuring accuracy against gold labels to test whether reasoning/evidence-first prompts outperform verdict-first, while noting the confound that reasoning-capable models might think internally regardless of field order.

Moving to E3, I'm designing a cardinality test on in-taxonomy ticket classification across flat label counts of 3, 5, 8, 12, and 20, plus a hierarchical two-call approach (coarse then fine), using a cheap model with short max tokens and label definitions pulled from the taxonomy, scoring accuracy and macro-F1 per condition to test how label-set size affects classification accuracy.

I'm flagging that this claim is confounded since merging categories mechanically raises chance accuracy and removes confusable boundaries, so cardinality effects aren't isolatedâI need to note this when the test fails to support cleanly. For E4, I'm sketching an escape-hatch test adding out-of-taxonomy tickets to the test and smoke sets, though I'm worried a smoke set with too few OOT examples will give unreliable stats.

I'm revising the smoke composition to 15 in-taxonomy and 5 OOT, defining two conditions (with and without an escape hatch for other/unsure labels), and specifying the metrics: OOT error rate, in-taxonomy accuracy, and abstention rate on in-taxonomy items. The claim is that adding the hatch reduces OOT error at the cost of more in-taxonomy abstention, which I'll test via bootstrap confidence intervals over OOT items and report the accuracy tradeoff. Moving to E5, I'm setting up paired comparisons of good versus defective responses per question from the grading set, with sixty pairs total.

Now I'm designing the position and verbosity test with a smaller smoke set of 10, using original and swapped answer orderings plus a padded-verbose variant of the defective response, having a judge model output its reasoning and pick a winner. I'm defining metrics for accuracy, flip rate (inconsistency between swapped orderings), first-position bias rate, and the verbosity effect, with thresholds for supporting or refuting position bias based on confidence interval bounds, plus a mitigation approach that scores swap-consistent verdicts.

Then I move on to planning E6, comparing same-family versus cross-family judging by having two cheap models grade each other's generations and measuring self-preference bias, followed by E7's jury-of-judges setup comparing majority vote among cheap judges against a single strong judge using kappa agreement and cost metrics. For E8, I'm sketching a few-shot learning curve experiment across shot counts and example types, with deterministic seeded example selection balanced across labels.

Since 2 shots can't cover all 12 labels, I'll shuffle the pool by seed 0 and take the first k per type, keeping the same static example set across all items. I'm defining the accuracy metrics and expected claim that boundary examples outperform prototypes at equal k, while flagging label balance and ordering as confounds. Then I start outlining E9, a context-distractor experiment with a fictional-fact question embedded among varying numbers of distractors at different positions.

Scoring for needle_v1 uses exact-match normalized against the gold answer, with items including a key passage plus 16 distractor passages split into "near" (topic-similar but wrong entity) and "far" categories, where each D condition pulls from a predefined interleaved list. I'm sizing the token budget for D=16 at roughly 2700 tokens, which is manageable, and settling on accuracy as the metric with the core claim being that accuracy drops meaningfully as distractors increase, especially with the key passage buried in the middle.

For the test set I'm planning 80 full items with a 10-item smoke test, and flagging a confound: modern models tend to be robust at short 3k-token contexts, so lost-in-the-middle effects might not surface at this scale.

Moving to E10's cascade design, I'm working out the ticket triage test using the full set with k=5 or k=12 difficulty settings, sampling the cheap model 3 times at temperature 0.7 across different seeds plus a temp-0 pass, then taking majority vote to get an agreement score. The strong model answers every item once at temp 0 so I can sweep escalation thresholds offline while still reporting costs as if only escalated items were paid for, with escalation triggered when agreement falls below a threshold or the majority label is "unsure" or "other."

I'm defining four policies â no escalation, escalate below 2/3 agreement, escalate below 1/3 agreement, and always use the strong model â then computing cost (cheap sampling cost plus strong cost only on escalated items) and accuracy for each, outputting a frontier CSV; my hypothesis is some policy will land within 2 accuracy points of the always-strong baseline at under half the cost, while noting that running strong on everything is actually more expensive than a real cascade would be.

For E11 I'm specifying a calibration test on ticket classification using verbalized confidence, first-token logprobs, and 5-sample agreement, scored with 10-bin ECE and Brier score.

Then for E12, the ceiling test splits into three conditions on the needle task â cheap model without the key passage, cheap model with the key passage plus distractors, and strong model with the oracle context â so I can separate whether C1 failures are due to missing context (fixed when C2 succeeds) or a genuine capability gap (fixed only when C3 succeeds).

Failures where even the strong oracle model gets it wrong go into an unresolved bucket for human review, likely flagging either a real capability limit or label ambiguity. I'm also noting that since needle questions are designed to be answerable only from the passage, failing without the passage is expected and just illustrates the context lesson â to actually isolate capability limits I should add 2-hop items that require combining two passages, since those are more likely to expose genuine reasoning limits; the dataset already has a hops field distinguishing 1-hop from 2-hop items.

I'm defining the failure-attribution metrics and a claim to test: that most failures stem from missing context rather than capability, meaning the fixed_by_context share should be at least 0.5. Unresolved items get written out to a review queue file for human ambiguity checks.

E13, judge distillation, I'm leaving as a specified but not yet runnable experiment.

Finally I'm sketching L-001, an offline error-analysis exercise using 60 synthetic support-bot traces with seeded failure modes from a catalog, where the learner does open coding on the traces while the true labels stay hidden in a separate file.

I'm defining the coding output format and the metrics the harness computes: how fast new failure categories saturate across blocks of ten traces, how well the learner's self-defined categories map onto the real seeded failure modes, and how accurately they identify the first upstream failing step compared to the constructed ground truth. This costs nothing since it's offline with no API calls required, and I'm adding a "step" structure (retrieve, generate, format) to the traces to support that upstream-failure analysis. I'm deciding this needs its own dataset ticket rather than folding it into T-020.

Then I start sketching L-002, a judge validation exercise splitting the grading dataset into 40 dev and 120 test examples.

For L-003, I'm designing tiered checking: deterministic tier1 filters catch obvious fails before invoking the judge â empty/short responses, numeric mismatches against the reference, and off-topic answers with no content-word overlap with the question. Anything passing tier1 then goes to the LLM judge for binary grading.

I want to compare judge_all against the tiered approach on accuracy, kappa, LLM calls, cost, and tier1 precision, with the hypothesis that tiering gets nearly the same accuracy for much lower cost. I'm also defining the defect taxonomy â none, missing_key_fact, wrong_fact (including number swaps), unsupported_claim, off_topic, truncated â so some defect types are deliberately catchable by the deterministic checks.

Now I'm designing the dataset itself: a knowledge base of 30 fictional Northwind Labs product docs, 40 questions each with 4 candidate answers (one clean pass, plus a mix of pass/fail variants), split 10/30 questions into dev/test (40/120 items) to avoid leakage. I'm aiming for roughly 50% pass prevalence per question, balancing two passing candidates (concise and paraphrased) against two failing ones with distinct defect types.

I'm also sketching pairing structure for grading (60 test pairs plus a smoke set of 10), confirming each of 5 defect types appears at least 12 times, and deciding to drop anchored_score since there's no human rating scale here. For tickets_v1, I'm sizing it at 300 items (200 test, 40 dev, 60 examples split into 30 prototype and 30 boundary cases tagged with confusable_with labels). For needle_v1, I'm planning 80 items (60 single-hop, 20 two-hop), each with question, answer, aliases, key passages, and near/far distractors, using normalized exact-match scoring against the answer or any alias.

For traces_v1, I'm designing 60 traces with retrieve/generate/format steps and a hidden labels file marking failure modes, seeding 8 failure types across 45 traces while keeping 15 clean. I'm using fictional entities throughout to avoid contamination, with near-distractors referencing similar fictional entities with different values, and defaulting dataset licensing to CC-BY-4.0 since the content is synthetically authored for this repo.

For provenance, I'm requiring fields like `generated_by`, `label_origin: constructed`, and `human_spot_check: pending`, then gating live full-size runs to refuse unless the dataset manifest shows `spot_check.status == passed` -- smoke runs can proceed but must flag `dataset_spot_checked: false` in the results. Now I'm sketching the dataset manifest structure with name, version, and description fields.

I need to add a `dataset` schema kind, build pydantic validation models in `aiu/datasets.py` so `aiu validate` checks JSONL files against counts and structure, and decide that implementers author JSONL datasets directly while tests enforce count constraints. Then I start drafting ACCEPTANCE.md with concrete checks like AC-01, specifying the clean checkout and sync/test commands and their expected outcomes.

Continuing the list, I'm defining AC-02 through AC-11 covering network isolation, strict validation, trace coverage, lab audits for E1-E13, fixture runs, secrets checks, ledger verification claims, status/results checks, and a human-run live smoke test.

AC-12 requires run artifacts capturing model id, params, seed, cost, and timestamp, verifiable via artifact checks. AC-13 and AC-14 cover module completion checkpoints and hardware tier checks, while AC-15 ensures no unvalidated LLM judge is used for grading by prohibiting that field in the assessment schema.

On the governance side, I need to define content versioning (semver on card content plus schema version), a review workflow requiring human initials and date, and a verification queue tracking provenance status.

I'm also mapping out the re-verification interval, experiment log and trust-table formats, journal rules, and ADR-based change control with a redaction policy. The README functions as a living front page tied to the STATUS block, the journal starts with a genesis entry, and I need to check whether CHANGELOG.md is actually required by the deliverables list or just implied by section 4.7.

I'll fold CHANGELOG.md in anyway since extras seem allowed under "produce every deliverable listed." For the experiments template folder, I'm figuring out which files to include â prediction.md, postmortem.md, config.json, result.json, metrics.json, cost.json â and whether to define explicit schemas for each alongside a README describing the structure.

I need to add run artifact definitions to schemas/run_artifacts.schema.json, since the harness writes these via pydantic and results get validated against it, with templates documented in LAB_SPEC. I also need a status.json with its own schema file, and I have to carefully set its initial values â card counts by level, module/lab/test counts, cost, and provenance counts like total and unverified claims â making sure these numbers match what I'll actually have in the claim ledger once I count the rows.

For the ledger itself, I'm deciding to assign one row per source bullet across the main sections rather than tracking every sub-claim separately, treating the catalog and playbook as single aggregated rows since they aren't individually tagged claims, while giving numeric claims their own distinct rows. I'm now working through assigning P-IDs to each source bullet in section 1, starting with claims about output being a function of context and about binary/scale/pairwise comparison methods.

defaults change silently; pin and re-run. Section 2: binary pass/fail is most reliable since scales add run-to-run disagreement and alignment degrades with granularity, so decision trees of binary checks beat holistic scales -- replace 1-5 ratings with 3-6 binary questions. I also want to require quoted evidence per criterion, build in an escape hatch to avoid forced misclassification, and flag that overlapping categories are the top cause of inconsistent classification.

Observable criteria beat vague vibe-based definitions, and accuracy drops as label count grows, so I should cap at seven labels or go hierarchical. Boundary few-shot examples outperform prototypical ones, while unanchored scales tend to collapse toward the middle. Swapping order and requiring the verdict to survive the swap helps, and pairwise comparisons are easier than absolute judgments, with reference-based beating reference-free. Structured outputs guarantee valid syntax but not correctness, and field order plus enum descriptions can shift accuracy. I should design abstention and escalation routes, use open-to-axial coding across 50-100 traces until saturation, label the earliest failing step since downstream errors are just consequences, and watch for rationales longer than the rubric as a sign the rubric itself is under-specified.

Moving into section three, I'm noting a tiered checking structure, judging on a 5-20% sample, and ordering cheap deterministic checks first. I prefer workflows over agents per Anthropic's guidance, use cascades with escalation and threshold sweeps, and account for error compoundingâfive steps at 95% accuracy each nets roughly 77% overall, assuming independence. There's an asymmetry between verifying and generating, self-consistency works best for discrete answers but costs N times more, and a jury of three small diverse models can beat a single large judge, especially when the judge comes from a different model family to reduce self-preference bias. For RAG, I should evaluate retrieval and generation separately, using hybrid search, reranking, chunking, query rewriting, and contextual enrichment. I'm also considering context engineering with stable prefixes for caching, tool design principles, and reliability plumbing.

Now in section four, I'm starting with error analysis firstâdevelopers spend 60-80% of dev time on error analysis and evaluationâbuilding one evaluator per failure category rather than using judges for one-off bugs. A gold set needs 200-500 real traces with binary labels plus notes, and judge quality should be measured with kappa alongside TPR/TNR, requiring 85-90% agreement before gating with kappa below 0.6 as an alarm threshold. There's a notable gap between exact-match and kappa scoresâ33-41 points on MT-Bench per a 2026 studyâplus severe position bias despite high test-retest reliability, with judge rankings shifting up to 14 positions. Swapping order combined with chain-of-thought and a rubric gave the biggest gains, while chain-of-thought alone helped universally. I should freeze the judge model, rubric, and temperature, re-validating whenever anything changes.

I'm continuing through section four: using a dev/test split for the judge prompt, treating 100% pass rates as a sign the eval is too easy, applying prevalence correction with TPR/TNR, and distinguishing offline versus online evaluation flywheels. For agent evals, outcome matters versus trajectory, and pass@k differs from pass^k. I also need to eval the evals themselves using seeded known items and perturbations, watch for contamination, and report results per category.

Moving into section five, I'm noting the adaptation ladder's intended order, that prompt optimization requires a trustworthy metric plus a held-out set, and guidance specific to reasoning models. Prompt versioning needs regression testing, fine-tuning works well for narrow tasks but won't reliably inject new facts, and DPO shapes style while RLVR improves checkable tasksâthough it risks reward hacking.

Now I'm moving to synthetic data filtering and deduplication, noting the collapse risk, then tagging sections six through eight: nine knowledge rows and one skill row in section six, a single knowledge row cataloging section seven, and one untagged-to-knowledge row for the playbook in section eight. I'm recounting totals across all sections to confirm the row numbering lands at 82 total entries, then starting to assign precise IDs to each item in section fourâcovering error analysis priorities, pass rate thresholds, kappa and TPR/TNR benchmarks, and specific numeric targets for each sub-point.

Continuing the ID assignment through sections four, five, and six, labeling each as knowledge or skill, then finishing section seven and the untagged section eight entry. I'm also realizing I should add claims from the ADD card to the ledger too, starting with a Wilson interval note I'm contributing myself and a new entry about confidence intervals on proportions being unreliable when sample sizes are small.

I'm deciding there's only one genuine ADD row since the other sources trace back to the catalog and playbook, bringing the total to 83 claims, and I'm debating whether to mark the arithmetic claim as verified through direct computation given the independence assumption involved.

Actually, I'll keep all 83 as unverified since no real verification has been performed yet â that's the more honest stance. Now I'm tracing through the exemplar cards, mapping each one to its corresponding P-ID for verification: A-004 traces to P-005, B-003's escape hatch example links to P-017 and relates to P-026, and C-004's "measure the judge" card needs its own verification source traced.

I'm also double-checking that card IDs map correctly to their sections â C-001 through C-019 line up with sections 4.1 through 4.17 plus the catalog and ADD CIs, B-001 through B-014 map to 2.1 through 2.14, and A-001 through A-010 correspond to 1.1 through 1.10. Everything checks out consistently across modules.

Now I'm mapping out D-001 through D-014 to sections 3.1-3.14 plus D-015 for the playbook, E-001 through E-007 to 5.1-5.7, and F-001 through F-010 to 6.1-6.10, bringing the total card count to 75 across all categories. I'm also cross-referencing which cards and lab exercises belong to each module, like module A1 on context and module A2 on biases and confidence, making sure the assignments are consistent with the earlier mapping.

I'm continuing this module-by-module mapping, assigning cards B-003 through B-011 to the label sets module, B-012 through B-014 to the taxonomy module with lab L-001, and various C-series cards to modules covering error analysis, judge validation, and operating judges, each tied to their respective lab exercises like L-001 and L-002.

Moving into the D-series, I'm grouping checks-before-judges cards under D-001/D-002/D-004/D-015 with lab L-003, cascades and juries under D-003 through D-008 with lab E10, context/retrieval engineering under D-009 through D-011 with lab E9, and production plumbing as conceptual since fault injection is deferred. Then E-001 through E-004 go into the ladder-climbing module with lab E8, while E-005 through E-007 on training-side adaptation stay conceptual since there's no training component.

For the F-series I'm sorting through the pretraining data, scaling, tokenization, post-training, infra, ICL, interpretability, and small-model-labs cards, settling on F-001/F-002/F-005/F-006 for data-and-scaling and F-003/F-004/F-007/F-008/F-009/F-010 for mechanics-and-post-training. For the capstone I'm picking integrating cards across clusters â C-003, C-004, D-001, D-003, C-013, D-015 â making sure the card_ids count still falls within the 3-8 range even for the capstone module.

I'm deciding to leave the capstone lab (L-004) status as "specified" rather than fully implemented, since v1 only requires one module to be runnable and building out the actual scaffolding/harness for a learner-built app is out of scope right now. Now I'm starting to map each card to its experiment_id, going through A-001, A-002, etc., assigning either an experiment ID or null with justification.

Continuing through the mapping, I'm working out trickier cases like A-009 and A-010 where ambiguity and drift make a clean experiment assignment hardâleaning toward E12 for the unresolved-review bucket on A-009, and null for A-010 since v1 lacks a controlled experiment for drift. Moving into the B-series cards now, I'm similarly assigning experiment IDs, pausing on B-004 where the MECE categorization is unclear between E3 and E4 and settling on E3 with a note.

Now I'm reasoning through B-004 again, deciding MECE should actually be checked via checkpoint lint rather than a single experiment, then settling on E3 since merged views remove confusable boundaries. I continue mapping B-005 through B-014, adding a new metric to L-002 for rationale-to-rubric word ratio, then move into the C-series cards, assigning evaluators like L-001 and L-003 and reasoning about C-006's connection to position bias under E5.

I settle on using E5 for C-006 since it reveals flips despite determinism, and work through C-007 through C-012, including deciding to flag a `ceiling_effect` whenever any accuracy metric hits 1.0 rather than null that case out. I mark C-013 and C-014 as out of scope for v1, and start considering C-015 as a meta-eval question about seeding known-bad cases under L-003 tier one.

Continuing, I map C-016 as null since synthetic fictional data sidesteps contamination concerns without direct experimentation, settle C-017 on a confusion matrix output under E3, and assign C-018 and C-019 to L-001 and L-002 respectively. Moving into the D-series, I place D-001 under L-003, mark D-002 and D-004 null given agent and multi-step pipeline work is deferred, and work through D-003, D-005 through D-009, landing on things like self-consistency sampling for D-006 and deferring the best-of-N plus verifier lab to v1.1 for D-005.

For D-010 through D-015, I note E9 covers generation given retrieved passages but not retrieval evaluation itself, defer tool design and guardrails labs to null, and assign D-013 to a cost lever around cheaper models and D-015 to E12. In the E-series I map E-001 to E8, defer prompt optimization and reasoning-model cost control to null, tie E-004 to prompt hash versioning and regression under L-002, and assign E-005 to E13 while leaving E-006 and E-007 null. For Track F, I mark everything conceptual and null except F-005's label noise issue under E13 and F-008's in-context learning under E8, with F-003's tokenization item left null. Finally, I note the traceability section also needs to map section 7 items to failure catalog IDs FM-01 through FM-16, along with card C-018.

Section 8's steps connect to D-015 plus step IDs PB-1 through PB-8 and their related cards, section 9's E1-E13 map to lab IDs while its training-side content stays out of scope as read-only conceptual material under Track F, section 10 points to PROVENANCE sources, and section 11 ties to the CONSTITUTION schema. For L-001's seeded failure modes, I'm selecting eight: hallucinated facts, ungrounded claims, ignored instructions, format drift, truncation, sycophancy, prompt injection via retrieved content, and stale knowledge â now laying out the full failure catalog definitions for FM-01 through FM-06 and beyond.

I'm rounding out the catalog through FM-16 (covering tool loops, context overflow, over/under-refusal, reward hacking, persona drift, silent version changes, and judge failures), then mapping coverage to specific labs and tracking which playbook steps correspond to which cards. Now I'm starting to draft the ADR decisions list, beginning with repo layout, CLI structure, and content format choices.

Continuing through the ADRs: card schema validation separation, source reference and ID schemes, target card counts by category, model role indirection with pinned config, and the pricing/cost computation approach using OpenRouter snapshots as the basis for authoritative local cost calculation.

ADR-010 sets a hard $2/lab budget cap and $5 smoke cap with pre-run estimates and running guards. ADR-011 through 013 cover hash-keyed fixtures distinguishing synthetic from recorded data, smoke-only commits, and treating fixture runs as non-findings written to a gitignored directory, with ADR-013 adding network-free testing via a socket guard. ADR-014 and 015 establish sequential HTTP by default with a 4-thread concurrency cap, and tolerant JSON extraction from prompts rather than relying on provider structured outputs.

I'm continuing through the remaining ADRs: synthetic fictional datasets with spot-check gates, metrics and bootstrap decision rules, hardware tier policy, prediction locking, no LLM judge for grading with enumerated checkpoint types, generated transparency artifacts (status.json, README blocks, RESULTS checks), pinned Python 3.12 via uv, no plotting dependencies in favor of CSV outputs, a runnable lab subset, temperature/seed policy, versioned prompt templates hashed by sha256, secrets/forbidden file hooks, and UTC ISO-8601 timestamps throughout.

Now I'm sketching out the schema shapes for cost tracking (budget vs actual spend by role, retries, pricing snapshot), the run config (model pins, seeds, prompt hashes, dataset checksums, hardware probes), and the result file (status, call counts, validity fields).

I'm also outlining metrics.json with per-condition confidence intervals and comparison diffs, plus the calls.jsonl log for raw call records.

Now I'm defining the seeding and ordering rulesâbootstrap seed 0 with 2000 resamples, items sorted by id, and a smoke subset flagged separatelyâalong with the exit codes and the pydantic schemas for ChatRequest and ChatResponse covering roles, messages, sampling params, and metadata.

I'm specifying the canonical hash computation, which serializes the core request fields to a sorted, compact JSON string and hashes it with SHA-256 for deduplication, plus the fixture line format storing request hashes alongside cached responses and their origin and timestamp, and the fixture storage path convention.

I'm now sketching the OpenRouter request/response shape, noting that I'm uncertain about exact optional fields like cost and provider so I should tolerate missing data, and I'm also outlining the models endpoint response structure, flagging that I need to verify whether the pricing strings are truly USD-per-token.

I'm working out the lab directory and module naming convention, with a registry mapping lab IDs to Python module paths, and sketching a LabContext object holding the manifest, client, budget guard, and logger, plus the per-lab plan/run function interface.

For labs with dependent calls like hierarchical prediction or escalation chains, I realize the static plan can't fully predict later calls, so I'm considering an upper-bound estimate function and a fixture-synthesis approach using a synthetic client that generates responses on the fly while recording them for future replay.

Running each lab in "synthesize" mode handles the dependency issue cleanly â the client returns the lab's own synthetic response and records a fixture as it goes. I'm now thinking through how to specify deterministic synthetic behaviors per lab so fixture tests can snapshot and assert specific values, with acceptance criteria being a clean exit code from the fixture run.

For testing, rather than a separate golden file I'll favor a determinism check â running the same fixture twice should produce byte-identical metrics.json, plus confirming all expected metric keys are present and outcome equals "not_a_finding." I need to make sure metrics.json stays free of timestamps so this determinism check actually holds, and I'm sketching a rule for synthetic accuracy keyed off the request hash and prediction.

I'm defining a deterministic hash-based simulation of model accuracy: using the first 8 hex digits of the request hash to derive a value between 0-999, I bucket outcomes into malformed (2% of cases), correct (based on per-condition probability p from LAB_SPEC), or deterministically wrong â where wrong picks the next label cyclically after gold in the sorted label list.

Now I'm counting the number of distinct prompt templates I need to write across all experiments â roughly 15 total covering E1 through E12 and the L-series labs, with some reused for shared label schemas like classification tasks.

Writing the classification prompt template...

Still writing prompt templates...

Continuing down, 2 means an incorrect fact appears, and 1 covers off-topic, empty, or cut-off answers, with anything scoring 4 or higher counting as a pass. I'm noting that gold-standard passing candidates could include both paraphrased-longer and concise versions. Now I'm moving to the second evaluation set with three templates.

These templates vary by output structure: one asks for verdict then reasoning with keys in a fixed order, another flips to reasoning then verdict, and a third adds an evidence quote before reasoning and verdict. They share the same base task phrasing as the binary evaluation, just with different field orderings. For the pairwise evaluation, I'm setting up a comparison where both candidate answers are judged against a reference answer, asking which is more correct and complete with a short justification and a winner pick between A and B.

For the retrieval-based question answering setup, I'm designing conditions that vary context quality: one with a noisy, distractor-heavy context where the key passage is buried among many irrelevant ones, another with a clean oracle context containing only the necessary passages, and a stronger model paired with the oracle context. This lets me isolate whether failures stem from weak context (fixed by cleaning it up) versus model capability limits.

For sizing, I'm planning 80 full items and a 10-item smoke test split across one-hop and two-hop questions, running the strongest condition only on cases where the cheaper setups already failed to keep costs down, while using an upper-bound estimate for budgeting. I'm also noting that the strong model may need a higher token limit if it's a reasoning model, so I'm bumping max_tokens up for that role.

For the judge setup, I'm using a binary evidence/verdict template with a rubric file, tracking rubric word counts, and defining a rationale-to-rubric ratio based on reasoning length versus rubric length. Then for the deterministic tier-1 checks, I'm specifying exact rules like flagging candidates under five words as too short, and checking for number mismatches by comparing numeric values extracted via regex between candidate and reference.

I'm also defining a content-overlap check that fails when candidate tokens share nothing meaningful with the question or reference, then layering a tier-2 judge using the baseline prompt on top. I'm realizing the number-mismatch check could flag good paraphrases that legitimately introduce new numeric details, which is a tradeoff worth noting as a limitation of the design.

For the classification experiment, I'm setting up cheap-model sampling at temperature 0.7 across three seeds versus strong-model deterministic runs across all 200 test items, computing per-policy costs from measured or fixture-based token pricing. I'm also laying out the in-tax and smoke-test splits for the other experiments â 170 full in-tax items with 15-item smoke subsets, and a 20-item ticket smoke set mixing in-tax and out-of-tax examples.

I'm now working through the remaining experiment sizes: grading smoke uses 20 items across five questions, L-002's dev/test splits are 40 full with 8/12 smoke subsets, and the pairwise comparison experiment uses 10 smoke pairs (from 5 questions) each with four presentation orderings, totaling 40 calls, plus a 10-item needle smoke set.

Tallying up call counts across all experiments at smoke scale â roughly 240 for E1, 60 for E2, 105 for E3, 40 for E4, 40 for E5, 105 for E8, 70 for E9, 80 for E10, 30 for E12, 20 for L-002, and 40 for L-003 â I'm getting about 830 total calls, which should cost around $0.5 given cheap models dominate the volume and only a handful of strong-model calls are needed.

For the full runs, I'm scaling these up (E1 to 1440 calls, E3 to over a thousand) but estimating total cost stays under $2 since strong-model usage remains capped even at full scale. At smoke scale with concurrency of 4 and about 2 seconds per call, the whole smoke suite should finish in roughly 2 minutes.

Now I'm drafting an example card for A-004, setting up its YAML metadata with the schema version, level, module id, and title fields.

Writing card fields...

I'm continuing the A-004 card: the one-liner explains why verdict-before-reasoning is a problem since a left-to-right model commits to a verdict before any supporting reasoning exists, making the reasoning that follows purely post-hoc rationalization. The why_it_matters section argues that field order in output schemas functions as a prompt, and putting the verdict first removes any chance for evidence to shape it, while an evidence-first format keeps judge errors traceable to specific wrong or missing quotes. I'm writing the decision_rule to say fields should be ordered evidence â reasoning â verdict.

Now I'm covering the failure modes: reasoning models that think invisibly before emitting output may show no field-order effect, trivial exact-match decisions gain nothing from reasoning-first, some providers reorder keys regardless of request, and unscoped reasoning fields can drift off-topic. I'm adding the provenance and verification fields, flagging the core claim as unverified and needing a dedicated experiment or primary source.

I'm also sketching the schema constraints for the verify entry, misconceptions list, and assessment type enum.

Now I'm drafting the escape hatch entry B-003: closed label sets need "other" and "unsure" options so out-of-scope or underspecified inputs aren't forced into wrong labels, since forced misclassification hides drift and inflates category counts, and hatch usage becomes a monitoring signal that can route to escalation.

Both hatch labels should route to escalation (B-011) with weekly volume review. I'm also noting failure modes: models might over-abstain on genuinely hard but in-taxonomy items, so I need to measure in-taxonomy abstain rate; if downstream routing always requires a concrete label, the hatch needs a default handler; "other" risks becoming an unreviewed dumping ground; and if the two hatch labels aren't acted on differently, they should be merged.

Now turning to C-004, measuring the judge itself: a judge is just another model under test, so I need to verify its agreement with human labels via Cohen's kappa plus per-class TPR/TNR on held-out data before trusting its output. The reasoning is that an unmeasured judge turns unknown error into false confidence â raw accuracy is misleading under class imbalance, since a judge that always predicts "pass" on a 90%-pass set scores 90% while catching nothing.

My decision rule: before gating releases on a judge, report accuracy, kappa, and TPR/TNR with confidence intervals on a held-out human-labeled set, treating kappa under 0.6 as not release-ready. I also need to flag failure modes â kappa becomes unstable at extreme prevalence, and small gold sets produce wide confidence intervals, so the thresholds need caveats.

Importantly, these thresholds are vendor guidance rather than established law, and since human labels are noisy themselves, a judge's agreement can't exceed inter-annotator agreement â so I need to verify against the right sources and prerequisites before writing the schema.

Now I'm setting up the JSON schema structure using oneOf with discriminated kind constants, draft 2020-12, and common definitions for IDs, dates, and source references. Writing schema JSON...

Still defining ID patterns...

I'm simplifying the ref pattern to allow section numbers with optional subsection digits, and considering whether to support whole-section references like "7.0" to denote an entire section.

For ADD items that don't map directly to a failure item, I'll require them to cite the nearest related section using a new `relation` field (direct or adjacent, defaulting to direct), plus a mandatory `add_justification` explaining the addition.

Now I'm sketching out the remaining schema pieces: model role enums, hardware tier conditions requiring fallback info, dataset definitions with naming patterns and spot-check status, trust table rules, and the failure catalog item structure.

I'm also planning the playbook schema with step IDs like PB-1 through PB-8, plus the module definition and status schema. Then I need to move into writing out the TASKS tickets with full sections, noting the working directory and that PowerShell commands should be used.

For acceptance tests, I'm defining the CLI output format precisely: validate should print "OK <n> file(s)" on success, or "ERROR <path>: <message>" lines followed by "FAILED <k> of <n> file(s)" on failure, so tickets can reference exact expected output.

I also need to spec `aiu status build` and `aiu status check` outputs, plus the JOURNAL entry template with fields for timestamp, intent, changes, commands, cost, and next steps. I'm unsure what date to use for the genesis entry since I don't know today's actual dateâI'll need to use a placeholder.

Adding more table rows...

I need to decide how the trace check validates refs â either hardcoding the source ref list separately or deriving it from TRACEABILITY itself, and settle on having the implementer copy refs into a plain text file. The rule then is that rows in scope levels AâE need a valid card reference or an explicit out-of-scope justification, while level F rows can remain planned. Next I'm moving on to GOVERNANCE, then TASK.

Drafting the first ticket, T-001, which materializes the approved spec files into the repo and initializes git: it needs to verify git is available, create the directory structure, write out every file exactly as specified in the approved message, and add a `.gitattributes` file to normalize line endings to LF.

I'm also figuring out the secrets check â since the spec requires scanning for forbidden content before any commit, but Python isn't installed yet at this stage, I'll add a quick PowerShell pattern match for API key strings right in T-001's steps, before the commit happens. Then the ticket verifies the human-provided concept map file exists and contains the expected header text, runs `git init`, stages everything, commits with message "J-0001 genesis spec", and appends a journal entry with a real timestamp plus updates to status.json.

Moving to T-002, I'm planning the uv and pinned Python setup â installing uv, verifying its version, installing Python 3.12 through uv, and confirming via a quick script that the interpreter reports version 3.12. The acceptance criteria will check exit codes and the printed version tuple, and I'll record the exact uv/Python versions in the journal while clearing the corresponding gaps from status.json. Then T-003 starts scaffolding the actual Python project files like pyproject.toml and .python-version.

Writing pyproject.toml...

Still writing config...

Now I'm setting up the gitignore to exclude environment files, caches, build artifacts, and model weights, then moving on to defining T-004's status build and check requirements along with how the README block should render.

For the CLI interface, I'm sketching out the status.py functions that compute status, render a README block, and write status files, plus the counting logic that tallies cards, modules, labs, runnable items, experiment runs, costs, provenance entries, and known gaps.

Since git_commit changes with every commit, I'm thinking status check should exclude generated_at, git_commit, and tests from its comparison, reading YAML files with safe_load and only pulling the kind, review status, and status fields without full schema validation. Now I'm drafting the README markdown table format between the STATUS:BEGIN/END markers.

The targets file confirms 75 cards, 18 modules, 17 labs. I'm also thinking the status check needs to exclude volatile fields like generated_at and git_commit when comparing, recomputing everything else deterministically. The README's "what works/doesn't" table is hand-maintained separately and must stay consistent with the governance rule for T-004's acceptance criteria.

For T-005, I'm planning the network guard test â a conftest fixture that patches socket connections and httpx requests so any outbound network call raises a NetworkBlockedError during tests.

Then for T-006, I'm sketching .env.example with the OpenRouter API key placeholder and a title field, plus a config loader that reads .env values without clobbering existing environment variables.

For the doctor command, I'm designing checks for Python version, uv availability, repo root, .env git-tracking status, API key presence, and disk space, each printing a PASS/FAIL/WARN line without ever leaking the actual key value -- and I want a test asserting the secret never appears in doctor's output.

Now I'm moving to T-007, planning a secrets and forbidden-files checker along with a corresponding git hook.

Writing forbidden.yaml patterns...

I'm realizing test fixtures shouldn't contain committed sample secrets â better to construct them at runtime via string concatenation so the scanner doesn't flag them, and the empty-value case in `.env.example` naturally passes the regex check since it requires at least one non-whitespace character after the equals sign, so no allowlist entry is needed there.

I also need to be careful that documentation examples describing the secret pattern don't themselves get flagged â using placeholder notation like building the key from a prefix plus repeated characters, or showing `<key>` in auth header examples, avoids accidentally matching the detection regex while still being illustrative.

For file scanning, I'm planning to enumerate tracked and untracked files (respecting gitignore) or staged files depending on mode, skip binary files by checking for NUL bytes early in content, and report findings as path:line plus pattern name without ever printing the actual matched secret text. The install hook script will write a pre-commit hook that runs the secrets check against staged files, and I also want to verify `.env` stays gitignored.

Next I'm defining T-008, content schema validation via `aiu validate`, with a function and CLI that check curriculum, module, lab, dataset, trust, and reference YAML files against the schema, testing both valid exemplar cards and deliberately broken ones. Then I start outlining T-009's semantic validation rules, beginning with the requirement that a card's id prefix matches its level and that its file path follows the level/id convention.

Now I'm working through the remaining semantic checks: duplicate ID detection across all content, prerequisite existence checks against a planned ID set or actual files depending on strict mode, cycle detection on prerequisites, valid experiment_id references into the 17 lab IDs, verify ledger_id consistency against PROVENANCE.md, module and lab cross-reference checks for card_ids, module_id, and concept_ids, and a check on lab hardware tier.

I'm defining a hardware tier fallback and requiring runnable labs to have a synthetic smoke fixture file, plus enforcing that assessment/checkpoint types can never be `llm_judge` via both schema and a grep-based lint. Now I'm moving to T-010, designing a HardwareProbe data model capturing OS, CPU, RAM, disk, and GPU details for the hardware check and tier validation logic.

I'm sketching the probe and tier-check functions, then the `aiu hw-check` CLI that prints the probe JSON and a pass/fail tier verdict with exit codes, testing against a fixture for the dev machine where API_ONLY passes and LOCAL_SMALL_GPU_6GB passes at 2.0GB weights but fails once weights grow to 3.5GB given the free VRAM budget.

I'm defining the hardware rules for LOCAL_SMALL_GPU_6GB (GPU presence, VRAM thresholds, weight size limits, context/batch constraints, free VRAM/disk margins, RAM minimum) and LOCAL_CPU_TINY (parameter count cap, available RAM relative to weight size, disk margin, expected token throughput).

I also need an `aiu lab audit` check ensuring every lab.yaml has a valid tier and local tiers specify an api_fallback, tested against a fixture lab.yaml outside the main labs directory. Local runs need measured tokens/sec and peak VRAM recorded under a `local_measurement` field whenever the tier isn't API_ONLY, with validation enforcing this (v1 has no local measurements yet).

Now moving to T-011, I'm setting up model, pricing, and budget configuration across models.yaml, pricing.yaml, budget.yaml, the config loader, and the `aiu models show`/`aiu models verify` commands, starting with the models.yaml schema.

Still writing config schema...

The judge role aliases to cheap_b to guarantee it's cross-family from cheap_a, with a constraint that cheap_a, cheap_b, and cheap_c must belong to distinct families once pinned. The pricing file tracks retrieval timestamp, source URL, and per-model token costs and context length, while the budget file sets hard caps for lab runs and smoke suites plus a token estimation ratio. I'm now thinking through `aiu models verify --write-pricing`, which hits the public models endpoint, confirms each pinned model id exists, writes fresh pricing data with a timestamp, and checks that labs' required parameters like seed are supported.

If a pinned model doesn't support seed, I'll warn; missing pinned ids should exit with an error, and unpinned roles should exit with a specific code pointing to the open decision about human pinning. I'm planning tests for config parsing, unpinned detection, and verification using a mocked HTTP transport with a canned models payload fixture.

For fixture mode, I need assumed pricing since there's no real pinning yet â I'll add an "assumed_role_prices" section to the pricing file with placeholder rates for cheap and strong roles, used during fixture runs or pre-pinning cost estimates. Now I'm moving into T-012, designing the chat client abstraction and its fixture implementation.

I'm defining the chat message/request/response types, a request hashing function, a ChatClient protocol with a complete method, and a FixtureClient that raises a specific error when no matching fixture is found. For T-013, I'm designing the real OpenRouter client with configurable timeout and retry settings, retrying on timeouts, connection errors, and specific server error codes with exponential backoff while honoring short Retry-After headers, raising provider errors on non-retryable client errors, and making sure the API key is never logged or exposed in its string representation. I'm also planning tests covering successful parsing, retry-then-success behavior, immediate failure on bad requests, and missing cost data.

Now for T-014, I'm working out token estimation and a BudgetGuard class that reserves and commits spending against a cap, along with a CLI estimate command, and defining the exact abort message format when a pre-run cost estimate exceeds the budget cap.


