## FILE: GOVERNANCE.md
```markdown
# GOVERNANCE.md

Governs how content, claims, runs, and trust entries change. Where this file and CONSTITUTION.md disagree, CONSTITUTION.md wins.

## 1. Roles

| Role | Who | May change |
|---|---|---|
| Maintainer | Repo owner (Joe) | Everything except rewriting JOURNAL.md history and deleting committed runs |
| Reviewer | A human named in a ledger row's `method` | PROVENANCE.md `status` / `method` / `date`. Only a reviewer may set `verified` or `disputed`. |
| Author | Maintainer or contributor, via PR or commit | Cards, modules, lab manifests, docs. Not the ledger `status`. |
| Learner | Anyone using the course | `learner/` only (trust table, checkpoints, portfolio) and their own `experiments/` runs |
| Tooling (`aiu`) | Generated output | `status.json`, the README STATUS block, and the run-dir artifacts it writes |

No LLM may set a ledger status. No LLM may grade a learner (CONSTITUTION §3).

## 2. Content versioning

- The repo follows SemVer through `src/aiu/__init__.py::__version__` and `CHANGELOG.md`.
  - MAJOR: a breaking schema change in `schemas/*.json`, or a removed card, lab, or module ID.
  - MINOR: new cards, labs, or modules; a new CLI command.
  - PATCH: wording, fixes, or ledger status changes.
- Card, lab, and module IDs are permanent. A retired ID is marked `deprecated: true`. It is never reused.
- Every card edit that changes a claim, number, or `when_it_fails` needs all of the following:
  - a CHANGELOG line;
  - a new ledger row, or an updated existing row;
  - a JOURNAL entry if the edit was driven by a run.
- Model IDs and prices change only in `config/models.yaml` and `config/pricing.yaml`. Each change includes a date. Each change requires a recompute of expected costs (T-036).

## 3. Verification queue

The queue is the set of PROVENANCE.md rows with status `unverified`, ordered by:
1. the claim is used in a Core (A–E) card;
2. the claim has a number;
3. the claim has a runnable lab.

Workflow:
1. **Queue.** An author adds a row: `P-###`, claim text, `unverified`, source, date added, method `—`.
2. **Claim.** A reviewer writes their name and the intended method in the row's `method` field, prefixed `IN REVIEW:`.
3. **Check.** The reviewer performs one of two checks:
   - a primary-source check: paper or official doc, dated within 12 months of the check;
   - a replication: a live run committed in `experiments/<lab>/<run_id>/`.
4. **Decide.** The reviewer sets one status:
   - `verified`: meets all four conditions of CONSTITUTION §6. If the evidence is a replication, append "(our setup only)".
   - `disputed`: credible primary evidence contradicts the claim. The card's `when_it_fails` must cite the row within the same commit.
   - `unverified`: evidence is insufficient. The reviewer records what was tried in `method`.
5. **Propagate.** When a row becomes `verified`, the card's wording may drop "reported"/"claimed" for that number. When a row becomes `disputed`, the card must change.
6. **Expire.** A `verified` row whose source is older than 12 months reverts to `unverified` at the next review. Own-run sources do not expire, but they remain scoped to our setup.

The ledger check is `aiu provenance check` (T-026; not yet built).

## 4. Experiment / results log format

Every live run lives in `experiments/<lab_id>/<run_id>/` and contains exactly the files in `experiments/_template/`:

| File | Written by | When |
|---|---|---|
| `prediction.md` | Learner | Before the run. The prediction gate (T-014) refuses to run without it. |
| `config.json` | `aiu` | At run start |
| `result.json` | `aiu` | At run end, including aborted or failed runs |
| `metrics.json` | `aiu` | At run end, if any items completed |
| `cost.json` | `aiu` | Always. Values are computed from token counts and `config/pricing.yaml`. |
| `postmortem.md` | Learner | After the run. The lab is incomplete without it (T-016). |

Rules:
- Aborted and failed runs are committed with `result.json.status` set to `aborted` or `failed`.
- No run directory is ever deleted or edited after commit. Corrections go in a new run directory, plus a JOURNAL entry.
- Every live run gets one row in RESULTS.md.
- Fixture-mode runs go to `.runs/`. They are never committed and never counted as measured.

## 5. Trust-table format

The trust table lives in `learner/trust_table.yaml`. Its schema is in `schemas/curriculum.schema.json` (trust table).

```yaml
- rule: "<one-sentence rule of thumb>"
  card: "<card ID>"
  ledger: ["P-###"]
  evidence_runs: ["experiments/<lab>/<run_id>"]   # at least one own live run
  setup: "<model ID @ date, dataset, n>"
  result: "<measured number(s) with CI>"
  trust: "trust | trust-with-conditions | do-not-trust"
  conditions: "<when it held>"
  fails_when: "<observed or expected failure condition>"
  added: "YYYY-MM-DD"
  revisited: "YYYY-MM-DD | null"
```

Rules for the trust table:
- An entry with no `evidence_runs` must use `trust: do-not-trust`.
- Negative results are valid entries.

## 6. Who may change what (summary)

| Artifact | Change rule |
|---|---|
| CONSTITUTION.md | Maintainer only, with an ADR in DECISIONS.md |
| JOURNAL.md | Append-only for everyone (enforced by T-005 hook) |
| PROVENANCE.md status | Reviewer only, following §3 |
| experiments/ run dirs | Write-once |
| status.json, README STATUS block | Generated only. Never hand-edited (T-007). |
| config/*.yaml | Maintainer only. Changes must be dated and trigger a cost recompute. |
| learner/ | Learner |
```

## FILE: README.md
```markdown
# AI University (v1)

A hands-on course for working engineers on making LLM systems reliable. It covers:
- diagnosing failures;
- redesigning decisions;
- validating judges;
- building cascades;
- choosing adaptation rungs.

Every lab requires a written prediction before the run and a post-mortem after it.

See CONSTITUTION.md for audience, outcomes, and standards.

<!-- STATUS:BEGIN (generated by `aiu status`; do not edit by hand — generator not yet built, T-007) -->
- Stage: architecture handoff (spec documents only)
- Cards drafted: 3
- Labs runnable: 0 of 17
- Live runs: 0
- Total spend: **0.00 USD** (no live runs exist; nothing to recompute)
- Last verified: never (no ACCEPTANCE.md check has been run)
<!-- STATUS:END -->

## Current status

The repo contains specification documents and three drafted exemplar cards. No code has been implemented.

## Quickstart (planned, not yet working)

The bootstrap (`ops/bootstrap.ps1`, T-002) and CLI (`aiu`, T-006 onward) do not exist yet. None of these commands currently work:

```powershell
# planned
./ops/bootstrap.ps1
uv run aiu validate
uv run aiu labs list
```

## What works

- Reading the specs:
  - CONSTITUTION.md
  - REPO_LAYOUT.md
  - GOVERNANCE.md
  - TASKS.md
  - ACCEPTANCE.md
  - LAB_SPEC.md
- Reading the 3 drafted cards. Their claims are **unverified** (see PROVENANCE.md).

## What does not work yet

- Package, CLI, and validation (T-002, T-006)
- Cost guard and clients (T-011–T-013)
- All labs (T-015–T-023)
- Smoke suite (T-024)
- Checkpoints (T-025)
- Provenance and traceability checks (T-026, T-027)
- Modules and remaining cards (T-028–T-033)
- Learner guide (T-034)
- Live runs (T-036, T-037)
- Acceptance (T-038)

## Links

- Journal: [JOURNAL.md](JOURNAL.md)
- Claim ledger: [PROVENANCE.md](PROVENANCE.md)
- Run index: [RESULTS.md](RESULTS.md) (empty)
- Changes: [CHANGELOG.md](CHANGELOG.md)
- Learnings: [docs/learnings/](docs/learnings/)
```

## FILE: JOURNAL.md
```markdown
# JOURNAL.md

Append-only. Never edit or delete a past entry. To correct an entry, add a new one that references it. Enforcement: pre-commit check (T-005, not yet built).

## Entry template

```
## Entry <n> — YYYY-MM-DD — <title>
- Author:
- Context:
- What I did:
- What I observed (measured / sourced / assumed — label each):
- Runs: experiments/<lab>/<run_id> | none
- Spend this session (USD, from cost.json): 
- Cumulative spend (USD, recomputed): 
- Decisions / open questions:
- Next:
```

---

## Entry 0 — date of architecture handoff (fill in at commit) — Project genesis

- Author: Maintainer
- Context: AI University v1 starts from a source concept map (`source/concept_map.txt`; the PDF is authoritative). The goal is to build a lab-first curriculum for working engineers.
- Architecture call provenance:
  - The spec set was produced in an architecture session with an LLM assistant acting as architect.
  - The spec set comprises CONSTITUTION, REPO_LAYOUT, GOVERNANCE, TASKS T-001..T-038, ACCEPTANCE, LAB_SPEC, and the ledger seeds.
  - These are proposals, not evidence (assumed).
  - The maintainer has accepted them as the v1 baseline. Changes go through DECISIONS.md.
- Measured hardware: **none yet**. The hardware check (`aiu hwcheck`, T-009) is not built, so no hardware numbers are recorded. The only fact here is the target platform from REPO_LAYOUT: Windows path, Python 3.12 (sourced from the spec, not measured).
- What I observed: nothing measured. No live or fixture runs exist.
- Runs: none
- Spend this session (USD): 0.00 (no API calls by the project)
- Cumulative spend (USD): 0.00
- Current state:
  - Spec documents exist.
  - 3 exemplar cards drafted.
  - 0 labs runnable.
  - 0 live runs.
  - All ledger rows are `unverified`.
- Next: T-001 → T-007 (repo, bootstrap, ignore rules, secrets hook, journal check, validate, status).
```

## FILE: PROVENANCE.md
```markdown
# PROVENANCE.md — Claim ledger

Statuses: `unverified` | `verified` | `disputed`. Status rules are in CONSTITUTION §6 and the workflow is in GOVERNANCE §3.

Until a row is `verified`, any number in its claim is "reported" or "claimed".

## Notes on the seed rows

- `date` for seed rows is the date the row was added (fill in at commit). It is not a check date.
- `source` points to the concept map. Exact section anchors are added when T-026 parses the source. Rows without an exact section anchor stay `unverified`.
- Rows P-001, P-011, and P-042 are seeded from the three exemplar cards. Their claim text must match the card text verbatim at commit; see OPEN DECISIONS.
- The other rows (P-002..P-010, P-012) are the source's main [K] claims, paraphrased.

| ID | Claim | Status | Source | Date | Method |
|---|---|---|---|---|---|
| P-001 | (Exemplar card 1, level A) Many LLM failures are context failures — missing, distracting, or badly positioned information — rather than capability failures (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-002 | Irrelevant distractor content in context degrades answer accuracy (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-003 | Information position within a long context affects recall (middle-of-context weaker) (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-004 | In structured output, placing a reasoning field before the answer field changes accuracy (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-005 | Adding an explicit escape-hatch label (e.g., "unknown/other") reduces forced misclassification (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-006 | LLM judges exhibit position bias in pairwise comparison (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-007 | LLM judges exhibit verbosity bias, favoring longer answers (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-008 | An LLM judge should be validated against human labels (kappa, TPR, TNR) before use (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-009 | Tiered/cascaded pipelines can cut cost at small accuracy loss (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-010 | Prefer the cheapest adaptation rung (prompting → retrieval → fine-tuning) that passes a held-out set (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-011 | (Exemplar card 2, level B) Binary checks or a ≤7-label MECE enum with an escape hatch are more reliable than open-ended or large-label decisions (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-012 | Small, fixed label sets improve labeling consistency (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |
| P-042 | (Exemplar card 3, level C) Judge agreement measured as kappa against human labels is a better acceptance criterion than raw accuracy under class imbalance (claimed) | unverified | source/concept_map.txt [K], section TBD | TBD | — |

P-013..P-041 are reserved for claims added by T-029..T-033.
```

## FILE: RESULTS.md
```markdown
# RESULTS.md — Live run index

**No live runs exist yet.** Cumulative spend: 0.00 USD.

Every committed run in `experiments/<lab_id>/<run_id>/` gets exactly one row, including aborted and failed runs. Fixture runs (`.runs/`) are never listed here.

| run_id | lab | date | model (pinned ID @ date) | n items | status | headline metric (measured) | prediction held? | cost_usd | ledger rows | run dir |
|---|---|---|---|---|---|---|---|---|---|---|
| _template_ | E9 | YYYY-MM-DD | provider/model@YYYY-MM-DD | 0 | completed / aborted / failed | metric = value [CI] | yes / no / partial | 0.00 | P-### | experiments/E9/<run_id> |
```

## FILE: schemas/status.schema.json
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "aiu/status.schema.json",
  "title": "AI University status.json",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "aiu_version",
    "generated_at",
    "stage",
    "cards",
    "labs",
    "modules",
    "live_runs",
    "cumulative_cost_usd",
    "ledger",
    "last_verified",
    "known_gaps"
  ],
  "properties": {
    "schema_version": { "type": "integer", "const": 1 },
    "aiu_version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+" },
    "generated_at": { "type": "string", "format": "date-time" },
    "stage": {
      "type": "string",
      "enum": ["architecture", "building", "core-complete", "v1-accepted"]
    },
    "cards": {
      "type": "object",
      "additionalProperties": false,
      "required": ["drafted", "by_level"],
      "properties": {
        "drafted": { "type": "integer", "minimum": 0 },
        "by_level": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "A": { "type": "integer", "minimum": 0 },
            "B": { "type": "integer", "minimum": 0 },
            "C": { "type": "integer", "minimum": 0 },
            "D": { "type": "integer", "minimum": 0 },
            "E": { "type": "integer", "minimum": 0 },
            "F": { "type": "integer", "minimum": 0 }
          }
        }
      }
    },
    "labs": {
      "type": "object",
      "additionalProperties": false,
      "required": ["total", "runnable"],
      "properties": {
        "total": { "type": "integer", "minimum": 0 },
        "runnable": { "type": "integer", "minimum": 0 }
      }
    },
    "modules": {
      "type": "object",
      "additionalProperties": false,
      "required": ["total", "authored"],
      "properties": {
        "total": { "type": "integer", "minimum": 0 },
        "authored": { "type": "integer", "minimum": 0 }
      }
    },
    "live_runs": {
      "type": "object",
      "additionalProperties": false,
      "required": ["total", "completed", "aborted", "failed"],
      "properties": {
        "total": { "type": "integer", "minimum": 0 },
        "completed": { "type": "integer", "minimum": 0 },
        "aborted": { "type": "integer", "minimum": 0 },
        "failed": { "type": "integer", "minimum": 0 }
      }
    },
    "cumulative_cost_usd": { "type": "number", "minimum": 0 },
    "ledger": {
      "type": "object",
      "additionalProperties": false,
      "required": ["total", "unverified", "verified", "disputed"],
      "properties": {
        "total": { "type": "integer", "minimum": 0 },
        "unverified": { "type": "integer", "minimum": 0 },
        "verified": { "type": "integer", "minimum": 0 },
        "disputed": { "type": "integer", "minimum": 0 }
      }
    },
    "last_verified": {
      "description": "Date of last passing ACCEPTANCE.md run; null if never.",
      "type": ["string", "null"],
      "format": "date"
    },
    "known_gaps": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["ticket", "title"],
        "properties": {
          "ticket": { "type": "string", "pattern": "^T-\\d{3}$" },
          "title": { "type": "string", "minLength": 1 }
        }
      }
    }
  }
}
```

## FILE: status.json
```json
{
  "schema_version": 1,
  "aiu_version": "0.0.0",
  "generated_at": "2000-01-01T00:00:00Z",
  "stage": "architecture",
  "cards": { "drafted": 3, "by_level": { "A": 1, "B": 1, "C": 1, "D": 0, "E": 0, "F": 0 } },
  "labs": { "total": 17, "runnable": 0 },
  "modules": { "total": 13, "authored": 0 },
  "live_runs": { "total": 0, "completed": 0, "aborted": 0, "failed": 0 },
  "cumulative_cost_usd": 0.0,
  "ledger": { "total": 13, "unverified": 13, "verified": 0, "disputed": 0 },
  "last_verified": null,
  "known_gaps": [
    { "ticket": "T-001", "title": "Create repository and install spec documents" },
    { "ticket": "T-002", "title": "Bootstrap Python 3.12, uv, and package skeleton" },
    { "ticket": "T-003", "title": "Add .gitignore and .env.example" },
    { "ticket": "T-004", "title": "Implement secrets and forbidden-file scanner with pre-commit hook" },
    
