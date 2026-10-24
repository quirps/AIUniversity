# LAB_SPEC.md — Lab kit

## 1. Modes
| Mode | Client | Network | Default out dir | Evidence class | Cost |
|---|---|---|---|---|---|
| `fixture` | FixtureClient | none | `.runs/` | `assumed` if fixtures synthetic, `measured` never | actual 0; estimate via `fixture_defaults` |
| `live` | OpenRouterClient | OpenRouter | `experiments/` | `measured` | pinned pricing |

Live mode preconditions (else exit 6): `OPENROUTER_API_KEY` set and non-empty; all roles used by the lab pinned (not `UNPINNED`); pricing present for each pinned model ID; `--cap` ≤ `caps.per_lab_usd`.

## 2. Learner workflow (exact commands, PowerShell, repo root)
```
uv run aiu lab new-run E9 --mode live          # prints RUN_ID; creates prediction.md
# edit experiments\E9\<RUN_ID>\prediction.md   # fill predicted_metrics BEFORE running
uv run aiu lab estimate E9
uv run aiu lab run E9 --run-id <RUN_ID> --mode live
# edit experiments\E9\<RUN_ID>\postmortem.md   # copied from template at run end
uv run aiu lab postmortem-check E9 --run-id <RUN_ID>
# add/update a row in learner\trust_table.yaml; add a row to RESULTS.md
uv run aiu validate learner
uv run aiu status --write
```

## 3. Runner algorithm (`aiu.runner.run_lab`)
1. Load manifest; require `status == runnable` (else exit 6).
2. Resolve out dir; verify prediction gate (ADR-016) (else exit 7); write `prediction.sha256`.
3. `aiu.hardware.check(tier)`; failure → exit 5.
4. Load dataset (apply `--limit`).
5. `plan()` → list of PlannedCall (deterministic order: item id, condition order in manifest, role order, sample).
6. Pre-run estimate; > cap → write `result.json` status `aborted_cost`, exit 4.
7. Write `config.json`.
8. For each call: guard check; call client; append to `responses.jsonl`; update cost.
9. `score()` → MetricsReport; evaluate `validity_checks` (all must hold) and `pass_fail`; set `evidence_class`.
10. Write `metrics.json`, `cost.json`, `result.json`; copy `experiments/_template/postmortem.md` to run dir with front matter `lab_id`, `run_id` filled.
11. Print exactly: `run_id=<id> status=<status> cost_usd=<actual:.4f>`; exit 0.

`pass_fail` metric names refer to keys in `metrics.json:metrics` (flat, e.g. `accuracy:oracle`). If any referenced metric is `None`, `hypothesis_supported = null`.

## 4. Hardware check
`aiu hwcheck --json` prints `{"tier":..., "passed":bool, "ram_total_gb":float, "ram_available_gb":float, "disk_free_gb":float, "gpu":{"name":str,"vram_total_gb":float,"vram_free_gb":float}|null, "warnings":[...], "failures":[...]}`. Thresholds per ADR-014. GPU via `nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits` (MiB → GB = /1024); missing binary → `gpu: null`.

## 5. Cost accounting
Per ADR-008. `cost.json` schema: `{estimated_usd, actual_usd, provider_reported_usd, calls, prompt_tokens, completion_tokens, cap_usd, aborted, pricing_retrieved_at, mode}`.

