#!/usr/bin/env python3
"""Bounded exact economic checks. No native/compiler execution or root search.

Apache-2.0. Substantial OpenAI Codex assistance. See source/credit in proof.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    receipt = []
    for item in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        path = HERE / item["snapshot"] if item["snapshot"] else ROOT / item["provenance"]
        actual = sha256(path.read_bytes()).hexdigest()
        need(actual == item["sha256"], "Changed source: " + str(path))
        receipt.append({"commit": item["commit"], "path": item["upstream_path"], "sha256": actual})
    return receipt


def comparison(case):
    """Exact tariff gate only, never a physical-admission verdict."""
    need(case["price_unit"] == "complete_native_call_price", "Rank powers alone are not complete native prices")
    need(case["same_complete_target"] is True, "Independent complete target equality required")
    need(case["same_volume_and_width"] is True, "Owner volume cannot be substituted for address width")
    need(case["same_orientation_and_precision"] is True, "Orientation/precision mismatch")
    need(case["uniform_label_and_pair_prices"] is True, "Label/pair-dependent tariffs require their actual sum")
    need(case["outside_overhead_complete"] is True, "Unknown outside-call bill")
    f, q, b, delta = (Q(case[k]) for k in ("F", "Q", "B", "Delta"))
    need(f > 0 and q >= 0 and b >= 0, "Nonnegative complete prices required")
    old_upper = 3 * f + 6 * q
    new = f + 4 * b + delta
    threshold = (2 * f + 6 * q - delta) / 4
    need((new < old_upper) == (b < threshold), "Threshold algebra")
    return {"new_adjusted_tariff": str(new), "direct_recipe_upper_tariff": str(old_upper),
            "B_strict_threshold": str(threshold), "difference": str(new - old_upper),
            "status": "ECONOMIC_INEQUALITY_ONLY" if new < old_upper else "NO_GAIN_AGAINST_DIRECT_RECIPE"}


def reserve_screen(u_upper, l_lower, epsilon):
    u, l, e = Q(u_upper), Q(l_lower), Q(epsilon)
    need(u > 0 and l >= 0 and 0 < e < 1, "Invalid simultaneous U,L,reserve")
    bound = (1 - e) * u - l
    return {"reserve_adjusted_upper": str(bound),
            "status": "EXCLUDED_FOR_DECLARED_RESERVE" if bound <= 0 else "INCONCLUSIVE_OPTIMISTIC_SCREEN"}


def main():
    sources = authenticate()
    # Entire C domain [0,17/5000], tau>=4983/5000. Exact integers only.
    need(399 ** 5000 < 2 ** 4983 * 200 ** 5000, "Uniform power-tariff lower bound")
    x = Q(399, 200)
    floor_price_cap = Q(1, 2) + Q(3, 2) / x
    deficit = 4 * x - 2 - 6 / x
    need(floor_price_cap == Q(333, 266), "Break-even rational cap")
    need(deficit == Q(19767, 6650) > 0, "Nominal tariff deficit")
    algebra_cases = 0
    for n in range(1, 41):
        z = Q(n, 10)
        value = 1 + 4 * z - (3 + 6 / z)
        need(value == 2 * (2 * z - 3) * (z + 1) / z, "Factored price difference")
        need((value > 0) == (z > Q(3, 2)), "Scoped transition sign")
        algebra_cases += 1
    need(1 + 4 * Q(7, 5) < 3 + 6 / Q(7, 5), "Below-transition reversal control")
    need(1 + 4 * Q(3, 2) == 3 + 6 / Q(3, 2), "Break-even control")
    # tau=1 exact floor tests, including H_0=0 at f=1.
    floor_cases = 0
    for f in range(1, 65):
        half = f // 2
        direct = 3 * f + 6 * half
        new = 9 * f
        need(new > direct, "Known separate-owner tariff must lose")
        if f % 2 == 0:
            need(new - direct == 3 * f, "Even-width sharpness")
        else:
            need(new - direct == 3 * f + 3, "Odd-width floor strengthening")
        floor_cases += 1
    template = {"price_unit": "complete_native_call_price", "same_complete_target": True,
                "same_volume_and_width": True, "same_orientation_and_precision": True,
                "uniform_label_and_pair_prices": True,
                "outside_overhead_complete": True, "F": "1", "Q": "1/2", "B": "6/5", "Delta": "0"}
    cases = {}
    for name, patch in [("synthetic_positive", {}), ("break_even", {"B": "5/4"}),
                        ("formal_gain_but_direct_loss", {"B": "3/2"}),
                        ("positive_outside_cost_closes_gain", {"Delta": "1/5"}),
                        ("negative_outside_cost_can_change_decision", {"B": "3/2", "Delta": "-2"})]:
        cases[name] = comparison(dict(template, **patch))
    need(cases["synthetic_positive"]["status"] == "ECONOMIC_INEQUALITY_ONLY", "Positive synthetic control")
    need(cases["break_even"]["difference"] == "0", "Strict inequality rejects equality")
    need(cases["formal_gain_but_direct_loss"]["status"] == "NO_GAIN_AGAINST_DIRECT_RECIPE", "Wrong comparator control")
    need(cases["positive_outside_cost_closes_gain"]["difference"] == "0", "Outside cost charged once")
    need(cases["negative_outside_cost_can_change_decision"]["status"] == "ECONOMIC_INEQUALITY_ONLY", "No universal overhead exclusion")
    rejected = []
    for name, patch in [("H_scalar2_as_native_price", {"price_unit": "H_scalar_rank"}),
                        ("unproved_output_inventory", {"same_complete_target": False}),
                        ("volume_to_width_substitution", {"same_volume_and_width": False}),
                        ("orientation_mismatch", {"same_orientation_and_precision": False}),
                        ("unequal_label_prices", {"uniform_label_and_pair_prices": False}),
                        ("missing_finite_work", {"outside_overhead_complete": False})]:
        try:
            comparison(dict(template, **patch))
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("Failed semantic rejection: " + name)
    raw_positive_reserve_closed = reserve_screen(100, "199/2", "1/100")
    need(raw_positive_reserve_closed["status"] == "EXCLUDED_FOR_DECLARED_RESERVE", "Raw positive moment is not reserve")
    need(reserve_screen(100, 99, "1/100")["status"] == "EXCLUDED_FOR_DECLARED_RESERVE", "Strict reserve equality control")
    need(reserve_screen(100, 98, "1/100")["status"] == "INCONCLUSIVE_OPTIMISTIC_SCREEN", "U,L passing is not admission")
    out = {"status": "PASS_SCOPED_DIRECT_COMPARATOR_AND_RESERVE_CONTROLS",
           "C_domain": ["0", "17/5000"], "hypothetical_power_tariff_only": True,
           "uniform_x_strict_lower": "399/200", "B_over_F_strict_necessary_cap": str(floor_price_cap),
           "nominal_new_minus_direct_over_F_strict_lower": str(deficit),
           "algebra_cases": algebra_cases, "floor_cases_tau_one": floor_cases,
           "synthetic_tariff_cases": cases, "semantic_rejections": rejected,
           "raw_positive_but_reserve_closed_control": raw_positive_reserve_closed,
           "sources": sources, "physical_supplier_verified": False,
           "independent_output_inventory_verified": False, "compiler_run": False,
           "native_or_author_formal_replay_run": False, "new_kappa": None}
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
