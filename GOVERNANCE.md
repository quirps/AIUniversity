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
1. the claim is used in a Core (A-E) card;
2. the claim has a number;
3. the claim has a runnable lab.

Workflow:
1. **Queue.** An author adds a row: `P-###`, claim text, `unverified`, source, date added, method `-`.
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