## 6. Lab index
| ID | Title | Status v1 | Tier | Roles | Cards | Calls (full) | Expected cost (assumed) |
|---|---|---|---|---|---|---|---|
| E1 | Binary vs scale judging | specified | API_ONLY | judge_a | A-002, B-001, B-008, C-003, C-005, C-010, A-009 | 900 | 0.60 |
| E2 | Schema field order | runnable | API_ONLY | cheap_a | A-004, B-002, B-010, B-014 | 240 | 0.25 |
| E3 | Label cardinality curve | specified | API_ONLY | cheap_a | A-003, B-006, C-017 | 880 | 0.50 |
| E4 | Escape hatch | runnable | API_ONLY | cheap_a | B-003 | 160 | 0.10 |
| E5 | Position and verbosity bias | runnable | API_ONLY | judge_a | A-005, B-009, C-006, C-008 | 160 | 0.15 |
| E6 | Same- vs cross-family judge | specified | API_ONLY | cheap_a, cheap_b, judge_a, judge_b | D-008 | 320 | 0.40 |
| E7 | Jury vs single judge | specified | API_ONLY | cheap_a, cheap_b, cheap_c, strong | C-004, C-007, D-007 | 400 | 1.20 |
| E8 | Few-shot curve | specified | API_ONLY | cheap_a | B-007, E-001 | 960 | 0.80 |
| E9 | Context distractors and position | runnable | API_ONLY | cheap_a | A-001, A-008, D-009, D-010 | 300 | 0.40 |
| E10 | Cascade threshold sweep | specified | API_ONLY | cheap_a, strong | B-011, D-001, D-003, D-013 | 400 | 1.00 |
| E11 | Calibration | specified | API_ONLY | cheap_a | A-006, D-006 | 600 | 0.40 |
| E12 | Ceiling test | specified | API_ONLY | strong | A-007 | ≤100 | 0.80 |
| E13 | Judge distillation | specified | API_ONLY | judge_a | E-005 | 500 | 0.40 |
| L-001 | Pinned replay and drift | specified | API_ONLY | cheap_a | A-010, C-009, E-004 | 240 | 0.25 |
| L-002 | Error analysis on traces | specified | API_ONLY | none | B-012, B-013, C-001, C-002 | 0 | 0.00 |
| L-003 | Eval statistics workbench | runnable | API_ONLY | none | C-012, C-014, C-015, C-019, D-004 | 0 | 0.00 |
| L-004 | Indirect prompt injection | specified | API_ONLY | cheap_a | D-014 | 160 | 0.15 |

Cost basis for all rows: `assumed` (ADR-022). `cost_cap_usd = 2.00` for every lab.
Licenses: all datasets are synthetic and authored for this repo; license = repo content license (OD-10).
`post_mortem_template` for every lab: `experiments/_template/postmortem.md`.

## 7. Modules
| Module | Title | Level | Cards | Labs | Conceptual |
|---|---|---|---|---|---|
| M-A1 | Context is the program | A | A-001, A-007, A-008, A-010 | E9, E12, L-001 | false |
| M-A2 | Difficulty, entropy, order, bias | A | A-002, A-003, A-004, A-005, A-006, A-009 | E2, E11 | false |
| M-B1 | Designing decisions and labels | B | B-001, B-003, B-004, B-005, B-006, B-007 | E3, E4, E8 | false |
| M-B2 | Schemas and scales | B | B-002, B-008, B-009, B-010, B-011, B-014 | E1, E2, E5 | false |
| M-B3 | Taxonomies from traces | B | B-012, B-013, C-001, C-002, C-018 | L-002 | false |
| M-C1 | Gold sets and judge validation | C | C-003, C-004, C-005, C-009, C-010, C-019 | E1, E7 | false |
| M-C2 | Judge bias | C | C-006, C-007, C-008, D-008 | E5, E6 | false |
| M-C3 | Eval statistics and operations | C | C-011, C-012, C-013, C-014, C-015, C-016, C-017 | L-003 | false |
| M-D1 | Tiers, cascades, ensembles | D | D-001, D-003, D-004, D-005, D-006, D-007, D-013 | E10 | false |
| M-D2 | Context, retrieval, tools, safety | D | D-002, D-009, D-010, D-011, D-012, D-014, D-015 | L-004 | false |
| M-E1 | The adaptation ladder | E | E-001, E-002, E-003, E-004, E-005, E-006, E-007 | E8, E13 | false |
| M-F1 | Machine intuition I (reading) | F | F-001, F-002, F-003, F-004, F-005 | — | true |
| M-F2 | Machine intuition II (reading) | F | F-006, F-007, F-008, F-009, F-010 | — | true |

## 8. Runnable lab specifications (exact)

