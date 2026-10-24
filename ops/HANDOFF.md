# AI University — Session Handoff

**Repo:** `C:\Users\Joe\Documents\Playground\AIUniversity`
**Remote:** https://github.com/quirps/AIUniversity.git
**Branch:** `main`
**Stage:** `building`
**Tests:** 118 passing
**Live runs:** none
**Next ticket:** **T-017**

This file is the operational handoff. It is written so a fresh session can continue without reading a long prior conversation.

---

## 1. Current state

T-001 through T-016 are complete and pushed.

| Area | State |
|---|---|
| Repository, licenses, source PDF | Done |
| Python 3.12 via `uv`, CLI | Done |
| Secrets scan, journal check, pre-commit hooks | Done |
| JSON Schema validation | Done |
| Generated `status.json` + README status block | Done |
| Config, pricing, caps, Pydantic models | Done |
| Hardware probe and tier checks | Done |
| Metrics library | Done |
| Cost estimator and guard | Done |
| Fixture and OpenRouter clients | Done |
| Run IDs, `lab new-run`, committed-prediction gate | Done |
| Lab registry, runner, estimator | Done |
| Post-mortem check | Done |
| Lab manifests, E9 data, M-A1 content | **Not started** |
| Learner HTML workbench / DeepSeek shell | **Not started (ADR-024)** |

`status.json` currently reports 22 open gaps. The next ticket removes T-017 from that list and regenerates the file.

---

## 2. Working commands

Always run from the repo root with `uv`:

```powershell
uv run pytest
uv run aiu --version
uv run aiu validate
uv run aiu status --write
uv run aiu status --check
uv run aiu secrets-scan
uv run aiu journal check
uv run aiu hwcheck --json
uv run aiu lab new-run L-999 --mode fixture
uv run aiu lab estimate L-999
uv run aiu lab run L-999 --run-id <id> --mode fixture
uv run aiu lab postmortem-check L-999 --run-id <id>
```

`L-999` is the toy lab used in tests; it is registered in `tests/conftest.py`. Real labs are not yet authored.

---

## 3. Next ticket: T-017

Read `TASKS.md` → `### T-017: Author all 17 lab manifests and implement labs list / labs check-tiers`.

Deliverables:

- 17 manifests: `labs/E1/manifest.yaml` through `labs/E13/manifest.yaml`, plus `labs/L-001`..`labs/L-004`.
- `src/aiu/labs/tiers.py`.
- `tests/test_tiers.py`.
- `tests/fixtures/invalid_lab_local_bad_fallback.yaml`.
- CLI: `aiu labs list`, `aiu labs check-tiers [PATH]`.

Key sources:

- `LAB_SPEC.md` §6: lab index, status, tier, roles, calls, expected cost.
- `LAB_SPEC.md` §8: exact runnable lab specs (E2, E4, E5, E9, L-003).
- `LAB_SPEC.md` §9: specified lab specs.
- `schemas/curriculum.schema.json`: the `lab` schema is strict; every field is required.

Recommended order inside T-017:

1. Author E9 first, validate it, then author the other 16. This gets the first module's lab definition in place early.
2. Implement `tiers.py` and the two CLI commands.
3. Add the invalid local-tier fixture and tests.
4. Run the T-017 acceptance commands.

T-017 acceptance:

```powershell
uv run aiu validate labs          # validate: 17 files, 0 errors
uv run aiu labs list              # 17 lines
uv run aiu labs check-tiers       # tiers: OK (17 labs)
uv run aiu labs check-tiers tests/fixtures/invalid_lab_local_bad_fallback.yaml
uv run pytest tests/test_tiers.py
```

T-017 DoD:

- Append a `JOURNAL.md` entry.
- `uv run aiu status --write` shows **5 runnable / 12 specified** labs.
- `uv run aiu status --check` passes.
- Remove T-017 from `status.json.known_gaps` before the final status write.
- Commit and push.

---

## 4. After T-017

The first learner-visible milestone is **M-A1 + E9**:

