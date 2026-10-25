# The `strong` model role

`strong` is the ceiling and escalation model, not the everyday model. It is used
where the harness needs a clearly more capable model than the cheap roles:

- **E12 ceiling test:** run failed items with oracle context to separate prompt or
  context failures from capability failures. This is the role's defining use.
- **E10 cascade:** the escalation target after the cheap model is uncertain.
- **E7 jury vs single:** the single strong-judge baseline.

E9, E2, E4, and E5 smoke work use `cheap_a` or `judge_a`; they do not need
`strong`.

## How powerful does it need to be?

It should be a frontier reasoning model for the task, not merely a mid-tier
model. In practice it needs:

- clearly better accuracy than `cheap_a` on the E2/E9 tasks when given oracle
  context;
- strong instruction following and reading comprehension over long inputs;
- reliable structured output for E2-style JSON;
- enough reasoning depth for multi-step or ambiguous cases;
- a price that keeps a full E10/E12 run under the $2.00 per-lab cap.

A model in the Gemini 2.5 Flash or DeepSeek Flash class is a cheap role, not a
ceiling role. Gemini 2.5 Pro was proposed and rejected as the ceiling; the owner
asked for something better. The right test is measured accuracy on the gold set
with oracle context, not a leaderboard label.

## What must be configured

1. Add the exact model ID, family, and provider to `config/models.yaml`:

   ```yaml
   strong: {model_id: <pinned-id>, family: <family>, provider: openrouter|deepseek}
   ```

2. Add its input/output prices to `config/pricing.yaml` under `models` and pin
   `retrieved_at`.
3. Provide the matching key: `OPENROUTER_API_KEY` for an OpenRouter model, or
   `DEEPSEEK_API_KEY` for a DeepSeek direct model.
4. Re-run `uv run aiu lab estimate E10` and `uv run aiu lab estimate E12` to check
   the per-lab cap.
5. No live acceptance run is required to pin the role, but E12 is the natural
   first live test.

## Current state

`strong` is intentionally `UNPINNED`. The cheapest path with the existing key is
DeepSeek direct `deepseek-v4-pro`; that is a candidate, not a decision. If the
owner wants a different frontier family, an OpenRouter key and the exact model ID
are required. Do not fabricate the ID, price, or benchmark claim.
