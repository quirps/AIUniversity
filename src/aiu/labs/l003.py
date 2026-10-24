from __future__ import annotations

from aiu.labs.base import register
from aiu.metrics import (
    accuracy,
    cohen_kappa,
    compound,
    pass_at_k,
    pass_hat_k,
    rogan_gladen,
    tnr,
    tpr,
)
from aiu.models import CallResult, Item, PlannedCall


@register
class L003:
    lab_id = "L-003"

    def plan(self, items: list[Item], manifest: dict, cfg) -> list[PlannedCall]:
        return []

    def score(
        self,
        items: list[Item],
        results: list[CallResult],
        manifest: dict,
    ) -> dict[str, float | None]:
        labels = [item for item in items if item.id.startswith("j")]
        agents = [item for item in items if item.id.startswith("t")]

        judge = [item.input["judge_label"] for item in labels]
        human = [item.input["human_label"] for item in labels]

        raw_agreement = accuracy(judge, human)
        kappa = cohen_kappa(judge, human)
        tpr_value = tpr(judge, human, "fail")
        tnr_value = tnr(judge, human, "fail")
        observed_fail_rate = (
            sum(1 for label in judge if label == "fail") / len(judge) if judge else None
        )
        true_fail_rate = (
            sum(1 for label in human if label == "fail") / len(human) if human else None
        )
        corrected_fail_rate = (
            rogan_gladen(observed_fail_rate, tpr_value, tnr_value)
            if observed_fail_rate is not None
            and tpr_value is not None
            and tnr_value is not None
            else None
        )

        if agents:
            pass_at = sum(
                pass_at_k(
                    int(item.expected["trials"]),
                    int(item.expected["successes"]),
                    3,
                )
                for item in agents
            ) / len(agents)
            pass_hat = sum(
                pass_hat_k(
                    int(item.expected["trials"]),
                    int(item.expected["successes"]),
                    3,
                )
                for item in agents
            ) / len(agents)
        else:
            pass_at = 0.0
            pass_hat = 0.0

        return {
            "raw_agreement": raw_agreement,
            "kappa": kappa,
            "tpr": tpr_value,
            "tnr": tnr_value,
            "observed_fail_rate": observed_fail_rate,
            "corrected_fail_rate": corrected_fail_rate,
            "true_fail_rate": true_fail_rate,
            "agreement_minus_kappa": (
                raw_agreement - kappa if kappa is not None else None
            ),
            "pass_at_3": pass_at,
            "pass_hat_3": pass_hat,
            "compound_0.95_5": compound(0.95, 5),
        }
