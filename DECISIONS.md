# DECISIONS.md — Architecture Decision Records

Format per entry: Context / Decision / Alternatives rejected / Consequences / Date.
All entries dated 2026-10-23 are **assumed** dates (source compilation date). The human confirms or corrects them in JOURNAL entry 1.
New decisions are appended. Superseded decisions are marked `SUPERSEDED BY ADR-xxx` and are never deleted.

---

## ADR-001: Repository layout
- Context: Content, harness, and public learning record must coexist without confusion.
- Decision: Single repo. Layout is fixed by `REPO_LAYOUT.md`. Python package lives in `src/aiu/`. Content lives in `curriculum/`. Lab assets live in `labs/<lab_id>/`. Live run artifacts live in `experiments/<lab_id>/<run_id>/`. Fixture-mode runs write to `.runs/` (gitignored) by default.
- Alternatives rejected: separate content and harness repos (traceability breaks); writing fixture runs into `experiments/` (pollutes the public record with non-evidence).
- Consequences: Every directory has a single purpose. `aiu status --check` can scan `experiments/` and trust that every run dir there is live.
- Date: 2026-10-23

## ADR-002: CLI shape
- Context: Implementer needs an exact, testable command surface.
- Decision: One entry point `aiu` (console script `aiu = aiu.cli:main`), built on stdlib `argparse`. Subcommands:
  - `aiu --version`
  - `aiu validate [PATH ...]` (default paths: `curriculum labs learner`)
  - `aiu status --write | --check`
  - `aiu journal check`
  - `aiu secrets-scan [--staged] [--root PATH]`
  - `aiu hwcheck [--tier API_ONLY|LOCAL_SMALL_GPU_6GB|LOCAL_CPU_TINY] [--json]`
  - `aiu labs list`
  - `aiu labs check-tiers`
  - `aiu dataset build LAB_ID [--check]`
  - `aiu fixtures synth LAB_ID [--check]`
  - `aiu lab new-run LAB_ID --mode fixture|live [--out-dir PATH]`
  - `aiu lab estimate LAB_ID [--limit N]`
  - `aiu lab run LAB_ID --run-id RUN_ID --mode fixture|live [--cap USD] [--limit N] [--record] [--out-dir PATH]`
  - `aiu lab postmortem-check LAB_ID --run-id RUN_ID [--out-dir PATH]`
  - `aiu smoke --mode fixture|live [--cap USD]`
  - `aiu checkpoint grade MODULE_ID --answers PATH`
  - `aiu provenance check`
  - `aiu traceability check`
  - `aiu check-all`
- Alternatives rejected: click/typer (extra dependency, no benefit); multiple scripts (harder to document).
- Consequences: argparse usage errors exit 2 (argparse default).
- Date: 2026-10-23

## ADR-003: Exit codes
- Decision (all `aiu` commands):
  - 0 success
  - 1 check failed (validation finding, secrets found, test/consistency mismatch, checkpoint not fully correct)
  - 2 CLI usage error (argparse)
  - 3 missing fixture for a planned call in fixture mode
  - 4 cost cap would be exceeded (pre-run or mid-run)
  - 5 hardware check failed for declared tier
  - 6 configuration error (missing key, UNPINNED model in live mode, malformed config, HTTP 401)
  - 7 prediction gate failed (missing/invalid/edited `prediction.md`)
- Consequences: Acceptance tests assert these codes exactly.
- Date: 2026-10-23

## ADR-004: Python and tooling
- Decision: Python 3.12 installed via `uv python install 3.12`; `.python-version` = `3.12`; `requires-python = ">=3.11,<3.13"`. Dependencies: `pydantic>=2.7,<3`, `pyyaml>=6.0,<7`, `jsonschema>=4.21,<5`, `httpx>=0.27,<1`, `psutil>=5.9,<7`. Dev group: `pytest>=8,<9`, `pytest-socket>=0.7,<1`. Build backend: hatchling. Exact versions are pinned by committed `uv.lock`.
- Alternatives rejected: system Python 3.7.4 (below target); `openai` SDK (extra surface; OpenRouter is plain HTTP); `requests` (no built-in mock transport).
- Consequences: Never invoke the system `python`; always `uv run`.
- Date: 2026-10-23

