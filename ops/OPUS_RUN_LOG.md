# Opus Architecture Run Log

Purpose: record every OpenRouter architecture call, its cost, and what failed. The point is to make the design process auditable, including the wasted calls.

- Provider: OpenRouter
- Model (pinned): `anthropic/claude-opus-5.5`
- Temperature: 0.2
- Date: 2026-10-24
- Key: loaded from an existing local `.env`; never printed or committed.
- Raw responses, repaired markdown, and `meta.json` are under `ops/opus/<timestamp>/`.

## Calls

| Run | Max tokens | Reasoning | Finish | Visible chars | Cost (USD) | Note |
|---|---:|---|---|---:|---:|---|
| 20261024-101340 | 60000 | default (high) | length | 0 | 1.263892 | All tokens spent on reasoning; empty content |
| 20261024-102349 | 64000 | `max_tokens: 6000` (ignored) | length | 0 | 1.343892 | Same failure; `max_tokens` reasoning cap not honored |
| 20261024-103442 | 64000 | low | length | 86274 | 1.343892 | First real output; 9 deliverables complete, TASKS partial |
| 20261024-104535 | 64000 | low | error | 0 | 0.000000 | 402 in-flight budget |
| 20261024-104554 | 32000 | low | length | 66539 | 0.857516 | TASKS part 2 through T-038 partial |
| 20261024-105034 | 16000 | low | error | 0 | 0.000000 | 402 in-flight budget |
| 20261024-105047 | 1000 | low | error | 0 | 0.000000 | 402; large system prompt |
| 20261024-105112 | 12000 | low | error | 0 | 0.000000 | 402 |
| 20261024-105113 | 8000 | low | error | 0 | 0.000000 | 402 |
| 20261024-105114 | 4000 | low | error | 0 | 0.000000 | 402 |
| 20261024-105347 | 3000 | low | stop | 2 | 0.000344 | Minimal-prompt probe after cooldown |
| 20261024-105404 | 6000 | low | length | 10507 | 0.133820 | T-038 complete; ACCEPTANCE through AC-13 |
| 20261024-105510 | 4000 | low | stop | 4924 | 0.057108 | ACCEPTANCE AC-14..AC-20 |
| 20261024-105546 | 8000 | low | length | 17609 | 0.177692 | Governance/README/JOURNAL/PROVENANCE/RESULTS/status schema; status partial |
| 20261024-105721 | 6000 | low | stop | 11847 | 0.112592 | status.json, CHANGELOG, templates, open decisions |

**Recorded total (15 logged attempts):** 5.290748 USD
**Direct diagnostic probes (not saved as run dirs):** one succeeded at 0.000128 USD; two were rejected with 402 at 0.00 USD.
**Project total:** **5.290876 USD**

This is the project's measured share from each response's `usage.cost`. The OpenRouter key has other usage; see the key's account page for the full total.

## What went wrong, and the rules we take forward

1. **Mandatory reasoning can eat the entire output budget.** Opus 5.5 has `mandatory: true` and defaults to `high` effort. With `max_tokens` equal to the intended output size, it reasoned until `finish_reason: length` and returned zero visible characters. It was still billed. Two calls cost 2.607784 USD and produced nothing.
2. **`reasoning.max_tokens` is not a universal cap.** For this model, the model metadata exposes only `supported_efforts`; the token-budget form was ignored. Use `reasoning.effort` and verify the model's `reasoning` object first.
3. **`effort: low` still reserves about 20% of `max_tokens` for reasoning.** Budget `max_tokens` as reasoning + visible output, not visible output alone.
4. **402 is not always "no credit".** The response was `in_flight_budget_exhausted`: the request's pre-authorized max cost exceeded the in-flight ceiling, even with 1.57 USD of credit left. The fixes are smaller `max_tokens`, smaller input, waiting for `Retry-After`, or adding credits.
5. **PowerShell 5.1 mangled UTF-8.** The first responses were decoded as Latin-1, producing mojibake. A later unconditional repair corrupted already-correct characters into U+FFFD. We switched to a marker-gated repair. Future calls should read raw response bytes and decode UTF-8 explicitly.
6. **Some characters were lost in transit entirely** (`§` became U+FFFD, `→`/`≈`/`≤` became `?`). They were repaired by context and the files rescanned. Lesson: prefer ASCII in machine-checked specs, or validate a non-ASCII allowlist on receipt.

## Artifacts produced

`DECISIONS.md`, `CONSTITUTION.md`, `schemas/curriculum.schema.json`, `schemas/status.schema.json`, `REPO_LAYOUT.md`, `LAB_SPEC.md`, `curriculum/{A,B,C}/*.yaml`, `TRACEABILITY.md`, `TASKS.md` (T-001..T-038), `ACCEPTANCE.md` (AC-01..AC-20), `GOVERNANCE.md`, `README.md`, `JOURNAL.md`, `PROVENANCE.md`, `RESULTS.md`, `status.json`, `CHANGELOG.md`, `experiments/_template/*`, `docs/learnings/_template.md`.

## Next time

- Pin the model and verify its `reasoning` metadata before building the request.
- Start with `max_tokens` large enough for reasoning plus output, or use `effort: low` with a reserved output budget.
- Keep prompts small for follow-up calls; the previous output is enough context.
- Save every raw response before parsing.
- Treat the architecture spend as part of the learning record, not overhead to hide.
