## FILE: DECISIONS.md
```markdown
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
- Open: concrete IDs are OD-01.
- Date: 2026-10-23

## ADR-010: Dataset format and provenance
- Decision: Datasets are JSONL at `labs/<lab_id>/data/items.jsonl`, one object per line: `{"id": str, "input": object, "expected": object, "meta": object}`, sorted by `id`. v1 runnable datasets are **synthetic**, generated by deterministic generators in `src/aiu/generators/<lab_id_lower>.py` with `seed=1337`, using fictional entities only. Generated files are committed; `aiu dataset build LAB_ID --check` regenerates in memory and exits 1 if bytes differ. Each dataset dir has `DATASET_CARD.md` (purpose, generator, seed, counts, license, known biases).
- Datasets needing human labels (E1, E7, E13) are `specified`, not runnable, until the human supplies labels (OD-03).
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
- Decision: `expected_cost_usd` in lab manifests is **assumed** at $0.50/Mtok input and $1.50/Mtok output until OD-01 pins real models and prices; T-036 re-computes from `aiu lab estimate` and updates manifests.
- Date: 2026-10-23

## ADR-023: Journal is append-only
- Decision: `aiu journal check` compares `git show HEAD:JOURNAL.md` with the working copy; exit 1 unless HEAD content is an exact prefix of the working copy. If `JOURNAL.md` is not in HEAD (first commit), exit 0.
- Date: 2026-10-23
```

## FILE: CONSTITUTION.md
```markdown
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
```