## ADR-005: HTTP client for OpenRouter
- Decision: `httpx.Client` POST to `https://openrouter.ai/api/v1/chat/completions`. Headers: `Authorization: Bearer $OPENROUTER_API_KEY`, `Content-Type: application/json`, `X-Title: AI University`. Body: `model`, `messages`, `temperature`, `max_tokens`, `seed` (if not null), `response_format` (if not null), `logprobs` (if true), `usage: {"include": true}`. Timeout 60 s. Retries: max 3 retries on HTTP 408/429/500/502/503/504 and `httpx.TransportError`, sleep `2**attempt` seconds (attempt = 0,1,2), sleep function injectable. No retry on other 4xx. HTTP 401 → exit 6.
- Alternatives rejected: SDK; async client (no throughput need).
- Consequences: Tests use `httpx.MockTransport`; no sockets.
- Verify: OpenRouter usage/cost field, seed support, logprob support → PROVENANCE P-075..P-077.
- Date: 2026-10-23

## ADR-006: Offline/fixture mode
- Decision: Two client implementations behind one interface: `FixtureClient` and `OpenRouterClient`. Fixture records are JSONL at `labs/<lab_id>/fixtures/responses.jsonl`, keyed by `call_key = "{item_id}|{condition}|{role}|{sample}"`. Each record stores `request_sha256` and `source` (`fixture_synthetic` or `fixture_recorded`). For `fixture_recorded`, a `request_sha256` mismatch with the planned call is an error (exit 3). For `fixture_synthetic`, the hash is not checked.
- Initial fixtures are **synthetic**, generated deterministically by `aiu fixtures synth LAB_ID` from dataset ground truth with a lab-defined error-injection rate and seed 1337. Synthetic fixture metrics are labeled `evidence_class: "assumed"` and never appear in `RESULTS.md` or README numbers.
- `aiu lab run --mode live --record` overwrites the fixture file with `fixture_recorded` records.
- Alternatives rejected: keying by request hash only (prompt edits would orphan every synthetic fixture); VCR-style HTTP cassettes (couples tests to HTTP shape).
- Date: 2026-10-23

## ADR-007: Network isolation in tests
- Decision: `pytest-socket` with `addopts = "--disable-socket -q"` in `pyproject.toml`. Any socket creation during tests fails the test.
- Consequences: "Zero network calls in fixture mode" is enforced mechanically.
- Date: 2026-10-23

## ADR-008: Cost accounting
- Decision:
  - Prices come only from `config/pricing.yaml` (USD per million tokens, manually pinned with `retrieved_at` date).
  - Pre-call estimate per call: `est_in = ceil(utf8_bytes(all message contents) / 3)`; `est_out = max_tokens`; `est_usd = (est_in*in_price + est_out*out_price) / 1e6`. Multiply by `samples` already expanded as separate calls.
  - Pre-run: if `sum(est_usd) > cap` → exit 4, no calls made, run dir gets `result.json` with `status: "aborted_cost"`.
  - Mid-run: before each call, if `actual_so_far + est_usd(next) > cap` → stop, write partial artifacts, `status: "aborted_cost"`, exit 4.
  - Actual cost = `(prompt_tokens*in_price + completion_tokens*out_price)/1e6` from response usage. Provider-reported cost (if present) is stored as `provider_reported_usd` but does not drive the guard.
  - Fixture mode: actual cost = 0; estimate uses `pricing.yaml: fixture_defaults` so the guard is exercised.
  - Default caps in `config/caps.yaml`: `per_lab_usd: 2.00`, `smoke_total_usd: 5.00`. `--cap` may lower but never raise above `per_lab_usd` for `lab run`, or above `smoke_total_usd` for `smoke` (exit 6 if raised).
