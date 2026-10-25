# Learner Guide

This guide takes you from a fresh checkout through module M-A1, "Context is the
program", using only commands from the repository root. The CLI harness is the
source of truth for runs, metrics, costs, and artifacts.

## Setup

Run the bootstrap once. It installs Python 3.12, syncs the project, installs the
pre-commit hooks, and prints the CLI version.

```powershell
.\ops\bootstrap.ps1
```

Copy the environment template and add your API keys to `.env`. The file is
gitignored; never commit it and never paste a key into a command that writes a
tracked file. `DEEPSEEK_API_KEY` is used by the DeepSeek roles; `OPENROUTER_API_KEY`
is used by the OpenRouter roles.

```powershell
Copy-Item .env.example .env
# edit .env and set DEEPSEEK_API_KEY and OPENROUTER_API_KEY
```

Then check that the repository and hardware are ready for the API-only tier.

```powershell
uv run aiu hwcheck
uv run aiu validate learner
```

`hwcheck` should pass for `API_ONLY`. If it does not, read the failure line before
continuing; the harness will refuse a lab run on a failed hardware check.

## The learning loop

Every lab follows the same loop: commit a prediction, run the experiment, write a
post-mortem, and update the trust table. Do not skip the prediction or write it
after the run.

1. Create a run. This creates `prediction.md` with a `run_id`.
2. Fill in `written_at` and `predicted_metrics`, then commit the prediction before
   starting the run. The prediction gate checks the commit time.
3. Estimate the run, then run it with the printed `run_id`.
4. Edit the generated `postmortem.md`. It must cover prediction vs outcome, what
   surprised you, confounds, the rule-of-thumb update, and the next experiment.
5. Add or update a row in `learner/trust_table.yaml`, and record the run in
   `RESULTS.md`.
6. Validate and regenerate the status block.

The harness records the prediction hash, config, responses, metrics, and cost in
the run directory. A live run writes to `experiments/<LAB_ID>/<RUN_ID>/` and must
be kept. Do not edit the run artifacts after the run; record interpretation in the
post-mortem.

## Module M-A1 walkthrough

M-A1 uses E9 (context distractors and position), E12 (ceiling test), and L-001
(pinned replay). The first live run in this walkthrough is E9 using the exact
commands from `LAB_SPEC.md` section 2.

Live mode requires every model role used by the lab to be pinned to a real model
ID and price. The E9 walkthrough uses `cheap_a`, which is pinned to DeepSeek
direct (`deepseek-flash`); set `DEEPSEEK_API_KEY`. The OpenRouter roles are pinned
but are not required for this walkthrough. `strong` remains `UNPINNED` until a
later decision.

```powershell
uv run aiu lab new-run E9 --mode live          # prints RUN_ID; creates prediction.md
# edit experiments\E9\<RUN_ID>\prediction.md   # fill written_at and predicted_metrics BEFORE running
uv run aiu lab estimate E9
uv run aiu lab run E9 --run-id <RUN_ID> --mode live
# edit experiments\E9\<RUN_ID>\postmortem.md   # copied from the template at run end
uv run aiu lab postmortem-check E9 --run-id <RUN_ID>
# add or update a row in learner\trust_table.yaml; add a row to RESULTS.md
uv run aiu validate learner
uv run aiu status --write
```

The prediction must cover the E9 metrics you care about, including
`accuracy:oracle`, `accuracy:d20_middle`, `accuracy_drop:d20_middle`, and
`max_drop`. Commit it before the run. If the run aborts, keep the run directory
and its `cost.json`.

Create `learner/checkpoints/M-A1.answers.yaml` in this shape, replacing the
placeholders with your own answers. The module definition is in
`curriculum/modules/M-A1.yaml`; all three items are deterministic.

```yaml
module_id: M-A1
answers:
  Q01: <your numeric answer>
  Q02: <one of the Step choices>
  Q03: <your short answer>
```

Grade the checkpoint after the walkthrough.

```powershell
uv run aiu checkpoint grade M-A1 --answers learner/checkpoints/M-A1.answers.yaml
```

The checkpoint result is written to `learner/checkpoints/M-A1.result.json`. The
module portfolio artifact goes in `learner/portfolio/M-A1/`: a short diagnostic
note and the E9 post-mortem for one run, with each wrong answer classified as
missing-context or present-but-ignored.

## Fixture mode practice

Fixture mode uses saved or synthetic responses, makes no network calls, and
costs nothing. Results from fixture mode are assumed, not measured: they teach the
mechanics and never count as evidence about real model behavior. Do not add
fixture runs to `RESULTS.md`.

The full smoke suite is the supported practice path because fixture runs live
under the gitignored `.runs/` directory and cannot satisfy the committed-
prediction gate there.

```powershell
uv run aiu smoke --mode fixture
```

To practice the prediction loop for a single lab, use a scratch directory outside
`.runs/`, commit the prediction, and pass the same `--out-dir` to `new-run` and
`run`. Replace `<RUN_ID>` with the printed ID.

```powershell
uv run aiu lab new-run E9 --mode fixture --out-dir experiments/_fixture_practice
# edit the prediction, commit it, then run with the same out-dir
uv run aiu lab estimate E9
uv run aiu lab run E9 --run-id <RUN_ID> --mode fixture --out-dir experiments/_fixture_practice
uv run aiu lab postmortem-check E9 --run-id <RUN_ID> --out-dir experiments/_fixture_practice
```

Inspect the scratch run, then remove `experiments/_fixture_practice` before
committing anything else. Fixture artifacts are teaching material, not measured
evidence.

## Costs

E9 has a pinned full-run estimate of **$0.1021** as of the 2026-10-24 price pin.
The per-lab cap is **$2.00**; the harness aborts rather than exceed it. The
suite-level smoke cap is $5.00 and the daily soft target is $1.00.

The estimate is printed before the run. Fixture mode reports an estimate from
`config/pricing.yaml` fixture defaults but has an actual cost of $0.00. Live runs
use the pinned model prices to compute actual cost and record provider-reported
cost when the provider supplies it. If you need to lower spend for a first pass,
use `--limit N`; state the limit in the prediction and post-mortem.

## What the harness will refuse to do

The CLI uses explicit exit codes so a failed run is not mistaken for a successful
one.

| Exit code | Meaning |
|---:|---|
| 3 | A planned call has no fixture response in fixture mode. |
| 4 | The estimated or running cost would exceed the cap; the run is aborted. |
| 5 | The hardware check for the lab's tier failed. |
| 6 | A configuration or precondition failed: missing or invalid config, missing API key or authentication, an unpinned model role, missing pricing, or a lab that is not runnable. |
| 7 | The prediction gate rejected the run: missing or incomplete prediction, null metrics without `smoke: true`, a missing or uncommitted prediction, or a timestamp later than the run start. |

Exit 0 means the command completed. A run can still have status `failed` or
`aborted` inside its run directory when the lab executed but did not produce a
valid result; read `result.json` and `cost.json` before interpreting the output.