### E9 — Context distractors and position
- Dataset: `labs/E9/data/items.jsonl`, 60 items, generator `aiu.generators.e9`, seed 1337. Each item: fictional entity (e.g. "the town of Varnholt"), attribute ∈ {founding_year, river, mayor, export, twin_city}, value. `input = {question, key_passage, distractors[20]}`; each distractor states the same attribute with a different value for a **similarly named** entity (edit distance ≤ 2 on the name). Each passage 60–90 words. `expected = {answer}`.
- Conditions (order fixed): `oracle` (key passage only), `d5_start` (key first, then 5 distractors), `d5_middle` (key at index 3 of 6), `d5_end` (key last of 6), `d20_middle` (key at index 10 of 21).
- Prompt: system `"Answer using only the passages. Reply with the answer only, no explanation. If the passages do not contain the answer, reply UNKNOWN."`; user `"Passages:\n[1] ...\n[2] ...\n\nQuestion: <question>"`.
- Role `cheap_a`, temperature 0, seed 1337, max_tokens 16, samples 1. Calls 300.
- Metrics: `accuracy:<cond>` = exact_match rate per condition (5 keys); `accuracy_drop:<cond>` = accuracy:oracle − accuracy:<cond> for the 4 non-oracle conditions; `max_drop` = max of the 4 drops; `unknown_rate:<cond>`.
- pass_fail: rule `any`; `max_drop >= 0.05`. Interpretation: "supported = adding distractors or moving the key fact measurably hurts this model at this context length".
- validity_checks: `accuracy:oracle >= 0.80` (else the task itself is broken).
- Synthetic fixture error rates (seed 1337): oracle 0.02, d5_start 0.05, d5_middle 0.10, d5_end 0.07, d20_middle 0.15; wrong answer = the value from distractor 0.
- Confounds: synthetic facts are easy; similar-name distractors may test name matching rather than attention; short contexts (<4k tokens) may show no lost-in-the-middle effect.

### E2 — Schema field order
- Dataset: `labs/E2/data/items.jsonl`, 80 items, generator `aiu.generators.e2`. `input = {passage (80–120 words, fictional), claim}`; `expected = {label ∈ {"entailed","not_entailed"}}`, 40/40. Not-entailed claims change exactly one attribute (number, name, or date) from a passage fact.
- Conditions: `verdict_first` (JSON keys `verdict, reasoning`), `reasoning_first` (`reasoning, verdict`), `evidence_first` (`evidence_quote, reasoning, verdict`).
- Prompt: system describes task and says `"Return a single JSON object with exactly these keys in this order: <keys>. verdict must be \"entailed\" or \"not_entailed\"."`; no `response_format`.
- Parse: first `{` to last `}` → `json.loads`; key `verdict` with valid value else None.
- Role `cheap_a`, temperature 0, seed 1337, max_tokens 300. Calls 240.
- Metrics: `accuracy:<cond>`, `parse_rate:<cond>`, `evidence_valid_rate:evidence_first` (normalized evidence_quote is substring of normalized passage), `mean_rationale_chars:<cond>`, `delta_evidence_vs_verdict` = accuracy:evidence_first − accuracy:verdict_first.
- pass_fail: `all`; `delta_evidence_vs_verdict >= 0.05`.
- validity_checks: `parse_rate:verdict_first >= 0.90`, `parse_rate:reasoning_first >= 0.90`, `parse_rate:evidence_first >= 0.90`.
- Synthetic fixture error rates: verdict_first 0.15, reasoning_first 0.10, evidence_first 0.08; parse failure rate 0.02 all.
- Confounds: models may ignore requested key order; reasoning-native models reason internally regardless; single-attribute swaps may be too easy.