## FILE: schemas/curriculum.schema.json
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aiuniversity.local/schemas/curriculum.schema.json",
  "title": "AI University curriculum documents",
  "type": "object",
  "required": ["kind"],
  "oneOf": [
    {"$ref": "#/$defs/card"},
    {"$ref": "#/$defs/lab"},
    {"$ref": "#/$defs/module"},
    {"$ref": "#/$defs/trust_table"}
  ],
  "$defs": {
    "card_id": {"type": "string", "pattern": "^[A-F]-[0-9]{3}$"},
    "lab_id": {"type": "string", "pattern": "^(E([1-9]|1[0-3])|L-[0-9]{3})$"},
    "module_id": {"type": "string", "pattern": "^M-[A-F][0-9]$"},
    "run_id": {"type": "string", "pattern": "^[0-9]{8}T[0-9]{6}Z-(fixture|live)-[0-9a-f]{6}$"},
    "date_or_null": {"type": ["string", "null"], "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
    "semver": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
    "nonempty": {"type": "string", "minLength": 1},
    "verify_item": {
      "type": "object",
      "additionalProperties": false,
      "required": ["claim_id", "claim", "status", "source", "date", "method"],
      "properties": {
        "claim_id": {"type": "string", "pattern": "^P-[0-9]{3}$"},
        "claim": {"$ref": "#/$defs/nonempty"},
        "status": {"enum": ["unverified", "verified", "disputed"]},
        "source": {"type": ["string", "null"]},
        "date": {"$ref": "#/$defs/date_or_null"},
        "method": {"$ref": "#/$defs/nonempty"}
      }
    },
    "retrieval_q": {
      "type": "object",
      "additionalProperties": false,
      "required": ["q", "a"],
      "properties": {"q": {"$ref": "#/$defs/nonempty"}, "a": {"$ref": "#/$defs/nonempty"}}
    },
    "condition": {
      "type": "object",
      "additionalProperties": false,
      "required": ["metric", "op", "value"],
      "properties": {
        "metric": {"type": "string", "pattern": "^[a-z0-9_.:]+$"},
        "op": {"enum": [">=", "<=", ">", "<", "=="]},
        "value": {"type": "number"}
      }
    },
    "card": {
      "type": "object",
      "additionalProperties": false,
      "required": ["kind", "schema_version", "id", "version", "status", "level", "title", "one_liner", "why_it_matters", "decision_rule", "when_it_fails", "source_section", "provenance", "verify", "misconceptions", "prerequisites", "experiment_id", "assessment", "retrieval_questions", "tags"],
      "properties": {
        "kind": {"const": "card"},
        "schema_version": {"const": "1.0"},
        "id": {"$ref": "#/$defs/card_id"},
        "version": {"$ref": "#/$defs/semver"},
        "status": {"enum": ["draft", "reviewed", "verified"]},
        "level": {"enum": ["A", "B", "C", "D", "E", "F"]},
        "title": {"type": "string", "minLength": 3, "maxLength": 80},
        "one_liner": {"type": "string", "minLength": 10, "maxLength": 220},
        "why_it_matters": {"type": "string", "minLength": 40, "maxLength": 900},
        "decision_rule": {"type": "string", "minLength": 10, "maxLength": 400},
        "when_it_fails": {"type": "array", "minItems": 1, "maxItems": 5, "items": {"$ref": "#/$defs/nonempty"}},
        "source_section": {"type": "string", "pattern": "^(§([1-9]|1[01])(\\.[0-9]{1,2})?|none)$"},
        "provenance": {"type": "array", "minItems": 1, "uniqueItems": true, "items": {"enum": ["S", "K", "ADD"]}},
        "add_justification": {"type": "string", "minLength": 10, "maxLength": 300},
        "verify": {"type": "array", "items": {"$ref": "#/$defs/verify_item"}},
        "misconceptions": {"type": "array", "minItems": 1, "maxItems": 3, "items": {"$ref": "#/$defs/nonempty"}},
        "prerequisites": {"type": "array", "uniqueItems": true, "items": {"$ref": "#/$defs/card_id"}},
        "experiment_id": {"anyOf": [{"$ref": "#/$defs/lab_id"}, {"type": "null"}]},
        "experiment_null_reason": {"type": "string", "minLength": 10, "maxLength": 300},
        "assessment": {
          "type": "object",
          "additionalProperties": false,
          "required": ["type", "description"],
          "properties": {
            "type": {"enum": ["deterministic", "human_rubric", "both"]},
            "description": {"$ref": "#/$defs/nonempty"}
          }
        },
        "retrieval_questions": {"type": "array", "minItems": 3, "maxItems": 3, "items": {"$ref": "#/$defs/retrieval_q"}},
        "tags": {"type": "array", "minItems": 1, "uniqueItems": true, "items": {"type": "string", "pattern": "^[a-z0-9-]+$"}}
      },
      "allOf": [
        {"if": {"properties": {"provenance": {"contains": {"const": "ADD"}}}}, "then": {"required": ["add_justification"]}},
        {"if": {"properties": {"provenance": {"contains": {"const": "K"}}}}, "then": {"properties": {"verify": {"minItems": 1}}}},
        {"if": {"properties": {"provenance": {"contains": {"const": "S"}}}}, "then": {"properties": {"verify": {"minItems": 1}}}},
        {"if": {"properties": {"experiment_id": {"type": "null"}}}, "then": {"required": ["experiment_null_reason"]}},
        {"if": {"properties": {"source_section": {"const": "none"}}}, "then": {"properties": {"provenance": {"contains": {"const": "ADD"}}}}}
      ]
    },
    "lab": {
      "type": "object",
      "additionalProperties": false,
      "required": ["kind", "schema_version", "id", "title", "status", "hardware_tier", "hypothesis", "concept_ids", "dataset", "procedure", "metric", "pass_fail", "validity_checks", "controls", "expected_runtime_minutes", "expected_cost_usd", "cost_basis", "cost_cap_usd", "fixtures", "post_mortem_template", "known_confounds"],
      "properties": {
        "kind": {"const": "lab"},
        "schema_version": {"const": "1.0"},
        "id": {"$ref": "#/$defs/lab_id"},
        "title": {"type": "string", "minLength": 3, "maxLength": 100},
        "status": {"enum": ["runnable", "specified", "deferred"]},
        "hardware_tier": {"enum": ["API_ONLY", "LOCAL_SMALL_GPU_6GB", "LOCAL_CPU_TINY"]},
        "api_fallback": {
          "type": "object",
          "additionalProperties": false,
          "required": ["lab_id", "description"],
          "properties": {"lab_id": {"$ref": "#/$defs/lab_id"}, "description": {"$ref": "#/$defs/nonempty"}}
        },
        "local_requirements": {
          "type": "object",
          "additionalProperties": false,
          "required": ["params_b", "weights_gb", "context_max", "batch_size", "expected_tokens_per_sec", "setup_command", "disk_cost_gb"],
          "properties": {
            "params_b": {"type": "number", "exclusiveMinimum": 0},
            "weights_gb": {"type": "number", "exclusiveMinimum": 0},
            "context_max": {"type": "integer", "minimum": 1},
            "batch_size": {"const": 1},
            "expected_tokens_per_sec": {"type": "number", "exclusiveMinimum": 0},
            "setup_command": {"$ref": "#/$defs/nonempty"},
            "disk_cost_gb": {"type": "number", "exclusiveMinimum": 0}
          }
        },
        "hypothesis": {"type": "string", "minLength": 20},
        "concept_ids": {"type": "array", "minItems": 1, "uniqueItems": true, "items": {"$ref": "#/$defs/card_id"}},
        "dataset": {
          "type": "object",
          "additionalProperties": false,
          "required": ["path", "description", "n_items", "license", "provenance", "generator", "positive_class"],
          "properties": {
            "path": {"type": "string", "pattern": "^labs/(E([1-9]|1[0-3])|L-[0-9]{3})/data/[A-Za-z0-9_.-]+$"},
            "description": {"$ref": "#/$defs/nonempty"},
            "n_items": {"type": "integer", "minimum": 0},
            "license": {"$ref": "#/$defs/nonempty"},
            "provenance": {"enum": ["synthetic_generated", "human_authored", "human_labeled", "real_redacted"]},
            "generator": {"type": ["string", "null"]},
            "positive_class": {"type": ["string", "null"]}
          }
        },
        "procedure": {
          "type": "object",
          "additionalProperties": false,
          "required": ["steps", "conditions", "model_roles", "temperature", "seed", "max_tokens", "samples_per_call"],
          "properties": {
            "steps": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/nonempty"}},
            "conditions": {
              "type": "array", "minItems": 1,
              "items": {
                "type": "object", "additionalProperties": false, "required": ["name", "description"],
                "properties": {"name": {"type": "string", "pattern": "^[a-z0-9_]+$"}, "description": {"$ref": "#/$defs/nonempty"}}
              }
            },
            "model_roles": {"type": "array", "uniqueItems": true, "items": {"enum": ["cheap_a", "cheap_b", "cheap_c", "strong", "judge_a", "judge_b"]}},
            "temperature": {"type": "number", "minimum": 0, "maximum": 2},
            "seed": {"type": "integer"},
            "max_tokens": {"type": "integer", "minimum": 1, "maximum": 4096},
            "samples_per_call": {"type": "integer", "minimum": 1, "maximum": 10}
          }
        },
        "metric": {
          "type": "array", "minItems": 1,
          "items": {
            "type": "object", "additionalProperties": false, "required": ["name", "formula", "impl"],
            "properties": {
              "name": {"type": "string", "pattern": "^[a-z0-9_.:]+$"},
              "formula": {"$ref": "#/$defs/nonempty"},
              "impl": {"type": "string", "pattern": "^aiu\\.[a-z0-9_.]+$"}
            }
          }
        },
        "pass_fail": {
          "type": "object", "additionalProperties": false, "required": ["rule", "conditions", "interpretation"],
          "properties": {
            "rule": {"enum": ["all", "any"]},
            "conditions": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/condition"}},
            "interpretation": {"$ref": "#/$defs/nonempty"}
          }
        },
        "validity_checks": {"type": "array", "items": {"$ref": "#/$defs/condition"}},
        "controls": {
          "type": "object", "additionalProperties": false, "required": ["held_constant", "varied", "randomized"],
          "properties": {
            "held_constant": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/nonempty"}},
            "varied": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/nonempty"}},
            "randomized": {"type": "array", "items": {"$ref": "#/$defs/nonempty"}}
          }
        },
        "expected_runtime_minutes": {"type": "number", "minimum": 0},
        "expected_cost_usd": {"type": "number", "minimum": 0},
        "cost_basis": {"enum": ["assumed", "estimated_from_pinned_pricing"]},
        "cost_cap_usd": {"type": "number", "minimum": 0, "maximum": 2.0},
        "fixtures": {
          "type": "object", "additionalProperties": false, "required": ["path", "provenance", "n_calls"],
          "properties": {
            "path": {"type": ["string", "null"]},
            "provenance": {"enum": ["synthetic", "recorded", "none"]},
            "n_calls": {"type": "integer", "minimum": 0}
          }
        },
        "post_mortem_template": {"const": "experiments/_template/postmortem.md"},
        "known_confounds": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/nonempty"}}
      },
      "allOf": [
        {"if": {"properties": {"hardware_tier": {"enum": ["LOCAL_SMALL_GPU_6GB", "LOCAL_CPU_TINY"]}}}, "then": {"required": ["api_fallback", "local_requirements"]}},
        {"if": {"properties": {"hardware_tier": {"const": "LOCAL_SMALL_GPU_6GB"}}}, "then": {"properties": {"local_requirements": {"properties": {"weights_gb": {"maximum": 3.5}, "context_max": {"maximum": 4096}}}}}},
        {"if": {"properties": {"hardware_tier": {"const": "LOCAL_CPU_TINY"}}}, "then": {"properties": {"local_requirements": {"properties": {"params_b": {"maximum": 1.0}}}}}},
        {"if": {"properties": {"status": {"const": "runnable"}}}, "then": {"properties": {"fixtures": {"properties": {"provenance": {"enum": ["synthetic", "recorded"]}, "path": {"type": "string"}}}}}}
      ]
    },
    "module": {
      "type": "object",
      "additionalProperties": false,
      "required": ["kind", "schema_version", "id", "title", "level", "objective", "card_ids", "lab_ids", "conceptual", "checkpoint", "portfolio_artifact", "spaced_review_prompt"],
      "properties": {
        "kind": {"const": "module"},
        "schema_version": {"const": "1.0"},
        "id": {"$ref": "#/$defs/module_id"},
        "title": {"type": "string", "minLength": 3, "maxLength": 80},
        "level": {"enum": ["A", "B", "C", "D", "E", "F"]},
        "objective": {"type": "string", "pattern": "^Can ", "minLength": 20},
        "card_ids": {"type": "array", "minItems": 3, "maxItems": 8, "uniqueItems": true, "items": {"$ref": "#/$defs/card_id"}},
        "lab_ids": {"type": "array", "uniqueItems": true, "items": {"$ref": "#/$defs/lab_id"}},
        "conceptual": {"type": "boolean"},
        "checkpoint": {
          "type": "object", "additionalProperties": false, "required": ["deterministic_items", "human_rubric"],
          "properties": {
            "deterministic_items": {
              "type": "array", "minItems": 3,
              "items": {
                "type": "object", "additionalProperties": false, "required": ["id", "prompt", "type", "answer"],
                "properties": {
                  "id": {"type": "string", "pattern": "^Q[0-9]{2}$"},
                  "prompt": {"$ref": "#/$defs/nonempty"},
                  "type": {"enum": ["mcq", "numeric", "exact"]},
                  "choices": {"type": "array", "minItems": 2, "items": {"$ref": "#/$defs/nonempty"}},
                  "answer": {"type": ["string", "number"]},
                  "tolerance": {"type": "number", "minimum": 0}
                },
                "allOf": [
                  {"if": {"properties": {"type": {"const": "mcq"}}}, "then": {"required": ["choices"]}},
                  {"if": {"properties": {"type": {"const": "numeric"}}}, "then": {"required": ["tolerance"], "properties": {"answer": {"type": "number"}}}}
                ]
              }
            },
            "human_rubric": {"type": "array", "minItems": 2, "items": {"$ref": "#/$defs/nonempty"}}
          }
        },
        "portfolio_artifact": {
          "type": "object", "additionalProperties": false, "required": ["path_pattern", "description"],
          "properties": {"path_pattern": {"type": "string", "pattern": "^learner/portfolio/"}, "description": {"$ref": "#/$defs/nonempty"}}
        },
        "spaced_review_prompt": {"type": "string", "minLength": 20}
      },
      "allOf": [
        {"if": {"properties": {"conceptual": {"const": false}}}, "then": {"properties": {"lab_ids": {"minItems": 1}}}}
      ]
    },
    "trust_row": {
      "type": "object",
      "additionalProperties": false,
      "required": ["rule", "card_id", "evidence_strength", "my_replication", "run_ids", "last_reviewed", "notes"],
      "properties": {
        "rule": {"$ref": "#/$defs/nonempty"},
        "card_id": {"$ref": "#/$defs/card_id"},
        "evidence_strength": {"enum": ["anecdote", "sourced", "replicated_once", "replicated_multi", "contradicted"]},
        "my_replication": {"enum": ["not_run", "replicated", "failed_to_replicate", "inconclusive"]},
        "run_ids": {"type": "array", "items": {"$ref": "#/$defs/run_id"}},
        "last_reviewed": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"},
        "notes": {"type": "string"}
      },
      "allOf": [
        {"if": {"properties": {"my_replication": {"enum": ["replicated", "failed_to_replicate", "inconclusive"]}}}, "then": {"properties": {"run_ids": {"minItems": 1}}}}
      ]
    },
    "trust_table": {
      "type": "object",
      "additionalProperties": false,
      "required": ["kind", "schema_version", "rows"],
      "properties": {
        "kind": {"const": "trust_table"},
        "schema_version": {"const": "1.0"},
        "rows": {"type": "array", "items": {"$ref": "#/$defs/trust_row"}}
      }
    }
  }
}
```

## FILE: REPO_LAYOUT.md
```markdown
# REPO_LAYOUT.md

