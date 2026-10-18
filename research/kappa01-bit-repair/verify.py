#!/usr/bin/env python3
"""Exact target-scale window obstruction and optimistic repair budgets.

No floating point is used for an acceptance decision.  This does not construct
a supplier; PROOF.md lists the necessary scope hypotheses.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SCALE = 10**36


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def floor_root(value: int, degree: int) -> int:
    require(value >= 0 and degree > 0, "invalid integer-root input")
    lo, hi = 0, 1 << ((value.bit_length() + degree - 1) // degree)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**degree <= value:
            lo = mid
        else:
            hi = mid
    if hi**degree <= value:
        lo = hi
    require(lo**degree <= value < (lo + 1)**degree, "root bracket")
    return lo


def power(value: F, numerator: int, denominator: int) -> tuple[F, F]:
    require(value > 0, "positive power input required")
    a = value.numerator**numerator * SCALE**denominator
    b = value.denominator**numerator
    lower = floor_root(a // b, denominator)
    require(lower**denominator * b <= a, "power lower witness")
    require((lower + 1)**denominator * b > a, "power upper witness")
    return F(lower, SCALE), F(lower + 1, SCALE)


def add(left: tuple[F, F], right: tuple[F, F]) -> tuple[F, F]:
    return left[0] + right[0], left[1] + right[1]


def scale(value: tuple[F, F], coefficient: F) -> tuple[F, F]:
    values = coefficient * value[0], coefficient * value[1]
    return min(values), max(values)


def divide(left: tuple[F, F], right: tuple[F, F]) -> tuple[F, F]:
    require(right[0] > 0, "positive denominator interval required")
    values = [a / b for a in left for b in right]
    return min(values), max(values)


def decimal(value: F, places: int = 18) -> str:
    # A display only, truncated toward zero. Exact endpoints are also retained.
    sign = "-" if value < 0 else ""
    scaled = abs(value.numerator) * 10**places // value.denominator
    return f"{sign}{scaled // 10**places}.{scaled % 10**places:0{places}d}"


def record(interval: tuple[F, F]) -> dict[str, str]:
    return {
        "lower": str(interval[0]),
        "upper": str(interval[1]),
        "lower_decimal": decimal(interval[0]),
        "upper_decimal": decimal(interval[1]),
    }


def data_bill(h: int, k: int, stages: int = 3) -> tuple[F, F]:
    require(h > k > 0 and stages >= 3 and stages % 2 == 1, "geometry")
    climb, width = h - k, k + stages * (h - k)
    return scale(power(F(climb, width), 8, 9), F(2 * stages, stages - 1))


def data_pressure(h: int, k: int, stages: int) -> tuple[F, F]:
    climb, width = h - k, k + stages * (h - k)
    return scale(add(power(F(width, climb), 1, 9), (F(-1), F(-1))),
                 F(2 * stages * climb, k))


def copy_allowance(h: int, k: int) -> tuple[F, F]:
    # C/(v*k), granting every copy rank unit a rank-h child, no helpers,
    # and rank-m children for every other paid unit.
    climb, width = h - k, k + 3 * (h - k)
    remaining = add((F(2), F(2)), scale(data_pressure(h, k, 3), F(-1)))
    tariff = scale(power(F(width, h), 1, 9), F(3))
    return divide(remaining, tariff)


def build() -> dict:
    # Finite integer inequalities used by the analytic all-stage proof.
    integer_checks = {
        "s5_t2": (2 * 6**9, 11 * 5**9),
        "s7_t2_relaxed": (17**9, 7 * 14**9),
        "s_ge_9_t2_relaxed": (5**9, 9 * 4**9),
        "density_one_quarter_s3": (10**8, 3**17),
        "density_one_third_s3_pass": (3**9 * 2**8, 7**8),
    }
    for name, (lo, hi) in integer_checks.items():
        require(lo < hi, name)

    x = power(F(3), 9, 8)
    density = ((x[0] - 3) / (x[0] - 2), (x[1] - 3) / (x[1] - 2))
    width_ratio = (1 / density[1], 1 / density[0])
    require(F(3, 10) < density[0] < density[1] < F(1, 3), "density threshold")

    geometries = [(8, 1), (16, 2), (24, 3), (8, 2), (9, 2),
                  (3, 1), (9, 3), (8, 3), (5, 2), (8, 4)]
    candidates = []
    for h, k in geometries:
        bill = data_bill(h, k)
        fee = copy_allowance(h, k)
        candidates.append({"ambient_h": h, "label_rank_k": k,
                           "density_k_over_h": str(F(k, h)),
                           "s3_width_m": k + 3 * (h - k),
                           "s3_data_only_bill": record(bill),
                           "s3_copy_rank_C_over_vk_strict_upper_budget": record(fee),
                           "data_relaxation_passes": bill[1] < 1})

    # Positive controls outside the obstruction, and negative controls inside.
    require(data_bill(3, 1)[1] < 1, "rank density 1/3 must remain open")
    require(copy_allowance(3, 1)[1] < F(1, 4), "positive-definite three-line decoder floor")
    require(data_bill(8, 4)[1] < 1, "rank density 1/2 must remain open")
    require(data_bill(8, 2)[0] > 1, "rank density 1/4 must fail")
    require(data_pressure(3, 1, 5)[0] > 4, "s5 endpoint at h/k=3")
    require(data_pressure(3, 1, 7)[0] > 6, "s7 endpoint at h/k=3")
    require(data_pressure(3, 1, 9)[0] > 8, "s9 endpoint at h/k=3")
    require(data_bill(8, 1) == data_bill(24, 3), "direct-sum invariance")
    require(copy_allowance(8, 1) == copy_allowance(24, 3), "copy-scale invariance")
    require(data_bill(64, 1)[0] > data_bill(8, 1)[1], "literal tensor powers worsen density")

    # Removing the active rank cap makes the otherwise failing h=8,k=1
    # three-stage family pass this *fractional* cost screen. This is not a word.
    all_mass_at_m = F(3 * (8 - 1), 1 + 3 * (8 - 1))
    require(all_mass_at_m < 1, "active-child-cap scope control")
    return {
        "status": "scoped necessary conditions; no supplier or kappa improvement",
        "target_kappa": "1/10", "target_primitive_saving": "1/9",
        "all_odd_stage_obstruction": "h/k >= 1 + 1/(3^(9/8)-3)",
        "stages_at_least_five_obstruction": "h/k >= 3",
        "minimum_density_k_over_h_for_any_odd_stage": record(density),
        "maximum_width_ratio_h_over_k_for_any_odd_stage": record(width_ratio),
        "strict_integer_witnesses": {name: {"left": a, "right": b}
                                      for name, (a, b) in integer_checks.items()},
        "candidate_budgets": candidates,
        "positive_definite_h3_k1_label_decoder_copy_floor_C_over_v": "1/4",
        "scope_control_without_active_child_rank_cap": str(all_mass_at_m),
        "power_scale": str(SCALE),
    }


def check_sources() -> None:
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for entry in manifest["sources"]:
        value = subprocess.run(["git", "show", f"{manifest['base_commit']}:{entry['path']}"],
                               cwd=ROOT, check=True, stdout=subprocess.PIPE).stdout
        require(hashlib.sha256(value).hexdigest() == entry["sha256"], "source digest " + entry["path"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate this package's RESULT.json")
    parser.add_argument("--check-sources", action="store_true", help="check pinned source bytes from Git")
    args = parser.parse_args()
    if args.check_sources:
        check_sources()
    result = build()
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads(path.read_text()), "receipt differs")
    print("PASS_KAPPA01_BIT_WINDOW_DENSITY exact_integer_witnesses=5 scope_controls=12 no_new_kappa")


if __name__ == "__main__":
    main()
