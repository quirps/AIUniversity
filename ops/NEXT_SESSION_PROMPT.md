# Next-Session Prompt

Paste the block below into a fresh session.

---

You are continuing the AI University project at `C:\Users\Joe\Documents\Playground\AIUniversity` (remote: `https://github.com/quirps/AIUniversity.git`).

Read, in this order:

1. `ops/HANDOFF.md`
2. `TASKS.md` from `T-031` onward
3. `LAB_SPEC.md` sections 6, 8, and 9
4. `schemas/curriculum.schema.json`
5. `DECISIONS.md` ADR-024 and the decision register
6. The latest entries in `JOURNAL.md`

Current state: T-001 through T-038 are complete, v1.0.0 is tagged, 213 tests pass, all 17 lab manifests, 13 modules, and all 75 cards validate, `aiu check-all` reports 19/19 checks OK, AC-01..AC-20 pass in a clean clone with no provider keys, and 15 live runs are committed (total lab-run spend $0.1704). The ADR-024 first slice is implemented: `aiu workbench serve M-A1` serves a local lesson page with cards, latest run artifacts, trust rows, the checkpoint form, and a lesson-scoped DeepSeek chat; ADR-026 records the shell scope. Remaining work is the ADR-024 UI/content polish, human review of the 75 draft cards (M-A1 first; see `docs/DRAFT_CARD_REVIEW.md`), and an exact pin for the `strong` role (see `docs/STRONG_ROLE.md`).

If the current context is already long, stop after reading `ops/HANDOFF.md` and start the next ticket in a fresh session.

Follow `TASKS.md` exactly: files, interfaces, acceptance tests, and definition of done.

After each ticket:

```powershell
uv run pytest
uv run aiu validate
uv run aiu status --write
uv run aiu status --check
uv run aiu secrets-scan
uv run aiu journal check
```

Rules:

- Do not edit old `JOURNAL.md` entries; append only.
- Remove the completed ticket from `status.json.known_gaps` before the final status write.
- Do not commit secrets. Use `OPENROUTER_API_KEY` from the environment only.
- Do not add network calls to tests.
- API-only v1; no local models or GPU training.
- Do not call Opus unless the user explicitly asks.
- Keep the learner-facing HTML workbench and lesson-scoped DeepSeek shell (ADR-024) in scope for M-A1.

Report progress at ticket checkpoints and keep the repo clean and pushed.