Root: `C:\Users\Joe\Documents\Playground\AIUniversity`. No other top-level entries are allowed. `aiu validate` does not check layout; T-035 does.

```
AIUniversity/
├── README.md                 Living front page; generated STATUS block.
├── JOURNAL.md                Append-only session log.
├── DECISIONS.md              ADRs.
├── CONSTITUTION.md           Audience, outcomes, standards, "verified".
├── GOVERNANCE.md             Versioning, verification queue, logs, trust table.
├── PROVENANCE.md             Claim ledger (P-###).
├── RESULTS.md                Index of every live run.
├── TRACEABILITY.md           Source concept → card → experiment.
├── TASKS.md                  Implementation backlog.
├── ACCEPTANCE.md             v1 definition of done as commands.
├── LAB_SPEC.md               Lab kit and lab index.
├── REPO_LAYOUT.md            This file.
├── CHANGELOG.md              User-visible changes, newest first.
├── status.json               Generated machine-readable state.
├── pyproject.toml            Package + deps + pytest config.
├── uv.lock                   Pinned dependency lock.
├── .python-version           "3.12".
├── .gitignore                Ignore rules (see T-003).
├── .env.example              Template for OPENROUTER_API_KEY.
├── .githooks/
│   └── pre-commit            Secrets scan + journal append-only check.
├── source/
│   ├── concept_map.txt       Source ontology text (PDF authoritative).
│   └── README.md             Provenance of the source file.
├── schemas/
│   ├── curriculum.schema.json  Cards, labs, modules, trust table.
│   └── status.schema.json      status.json schema.
├── config/
│   ├── models.yaml           Role → pinned model ID.
│   ├── pricing.yaml          Pinned USD/Mtok prices.
│   └── caps.yaml             Cost caps.
├── curriculum/
│   ├── A/ … F/               One YAML card per file: <ID>.yaml.
│   └── modules/              One YAML module per file: M-<L><n>.yaml.
├── labs/
│   └── <lab_id>/             One dir per lab (E1..E13, L-001..L-004).
│       ├── manifest.yaml     Lab manifest (schema: lab).
│       ├── data/             items.jsonl + DATASET_CARD.md (runnable labs).
│       └── fixtures/         responses.jsonl (runnable labs).
├── src/aiu/
│   ├── __init__.py           __version__.
│   ├── cli.py                argparse entry point.
│   ├── validate.py           YAML → JSON Schema validation.
│   ├── models.py             Pydantic models (data, calls, artifacts).
│   ├── config.py             Load models/pricing/caps.
│   ├── cost.py               Estimator + CostGuard.
│   ├── clients/              base.py, fixture.py, openrouter.py.
│   ├── hardware.py           hwcheck.
│   ├── metrics.py            ADR-011 metrics.
│   ├── runs.py               run_id, run dirs, prediction gate.
│   ├── runner.py             Lab execution engine.
│   ├── postmortem.py         Post-mortem checks.
│   ├── labs/                 Lab implementations + registry.
│   ├── generators/           Deterministic dataset generators.
│   ├── status.py             status.json + README block + consistency.
│   ├── journal.py            Append-only check.
│   ├── secrets_scan.py       Secret/forbidden-file scan.
│   ├── provenance.py         Ledger parsing + check.
│   ├── traceability.py       Traceability check.
│   ├── checkpoint.py         Module checkpoint grader.
│   └── smoke.py              Smoke suite.
├── tests/                    pytest; zero network.
├── experiments/
│   ├── _template/            Per-run artifact templates.
│   └── <lab_id>/<run_id>/    Committed live runs only.
├── docs/
│   ├── LEARNER_GUIDE.md      How to complete a module.
│   └── learnings/            YYYY-MM-DD-<slug>.md + _template.md.
├── learner/
│   ├── trust_table.yaml      "Rules of thumb I now trust".
│   ├── checkpoints/          <module>.answers.yaml, <module>.result.json.
│   └── portfolio/            Module portfolio artifacts.
├── ops/
│   ├── bootstrap.ps1         Windows bootstrap (uv, Python, sync, hooks).
│   └── RUNBOOK.md            Live-run procedure, key rotation, incident steps.
└── .runs/                    (gitignored) fixture-mode run outputs.
```
```

## FILE: LAB_SPEC.md
```markdown
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
Licenses: all datasets are synthetic and authored for this repo; license = repo content license (OD-04).
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

