Emit ONLY the following files, in this order, using exact ## FILE: <path> headings and fenced code blocks. No commentary outside file sections.

1. status.complete.json - a complete, valid status.json. It must satisfy the schema below. Values: aiu_version "0.1.0"; generated_at "2026-10-24T00:00:00Z"; stage "architecture"; 3 cards drafted (A/B/C 1 each, D/E/F 0); labs 17 total, 0 runnable; modules 13 total, 0 authored; 0 live runs; cumulative_cost_usd 0.0; ledger 13 unverified; last_verified null; known_gaps = every ticket T-001..T-038 with its title.
2. CHANGELOG.md - newest first, initial entry 0.1.0 - 2026-10-24 - Architecture handoff, listing the spec artifacts added.
3. experiments/_template/prediction.md - required fields: hypothesis, expected direction, metric, pass/fail threshold, confounds, written_at, author. Placeholders only.
4. experiments/_template/postmortem.md - prediction vs result, observed, why, what I now trust, what I will change, next.
5. experiments/_template/config.json - valid JSON with run_id, lab_id, mode, model_id, temperature, seed, dataset_path, n_items, created_at. Placeholders as strings or null.
6. experiments/_template/result.json - valid JSON with status (enum completed/aborted/failed), started_at, ended_at, error, items_completed, artifacts.
7. experiments/_template/metrics.json - valid JSON with metrics array (name, value, n, ci_low, ci_high) and notes.
8. experiments/_template/cost.json - valid JSON with model_id, prompt_tokens, completion_tokens, reasoning_tokens, usd, cap_usd, within_cap.
9. docs/learnings/_template.md - narrative post: question, prediction, setup, result, interpretation, limits, what changed in the trust table, links to run and cost.
10. ## OPEN DECISIONS - only genuine unresolved decisions, numbered OD-01 onward.

Constraints: no implementation code; no fabricated results or costs; templates must be directly usable; status.complete.json must validate against the schema; do not contradict existing docs.

Status schema:
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


Partial status.json (truncated):
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


Tickets:
T-001: Create repository and install spec documents
T-002: Bootstrap Python 3.12, uv, and package skeleton
T-003: Add .gitignore and .env.example
T-004: Implement secrets and forbidden-file scanner with pre-commit hook
T-005: Implement append-only journal check
T-006: Implement YAML schema validation command
T-007: Implement status.json generation, README block, and consistency check
T-008: Implement config loading and core pydantic models
T-009: Implement hardware check
T-010: Implement metrics library
T-011: Implement cost estimator and CostGuard
T-012: Implement client interface and FixtureClient
T-013: Implement OpenRouterClient with retries and mock-transport tests
T-014: Implement run IDs, `lab new-run`, and the prediction gate
T-015: Implement the lab registry, runner engine, and `lab run` / `lab estimate`
T-016: Implement post-mortem check
T-017: Author all 17 lab manifests and implement `labs list` / `labs check-tiers`
T-018: Implement dataset build and synthetic fixture framework
T-019: Implement lab L-003 (eval statistics workbench)
T-020: Implement lab E9 (context distractors and position)
T-021: Implement lab E2 (schema field order)
T-022: Implement lab E4 (escape hatch)
T-023: Implement lab E5 (position and verbosity bias)
T-024: Implement smoke suite with total cost cap
T-025: Implement module checkpoint grader
T-026: Implement provenance ledger check
T-027: Implement traceability check
T-028: Author the 13 module YAML files
T-029: Author level A cards A-002..A-010
T-030: Author level B cards B-002..B-014
T-031: Author level C cards (18 remaining)
T-032: Author level D and E cards
T-033: Author level F cards and close traceability
T-034: Write learner guide and M-A1 walkthrough
T-035: Implement repo-layout test and `aiu check-all`
T-036: Pin models and prices, recompute expected costs, and run live smoke
T-037: Complete module M-A1 end-to-end with a live E9 run
T-038: Run final v1 acceptance