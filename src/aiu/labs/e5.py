from __future__ import annotations

import random

from aiu.fixtures_synth import register_synth
from aiu.labs.base import register
from aiu.metrics import first_slot_rate, flip_rate
from aiu.models import CallResult, Item, Message, PlannedCall

CONDITIONS = {
    "cw_plain": {"A": "correct", "B": "wrong", "padded": False},
    "wc_plain": {"A": "wrong", "B": "correct", "padded": False},
    "cw_padwrong": {"A": "correct", "B": "wrong", "padded": True},
    "wc_padwrong": {"A": "wrong", "B": "correct", "padded": True},
}
PLAIN = ("cw_plain", "wc_plain")
PADDED = ("cw_padwrong", "wc_padwrong")
FIRST_SLOT_RATE = 0.15
PADDED_WRONG_RATE = 0.10


def parse_choice(text: str | None) -> str | None:
    if text is None:
        return None
    for char in text:
        if not char.isspace():
            choice = char.upper()
            return choice if choice in ("A", "B") else None
    return None


def _answer_text(item: Item, identity: str, padded: bool) -> str:
    if identity == "correct":
        return item.input["correct"]
    if padded:
        return f"{item.input['wrong']} {item.input['padding']}"
    return item.input["wrong"]


@register
class E5:
    lab_id = "E5"

    def plan(self, items: list[Item], manifest: dict, cfg) -> list[PlannedCall]:
        procedure = manifest["procedure"]
        calls: list[PlannedCall] = []

        for item in items:
            for condition, slots in CONDITIONS.items():
                a_text = _answer_text(item, slots["A"], slots["padded"])
                b_text = _answer_text(item, slots["B"], slots["padded"])
                user = (
                    f"Question: {item.input['question']}\n\n"
                    f"A: {a_text}\n\n"
                    f"B: {b_text}\n\n"
                    "Which answer is better? Reply with A or B only."
                )
                calls.append(
                    PlannedCall(
                        call_key=f"{item.id}|{condition}|judge_a|0",
                        item_id=item.id,
                        condition=condition,
                        role="judge_a",
                        sample=0,
                        messages=[
                            Message(
                                role="system",
                                content="You are comparing two answers. Reply with A or B only.",
                            ),
                            Message(role="user", content=user),
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
        choices: dict[str, list[str | None]] = {}
        parsed_all: list[str | None] = []

        for condition in CONDITIONS:
            condition_choices: list[str | None] = []
            for item in items:
                choice = parse_choice(
                    answers.get(f"{item.id}|{condition}|judge_a|0")
                )
                condition_choices.append(choice)
                parsed_all.append(choice)
            choices[condition] = condition_choices

        parse_rate = (
            sum(1 for choice in parsed_all if choice is not None) / len(parsed_all)
            if parsed_all
            else None
        )

        def identities(condition: str) -> list[str | None]:
            mapping = CONDITIONS[condition]
            return [
                mapping[choice] if choice in ("A", "B") else None
                for choice in choices[condition]
            ]

        plain_identities = [identities(condition) for condition in PLAIN]
        padded_identities = [identities(condition) for condition in PADDED]

        plain_pairs = [
            (left, right)
            for left, right in zip(*plain_identities)
            if left is not None and right is not None
        ]
        padded_pairs = [
            (left, right)
            for left, right in zip(*padded_identities)
            if left is not None and right is not None
        ]

        flip = flip_rate(
            [pair[0] for pair in plain_pairs],
            [pair[1] for pair in plain_pairs],
        )
        flip_padded = flip_rate(
            [pair[0] for pair in padded_pairs],
            [pair[1] for pair in padded_pairs],
        )

        plain_choices = [
            choice
            for condition in PLAIN
            for choice in choices[condition]
            if choice is not None
        ]
        plain_correct = [
            identity
            for condition in PLAIN
            for identity in identities(condition)
            if identity is not None
        ]
        padded_correct = [
            identity
            for condition in PADDED
            for identity in identities(condition)
            if identity is not None
        ]

        correct_pref_plain = (
            sum(1 for identity in plain_correct if identity == "correct")
            / len(plain_correct)
            if plain_correct
            else None
        )
        correct_pref_padded = (
            sum(1 for identity in padded_correct if identity == "correct")
            / len(padded_correct)
            if padded_correct
            else None
        )
        verbosity_shift = (
            correct_pref_plain - correct_pref_padded
            if correct_pref_plain is not None and correct_pref_padded is not None
            else None
        )

        return {
            "flip_rate": flip,
            "first_slot_rate": first_slot_rate(plain_choices),
            "correct_pref:plain": correct_pref_plain,
            "correct_pref:padwrong": correct_pref_padded,
            "verbosity_shift": verbosity_shift,
            "flip_rate_padded": flip_padded,
            "parse_rate": parse_rate,
        }


@register_synth("E5")
def synthesize(
    items: list[Item],
    calls: list[PlannedCall],
    rng: random.Random,
) -> list[CallResult]:
    by_id = {item.id: item for item in items}
    results: list[CallResult] = []

    for call in calls:
        item = by_id[call.item_id]
        mapping = CONDITIONS[call.condition]
        correct_slot = next(
            slot for slot, identity in mapping.items() if identity == "correct"
        )
        wrong_slot = next(
            slot for slot, identity in mapping.items() if identity == "wrong"
        )

        draw = rng.random()
        if draw < FIRST_SLOT_RATE:
            text = "A"
        elif mapping["padded"] and draw < FIRST_SLOT_RATE + PADDED_WRONG_RATE:
            text = wrong_slot
        else:
            text = correct_slot

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