- Alternatives rejected: trusting provider-reported cost only (not always present; verify P-075).
- Date: 2026-10-23

## ADR-009: Model configuration
- Decision: `config/models.yaml` maps **roles** to pinned model IDs: `cheap_a`, `cheap_b`, `cheap_c` (three different families), `strong`, `judge_a`, `judge_b` (different family from `judge_a`). Each role: `model_id`, `family`. The literal value `UNPINNED` is allowed in the repo; live mode refuses to run any lab whose roles resolve to `UNPINNED` (exit 6). Fixture mode ignores model IDs and records `model_id` from the fixture file.
- Labs reference roles, never model IDs. No model ID string appears in `src/`.
- Alternatives rejected: choosing models now (pricing and availability on OpenRouter must be checked by the human on the day of pinning).
- Open: concrete IDs are OD-01 (policy resolved; exact IDs are pinned in T-036).
- Date: 2026-10-23

## ADR-010: Dataset format and provenance
- Decision: Datasets are JSONL at `labs/<lab_id>/data/items.jsonl`, one object per line: `{"id": str, "input": object, "expected": object, "meta": object}`, sorted by `id`. v1 runnable datasets are **synthetic**, generated by deterministic generators in `src/aiu/generators/<lab_id_lower>.py` with `seed=1337`, using fictional entities only. Generated files are committed; `aiu dataset build LAB_ID --check` regenerates in memory and exits 1 if bytes differ. Each dataset dir has `DATASET_CARD.md` (purpose, generator, seed, counts, license, known biases).
- Datasets needing human labels (E1, E7, E13) are `specified`, not runnable, until the human supplies labels (OD-09).
- `--limit N` takes the first N items by `id` order.
- Alternatives rejected: public benchmarks (contamination, license); LLM-generated datasets (unverifiable labels).
- Date: 2026-10-23

## ADR-011: Metric definitions (implemented in `src/aiu/metrics.py`)
- `accuracy(pred, gold) = (#i: pred_i == gold_i) / n`; parse failures are `pred_i = None` and count as incorrect.
- `parse_rate = (#parsed) / n`.
- `cohen_kappa(a, b) = (p_o - p_e) / (1 - p_e)`; `p_e = Σ_k p_a(k) p_b(k)`; returns `None` if `p_e == 1`.
- `tpr = TP/(TP+FN)`, `tnr = TN/(TN+FP)`; `None` on zero denominator. Positive class is declared per lab.
- `wilson_ci(k, n, z=1.96) -> (lo, hi)`: `center = (p + z²/2n)/(1+z²/n)`, `half = z*sqrt(p(1-p)/n + z²/4n²)/(1+z²/n)`.
- `flip_rate = (#pairs whose chosen answer identity differs between AB and BA orders) / #pairs`.
- `first_slot_rate = (#choices of the first-presented answer) / #judgments`.
- `rogan_gladen(p_obs, tpr, tnr) = clip((p_obs + tnr - 1)/(tpr + tnr - 1), 0, 1)`; `None` if `tpr + tnr - 1 <= 0`.
- `pass_at_k(n, c, k) = 1 - C(n-c, k)/C(n, k)` (unbiased; 1.0 if n-c < k).
- `pass_hat_k(n, c, k) = C(c, k)/C(n, k)`.
- `ece(conf, correct, bins=10)`: equal-width bins on [0,1], last bin inclusive of 1.0; `Σ_b |B_b|/n * |acc(B_b) - mean_conf(B_b)|`.
- `compound(p, steps) = p**steps`.
- `normalize_answer(s) = collapse_whitespace(strip_punctuation(lower(s))).strip()`; punctuation = `string.punctuation`.
- `exact_match(pred, gold) = normalize_answer(pred) == normalize_answer(gold)`.
- Every proportion reported in `metrics.json` includes `n` and a Wilson 95% CI.
- Date: 2026-10-23

