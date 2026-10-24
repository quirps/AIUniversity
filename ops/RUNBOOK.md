# RUNBOOK

Operational procedures for AI University.

## Live run procedure

1. Load the key into the current shell only. Never write it to a file in the repo.
2. Run the estimate first, then the lab.
3. Commit the run directory, including aborted and failed runs.
4. Add one row to `RESULTS.md`.
5. Append a `JOURNAL.md` entry.

The exact commands are in `LAB_SPEC.md` section 2.

## Key rotation

1. Revoke the old key at openrouter.ai.
2. Update the local `.env` or shell environment.
3. Never commit the key.
4. Run `uv run aiu secrets-scan` before committing.

## Incident: key committed

1. Revoke the key immediately.
2. Do not rewrite history to hide it. Add a `JOURNAL.md` entry describing the incident.
3. Remove the key from the working tree and rotate it.
4. If the commit was pushed, treat the key as public until revoked.

## Incident: cost overrun

1. Stop the run.
2. Keep the run directory and `cost.json`.
3. Add a `JOURNAL.md` entry with the actual cost, the cap, and the cause.
4. If the cause is a harness bug, open a ticket before running again.
