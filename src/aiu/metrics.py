from __future__ import annotations

import math
import string
from collections import Counter
from collections.abc import Sequence


def accuracy(pred: Sequence[object | None], gold: Sequence[object]) -> float:
    if not gold:
        return 0.0
    return sum(1 for p, g in zip(pred, gold) if p == g) / len(gold)


def parse_rate(pred: Sequence[object | None]) -> float:
    if not pred:
        return 0.0
    return sum(1 for value in pred if value is not None) / len(pred)


def cohen_kappa(a: Sequence[str], b: Sequence[str]) -> float | None:
    if len(a) != len(b):
        raise ValueError("kappa inputs must have the same length")
    n = len(a)
    if n == 0:
        return None

    observed = sum(1 for left, right in zip(a, b) if left == right) / n
    left_counts = Counter(a)
    right_counts = Counter(b)
    expected = sum(
        (left_counts[label] / n) * (right_counts[label] / n)
        for label in set(a) | set(b)
    )
    if math.isclose(expected, 1.0, abs_tol=1e-12):
        return None
    return (observed - expected) / (1 - expected)


def tpr(pred: Sequence[str], gold: Sequence[str], positive: str) -> float | None:
    true_positives = sum(
        1 for p, g in zip(pred, gold) if g == positive and p == positive
    )
    false_negatives = sum(
        1 for p, g in zip(pred, gold) if g == positive and p != positive
    )
    denominator = true_positives + false_negatives
    return true_positives / denominator if denominator else None


def tnr(pred: Sequence[str], gold: Sequence[str], positive: str) -> float | None:
    true_negatives = sum(
        1 for p, g in zip(pred, gold) if g != positive and p != positive
    )
    false_positives = sum(
        1 for p, g in zip(pred, gold) if g != positive and p == positive
    )
    denominator = true_negatives + false_positives
    return true_negatives / denominator if denominator else None


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)

    p = k / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = (
        z
        * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
        / denominator
    )
    low = max(0.0, center - half)
    high = min(1.0, center + half)
    return (low, high)


def flip_rate(ab: Sequence[str], ba: Sequence[str]) -> float:
    if len(ab) != len(ba):
        raise ValueError("flip_rate inputs must have the same length")
    if not ab:
        return 0.0
    return sum(1 for left, right in zip(ab, ba) if left != right) / len(ab)


def first_slot_rate(choices: Sequence[str]) -> float:
    if not choices:
        return 0.0
    return sum(1 for choice in choices if choice == "A") / len(choices)


def rogan_gladen(p_obs: float, tpr_: float, tnr_: float) -> float | None:
    denominator = tpr_ + tnr_ - 1
    if denominator <= 0:
        return None
    return min(1.0, max(0.0, (p_obs + tnr_ - 1) / denominator))


def pass_at_k(n: int, c: int, k: int) -> float:
    if n <= 0 or k <= 0 or k > n:
        return 0.0
    if n - c < k:
        return 1.0
    return 1 - math.comb(n - c, k) / math.comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    if n <= 0 or k <= 0 or k > n or c < k:
        return 0.0
    return math.comb(c, k) / math.comb(n, k)


def ece(conf: Sequence[float], correct: Sequence[bool], bins: int = 10) -> float:
    if len(conf) != len(correct):
        raise ValueError("ece inputs must have the same length")
    if not conf:
        return 0.0

    groups: list[list[tuple[float, bool]]] = [[] for _ in range(bins)]
    for confidence, is_correct in zip(conf, correct):
        index = min(int(confidence * bins), bins - 1)
        index = max(0, index)
        groups[index].append((confidence, is_correct))

    total = len(conf)
    result = 0.0
    for group in groups:
        if not group:
            continue
        mean_conf = sum(value for value, _ in group) / len(group)
        mean_acc = sum(1 for _, is_correct in group if is_correct) / len(group)
        result += (len(group) / total) * abs(mean_acc - mean_conf)
    return result


def compound(p: float, steps: int) -> float:
    return p**steps


def normalize_answer(s: str) -> str:
    lowered = s.lower()
    without_punctuation = lowered.translate(str.maketrans("", "", string.punctuation))
    return " ".join(without_punctuation.split()).strip()


def exact_match(pred: str | None, gold: str) -> bool:
    if pred is None:
        return False
    return normalize_answer(pred) == normalize_answer(gold)


def proportion(k: int, n: int) -> dict:
    value = k / n if n else None
    low, high = wilson_ci(k, n)
    return {"value": value, "n": n, "k": k, "ci95": [low, high]}