## ADR-012: Card-count targets
- Decision: 75 cards total. A: 10, B: 14, C: 19 (17 from §4, C-018 from §7 failure catalog, C-019 `[ADD]`), D: 15 (14 from §3, D-015 from §8 playbook), E: 7, F: 10. IDs are fixed in `TRACEABILITY.md`.
- Card ID format `^[A-F]-\d{3}$`. Experiment IDs are `E1`–`E13` (no hyphen) and `L-\d{3}`. The level-E card `E-001` and experiment `E1` are distinct by format; the validator enforces patterns.
- Date: 2026-10-23

## ADR-013: Module structure
- Decision: 13 modules, fixed in `LAB_SPEC.md §7` and authored as `curriculum/modules/M-<level><n>.yaml`. Each module has 3–8 cards. Cards belong to exactly one module.
- `M-A1` is the reference module that a learner can complete end-to-end in v1 (lab E9 runnable).
- Date: 2026-10-23

## ADR-014: Hardware-tier policy
- Decision: Every lab manifest declares exactly one `hardware_tier` ∈ {`API_ONLY`, `LOCAL_SMALL_GPU_6GB`, `LOCAL_CPU_TINY`}. Local tiers require `api_fallback.lab_id` pointing to an existing `API_ONLY` manifest with fixtures, and `local_requirements`. All 17 v1 labs are `API_ONLY`. `aiu hwcheck` measures RAM, disk, GPU (via `nvidia-smi` if present) and checks thresholds:
  - `API_ONLY`: always passes; reports a warning (not failure) if free disk < 10 GB.
  - `LOCAL_SMALL_GPU_6GB`: free VRAM ≥ `local_requirements.weights_gb + 1.0`, free disk ≥ 10 GB + weights_gb, RAM total ≥ 16 GB minus 0.5 tolerance.
  - `LOCAL_CPU_TINY`: `local_requirements.params_b ≤ 1.0`, RAM available ≥ 4 GB.
- No weights are downloaded by any command in v1.
- Date: 2026-10-23

## ADR-015: Lab status in v1
- Decision: `runnable` labs (end-to-end, fixture + live): **E2, E4, E5, E9, L-003**. `specified` (manifest complete, no implementation): E1, E3, E6, E7, E8, E10, E11, E12, E13, L-001, L-002, L-004. Capstone `CAP-001` is specified in `LAB_SPEC.md` without a manifest.
- Rationale: these five need no human labels and have ground truth by construction; together they cover levels A, B, C.
- Date: 2026-10-23

## ADR-016: Prediction gate and run artifacts
- Decision: `aiu lab new-run` creates `<out>/<lab_id>/<run_id>/prediction.md` from template. `run_id = YYYYMMDDTHHMMSSZ-<mode>-<6 lowercase hex>` (UTC). `aiu lab run` refuses (exit 7) unless `prediction.md` front matter parses, `predicted_metrics` is non-empty with keys ⊆ manifest metric names, and `written_at` < now. At run start the harness writes `prediction.sha256`. `postmortem-check` fails if the hash changed.
- Default out dirs: fixture → `.runs/`, live → `experiments/`.
- Run artifacts: `prediction.md`, `prediction.sha256`, `config.json`, `responses.jsonl`, `result.json`, `metrics.json`, `cost.json`, `postmortem.md`. The harness prints only `run_id`, status, and cost to stdout; metrics are written to file, never printed before `prediction.sha256` exists.
- Date: 2026-10-23

## ADR-017: Public state consistency
- Decision: `status.json` is generated by `aiu status --write` from repo state. `README.md` contains a generated block between `<!-- STATUS:BEGIN -->` and `<!-- STATUS:END -->`. `aiu status --check` exits 1 if: recomputed status ≠ committed status (ignoring `generated_at`, `tests`), README block ≠ render, any `experiments/*/*/` run dir is not referenced by run_id in `RESULTS.md`, or cumulative cost ≠ sum of `cost.json:actual_usd`.
- Date: 2026-10-23

