from __future__ import annotations

import random

from aiu.generators.base import register_generator
from aiu.models import Item

ATTRIBUTES = ("founding_year", "population", "river", "mayor", "export", "twin_city")

PREFIXES = (
    "Wren", "Ash", "Bram", "Cal", "Dun", "Elm", "Fen", "Glen", "Harrow", "Ivy",
    "Jar", "Kel", "Lark", "Mar", "North", "Oak", "Pell", "Quill", "Rook", "Stone",
)
SUFFIXES = (
    "ford", "field", "wick", "mere", "stead", "ton", "bury", "gate", "haven", "moor",
    "ridge", "vale", "well", "brook", "crest", "dale", "fell", "holm", "port", "shaw",
)

RIVER_STEMS = (
    "Kelv", "Mora", "Tarn", "Rill", "Vesh", "Sarn", "Dun", "Bral", "Cor", "Wen",
    "Yss", "Pell", "Quen", "Roth", "Sil", "Thal", "Umber", "Vale", "Wick", "Xan",
)
MAYOR_FIRST = (
    "Mara", "Tomas", "Iven", "Sela", "Rook", "Bryn", "Ada", "Corin", "Dema", "Ewan",
    "Fira", "Galen", "Hale", "Isol", "Jory", "Kael", "Lira", "Milo", "Nera", "Oren",
)
MAYOR_LAST = (
    "Voss", "Renn", "Dale", "Moor", "Kest", "Thorne", "Vale", "Brant", "Holt", "Fenn",
    "Grey", "March", "Nash", "Orr", "Pike", "Quill", "Reed", "Stone", "Tarn", "Vane",
)
EXPORTS = (
    "amber glass", "salt cod", "blue wool", "tin lamps", "reed paper",
    "copper wire", "dyed linen", "iron nails", "maple syrup", "smoked eels",
    "clay tiles", "silver buttons", "wax candles", "dried herbs", "river pearls",
    "carved bone", "green slate", "oak barrels", "spun flax", "brass bells",
)
TWIN_STEMS = (
    "Dornby", "Marrow", "Ellwick", "Bram", "Sable", "Harrow", "Lark", "Mirr", "Ost", "Pell",
    "Quarry", "Rook", "Sallow", "Thorn", "Umb", "Vell", "Wester", "Yarn", "Zephyr", "Ashby",
)

CLAIMS = {
    "founding_year": "The town was founded in {value}.",
    "population": "The town has a population of {value}.",
    "river": "The town is crossed by the {value} river.",
    "mayor": "The mayor of the town is {value}.",
    "export": "The town's main export is {value}.",
    "twin_city": "The town is twinned with the city of {value}.",
}

FILLERS = (
    "The surrounding fields are worked by a handful of families.",
    "A narrow road connects it to the larger market town to the south.",
    "Its stone bridge is repaired after every hard winter.",
    "Travelers sometimes stop for the small weekly market.",
    "The local archive keeps a record of the older families.",
    "Children from the outlying farms gather in the central square.",
    "A covered well stands at the edge of the old quarter.",
    "The council meets in a low hall beside the river.",
    "Most houses are built from the pale stone found nearby.",
    "A twice-yearly fair brings traders from the coast.",
)


def _words(text: str) -> int:
    return len(text.split())


def _passage(sentences: list[str], rng: random.Random) -> str:
    fillers = list(FILLERS)
    rng.shuffle(fillers)
    all_sentences = list(sentences)
    index = 0
    while _words(" ".join(all_sentences)) < 80:
        all_sentences.append(fillers[index % len(fillers)])
        index += 1
    text = " ".join(all_sentences)
    count = _words(text)
    assert 80 <= count <= 120, f"passage has {count} words"
    return text


def _entity_names(rng: random.Random) -> list[str]:
    combinations = [
        f"{prefix}{suffix}" for prefix in PREFIXES for suffix in SUFFIXES
    ]
    rng.shuffle(combinations)
    return combinations[:80]


def _facts(rng: random.Random) -> dict[str, str]:
    year = rng.randint(1500, 1950)
    population = rng.randint(1200, 9800)
    return {
        "founding_year": str(year),
        "population": f"{population:,}",
        "river": rng.choice(RIVER_STEMS),
        "mayor": f"{rng.choice(MAYOR_FIRST)} {rng.choice(MAYOR_LAST)}",
        "export": rng.choice(EXPORTS),
        "twin_city": rng.choice(TWIN_STEMS),
    }


def _change_value(attribute: str, value: str, rng: random.Random) -> str:
    if attribute == "founding_year":
        return str(int(value) + rng.choice((17, 31, 64, 109)))
    if attribute == "population":
        return f"{int(value.replace(',', '')) + rng.choice((137, 254, 481)):,}"
    if attribute == "river":
        pool = [stem for stem in RIVER_STEMS if stem != value]
        return rng.choice(pool)
    if attribute == "mayor":
        pool = [
            f"{first} {last}"
            for first, last in zip(MAYOR_FIRST, MAYOR_LAST)
            if f"{first} {last}" != value
        ]
        return rng.choice(pool)
    if attribute == "export":
        pool = [item for item in EXPORTS if item != value]
        return rng.choice(pool)
    pool = [stem for stem in TWIN_STEMS if stem != value]
    return rng.choice(pool)


def _fact_sentence(name: str, attribute: str, value: str) -> str:
    if attribute == "founding_year":
        return f"It was founded in {value}."
    if attribute == "population":
        return f"The town now has a population of {value}."
    if attribute == "river":
        return f"The {value} river runs through it."
    if attribute == "mayor":
        return f"Its mayor is {value}."
    if attribute == "export":
        return f"Its main export is {value}."
    return f"It is twinned with the city of {value}."


@register_generator("E2")
def generate(rng: random.Random) -> list[Item]:
    names = _entity_names(rng)
    entailed_flags = [True] * 40 + [False] * 40
    rng.shuffle(entailed_flags)
    items: list[Item] = []

    for index, (name, entailed) in enumerate(zip(names, entailed_flags)):
        facts = _facts(rng)
        claim_attr = ATTRIBUTES[index % len(ATTRIBUTES)]
        passage_value = facts[claim_attr]
        claim_value = passage_value if entailed else _change_value(
            claim_attr, passage_value, rng
        )
        evidence = _fact_sentence(name, claim_attr, passage_value)

        sentences = [
            f"{name} is a market town on the eastern plain.",
            *[
                _fact_sentence(name, attribute, facts[attribute])
                for attribute in ATTRIBUTES
            ],
        ]
        passage = _passage(sentences, rng)
        claim = CLAIMS[claim_attr].format(value=claim_value)

        items.append(
            Item(
                id=f"e2{index:03d}",
                input={"passage": passage, "claim": claim},
                expected={
                    "label": "entailed" if entailed else "not_entailed",
                },
                meta={
                    "changed_attr": None if entailed else claim_attr,
                    "claim_attr": claim_attr,
                    "passage_value": passage_value,
                    "claim_value": claim_value,
                    "evidence_sentence": evidence,
                },
            )
        )

    return items
