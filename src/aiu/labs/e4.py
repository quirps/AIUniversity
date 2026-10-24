from __future__ import annotations

import random

from aiu.fixtures_synth import register_synth
from aiu.labs.base import register
from aiu.metrics import normalize_answer
from aiu.models import CallResult, Item, Message, PlannedCall

IN_TAX_LABELS = ("billing", "login", "shipping", "refund", "bug")
ESCAPE_LABELS = (*IN_TAX_LABELS, "other", "insufficient_info")
CONDITION_LABELS = {
    "no_escape": IN_TAX_LABELS,
    "escape": ESCAPE_LABELS,
}
ERROR_RATES = {"no_escape": 0.05, "escape": 0.07}
ESCAPE_OTHER_RATE = 0.85


def parse_label(text: str | None, allowed: tuple[str, ...]) -> str | None:
    if text is None:
        return None
    normalized = normalize_answer(text)
    for label in allowed:
        if normalize_answer(label) == normalized:
            return label
    return None


def _system_prompt(condition: str) -> str:
    labels = ", ".join(CONDITION_LABELS[condition])
    return (
        "Classify the support message. Reply with exactly one label from this list: "
        f"{labels}. Reply with the label only."
    )


@register
class E4:
    lab_id = "E4"

    def plan(self, items: list[Item], manifest: dict, cfg) -> list[PlannedCall]:
        procedure = manifest["procedure"]
        calls: list[PlannedCall] = []

        for item in items:
            for condition in CONDITION_LABELS:
                calls.append(
                    PlannedCall(
                        call_key=f"{item.id}|{condition}|cheap_a|0",
                        item_id=item.id,
                        condition=condition,
                        role="cheap_a",
                        sample=0,
                        messages=[
                            Message(role="system", content=_system_prompt(condition)),
                            Message(
                                role="user",
                                content=item.input["message"],
                            ),
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
        in_tax = [item for item in items if item.expected["in_taxonomy"]]
        oot = [item for item in items if not item.expected["in_taxonomy"]]
        metrics: dict[str, float | None] = {}
        accuracy: dict[str, float | None] = {}
        error_rate: dict[str, float | None] = {}

        for condition in CONDITION_LABELS:
            allowed = CONDITION_LABELS[condition]
            correct = 0
            for item in in_tax:
                text = answers.get(f"{item.id}|{condition}|cheap_a|0")
                if parse_label(text, allowed) == item.expected["label"]:
                    correct += 1
            accuracy[condition] = correct / len(in_tax) if in_tax else None
            metrics[f"in_tax_accuracy:{condition}"] = accuracy[condition]

            errors = 0
            for item in oot:
                text = answers.get(f"{item.id}|{condition}|cheap_a|0")
                if parse_label(text, allowed) in IN_TAX_LABELS:
                    errors += 1
            error_rate[condition] = errors / len(oot) if oot else None
            metrics[f"oot_error_rate:{condition}"] = error_rate[condition]

        if (
            error_rate["no_escape"] is None
            or error_rate["escape"] is None
        ):
            metrics["oot_error_drop"] = None
        else:
            metrics["oot_error_drop"] = (
                error_rate["no_escape"] - error_rate["escape"]
            )

        if accuracy["no_escape"] is None or accuracy["escape"] is None:
            metrics["in_tax_cost"] = None
        else:
            metrics["in_tax_cost"] = accuracy["no_escape"] - accuracy["escape"]

        return metrics


@register_synth("E4")
def synthesize(
    items: list[Item],
    calls: list[PlannedCall],
    rng: random.Random,
) -> list[CallResult]:
    by_id = {item.id: item for item in items}
    results: list[CallResult] = []

    for call in calls:
        item = by_id[call.item_id]
        allowed = CONDITION_LABELS[call.condition]

        if item.expected["in_taxonomy"]:
            if rng.random() < ERROR_RATES[call.condition]:
                wrong = [label for label in allowed if label != item.expected["label"]]
                text = rng.choice(wrong)
            else:
                text = item.expected["label"]
        elif call.condition == "no_escape":
            text = rng.choice(IN_TAX_LABELS)
        elif rng.random() < ESCAPE_OTHER_RATE:
            text = "other"
        else:
            text = rng.choice(IN_TAX_LABELS)

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
