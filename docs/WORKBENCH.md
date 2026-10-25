# Learner workbench (ADR-024)

The workbench is a local, read-mostly HTML page over the CLI harness. It renders
the lesson from the module YAML and committed run artifacts; it does not replace
the CLI as the source of truth.

## Start it

```powershell
uv run aiu workbench serve M-A1
```

Open `http://127.0.0.1:8765/`. The server binds to localhost only.

Render a static page instead:

```powershell
uv run aiu workbench render M-A1 --out docs/workbench-M-A1.html
```

## What the page shows

- Module title, objective, and card summaries (one-liner, why it matters,
  decision rule, failure modes, misconceptions, retrieval questions).
- The module's labs and the latest live run for each: status, evidence class,
  hypothesis support, validity, cost, metrics, prediction, and post-mortem.
- The trust-table rows for the module's cards.
- The deterministic checkpoint form. Submitting it grades through the same
  `aiu.checkpoint` code and writes
  `learner/checkpoints/<module>.result.json`.
- A lesson-scoped DeepSeek shell.

## Shell scope

The shell is a chat REPL with the current lesson context. It is not a terminal
and it has no tool access.

- It reads the module YAML, the module's cards, the latest run summaries, and
  the trust rows, and puts a bounded summary in the system prompt.
- It accepts only `user` and `assistant` messages from the browser.
- It calls DeepSeek direct (`deepseek-flash`) with `DEEPSEEK_API_KEY`.
- It cannot run labs, edit files, read arbitrary paths, or execute commands.
- The local server exposes only `/`, `/health`, `/api/chat`, and
  `/api/checkpoint`. There is no arbitrary file-serving route.

The workbench is for a local learner session. It has no authentication and must
not be exposed to a network.

## Current boundaries

- The page is server-rendered; there is no database or second content source.
- The checkpoint result is written by the existing CLI checkpoint code.
- Prediction and post-mortem authoring stay in the CLI/markdown workflow.
- The full ADR-024 UI acceptance still needs a human pass on layout, content,
  and the shell's lesson boundaries.