### E4 — Escape hatch
- Dataset: `labs/E4/data/items.jsonl`, 80 items, generator `aiu.generators.e4`: 60 in-taxonomy support messages (12 each: billing, login, shipping, refund, bug) and 20 out-of-taxonomy (feature_request ×7, partnership ×7, press ×6). `expected = {label, in_taxonomy: bool}`.
- Conditions: `no_escape` (labels: billing, login, shipping, refund, bug), `escape` (+ `other`, `insufficient_info`).
- Output: label only. Parse: normalized text must equal one allowed label, else None.
- Role `cheap_a`, temperature 0, seed 1337, max_tokens 8. Calls 160.
- Metrics: `in_tax_accuracy:<cond>`; `oot_error_rate:<cond>` = fraction of OOT items assigned an in-taxonomy label (None counts as not error); `oot_error_drop` = oot_error_rate:no_escape − oot_error_rate:escape; `in_tax_cost` = in_tax_accuracy:no_escape − in_tax_accuracy:escape.
- pass_fail: `all`; `oot_error_drop >= 0.30`, `in_tax_cost <= 0.05`.
- validity_checks: `in_tax_accuracy:no_escape >= 0.80`.
- Synthetic fixture rates: no_escape: in-tax error 0.05, OOT → random in-tax label always; escape: in-tax error 0.07, OOT → `other` with p 0.85.
- Confounds: OOT categories may be obviously distinct; "other" may become a dumping ground on real data.

### E5 — Position and verbosity bias
- Dataset: `labs/E5/data/items.jsonl`, 40 items, generator `aiu.generators.e5`: fictional-domain question, `correct` answer, `wrong` answer (one-fact error), `padding` (2–3 on-topic sentences adding no facts). `expected = {better: "correct"}`.
- Conditions: `cw_plain` (A=correct, B=wrong), `wc_plain` (A=wrong, B=correct), `cw_padwrong` (A=correct, B=wrong+padding), `wc_padwrong` (A=wrong+padding, B=correct).
- Prompt: judge picks better answer; output `A` or `B` only.
- Role `judge_a`, temperature 0, seed 1337, max_tokens 4. Calls 160.
- Metrics: `flip_rate` (plain pair cw/wc per item: chosen identity differs); `first_slot_rate` (over plain conditions); `correct_pref:plain`; `correct_pref:padwrong`; `verbosity_shift` = correct_pref:plain − correct_pref:padwrong; `flip_rate_padded`.
- pass_fail: `any`; `flip_rate >= 0.10`, `verbosity_shift >= 0.10`.
- validity_checks: `correct_pref:plain >= 0.60`.
- Synthetic fixture: prefers first slot with p 0.15 regardless, else correct; with padded wrong, picks padded with p 0.10.
- Confounds: one-fact errors may be trivially detectable; frontier judges may show small verbosity bias (P-005).

### L-003 — Eval statistics workbench
- No model calls. Dataset `labs/L-003/data/items.jsonl`, generator `aiu.generators.l003`: 200 items `{judge_label, human_label}` with human prevalence 0.15 positive (`fail`), judge TPR 0.80, TNR 0.92 (exact counts: 30 positives, 24 TP, 6 FN; 170 negatives, 156 TN, 14 FP), plus `agent_trials`: 20 tasks × 5 trials with success counts fixed in generator (counts: [5,5,5,4,4,4,3,3,3,2,2,2,1,1,1,0,0,5,4,3]).
- Condition: `analysis`.
- Metrics: `raw_agreement`, `kappa`, `tpr`, `tnr`, `observed_fail_rate` (judge), `corrected_fail_rate` (Rogan–Gladen), `true_fail_rate` (human), `agreement_minus_kappa`, `pass_at_3`, `pass_hat_3` (means over tasks), `compound_0.95_5`.
- pass_fail: `all`; `agreement_minus_kappa >= 0.15`. Expected deterministic values are asserted in tests (T-019).
- validity_checks: none.
- fixtures: provenance `none`... (runnable labs require fixtures) → fixtures `{path: "labs/L-003/fixtures/responses.jsonl", provenance: "synthetic", n_calls: 0}` (empty file).

## 9. Specified labs (manifest content; not implemented in v1)
For each: dataset path `labs/<ID>/data/items.jsonl`, `n_items` as stated, temperature 0 unless stated, seed 1337, `fixtures: {path: null, provenance: "none", n_calls: 0}`.

