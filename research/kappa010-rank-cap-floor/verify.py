#!/usr/bin/env python3
"""Exact necessary budget screen for kappa > 1/10 under current supplier laws.

At kappa = 1/10, the retained conversion kappa = a/(1+a) gives a = 1/9.
For child rank r in (0,m), the a=1/9 cost is (r/m)^(8/9). If all child
ranks are at most R and their total rank mass is P, then

    sum n_r (r/m)^(8/9) / w >= (P/(Rw)) (R/m)^(8/9).

Writing S=P/w, the ninth power of this lower bound is exactly
S^9/(R*m^8). Its comparison with 1 is therefore a rational comparison; no
floating-point approximation or transcendental interval is needed.

The screen is deliberately optimistic: it permits every charged unit to be
repacked at the maximum child rank and, in the centre-free rows, deletes the
positive centre/copy charge. A failure rules out every histogram in that
coverage-law/rank-cap model. A pass is only an aggregate budget possibility,
not a realizable supplier.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SELECTED = "certificates/selected-result.json"
BIT_RESULT = "research/bit-revision3-levers-seed03/RESULT.json"
COMPLEX_RESULT = "research/complex-local-word-ceiling/RESULT.json"
PAIRED_PLANE_TASK = "research/paired-plane-identity-fit-seed21ef98/TASK.json"
BOTTLENECK_BRIEF = "docs/research/bottleneck-brief.md"


def read_json(path: str):
    return json.loads((ROOT / path).read_text())


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def frac(x) -> Q:
    return Q(str(x))


def cap(m: int, depth: int) -> int:
    """Largest integer R with m**depth > 2*R**depth."""
    return max(r for r in range(1, m) if m**depth > 2 * r**depth)


def floor_ninth_power_ratio(m: int, R: int, S: Q) -> Q:
    """The exact ninth power of the optimistic moment lower bound."""
    need(0 < R < m and S > 0, "positive mass and a proper child rank are required")
    return S**9 / (R * m**8)


def floor_lower_bound(m: int, R: int, S: Q) -> float:
    """Display-only approximation; proof decisions use the exact ratio above."""
    return float(floor_ninth_power_ratio(m, R, S)) ** (1 / 9)


def first_rank_below_one(m: int, S: Q) -> int:
    """Smallest integer R for which the ideal floor is strictly below one."""
    x = S**9 / (m**8)
    return x.numerator // x.denominator + 1


def minimum_unpaid(m: int, w: Q, centre: Q, R: int) -> int:
    for unpaid in range(1, m):
        S = m - unpaid + centre / w
        if floor_ninth_power_ratio(m, R, S) < 1:
            return unpaid
    raise ValueError("no unpaid count makes this aggregate floor pass")


def first_depth_for_rank(m: int, required_rank: int, maximum_depth: int = 64) -> int:
    for depth in range(1, maximum_depth + 1):
        if cap(m, depth) >= required_rank:
            return depth
    raise ValueError("no halving depth reached the required rank")


def case(m: int, R: int, w: Q, centre: Q, unpaid: int) -> dict[str, object]:
    S = Q(m - unpaid) + centre / w
    ratio = floor_ninth_power_ratio(m, R, S)
    return {
        "m": m,
        "rank_cap": R,
        "unpaid_coordinates": unpaid,
        "centre_mass_per_call": str(centre),
        "families_per_call": str(w),
        "mass_per_family_S": str(S),
        "moment_lower_bound_approx": format(floor_lower_bound(m, R, S), ".12f"),
        "moment_lower_bound_ninth_power": str(ratio),
        "passes_necessary_budget": ratio < 1,
    }


def supplier_screen(label: str, m: int, w: Q, centre: Q, depth: int) -> dict[str, object]:
    R = cap(m, depth)
    centre_free_min_u = minimum_unpaid(m, w, Q(0), R)
    charged_min_u = minimum_unpaid(m, w, centre, R)
    centre_free_rank = first_rank_below_one(m, Q(m - 1))
    charged_rank = first_rank_below_one(m, Q(m - 1) + centre / w)
    return {
        "supplier": label,
        "m": m,
        "families_per_call": str(w),
        "centre_mass_per_call": str(centre),
        "current_depth_envelope": depth,
        "maximum_rank_at_envelope": R,
        "one_unpaid_centre_free": case(m, R, w, Q(0), 1),
        "one_unpaid_centre_charged": case(m, R, w, centre, 1),
        "centre_free_minimum_unpaid_at_cap": centre_free_min_u,
        "charged_minimum_unpaid_at_cap": charged_min_u,
        "one_unpaid_minimum_rank_centre_free": centre_free_rank,
        "one_unpaid_minimum_depth_centre_free": first_depth_for_rank(m, centre_free_rank),
        "one_unpaid_minimum_rank_centre_charged": charged_rank,
        "one_unpaid_minimum_depth_centre_charged": first_depth_for_rank(m, charged_rank),
        "centre_free_boundary": {
            "previous_unpaid_count_fails": case(m, R, w, Q(0), centre_free_min_u - 1),
            "minimum_unpaid_count_passes": case(m, R, w, Q(0), centre_free_min_u),
        },
        "charged_boundary": {
            "previous_unpaid_count_fails": case(m, R, w, centre, charged_min_u - 1),
            "minimum_unpaid_count_passes": case(m, R, w, centre, charged_min_u),
        },
    }


def main() -> None:
    selected = read_json(SELECTED)
    bit = read_json(BIT_RESULT)
    complex_result = read_json(COMPLEX_RESULT)
    paired_plane = read_json(PAIRED_PLANE_TASK)
    brief = (ROOT / BOTTLENECK_BRIEF).read_text()

    need(selected["decimal"] == "0.001672660197076918", "selected-result pin/value changed")
    need("κ = a/(1+a)" in brief, "retained kappa conversion not found in the bottleneck brief")
    target_kappa = Q(1, 10)
    target_a = target_kappa / (1 - target_kappa)
    need(target_a == Q(1, 9), "kappa 1/10 must correspond to primitive saving 1/9")
    bit_replay = bit["replay"]
    need(bit["status"] == "PASS_BIT_REVISION3_LEVERS", "bit positive-control receipt is not passing")
    need(bit_replay["w"] == "296/3" and bit_replay["copy_charge_per_call"] == 63,
         "bit width-family/copy-charge binding changed")
    bit_depths = {d["halving_depth"]: d for d in bit_replay["halving_depths"]}
    need(bit_depths[4]["elementary_cover_admissible"] and bit_depths[4]["idle_cap"] == 53,
         "bit depth-four rank cap is not source-bound")
    need(not bit_depths[5]["elementary_cover_admissible"], "bit depth-five envelope changed")

    cm = complex_result["model"]
    need(complex_result["status"] == "PASS_COMPLEX_LOCAL_WORD_CEILING", "complex positive-control receipt is not passing")
    need(cm["m"] == 73 and cm["live_families_per_call"] == "896/9"
         and cm["centre_per_call"] == 64 and cm["idle_rank_cap"] == 51,
         "complex coverage/rank-cap binding changed")

    bit_screen = supplier_screen("bit", 64, Q(296, 3), Q(63), 4)
    complex_screen = supplier_screen("complex", 73, Q(896, 9), Q(64), 2)
    plane_cost = paired_plane["cost_accounting"]
    need(plane_cost["unpaid_coordinates"] == 2 and plane_cost["centre_charge"] == 112
         and plane_cost["local_mass"] == 5634,
         "paired-plane candidate parameters changed")
    plane_candidate = case(73, 51, Q(896, 9), Q(112), 2)
    plane_minimum_unpaid = minimum_unpaid(73, Q(896, 9), Q(112), 51)
    need(Q(plane_candidate["moment_lower_bound_ninth_power"]) > 1,
         "paired-plane two-unpaid target obstruction")
    need(plane_minimum_unpaid == 4, "paired-plane unpaid boundary at its copy charge")

    # The main target-level negative controls: even deleting the centre charge
    # and assigning all mass to the maximum admitted rank leaves a moment > 1.
    need(Q(bit_screen["one_unpaid_centre_free"]["moment_lower_bound_ninth_power"]) > 1,
         "bit one-unpaid target obstruction")
    need(Q(complex_screen["one_unpaid_centre_free"]["moment_lower_bound_ninth_power"]) > 1,
         "complex one-unpaid target obstruction")
    need(Q(bit_screen["one_unpaid_centre_charged"]["moment_lower_bound_ninth_power"]) > 1,
         "bit charged target obstruction")
    need(Q(complex_screen["one_unpaid_centre_charged"]["moment_lower_bound_ninth_power"]) > 1,
         "complex charged target obstruction")

    # Boundary controls ensure the exact strict thresholds are not rounded.
    need(bit_screen["centre_free_minimum_unpaid_at_cap"] == 2
         and bit_screen["charged_minimum_unpaid_at_cap"] == 2,
         "bit unpaid-coordinate boundary")
    need(complex_screen["centre_free_minimum_unpaid_at_cap"] == 3
         and complex_screen["charged_minimum_unpaid_at_cap"] == 4,
         "complex unpaid-coordinate boundary")
    need(bit_screen["one_unpaid_minimum_rank_centre_free"] == 56
         and bit_screen["one_unpaid_minimum_depth_centre_free"] == 6
         and bit_screen["one_unpaid_minimum_rank_centre_charged"] == 61
         and bit_screen["one_unpaid_minimum_depth_centre_charged"] == 15,
         "bit one-unpaid rank/depth thresholds")
    need(complex_screen["one_unpaid_minimum_rank_centre_free"] == 65
         and complex_screen["one_unpaid_minimum_depth_centre_free"] == 6
         and complex_screen["one_unpaid_minimum_rank_centre_charged"] == 70
         and complex_screen["one_unpaid_minimum_depth_centre_charged"] == 17,
         "complex one-unpaid rank/depth thresholds")

    result = {
        "status": "PASS_KAPPA010_RANK_CAP_FLOOR; scoped aggregate-budget obstruction only",
        "selected_kappa": selected["decimal"],
        "target_kappa": "1/10",
        "target_primitive_saving_a": "1/9",
        "comparison": "For a=1/9 the ninth power of the optimistic moment floor is S^9/(R*m^8), checked exactly.",
        "bit": bit_screen,
        "complex": complex_screen,
        "paired_plane_identity_fit_candidate": {
            "source_task": PAIRED_PLANE_TASK,
            "aggregate_floor": plane_candidate,
            "minimum_unpaid_at_cap_with_112_centre_mass": plane_minimum_unpaid,
            "scope": "Target-level budget check on the predecessor's reported u=2,c=112 candidate parameters; no local identity is replayed here.",
        },
        "limits": [
            "The floor assumes every charged unit may be reblocked at the maximum child rank; this is only a necessary-budget relaxation.",
            "The depth thresholds follow the halving guard alone; no row-coefficient invoice for the deeper depths is established here.",
            "Passing a floor does not provide a local decoder, physical interface, dirty-state restoration, or complete supplier.",
            "The result excludes only the stated one-unpaid coverage law with the stated child-rank envelopes; changed laws and algorithms remain open.",
        ],
    }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"])
    print("  bit one-unpaid, centre-free floor:", bit_screen["one_unpaid_centre_free"]["moment_lower_bound_approx"])
    print("  complex one-unpaid, centre-free floor:", complex_screen["one_unpaid_centre_free"]["moment_lower_bound_approx"])
    print("  required unpaid counts at current caps: bit=2, complex=4 with centre charges")


if __name__ == "__main__":
    main()
