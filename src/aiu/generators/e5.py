from __future__ import annotations

import random

from aiu.generators.base import register_generator
from aiu.models import Item

PLANETS = ("Vela", "Orin", "Tarn", "Mira", "Cael", "Dorn")
MOONS = ("Tarn", "Mira", "Vela", "Ost", "Pell", "Quill", "Rook", "Sarn", "Thal", "Umber")
PLACES = ("Kelv", "Dornby", "Wrenford", "Marrow", "Sable", "Harrow")
MATERIALS = (
    "blue slate", "green slate", "copper wire", "amber glass",
    "iron nails", "oak barrels", "silver buttons", "wax candles",
)
RIVERS = ("Kelv", "Mora", "Tarn", "Rill", "Vesh", "Sarn", "Dun", "Bral")
NAMES = (
    "Mara Voss", "Tomas Renn", "Iven Dale", "Sela Moor",
    "Rook Kest", "Bryn Thorne", "Corin Vale", "Dema Holt",
)
PADDING = (
    "The reference text is short and fictional.",
    "This detail appears in a later chapter.",
    "Readers often compare the two accounts.",
    "The surrounding notes add no further detail.",
    "The question is repeated in the practice set.",
    "The passage was written for a teaching exercise.",
)


def _two(pool: tuple[str, ...], rng: random.Random) -> tuple[str, str]:
    first, second = rng.sample(pool, 2)
    return first, second


def _question(rng: random.Random, index: int) -> tuple[str, str, str]:
    kind = index % 5

    if kind == 0:
        planet = rng.choice(PLANETS)
        correct, wrong = _two(MOONS, rng)
        return f"Which moon of the planet {planet} is the largest?", correct, wrong
    if kind == 1:
        place = rng.choice(PLACES)
        correct, wrong = _two(tuple(str(year) for year in range(1600, 1810, 7)), rng)
        return f"In what year was the treaty of {place} signed?", correct, wrong
    if kind == 2:
        place = rng.choice(PLACES)
        correct, wrong = _two(MATERIALS, rng)
        return (
            f"Which material is used for the bearings in the {place} clock?",
            correct,
            wrong,
        )
    if kind == 3:
        place = rng.choice(PLACES)
        correct, wrong = _two(RIVERS, rng)
        return f"Which river supplies the {place} reservoir?", correct, wrong
    place = rng.choice(PLACES)
    correct, wrong = _two(NAMES, rng)
    return f"Who wrote the chronicle of {place}?", correct, wrong


@register_generator("E5")
def generate(rng: random.Random) -> list[Item]:
    rows = [(index, *_question(rng, index)) for index in range(40)]
    rng.shuffle(rows)

    items: list[Item] = []
    for new_index, (_, question, correct, wrong) in enumerate(rows):
        sentences = list(PADDING)
        rng.shuffle(sentences)
        count = rng.choice((2, 3))
        padding = " ".join(sentences[:count])

        items.append(
            Item(
                id=f"e5{new_index:03d}",
                input={
                    "question": question,
                    "correct": correct,
                    "wrong": wrong,
                    "padding": padding,
                },
                expected={"better": "correct"},
                meta={},
            )
        )
    return items
