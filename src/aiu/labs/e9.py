from __future__ import annotations

import random

from aiu.fixtures_synth import register_synth
from aiu.labs.base import register
from aiu.metrics import exact_match, normalize_answer
from aiu.models import CallResult, Item, Message, PlannedCall

SYSTEM_PROMPT = (
    "Answer using only the passages. Reply with the answer only, no explanation. "
    "If the passages do not contain the answer, reply UNKNOWN."
)
CONDITION_ORDER = ("oracle", "d5_start", "d5_middle", "d5_end", "d20_middle")
NON_ORACLE = CONDITION_ORDER[1:]
ERROR_RATES = {
    "oracle": 0.02,
    "d5_start": 0.05,
    "d5_middle": 0.10,
    "d5_end": 0.07,
    "d20_middle": 0.15,
}


def _passages(item: Item, condition: str) -> list[str]:
    key = item.input["key_passage"]
    distractors = item.input["distractors"]
    order = item.meta["distractor_order"]
    ordered = [distractors[index] for index in order]

    if condition == "oracle":
        return [key]
    if condition == "d5_start":
        return [key, *ordered[:5]]
    if condition == "d5_middle":
        return [*ordered[:3], key, *ordered[3:5]]
    if condition == "d5_end":
        return [*ordered[:5], key]
    if condition == "d20_middle":
        return [*ordered[:10], key, *ordered[10:20]]
    raise ValueError(f"unknown E9 condition: {condition}")


def _user_prompt(item: Item, passages: list[str]) -> str:
    body = "\n".join(
        f"[{index}] {passage}" for index, passage in enumerate(passages, start=1)
    )
    return f"Passages:\n{body}\n\nQuestion: {item.input['question']}"


@register
class E9:
    lab_id = "E9"

    def plan(self, items: list[Item], manifest: dict, cfg) -> list[PlannedCall]:
        procedure = manifest["procedure"]
        conditions = [condition["name"] for condition in procedure["conditions"]]
        calls: list[PlannedCall] = []

        for item in items:
            for condition in conditions:
                passages = _passages(item, condition)
                calls.append(
                    PlannedCall(
                        call_key=f"{item.id}|{condition}|cheap_a|0",
                        item_id=item.id,
                        condition=condition,
                        role="cheap_a",
                        sample=0,
                        messages=[
                            Message(role="system", content=SYSTEM_PROMPT),
                            Message(role="user", content=_user_prompt(item, passages)),
                        ],
                        temperature=float(procedure["temperature"]),
                        max_tokens=int(procedure["max_tokens"]),
                        seed=int(procedure["seed"]),
                    )
                )
        return calls

    def score(
        self,
        items: list[Item],
        results: list[CallResult],
        manifest: dict,
    ) -> dict[str, float | None]:
        answers = {result.call_key: result.text for result in results}
        accuracy: dict[str, float | None] = {}
        unknown_rate: dict[str, float | None] = {}

        for condition in CONDITION_ORDER:
            if not items:
                accuracy[condition] = None
                unknown_rate[condition] = None
                continue
            correct = 0
            unknown = 0
            for item in items:
                text = answers.get(f"{item.id}|{condition}|cheap_a|0")
                if exact_match(text, item.expected["answer"]):
                    correct += 1
                if text is not None and normalize_answer(text) == "unknown":
                    unknown += 1
            accuracy[condition] = correct / len(items)
            unknown_rate[condition] = unknown / len(items)

        metrics: dict[str, float | None] = {}
        for condition in CONDITION_ORDER:
            metrics[f"accuracy:{condition}"] = accuracy[condition]

        drops: dict[str, float | None] = {}
        for condition in NON_ORACLE:
            oracle = accuracy["oracle"]
            value = accuracy[condition]
            drops[condition] = (
                oracle - value
                if oracle is not None and value is not None
                else None
            )
            metrics[f"accuracy_drop:{condition}"] = drops[condition]

        if all(drop is not None for drop in drops.values()):
            metrics["max_drop"] = max(drop for drop in drops.values() if drop is not None)
        else:
            metrics["max_drop"] = None

        for condition in CONDITION_ORDER:
            metrics[f"unknown_rate:{condition}"] = unknown_rate[condition]

        return metrics


@register_synth("E9")
def synthesize(
    items: list[Item],
    calls: list[PlannedCall],
    rng: random.Random,
) -> list[CallResult]:
    by_id = {item.id: item for item in items}
    results: list[CallResult] = []

    for call in calls:
        item = by_id[call.item_id]
        order = item.meta["distractor_order"]
        values = item.meta["distractor_values"]
        wrong_answer = values[order[0]]
        text = (
            wrong_answer
            if rng.random() < ERROR_RATES[call.condition]
            else item.expected["answer"]
        )
        results.append(
            CallResult(
                call_key=call.call_key,
                model_id="fixture",
                text=text,
                prompt_tokens=0,
                completion_tokens=0,
                provider_reported_usd=None,
                latency_ms=0,
                source="fixture_synthetic",
                request_sha256="",
                timestamp="1970-01-01T00:00:00Z",
            )
        )

    return results
