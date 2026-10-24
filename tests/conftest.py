from __future__ import annotations

from aiu.labs.base import register
from aiu.models import Message, PlannedCall


class ToyLab:
    lab_id = "L-999"

    def plan(self, items, manifest, cfg):
        calls = []
        for item in items:
            calls.append(
                PlannedCall(
                    call_key=f"{item.id}|base|cheap_a|0",
                    item_id=item.id,
                    condition="base",
                    role="cheap_a",
                    sample=0,
                    messages=[Message(role="user", content=item.input["prompt"])],
                    temperature=0.0,
                    max_tokens=16,
                    seed=None,
                )
            )
        return calls

    def score(self, items, results, manifest):
        answers = {result.call_key.split("|")[0]: result.text for result in results}
        correct = sum(
            1
            for item in items
            if answers.get(item.id) == item.expected["answer"]
        )
        return {"accuracy": correct / len(items) if items else None}


register(ToyLab)
