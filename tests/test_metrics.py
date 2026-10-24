from __future__ import annotations

import pytest

from aiu import metrics


def test_cohen_kappa_exact() -> None:
    assert metrics.cohen_kappa(["p", "p", "f", "f"], ["p", "f", "f", "f"]) == 0.5


def test_cohen_kappa_none_when_expected_agreement_is_one() -> None:
    assert metrics.cohen_kappa(["p", "p"], ["p", "p"]) is None


def test_wilson_interval() -> None:
    low, high = metrics.wilson_ci(24, 30)
    assert low == pytest.approx(0.6269, abs=1e-3)
    assert high == pytest.approx(0.9049, abs=1e-3)


def test_wilson_interval_empty_sample() -> None:
    assert metrics.wilson_ci(0, 0) == (0.0, 1.0)


def test_rogan_gladen() -> None:
    assert metrics.rogan_gladen(0.19, 0.8, 0.92) == pytest.approx(
        0.1527777777777778,
        abs=1e-9,
    )


def test_rogan_gladen_none_when_denominator_is_zero() -> None:
    assert metrics.rogan_gladen(0.2, 0.5, 0.5) is None


def test_pass_at_k() -> None:
    assert metrics.pass_at_k(5, 3, 3) == 1.0


def test_pass_hat_k() -> None:
    assert metrics.pass_hat_k(5, 3, 3) == 0.1


def test_compound() -> None:
    assert metrics.compound(0.95, 5) == pytest.approx(0.7737809375, abs=1e-10)


def test_ece_is_zero_for_perfectly_calibrated_bins() -> None:
    assert metrics.ece([0.5, 0.5], [True, False]) == 0.0


def test_confidence_one_lands_in_last_bin() -> None:
    assert metrics.ece([1.0], [True]) == 0.0


def test_normalize_answer() -> None:
    assert metrics.normalize_answer("  The, River! ") == "the river"


def test_flip_rate() -> None:
    assert metrics.flip_rate(["c", "c"], ["c", "w"]) == 0.5


def test_accuracy_counts_none_as_incorrect() -> None:
    assert metrics.accuracy([1, None, 2], [1, 2, 2]) == pytest.approx(2 / 3)


def test_parse_rate() -> None:
    assert metrics.parse_rate([1, None, 2]) == pytest.approx(2 / 3)


def test_tpr_and_tnr() -> None:
    pred = ["fail", "pass", "fail", "pass"]
    gold = ["fail", "fail", "pass", "pass"]
    assert metrics.tpr(pred, gold, "fail") == 0.5
    assert metrics.tnr(pred, gold, "fail") == 0.5


def test_tpr_returns_none_without_positives() -> None:
    assert metrics.tpr(["pass"], ["pass"], "fail") is None


def test_first_slot_rate() -> None:
    assert metrics.first_slot_rate(["A", "B", "A"]) == pytest.approx(2 / 3)


def test_exact_match() -> None:
    assert metrics.exact_match("  The, River! ", "the river") is True
    assert metrics.exact_match(None, "the river") is False


def test_proportion() -> None:
    result = metrics.proportion(24, 30)
    assert result["value"] == pytest.approx(0.8)
    assert result["n"] == 30
    assert result["k"] == 24
    assert result["ci95"][0] == pytest.approx(0.6269, abs=1e-3)
    assert result["ci95"][1] == pytest.approx(0.9049, abs=1e-3)


def test_proportion_empty_sample() -> None:
    result = metrics.proportion(0, 0)
    assert result["value"] is None
    assert result["ci95"] == [0.0, 1.0]