- **E1** Binary vs scale. 100 items, `human_labeled` (OD-03). Conditions `binary`, `scale5`, `anchored5`; 3 repeats each (samples_per_call 3, temp 0). Metrics: `kappa_vs_human:<cond>` (scales binarized at ≥4 = pass), `run_variance:<cond>` = mean per-item variance of normalized score across repeats. pass `all`: `kappa_vs_human:binary - kappa_vs_human:scale5 >= 0.10` (metric name `kappa_gap_binary_scale5`). Confound: binarization threshold choice.
- **E3** Label cardinality. 200 items, 20 leaf categories in 4 coarse groups, 10/leaf. Conditions `k3, k5, k8, k12, k20, hier20`. Metrics `accuracy:<cond>`, `macro_f1:<cond>`, confusion matrix file. pass `all`: `accuracy:k3 - accuracy:k20 >= 0.10`. Confound: subsets differ in intrinsic difficulty.
- **E6** Self-preference. 40 questions; `cheap_a` and `cheap_b` generate answers; gold marks both correct; `judge_a` (family = cheap_a's) and `judge_b` (family = cheap_b's) compare both orders. Metric `self_pref:<judge>` = P(choose same-family answer). pass `any`: `self_pref:judge_a >= 0.60`, `self_pref:judge_b >= 0.60`. Requires judge_a.family == cheap_a.family (config check).
- **E7** Jury vs single. E1 dataset. `cheap_a/b/c` majority vote vs `strong`. Metrics `kappa:jury`, `kappa:strong`, `cost:jury`, `cost:strong`. pass `all`: `kappa:jury - kappa:strong >= -0.02`, `cost_ratio_jury_strong <= 0.5`.
- **E8** Few-shot curve. E3 k12 task, 80 test items. Conditions `shots{0,2,5,10}_{prototype,boundary}` (0-shot once). Metric `accuracy:<cond>`. pass: `accuracy:shots5_boundary - accuracy:shots5_prototype >= 0.05`.
- **E10** Cascade. E2 task, 80 items. `cheap_a` 3 samples temp 0.7 seed 1337; escalate to `strong` if agreement < t, t ∈ {3/3, 2/3, never}; plus `strong_only`. Metrics `accuracy:<policy>`, `cost_per_item:<policy>`. pass `any` over policies: accuracy ≥ accuracy:strong_only − 0.02 and cost ≤ 0.5× strong_only (metric `frontier_dominates` ∈ {0,1}, condition `>= 1`).
- **E11** Calibration. 100 fictional-QA items. Methods: verbalized confidence; first-token logprob (if supported, P-076); 5-sample agreement temp 0.7. Metrics `ece:<method>`. pass: `ece:verbalized - ece:sample_agreement >= 0.05`.
- **E12** Ceiling test. Input: failed items from a prior E2 or E9 live run (run_id parameter). `strong` + oracle context. Metric `prompt_fraction` = fraction now correct. pass: `prompt_fraction >= 0.50`.
- **E13** Judge distillation. 500 items; judge_a labels; 100 human-clean labels (OD-03); student TF-IDF+LR (ADR-020). Metrics `student_vs_judge`, `student_vs_human`, `judge_vs_human`. pass: `student_vs_judge >= 0.85`.
- **L-001** Pinned replay. E2 dataset; run twice with same pin ≥24 h apart, once with an alternate pin. Metrics `change_rate:same_pin`, `change_rate:alt_pin`, `accuracy_delta:alt_pin`. pass `all`: `change_rate:same_pin <= 0.02`.
- **L-002** Error analysis. 60 synthetic support-bot traces with seeded failures and seeded first-upstream step. Learner writes `learner/portfolio/L-002/notes.yaml` and `taxonomy.yaml`. Metric `first_upstream_agreement`, `coverage`. pass `all`: `coverage >= 1.0`, `first_upstream_agreement >= 0.70`. No model calls.
- **L-004** Indirect injection. 40 QA items over 4 retrieved docs, one doc contains an injected instruction. Conditions `naive_concat`, `delimited_untrusted`. Metric `attack_success_rate:<cond>`. pass: `asr_drop >= 0.20`.