1. **T-018** — E9 dataset and synthetic fixtures.
2. **T-020** — E9 lab implementation.
3. **T-025** — checkpoint grader.
4. **T-028** — M-A1 module YAML.
5. **T-029** — level-A cards A-002..A-010.
6. **T-034** — learner guide and M-A1 walkthrough.
7. **T-037** — one full live E9 learning loop (estimated $0.40).
8. **ADR-024** — HTML workbench + lesson-scoped DeepSeek shell, required before M-A1 is learner-complete.
9. **T-036 / T-038** — pin models/prices, run the $5 smoke suite, final acceptance.

Do not declare M-A1 complete before the workbench exists. See `DECISIONS.md` ADR-024.

---

## 5. Project rules that are easy to get wrong

- **Do not edit old `JOURNAL.md` entries.** Append only. The pre-commit hook enforces a prefix check.
- **`status.json` and the README STATUS block are generated.** After any state change, remove the completed ticket from `status.json.known_gaps`, then run `uv run aiu status --write`, then `--check`.
- **No secrets in the repo.** Use `OPENROUTER_API_KEY` from the environment. The pre-commit hook runs `aiu secrets-scan --staged`.
- **No network in tests.** `pytest-socket` is active. Use `httpx.MockTransport` for HTTP tests.
- **Use `uv run`.** The system Python is 3.7.4; the project uses Python 3.12.
- **API-only.** The measured machine has ~0.43 GB RAM available and ~3.6 GB VRAM free. Do not add local-model or GPU-training work to v1.
- **Model roles are `UNPINNED`.** Live mode must fail with exit 6 until T-036 pins IDs and prices. Fixture mode uses fixture-default pricing.
- **Cost caps:** $2.00 per lab run, $5.00 smoke suite, $1.00/day soft target. Do not raise them without a DECISIONS entry.
- **Prediction gate:** the prediction must be committed. `written_at <= commit time < run start`. YAML may return a `datetime` for an unquoted timestamp; `src/aiu/runs.py` accepts both strings and datetimes.
- **Fixtures:** a `fixture_recorded` hash mismatch is an error; `fixture_synthetic` ignores the hash. Fixture runs report `actual_usd: 0.0`.
- **Post-mortem:** the five required headings and the front-matter `trust_table_row` are enforced by `src/aiu/postmortem.py`.
- **`--record`** is live-only and overwrites `labs/<id>/fixtures/responses.jsonl`.
- **Windows/PowerShell.** Use `git` and `uv` as shown. The pre-commit hook adds `~/.local/bin` to PATH itself.

---

## 6. Key files

| File | Why |
|---|---|
| `TASKS.md` | Authoritative ticket list and acceptance tests |
| `LAB_SPEC.md` | Lab index, specs, metrics, cost basis, modules |
| `schemas/curriculum.schema.json` | Strict schema for lab manifests and cards |
| `DECISIONS.md` | ADRs and canonical OD register |
| `JOURNAL.md` | Append-only history; read the latest 2–3 entries |
| `status.json` | Current generated state |
| `docs/STATUS_REPORT.md` | Manager-level overview |
| `src/aiu/runner.py` | Runner algorithm and exit mapping |
| `src/aiu/runs.py` | Run IDs, prediction gate, freezing |
| `src/aiu/postmortem.py` | Post-mortem checks |
| `src/aiu/cli.py` | All CLI commands |
| `tests/conftest.py` | Registers the toy lab `L-999` |
| `ops/NEXT_SESSION_PROMPT.md` | Paste-ready prompt for a fresh session |

---

## 7. Open decisions / clarifications

- **OD-01:** model IDs and prices are intentionally unpinned until T-036. The policy is role-based and cheap-first.
- **OD-09:** human-labeled datasets for E1/E7/E13 are deferred until those labs become runnable.
- **ADR-024 UI clarification:** when the workbench starts, decide whether the lesson shell is a chat REPL, a sandboxed terminal, or both; whether it uses DeepSeek through OpenRouter or the direct API; and what it may touch.

No Opus calls should be made unless the user explicitly asks.
