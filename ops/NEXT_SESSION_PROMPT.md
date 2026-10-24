# Next-Session Prompt

Paste the block below into a fresh session.

---

You are continuing the AI University project at `C:\Users\Joe\Documents\Playground\AIUniversity` (remote: `https://github.com/quirps/AIUniversity.git`).

Read, in this order:

1. `ops/HANDOFF.md`
2. `TASKS.md` from `T-017` onward
3. `LAB_SPEC.md` sections 6, 8, and 9
4. `schemas/curriculum.schema.json`
5. `DECISIONS.md` ADR-024 and the decision register
6. The latest entries in `JOURNAL.md`

Current state: T-001 through T-016 are complete, 118 tests pass, and the harness core works. The next ticket is **T-017: author all 17 lab manifests and implement `labs list` / `labs check-tiers`**.

Start with the E9 manifest, then author the other 16. Follow `TASKS.md` exactly: files, interfaces, acceptance tests, and definition of done.

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