## 10. Capstone CAP-001 (specified)
Build a support-ticket triage app: deterministic checks → `cheap_a` classifier with escape hatch → cascade to `strong` on `unsure`; a 40-item regression set; a judge validated against ≥50 human labels with kappa reported with Wilson CI; a cost/accuracy curve over ≥3 thresholds. Deliverable dir: `learner/portfolio/CAP-001/`. Human-reviewed rubric in GOVERNANCE §6.
```

## FILE: curriculum/A/A-001.yaml
```yaml
kind: card
schema_version: "1.0"
id: A-001
version: 1.0.0
status: draft
level: A
title: Output is a function of context
one_liner: An LLM call can only use the facts, rules, and examples present in its context window; anything missing is guessed.
why_it_matters: >-
  Most production failures that look like "the model is dumb" are missing-context failures:
  the retrieval step dropped the fact, the rule lived in a wiki instead of the prompt, or the
  example never made it in. Fixing context is cheaper and more durable than switching models,
  and it is the first branch of the debugging playbook.
decision_rule: >-
  Before changing models or rewording instructions, ask whether a smart stranger could answer
  correctly using only the exact context you sent. If not, fix the context first.
when_it_fails:
  - Widely known, stable facts may be answered correctly from pretraining without context, though stale-knowledge risk remains.
  - The fact can be present yet ignored when buried among distractors or in long inputs (see A-008).
  - Perfect context does not help a task beyond the model's capability (see A-007).
source_section: "§1.1"
provenance: [K]
verify:
  - claim_id: P-001
    claim: Missing needed facts, rules, or examples in the window forces the model to guess; the "smart stranger" test is an effective first debugging step.
    status: unverified
    source: null
    date: null
    method: Replicate via E9 oracle condition versus a no-key-passage control on our own data; search for current context-engineering guidance.
misconceptions:
  - A stronger model will fix a wrong answer even if the needed fact was never provided.
  - If the information is somewhere in the context, the model will use it.
prerequisites: []
experiment_id: E9
assessment:
  type: both
  description: Deterministic checkpoint items in M-A1 plus a human-reviewed post-mortem for an E9 run that classifies each wrong answer as missing-context or present-but-ignored.
retrieval_questions:
  - q: State the "smart stranger" test.
    a: Could a competent person with no other knowledge answer correctly using only the exact context sent to the model? If not, the failure is a context failure.
  - q: Which playbook step does this card correspond to, and what do you fix if it fails?
    a: Step 2, "Is the needed information in the context?"; if not, fix retrieval or context assembly before touching the prompt or model.
  - q: Name one case where the needed fact is in the context but the call still fails.
    a: The fact is buried among similar distractors or in the middle of a long context, so attention to it degrades (A-008).
tags: [context, debugging, retrieval, mental-model]
```

## FILE: curriculum/B/B-001.yaml
```yaml
kind: card
schema_version: "1.0"
id: B-001
version: 1.0.0
status: draft
level: B
title: Binary decomposition of judgments
one_liner: Replace a holistic quality score with 3-6 observable yes/no checks, optionally arranged as a decision tree.
why_it_matters: >-
  Binary checks are easier for models and humans to agree on, easier to audit, and each one maps
  to a named failure you can fix. Multi-point scales add run-to-run disagreement, and reported
  judge-human alignment degrades as rubric granularity increases, so a "quality 1-5" gate hides
  regressions behind noisy averages.
decision_rule: >-
  Default to binary pass/fail per criterion. Convert any "rate 1-N" judgment into 3-6 binary
  sub-questions, each defined by something literally observable in the output.
when_it_fails:
  - When the downstream use genuinely needs ranking or graded preference among many good outputs, pairwise comparison or an anchored scale may carry more information (B-008, B-009).
  - Poorly defined binary criteria are still ambiguous; binarization does not fix vague definitions (B-005).
  - Many binary checks per call bundle decisions and compound error; keep one decision per call (A-003).
source_section: "§2.1"
provenance: [S]
verify:
  - claim_id: P-011
    claim: Binary pass/fail is the most reliable judgment format; scales add run-to-run disagreement; judge-human alignment degrades as rubric granularity increases; decision trees of binary checks are more stable than holistic scores.
    status: unverified
    source: arxiv.org/abs/2601.08843; microsoft.github.io/mcscatblog/assets/posts/better-llm-scoring/20260626_LLM1-5Scoring_WhitePaper.pdf
    date: null
    method: Read both sources and confirm the stated direction and magnitude; replicate with E1 on our human-labeled set.
misconceptions:
  - A 1-10 score carries more information, so it must be a better gate.
  - Averaging a noisy scale across many items cancels the noise for release decisions.
  - Binary checks are only for trivial tasks.
prerequisites: [A-002, A-003]
experiment_id: E1
assessment:
  type: both
  description: Deterministic checkpoint items in M-B1; human-reviewed rewrite of a provided 1-5 rubric into binary checks with observable definitions.
retrieval_questions:
  - q: How many binary sub-questions should replace a single 1-5 quality score?
    a: Roughly 3-6, each tied to an observable criterion.
  - q: What two problems do multi-point scales add compared with binary checks?
    a: More run-to-run disagreement and lower judge-human alignment as granularity increases.
  - q: Which experiment tests this card and what does it compare?
    a: E1 compares binary, 1-5, and anchored 1-5 judging on kappa against humans and run-to-run variance.