- **E1** Binary vs scale. 100 items, `human_labeled` (OD-09). Conditions `binary`, `scale5`, `anchored5`; 3 repeats each (samples_per_call 3, temp 0). Metrics: `kappa_vs_human:<cond>` (scales binarized at ≥4 = pass), `run_variance:<cond>` = mean per-item variance of normalized score across repeats. pass `all`: `kappa_vs_human:binary - kappa_vs_human:scale5 >= 0.10` (metric name `kappa_gap_binary_scale5`). Confound: binarization threshold choice.
- **E3** Label cardinality. 200 items, 20 leaf categories in 4 coarse groups, 10/leaf. Conditions `k3, k5, k8, k12, k20, hier20`. Metrics `accuracy:<cond>`, `macro_f1:<cond>`, confusion matrix file. pass `all`: `accuracy:k3 - accuracy:k20 >= 0.10`. Confound: subsets differ in intrinsic difficulty.
- **E6** Self-preference. 40 questions; `cheap_a` and `cheap_b` generate answers; gold marks both correct; `judge_a` (family = cheap_a's) and `judge_b` (family = cheap_b's) compare both orders. Metric `self_pref:<judge>` = P(choose same-family answer). pass `any`: `self_pref:judge_a >= 0.60`, `self_pref:judge_b >= 0.60`. Requires judge_a.family == cheap_a.family (config check).
- **E7** Jury vs single. E1 dataset. `cheap_a/b/c` majority vote vs `strong`. Metrics `kappa:jury`, `kappa:strong`, `cost:jury`, `cost:strong`. pass `all`: `kappa:jury - kappa:strong >= -0.02`, `cost_ratio_jury_strong <= 0.5`.
- **E8** Few-shot curve. E3 k12 task, 80 test items. Conditions `shots{0,2,5,10}_{prototype,boundary}` (0-shot once). Metric `accuracy:<cond>`. pass: `accuracy:shots5_boundary - accuracy:shots5_prototype >= 0.05`.
- **E10** Cascade. E2 task, 80 items. `cheap_a` 3 samples temp 0.7 seed 1337; escalate to `strong` if agreement < t, t ∈ {3/3, 2/3, never}; plus `strong_only`. Metrics `accuracy:<policy>`, `cost_per_item:<policy>`. pass `any` over policies: accuracy ≥ accuracy:strong_only − 0.02 and cost ≤ 0.5× strong_only (metric `frontier_dominates` ∈ {0,1}, condition `>= 1`).
- **E11** Calibration. 100 fictional-QA items. Methods: verbalized confidence; first-token logprob (if supported, P-076); 5-sample agreement temp 0.7. Metrics `ece:<method>`. pass: `ece:verbalized - ece:sample_agreement >= 0.05`.
- **E12** Ceiling test. Input: failed items from a prior E2 or E9 live run (run_id parameter). `strong` + oracle context. Metric `prompt_fraction` = fraction now correct. pass: `prompt_fraction >= 0.50`.
- **E13** Judge distillation. 500 items; judge_a labels; 100 human-clean labels (OD-09); student TF-IDF+LR (ADR-020). Metrics `student_vs_judge`, `student_vs_human`, `judge_vs_human`. pass: `student_vs_judge >= 0.85`.
- **L-001** Pinned replay. E2 dataset; run twice with same pin ≥24 h apart, once with an alternate pin. Metrics `change_rate:same_pin`, `change_rate:alt_pin`, `accuracy_delta:alt_pin`. pass `all`: `change_rate:same_pin <= 0.02`.
- **L-002** Error analysis. 60 synthetic support-bot traces with seeded failures and seeded first-upstream step. Learner writes `learner/portfolio/L-002/notes.yaml` and `taxonomy.yaml`. Metric `first_upstream_agreement`, `coverage`. pass `all`: `coverage >= 1.0`, `first_upstream_agreement >= 0.70`. No model calls.
- **L-004** Indirect injection. 40 QA items over 4 retrieved docs, one doc contains an injected instruction. Conditions `naive_concat`, `delimited_untrusted`. Metric `attack_success_rate:<cond>`. pass: `asr_drop >= 0.20`.

## 10. Capstone CAP-001 (specified)
Build a support-ticket triage app: deterministic checks → `cheap_a` classifier with escape hatch → cascade to `strong` on `unsure`; a 40-item regression set; a judge validated against ≥50 human labels with kappa reported with Wilson CI; a cost/accuracy curve over ≥3 thresholds. Deliverable dir: `learner/portfolio/CAP-001/`. Human-reviewed rubric in GOVERNANCE §6.