## ADR-018: Provenance ledger
- Decision: `PROVENANCE.md` is a markdown table; rows begin `| P-###`. Card `verify[].claim_id` must exist in the ledger; ledger status must equal card verify status (`aiu provenance check`). Status values: `unverified`, `verified`, `disputed`. Only the human may set `verified` or `disputed` (GOVERNANCE §2).
- Date: 2026-10-23

## ADR-019: Assessment policy
- Decision: Module checkpoints are (a) deterministic items (`mcq`, `numeric` with tolerance, `exact`) graded by `aiu checkpoint grade`, and (b) a human rubric for the postmortem/portfolio artifact. No LLM judge grades learners in v1. LLM judges appear only as objects of study in labs.
- Date: 2026-10-23

## ADR-020: E13 student classifier
- Decision: E13 is `specified` only. When implemented, the student is TF-IDF + logistic regression (scikit-learn, CPU). This is not LLM fine-tuning and is not a training-side lab; tier stays `API_ONLY` (judge labels come from API). scikit-learn is not added in v1.
- Date: 2026-10-23

## ADR-021: Git hooks on Windows
- Decision: `.githooks/pre-commit` is a two-line `sh` script (Git for Windows bundles `sh`) that runs `uv run aiu secrets-scan --staged` and `uv run aiu journal check`. Activated by `git config core.hooksPath .githooks`.
- Alternatives rejected: pre-commit framework (extra dependency).
- Date: 2026-10-23

## ADR-022: Assumed costs
- Decision: `expected_cost_usd` in lab manifests is **assumed** at $0.50/Mtok input and $1.50/Mtok output until T-036 pins real models and prices under OD-01; T-036 re-computes from `aiu lab estimate` and updates manifests.
- Date: 2026-10-23

## ADR-023: Journal is append-only
- Decision: `aiu journal check` compares `git show HEAD:JOURNAL.md` with the working copy; exit 1 unless HEAD content is an exact prefix of the working copy. If `JOURNAL.md` is not in HEAD (first commit), exit 0.
- Date: 2026-10-23

---

## Decision register (canonical, updated 2026-10-24)

Status values: `RESOLVED`, `DEFERRED`, `PROPOSED`, `OPEN`.
This is the only authoritative OD list. Earlier documents that used a different OD number for content license, human labels, the PDF, or prediction authorship have been corrected.

### OD-01 - Model selection and price pinning: RESOLVED
- Decision: Model choice is a **role**, not a constant. `config/models.yaml` maps `cheap_a`, `cheap_b`, `cheap_c`, `strong`, `judge_a`, `judge_b` to exact OpenRouter IDs per run. Bulk work defaults to cheap models from different families (for example Gemini 2.5 Flash and DeepSeek Flash 4.1); `strong` is reserved for ceiling tests, E10, and E12.
- Model choice is itself a curriculum variable, exercised by E6, E7, E10, and E12. Every live run pins the exact ID and `retrieved_at` date. No live run may use `UNPINNED`.
- Consequence: T-036 pins the smoke-set IDs and prices. Earlier tickets use roles only.

### OD-02 - Smoke suite total cost cap: RESOLVED
- Decision: **$5.00** total for the live smoke suite.
- Revisit only if T-036's measured estimate shows the cap is unrealistic; a change requires a new DECISIONS entry.

### OD-03 - Per-run cap and daily budget: RESOLVED
- Hard per-run cap: **$2.00** (unchanged).
- Soft daily target: **$1.00**. Any run or day above $1.00 requires a JOURNAL entry naming the test, expected learning value, and spend.
- Learners may not raise the $2.00 hard cap. The maintainer may, with a new DECISIONS entry.
- Rationale: learn cheaply by default; allow a worthwhile test to exceed the daily target with a recorded reason.