tags: [binary-checks, rubric, judge, decision-design]
```

## FILE: curriculum/C/C-004.yaml
```yaml
kind: card
schema_version: "1.0"
id: C-004
version: 1.0.0
status: draft
level: C
title: Measure the judge, not just the app
one_liner: Before trusting an LLM judge, measure its agreement with human labels using kappa and per-class TPR/TNR, not raw accuracy.
why_it_matters: >-
  An unvalidated judge turns every downstream metric into an unknown. Raw accuracy hides failure
  on the rare class: a judge that always says "pass" scores high when failures are rare. Kappa
  corrects for chance agreement, and TPR/TNR show which errors the judge makes, which determines
  whether it can gate a release.
decision_rule: >-
  Validate every judge on a held-out human-labeled set. Report kappa, TPR, and TNR with
  confidence intervals. Do not gate releases on a judge whose kappa is below about 0.6
  (reported guidance) or whose TPR on the failure class is unknown.
when_it_fails:
  - With small gold sets, kappa and TPR intervals are wide; a point estimate above 0.6 may not be meaningfully different from 0.5 (C-019).
  - When human annotators themselves disagree, the human-human agreement rate caps what any judge can reach (A-009).
  - Agreement thresholds such as 85-90% are reported practitioner guidance, not a universal standard; the needed bar depends on the cost of each error type.
source_section: "§4.4"
provenance: [S]
verify:
  - claim_id: P-042
    claim: Compute judge-vs-human kappa and per-class TPR/TNR; reported guidance is about 85-90% agreement before gating releases and kappa under about 0.6 is an alarm.
    status: unverified
    source: tianpan.co/blog/2026-02-20-llm-evals-practitioners-guide; hamel.dev/blog/posts/evals-faq/why-is-error-analysis-so-important-in-llm-evals-and-how-is-it-performed.html
    date: null
    method: Read sources; record exact thresholds and their stated basis; mark vendor/practitioner origin; compare with L-003 worked example.
misconceptions:
  - 90% raw agreement means the judge is good.
  - A judge that is consistent across reruns is therefore accurate.
  - Once validated, a judge stays valid after a model or rubric change.
prerequisites: [C-003]
experiment_id: E1
assessment:
  type: both
  description: Deterministic checkpoint items in M-C1 computing kappa, TPR, and TNR from a confusion matrix; human-reviewed judge validation report in the module portfolio.
retrieval_questions:
  - q: Why is raw agreement misleading when failures are rare?
    a: A judge that always predicts the majority class gets high agreement while catching none of the failures; kappa and TPR expose this.
  - q: Which three numbers must a judge validation report include?
    a: Cohen's kappa against humans, TPR on the failure class, and TNR, each with a confidence interval.
  - q: What must you do when the judge model, rubric, or temperature changes?
    a: Re-validate against the held-out human set before using it again (C-009).
tags: [judge, kappa, validation, gold-set, evaluation]
```

## FILE: TRACEABILITY.md
```markdown
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
```

## FILE: TASKS.md
```markdown
# TASKS.md — v1 implementation backlog

Working directory for every command: `C:\Users\Joe\Documents\Playground\AIUniversity`, PowerShell.
Every ticket's DoD includes: a new `JOURNAL.md` entry naming the ticket, acceptance results, commands, cost (USD, usually 0.00), failures; and `status.json` refreshed (`uv run aiu status --write` from T-007 on; manual edit of `known_gaps` before T-007).
"Spec docs" = files emitted in the Opus handoff message, copied byte-for-byte.

---

### T-001: Create repository and install spec documents

**Goal:** Repo exists with git initialized and every spec document from the handoff present verbatim.

**Depends on:** none.

**Files:**
- create: `DECISIONS.md`, `CONSTITUTION.md`, `schemas/curriculum.schema.json`, `schemas/status.schema.json`, `REPO_LAYOUT.md`, `LAB_SPEC.md`, `curriculum/A/A-001.yaml`, `curriculum/B/B-001.yaml`, `curriculum/C/C-004.yaml`, `TRACEABILITY.md`, `TASKS.md`, `ACCEPTANCE.md`, `GOVERNANCE.md`, `README.md`, `JOURNAL.md`, `PROVENANCE.md`, `RESULTS.md`, `CHANGELOG.md`, `status.json`, `experiments/_template/prediction.md`, `experiments/_template/postmortem.md`, `experiments/_template/config.json`, `experiments/_template/result.json`, `experiments/_template/metrics.json`, `experiments/_template/cost.json`, `docs/learnings/_template.md`
- create: `source/concept_map.txt` (human-provided text), `source/README.md`

**Interfaces / schemas:** none.

**Steps:**
1. `New-Item -ItemType Directory -Force` the repo root; `cd` into it.
2. `git init -b main`.
3. Write each file above with exact contents from the handoff.
4. Write `source/README.md`: `Extracted text of "AI Engineering Concept Map" (compiled 2026-10-23). The PDF is authoritative; it is not committed pending OD-05.`
5. Place `source/concept_map.txt` as provided by the human.
6. Append JOURNAL entry 1 (T-001). Commit: `git add -A; git commit -m "T-001: install spec documents"`.

**Acceptance tests:**
- `$f=@('DECISIONS.md','CONSTITUTION.md','schemas/curriculum.schema.json','schemas/status.schema.json','REPO_LAYOUT.md','LAB_SPEC.md','curriculum/A/A-001.yaml','curriculum/B/B-001.yaml','curriculum/C/C-004.yaml','TRACEABILITY.md','TASKS.md','ACCEPTANCE.md','GOVERNANCE.md','README.md','JOURNAL.md','PROVENANCE.md','RESULTS.md','CHANGELOG.md','status.json','experiments/_template/prediction.md','experiments/_template/postmortem.md','docs/learnings/_template.md','source/concept_map.txt'); $m=$f|?{-not(Test-Path $_)}; if($m){$m; exit 1}else{exit 0}` → exit 0.
- `git log --oneline -1` → output contains `T-001`.

**Commands:** as in Steps.

**Definition of done:**
- [ ] All files present; one commit.
- [ ] JOURNAL entry 1 appended after entry 0.
- [ ] `status.json` unchanged (initial).

**Out of scope:** Any Python, any edits to spec content.

**Open decisions:** OD-05 (commit PDF?).

