from __future__ import annotations

import random

from aiu.generators.base import register_generator
from aiu.models import Item

ATTRIBUTES = ("founding_year", "river", "mayor", "export", "twin_city")
ALPHABET = "abcdefghijklmnopqrstuvwxyz"

PREFIXES = (
    "Varn", "Kelv", "Dorn", "Mira", "Sol", "Bran", "Tav", "Orin", "Hale", "Cor",
    "Fenn", "Gild", "Harrow", "Ith", "Jor", "Kest", "Lorn", "Marl", "Nor", "Ost",
)
SUFFIXES = (
    "holt", "wick", "mere", "gard", "ton", "by", "fell", "stead", "port", "vale",
    "moor", "reach", "field", "bury", "ford", "gate", "haven", "keep", "march", "shaw",
)

RIVER_STEMS = (
    "Kelv", "Mora", "Tarn", "Rill", "Vesh", "Sarn", "Dun", "Bral", "Cor", "Wen",
    "Yss", "Pell", "Quen", "Roth", "Sil", "Thal", "Umber", "Vale", "Wick", "Xan",
    "Yar", "Zell", "Ash", "Bree", "Cael",
)
MAYOR_FIRST = (
    "Mara", "Tomas", "Iven", "Sela", "Rook", "Bryn", "Ada", "Corin", "Dema", "Ewan",
    "Fira", "Galen", "Hale", "Isol", "Jory", "Kael", "Lira", "Milo", "Nera", "Oren",
    "Pia", "Quin", "Rhea", "Soren", "Talia",
)
MAYOR_LAST = (
    "Voss", "Renn", "Dale", "Moor", "Kest", "Thorne", "Vale", "Brant", "Holt", "Fenn",
    "Grey", "March", "Nash", "Orr", "Pike", "Quill", "Reed", "Stone", "Tarn", "Vane",
    "Wren", "Yarrow", "Ash", "Brook", "Crane",
)
EXPORTS = (
    "amber glass", "salt cod", "blue wool", "tin lamps", "reed paper",
    "copper wire", "dyed linen", "iron nails", "maple syrup", "smoked eels",
    "clay tiles", "silver buttons", "wax candles", "dried herbs", "river pearls",
    "carved bone", "green slate", "oak barrels", "spun flax", "brass bells",
    "sealed honey", "felt hats", "lamp oil", "rope twine", "painted fans",
)
TWIN_STEMS = (
    "Dornby", "Marrow", "Ellwick", "Bram", "Sable", "Harrow", "Lark", "Mirr", "Ost", "Pell",
    "Quarry", "Rook", "Sallow", "Thorn", "Umb", "Vell", "Wester", "Yarn", "Zephyr", "Ashby",
    "Briar", "Colden", "Dunmore", "Elm", "Fen",
)

VALUE_POOLS = {
    "river": tuple(f"the {stem} river" for stem in RIVER_STEMS),
    "mayor": tuple(f"{first} {last}" for first, last in zip(MAYOR_FIRST, MAYOR_LAST)),
    "export": EXPORTS,
    "twin_city": tuple(f"the city of {stem}" for stem in TWIN_STEMS),
}

PHRASES = {
    "founding_year": "{name} was founded in {value}.",
    "river": "{name} is crossed by {value}.",
    "mayor": "{name} has a mayor named {value}.",
    "export": "{name} is known for exporting {value}.",
    "twin_city": "{name} is twinned with {value}.",
}

QUESTIONS = {
    "founding_year": "In what year was {name} founded?",
    "river": "Which river runs through {name}?",
    "mayor": "Who is the mayor of {name}?",
    "export": "What is {name}'s main export?",
    "twin_city": "Which city is twinned with {name}?",
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


def levenshtein(left: str, right: str) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            insert = current[j - 1] + 1
            delete = previous[j] + 1
            substitute = previous[j - 1] + (left_char != right_char)
            current.append(min(insert, delete, substitute))
        previous = current
    return previous[-1]


def _words(text: str) -> int:
    return len(text.split())


def _passage(core: str, rng: random.Random) -> str:
    sentences = [core]
    fillers = list(FILLERS)
    rng.shuffle(fillers)
    index = 0
    while _words(" ".join(sentences)) < 60:
        sentences.append(fillers[index % len(fillers)])
        index += 1
    text = " ".join(sentences)
    count = _words(text)
    assert 60 <= count <= 90, f"passage has {count} words"
    return text


def _entity_names(rng: random.Random) -> list[str]:
    combinations = [
        f"{prefix}{suffix}" for prefix in PREFIXES for suffix in SUFFIXES
    ]
    rng.shuffle(combinations)
    return combinations[:60]


def _similar_names(name: str, rng: random.Random) -> list[str]:
    lowered = name.lower()
    pool: set[str] = set()

    for index in range(len(lowered)):
        for char in ALPHABET:
            if char != lowered[index]:
                pool.add(lowered[:index] + char + lowered[index + 1 :])
        pool.add(lowered[:index] + lowered[index + 1 :])

    for index in range(len(lowered) + 1):
        for char in ALPHABET:
            pool.add(lowered[:index] + char + lowered[index :])

    pool.discard(lowered)
    variants = sorted(pool)
    rng.shuffle(variants)
    names = [variant.capitalize() for variant in variants[:20]]
    assert len(names) == 20
    return names


def _values(attribute: str, key_value: str, rng: random.Random) -> list[str]:
    if attribute == "founding_year":
        base = int(key_value)
        values = [str(base + offset) for offset in range(1, 21)]
        rng.shuffle(values)
        return values

    pool = [value for value in VALUE_POOLS[attribute] if value != key_value]
    rng.shuffle(pool)
    return pool[:20]


def _key_value(attribute: str, rng: random.Random) -> str:
    if attribute == "founding_year":
        return str(rng.randint(1500, 1950))
    return rng.choice(VALUE_POOLS[attribute])


@register_generator("E9")
def generate(rng: random.Random) -> list[Item]:
    names = _entity_names(rng)
    items: list[Item] = []

    for index, name in enumerate(names):
        attribute = ATTRIBUTES[index % len(ATTRIBUTES)]
        key_value = _key_value(attribute, rng)
        question = QUESTIONS[attribute].format(name=name)
        key_core = (
            f"{name} is a small settlement in the northern valley. "
            + PHRASES[attribute].format(name=name, value=key_value)
        )
        key_passage = _passage(key_core, rng)

        similar_names = _similar_names(name, rng)
        distractor_values = _values(attribute, key_value, rng)
        distractors = [
            _passage(
                f"{similar} is a small settlement in the northern valley. "
                + PHRASES[attribute].format(name=similar, value=value),
                rng,
            )
            for similar, value in zip(similar_names, distractor_values)
        ]

        for similar in similar_names:
            distance = levenshtein(name, similar)
            assert 0 < distance <= 2, (name, similar, distance)

        order = list(range(20))
        rng.shuffle(order)

        items.append(
            Item(
                id=f"e{index:03d}",
                input={
                    "question": question,
                    "key_passage": key_passage,
                    "distractors": distractors,
                },
                expected={"answer": key_value},
                meta={
                    "entity": name,
                    "attribute": attribute,
                    "distractor_order": order,
                    "distractor_values": distractor_values,
                },
            )
        )

    return items