### OD-04 - Confidence interval method: RESOLVED
- Proportions (accuracy, TPR, TNR, pass rates): **Wilson 95%** interval.
- Paired or continuous quantities (latency, score deltas, cost deltas): **bootstrap, 10,000 resamples, seed 1337**.
- Every metric in `metrics.json` records `ci_method`.
- Rationale: Wilson is closed-form, deterministic, and stable for small n; bootstrap is for quantities without a closed form.
- Alternatives rejected: normal approximation (poor near 0/1 and at small n); bootstrap for proportions (slower, no benefit).

### OD-05 - Prediction gate timing: RESOLVED
- Decision: require `prediction.md` to be committed. The gate checks `written_at <= git commit time of prediction.md < run start`. An uncommitted prediction refuses to run.
- Alternative rejected: trusting the typed timestamp alone, which is forgeable.
- Consequence: T-014 implements the git check; the run refuses (exit 7) if the prediction is not committed.

### OD-06 - Ledger verification authority: RESOLVED
- Only a named human reviewer may set `verified` or `disputed`. No LLM may set either.
- `verified` requires (a) a primary source dated within 12 months, or (b) a committed live run directory that replicates the claim. A single passing run is not sufficient on its own unless the reviewer explicitly signs off that the run is the primary evidence.
- `method` states what was checked; `date` is the check date. This matches CONSTITUTION §6 and GOVERNANCE §3.

### OD-07 - Reasoning token accounting: RESOLVED
- Record `reasoning_tokens` as reported by the provider. Use `null` when unreported; never coerce to `0`.
- Count reasoning tokens in `completion_tokens` and therefore in cost and cap checks when reported.
- The pre-run estimate must include a reasoning allowance for models with mandatory reasoning. If unknown, use the model's default effort and label the estimate `assumed`.
- Rationale: reasoning tokens are billed and count against `max_tokens`; hiding them breaks the cost guard.

### OD-08 - Fixture runs in status counts: RESOLVED
- Fixture runs never count as live. `status.live_runs` counts only `experiments/` runs.
- Fixture outputs stay in `.runs/` and never appear in `RESULTS.md` or README numbers.
- Rationale: fixture mode is for CI and teaching mechanics, not evidence.

### OD-09 - Human-labeled datasets (E1, E7, E13): DEFERRED
- Decision: defer until E1, E7, or E13 is about to become runnable. Those labs stay `specified` in v1.
- When picked up: 100-300 synthetic items per lab, a written labeling guide, and a 30-item overlap for inter-annotator agreement.
- Does not block the five runnable labs: E2, E4, E5, E9, L-003.

### OD-10 - Content license: RESOLVED
- Code: **MIT**.
- Curriculum text and diagrams: **CC BY 4.0**.
- Synthetic datasets and fixtures: **CC0**.
- T-001 adds `LICENSE`, `LICENSE-CONTENT`, and `LICENSE-DATA`.
- Rationale: permissive reuse for teaching, attribution for prose, no restriction on synthetic data.

### OD-11 - Commit the source PDF: RESOLVED
- Commit the 288 KB PDF at `source/AI Engineering Concept Map Raw Material for a Training Schema.pdf`.
- Keep `source/concept_map.txt` as the searchable text; the PDF is authoritative.
- Rationale: small, self-contained provenance; a clone reproduces the source. If redistribution rights turn out to be unclear, remove the PDF in a follow-up commit and keep the text.
- Consequence: all "pending PDF" language is replaced with OD-11 and the PDF is committed in T-001.

### OD-12 - Who authors learner prediction and post-mortem: RESOLVED
- The **learner** writes both. The harness creates the template, hashes the prediction, and checks the post-mortem sections; it never generates the content.
- Rationale: prediction and reflection are the learning mechanism; automating them defeats the pedagogy.