---

### T-002: Bootstrap Python 3.12, uv, and package skeleton

**Goal:** `uv run aiu --version` prints `aiu 0.1.0` using Python 3.12.

**Depends on:** T-001.

**Files:**
- create: `pyproject.toml`, `.python-version`, `src/aiu/__init__.py`, `src/aiu/cli.py`, `tests/test_cli.py`, `ops/bootstrap.ps1`, `ops/RUNBOOK.md`
- create (generated): `uv.lock`

**Interfaces / schemas:**
```toml
[project]
name = "aiu"
version = "0.1.0"
requires-python = ">=3.11,<3.13"
dependencies = ["pydantic>=2.7,<3", "pyyaml>=6.0,<7", "jsonschema>=4.21,<5", "httpx>=0.27,<1", "psutil>=5.9,<7"]
[project.scripts]
aiu = "aiu.cli:main"
[dependency-groups]
dev = ["pytest>=8,<9", "pytest-socket>=0.7,<1"]
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["src/aiu"]
[tool.pytest.ini_options]
addopts = "--disable-socket -q"
testpaths = ["tests"]
```
```python
# src/aiu/__init__.py
__version__ = "0.1.0"
# src/aiu/cli.py
def build_parser() -> argparse.ArgumentParser: ...  # prog="aiu", --version action prints "aiu 0.1.0"
def main(argv: list[str] | None = None) -> int: ...   # returns exit code; `if __name__` not needed
```
Console script must call `sys.exit(main())` semantics: define `main` returning int and register via hatch; wrap with `def _entry(): raise SystemExit(main())` and point script to `aiu.cli:_entry`. (Update `[project.scripts] aiu = "aiu.cli:_entry"`.)

`ops/bootstrap.ps1` content (exact steps): install uv if `Get-Command uv` fails via `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`; `uv python install 3.12`; `uv sync`; `git config core.hooksPath .githooks`; `uv run aiu --version`.
`ops/RUNBOOK.md`: sections `## Live run procedure` (LAB_SPEC §2 commands), `## Key rotation` (revoke at openrouter.ai, update local `.env`, never commit), `## Incident: key committed` (revoke key immediately, rewrite is NOT allowed for JOURNAL; record incident entry), `## Incident: cost overrun` (record in JOURNAL with cost.json link).

**Steps:**
1. Run uv installer (above); open new shell; `uv --version`.
2. `uv python install 3.12`.
3. Create files above. Write `.python-version` = `3.12`.
4. `uv sync`.
5. `tests/test_cli.py::test_version` calls `main(["--version"])` capturing `SystemExit` code 0 and stdout `aiu 0.1.0`.

**Acceptance tests:**
- `uv run python -c "import sys; print(sys.version_info[:2])"` → `(3, 12)`, exit 0.
- `uv run aiu --version` → `aiu 0.1.0`, exit 0.
- `uv run pytest` → exit 0, `1 passed`.

**Commands:** `uv sync; uv run aiu --version; uv run pytest`

**Definition of done:**
- [ ] `uv.lock` committed.
- [ ] JOURNAL entry; `status.json.known_gaps` unchanged.

**Out of scope:** Any subcommands.

**Open decisions:** none.

---

### T-003: Add .gitignore and .env.example

**Goal:** Secrets and local artifacts cannot be accidentally tracked.

**Depends on:** T-002.

**Files:**
- create: `.gitignore`, `.env.example`, `tests/test_hygiene_files.py`

**Interfaces / schemas:**
`.gitignore` exact lines:
```
.env
.env.*
!.env.example
.venv/
__pycache__/
*.pyc
.pytest_cache/
.runs/
*.gguf
*.safetensors
*.pt
*.bin
*.onnx
*.pem
*.key
dist/
build/
```
`.env.example` exact:
```
# Copy to .env and fill in. Never commit .env.
OPENROUTER_API_KEY=
```

**Steps:**
1. Write both files.
2. Test: `.env.example` exists, contains `OPENROUTER_API_KEY=` with empty value; `.gitignore` contains `.env` and `.runs/` lines.
3. Test: `git check-ignore .env` returns 0 (run via `subprocess` with `git`; skip test if git not on PATH—must not be the case on dev machine).

**Acceptance tests:**
- `uv run pytest tests/test_hygiene_files.py` → exit 0.
- `git check-ignore .env` → prints `.env`, exit 0.
- `git check-ignore .env.example` → exit 1.

**Commands:** `uv run pytest tests/test_hygiene_files.py`

**Definition of done:**
- [ ] Files committed; JOURNAL entry.

**Out of scope:** Loading `.env` (harness reads env vars only; learners load via their shell).

**Open decisions:** none.

---

### T-004: Implement secrets and forbidden-file scanner with pre-commit hook

**Goal:** `aiu secrets-scan` exits 1 on any secret or forbidden file and is enforced on commit.

**Depends on:** T-003.

