from __future__ import annotations

import json
import random

from aiu.fixtures_synth import register_synth
from aiu.labs.base import register
from aiu.metrics import normalize_answer
from aiu.models import CallResult, Item, Message, PlannedCall

ALLOWED_VERDICTS = {"entailed", "not_entailed"}
CONDITION_KEYS = {
    "verdict_first": ("verdict", "reasoning"),
    "reasoning_first": ("reasoning", "verdict"),
    "evidence_first": ("evidence_quote", "reasoning", "verdict"),
}
ERROR_RATES = {
    "verdict_first": 0.15,
    "reasoning_first": 0.10,
    "evidence_first": 0.08,
}
PARSE_FAILURE_RATE = 0.02


def parse_json(text: str | None) -> dict | None:
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        payload = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def parse_verdict(text: str | None) -> str | None:
    payload = parse_json(text)
    if payload is None:
        return None
    verdict = payload.get("verdict")
    return verdict if verdict in ALLOWED_VERDICTS else None


def _system_prompt(condition: str) -> str:
    keys = ", ".join(CONDITION_KEYS[condition])
    return (
        "Decide whether the claim is entailed by the passage. "
        f"Return a single JSON object with exactly these keys in this order: {keys}. "
        'verdict must be "entailed" or "not_entailed".'
    )


def _user_prompt(item: Item) -> str:
    return f"Passage:\n{item.input['passage']}\n\nClaim: {item.input['claim']}"


@register
class E2:
    lab_id = "E2"

    def plan(self, items: list[Item], manifest: dict, cfg) -> list[PlannedCall]:
        procedure = manifest["procedure"]
        calls: list[PlannedCall] = []

        for item in items:
            for condition in CONDITION_KEYS:
                calls.append(
                    PlannedCall(
                        call_key=f"{item.id}|{condition}|cheap_a|0",
                        item_id=item.id,
                        condition=condition,
                        role="cheap_a",
                        sample=0,
                        messages=[
                            Message(role="system", content=_system_prompt(condition)),
                            Message(role="user", content=_user_prompt(item)),
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
        metrics: dict[str, float | None] = {}
        accuracy: dict[str, float | None] = {}

        for condition in CONDITION_KEYS:
            if not items:
                accuracy[condition] = None
                metrics[f"accuracy:{condition}"] = None
                metrics[f"parse_rate:{condition}"] = None
                metrics[f"mean_rationale_chars:{condition}"] = None
                continue

            correct = 0
            parsed = 0
            rationale_lengths: list[int] = []
            for item in items:
                text = answers.get(f"{item.id}|{condition}|cheap_a|0")
                verdict = parse_verdict(text)
                if verdict is not None:
                    parsed += 1
                if verdict == item.expected["label"]:
                    correct += 1
                payload = parse_json(text)
                if payload is not None and isinstance(payload.get("reasoning"), str):
                    rationale_lengths.append(len(payload["reasoning"]))

            accuracy[condition] = correct / len(items)
            metrics[f"accuracy:{condition}"] = accuracy[condition]
            metrics[f"parse_rate:{condition}"] = parsed / len(items)
            metrics[f"mean_rationale_chars:{condition}"] = (
                sum(rationale_lengths) / len(rationale_lengths)
                if rationale_lengths
                else 0.0
            )

        valid_evidence = 0
        for item in items:
            text = answers.get(f"{item.id}|evidence_first|cheap_a|0")
            payload = parse_json(text)
            quote = payload.get("evidence_quote") if payload is not None else None
            if isinstance(quote, str) and normalize_answer(quote) in normalize_answer(
                item.input["passage"]
            ):
                valid_evidence += 1
        metrics["evidence_valid_rate:evidence_first"] = (
            valid_evidence / len(items) if items else None
        )

        if accuracy["evidence_first"] is None or accuracy["verdict_first"] is None:
            metrics["delta_evidence_vs_verdict"] = None
        else:
            metrics["delta_evidence_vs_verdict"] = (
                accuracy["evidence_first"] - accuracy["verdict_first"]
            )

        return metrics


@register_synth("E2")
def synthesize(
    items: list[Item],
    calls: list[PlannedCall],
    rng: random.Random,
) -> list[CallResult]:
    by_id = {item.id: item for item in items}
    results: list[CallResult] = []

    for call in calls:
        item = by_id[call.item_id]
        if rng.random() < PARSE_FAILURE_RATE:
            text = "not json"
        else:
            correct = item.expected["label"]
            wrong = "not_entailed" if correct == "entailed" else "entailed"
            verdict = wrong if rng.random() < ERROR_RATES[call.condition] else correct
            reasoning = (
                "The passage states the relevant fact directly."
                if verdict == "entailed"
                else "The claim conflicts with a fact stated in the passage."
            )
            payload = {}
            for key in CONDITION_KEYS[call.condition]:
                if key == "verdict":
                    payload[key] = verdict
                elif key == "reasoning":
                    payload[key] = reasoning
                else:
                    payload[key] = item.meta["evidence_sentence"]
            text = json.dumps(payload, ensure_ascii=False)

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
