from __future__ import annotations

import random

from aiu.generators.base import register_generator
from aiu.models import Item

POSITIVE = "fail"
NEGATIVE = "pass"

# TP, FN, FP, TN
LABEL_COUNTS = (
    (POSITIVE, POSITIVE, 24),
    (NEGATIVE, POSITIVE, 6),
    (POSITIVE, NEGATIVE, 14),
    (NEGATIVE, NEGATIVE, 156),
)

AGENT_SUCCESS_COUNTS = (5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 1, 1, 1, 0, 0, 5, 4, 3)
TRIALS = 5


@register_generator("L-003")
def generate(rng: random.Random) -> list[Item]:
    pairs: list[tuple[str, str]] = []
    for judge_label, human_label, count in LABEL_COUNTS:
        pairs.extend([(judge_label, human_label)] * count)
    rng.shuffle(pairs)

    items = [
        Item(
            id=f"j{index:03d}",
            input={"judge_label": judge_label, "human_label": human_label},
            expected={},
            meta={},
        )
        for index, (judge_label, human_label) in enumerate(pairs)
    ]

    for index, successes in enumerate(AGENT_SUCCESS_COUNTS):
        items.append(
            Item(
                id=f"t{index:02d}",
                input={},
                expected={"successes": successes, "trials": TRIALS},
                meta={},
            )
        )

    return sorted(items, key=lambda item: item.id)