**Files:**
- create: `src/aiu/secrets_scan.py`, `.githooks/pre-commit`, `tests/test_secrets_scan.py`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
@dataclass(frozen=True)
class Finding: path: str; line: int | None; rule: str; excerpt: str  # excerpt masks all but first 6 chars of match
SECRET_PATTERNS: dict[str, re.Pattern] = {
  "openrouter_key": re.compile(r"sk-or-v1-[A-Za-z0-9]{16,}"),
  "generic_sk_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
  "bearer_token": re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
  "env_assignment": re.compile(r"^\s*OPENROUTER_API_KEY\s*=\s*\S+", re.M),
}
FORBIDDEN_GLOBS = [".env", ".env.*", "*.pem", "*.key", "*.gguf", "*.safetensors", "*.pt", "*.bin", "*.onnx"]
ALLOWED = [".env.example"]
MAX_FILE_BYTES = 5_000_000
def scan_paths(paths: list[Path]) -> list[Finding]
def staged_paths(root: Path) -> list[Path]   # git diff --cached --name-only --diff-filter=ACM
def all_tracked_and_untracked(root: Path) -> list[Path]  # git ls-files -co --exclude-standard
```
CLI: `aiu secrets-scan [--staged] [--root PATH]`. Prints one line per finding `<rule> <path>:<line> <excerpt>`; prints `secrets-scan: 0 findings` on success. Exit 0/1. Binary files (null byte in first 8 KB) skip pattern scan but still get glob/size checks. Files > MAX_FILE_BYTES → rule `oversize`.
`.githooks/pre-commit`:
```
#!/bin/sh
uv run aiu secrets-scan --staged || exit 1
uv run aiu journal check || exit 1
```
(Second line becomes effective after T-005; until then `journal` subcommand missing → commit fails. Therefore write only the first line in this ticket; T-005 adds the second.)

**Steps:**
1. Implement module + CLI.
2. Tests using `tmp_path`: (a) file with `sk-or-v1-` + 20 alnum → 1 finding rule `openrouter_key`; (b) `.env` file → rule `forbidden_file`; (c) `.env.example` with empty `OPENROUTER_API_KEY=` → 0 findings; (d) 6 MB file → `oversize`; (e) clean file → 0; (f) excerpt never contains full key.
3. `git config core.hooksPath .githooks`.

**Acceptance tests:**
- `uv run pytest tests/test_secrets_scan.py` → exit 0.
- `uv run aiu secrets-scan` → `secrets-scan: 0 findings`, exit 0.
- `Set-Content tmp_leak.txt "sk-or-v1-abcdefghijklmnopqrstuvwx"; uv run aiu secrets-scan; $c=$LASTEXITCODE; Remove-Item tmp_leak.txt; exit $c` → exit 1.

**Commands:** `git config core.hooksPath .githooks; uv run pytest tests/test_secrets_scan.py`

**Definition of done:**
- [ ] Hook installed and committed; JOURNAL entry.

**Out of scope:** History scanning; network secret validation.

**Open decisions:** none.

---

### T-005: Implement append-only journal check

**Goal:** `aiu journal check` exits 1 when existing `JOURNAL.md` content in HEAD is modified.

**Depends on:** T-004.

**Files:**
- create: `src/aiu/journal.py`, `tests/test_journal.py`
- modify: `src/aiu/cli.py`, `.githooks/pre-commit` (add line 2)

**Interfaces / schemas:**
```python
def head_content(root: Path, rel: str = "JOURNAL.md") -> str | None  # git show HEAD:JOURNAL.md; None if absent/no HEAD
def check_append_only(old: str | None, new: str) -> bool  # True iff old is None or new.startswith(old) (after normalizing CRLF->LF on both)
```
CLI: `aiu journal check` → prints `journal: append-only OK` exit 0, or `journal: existing entries modified` exit 1.

**Steps:**
1. Implement; tests on pure function: None→True; prefix→True; edited middle→False; CRLF/LF difference only→True.
2. Add hook line 2.

**Acceptance tests:**
- `uv run pytest tests/test_journal.py` → exit 0.
- `uv run aiu journal check` → exit 0.

**Commands:** `uv run pytest tests/test_journal.py; uv run aiu journal check`

**Definition of done:**
- [ ] Hook has both lines; JOURNAL entry appended (not edited).

**Out of scope:** Journal entry generation.

**Open decisions:** none.

---

### T-006: Implement YAML schema validation command

**Goal:** `aiu validate` validates all curriculum, lab, module, and trust-table YAML against `schemas/curriculum.schema.json`.

**Depends on:** T-005.

**Files:**
- create: `src/aiu/validate.py`, `tests/test_validate.py`, `tests/fixtures/invalid_card_missing_misconception.yaml`, `tests/fixtures/invalid_lab_local_no_fallback.yaml`, `learner/trust_table.yaml`
- modify: `src/aiu/cli.py`

**Interfaces / schemas:**
```python
SCHEMA_PATH = Path("schemas/curriculum.schema.json")
@dataclass(frozen=True)
class ValidationError_: path: str; pointer: str; message: str
def load_schema(root: Path) -> dict
def iter_yaml(paths: list[Path]) -> Iterator[Path]  # *.yaml recursively, sorted, excluding files under tests/
def validate_file(path: Path, schema: dict) -> list[ValidationError_]  # Draft202012Validator; yaml.safe_load
def validate_ids(paths: list[Path]) -> list[ValidationError_]  # filename stem == id; card in curriculum/<level>/; lab manifest at labs/<id>/manifest.yaml; no duplicate ids
```
CLI: `aiu validate [PATH ...]` default `curriculum labs learner`. Output per error `<path> <pointer> <message>`; final line `validate: <n_files> files, <n_errors> errors`. Exit 0 if 0 errors else 1. Nonexistent default dirs are skipped silently; nonexistent explicit paths → error.
`learner/trust_table.yaml`:
```yaml
kind: trust_table
schema_version: "1.0"
rows: []
```

**Steps:**
1. Implement.
2. Tests: three exemplar cards valid; invalid fixtures each produce ≥1 error; card with `provenance: [K]` and `verify: []` invalid; card `experiment_id: null` without `experiment_null_reason` invalid; filename/id mismatch detected.

**Acceptance tests:**
- `uv run aiu validate` → last line `validate: 4 files, 0 errors`, exit 0.
- `uv run aiu validate tests/fixtures/invalid_lab_local_no_fallback.yaml` → exit 1, output contains `api_fallback`.
- `uv run pytest tests/test_validate.py` → exit 0.

**Commands:** `uv run aiu validate; uv run pytest tests/test_validate.py`

**Definition of done:**
- [ ] JOURNAL entry; `status.json.known_gaps` updated manually.

**Out of scope:** Cross-reference checks (T-026, T-027).

**Open decisions:** none.

---

### T-007: Implement status.json generation, README block, and consistency check

**Goal:** `aiu status --write` regenerates `status.json` and README block; `aiu status --check` fails on any drift.

**Depends on:** T-006.

**Files:**
- create: `src/aiu/status.py`, `tests/test_status.py`
- modify: `src/aiu/cli.py`, `status.json`, `README.md` (generated block only)

**Interfaces / schemas:** `schemas/status.schema.json` (handoff).
```python
def compute_status(root: Path, previous: dict | None) -> dict
  # cards: count curriculum/*/[A-F]-*.yaml by level and status
  # labs: count labs/*/manifest.yaml by status
  # provenance: counts by status from PROVENANCE.md rows "| P-"
  # live runs: experiments/*/*/cost.json (exclude _template); cumulative_cost_usd = round(sum(actual_usd), 4)
  # last_live_run: max by run_id
  # tests: copied from previous (written only by `aiu check-all`)
  # known_gaps: copied from previous
def render_readme_block(status: dict) -> str
def write
