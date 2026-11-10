#!/usr/bin/env python3
"""Independent rational binomial certificate for the frozen relative bill.

No source, profile extractor, or other tariff evaluator is imported. Classical
binomial-series bounds supply arithmetic; PROOF.md supplies the real-variable
sign argument whose finite coefficient and endpoint identities are checked here.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
PINS = {
    "SOURCE-PINS.json": "5eb5b9458165046dad7170d5801a12f84f92891ac16ef2fd8bcbacf357046237",
    "verify_profiles.py": "e7d2bf27b3ce2cca939d3fc8239876aa82dcdfcd816bd78df4c9171f37e09319",
    "oracle_profiles.py": "4840369f3311369c09762fccaadcbc2a9fecffc53bcf3dd925abf2b059014cb0",
    "PROFILES.json": "985500c0ebda3ba82570cf844d3acaed78d4aec7923956ea889b575e43c4e6d1",
    "ORACLE-PROFILES.json": "dd9abee4eed9bdf52cd731c2fb61d2ec17022ab136ab255e4325181652ba06e4",
    "PROFILE-PROOF.md": "b95cbfc30cfcf85016406801005a8284b0eca61cb8c1cc5661376e242b0a153e",
    "sources/CONTROLLER.json": "6fd67eaabe659956d6694471d3fd7d2824c0a4a79cf3b8f22922f7189b11b91f",
    "sources/LIFTS.json": "38960b70a074888a2aeaf3b543629a7ae747c0c5d4f5c853371a6e7c483766c5",
    "sources/NEW-WORD.json.gz": "9e31463a785c18a70f6ae6ef3d04a6560dbb965517109390fe820f9fac3371b3",
    "sources/NOTICE": "91f24d68004688bc0a56303a48edcb5ddabd66bfc2326950603bf98dec245bbe",
    "sources/OLD-WORD.json.gz": "e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491",
    "sources/constructor-source.py": "fe7dc1d9aa55da393465388ee90faaa687b1e5be48dfa816a421069fa3d2de08",
    "sources/controller-source.py": "8067ade84815b54d539cbaef9885db9fa4d7a23fdde2e683451d317038a8477c",
    "sources/upstream-PROOF.md": "769e0f87e6b85c557b48135d2d898bb485cf77ce9925540e0a3740e6283f41af",
}
TERMS = 192
WORK_GRID = 10**40
OUTPUT_GRID = 10**30
# This source-bound bracket is shared only as data, not an arithmetic method.
BRACKET = (F(11712509413, 13421772800), F(5856254707, 6710886400))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "Duplicate JSON member")
        result[key] = value
    return result


def read_json(path):
    def bad_constant(value):
        raise ValueError("Nonfinite JSON constant: " + value)
    return json.loads(path.read_text(), object_pairs_hook=pairs,
                      parse_constant=bad_constant)


def authenticate():
    for name, expected in PINS.items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        require(actual == expected, "Checkpoint sha256 mismatch: " + name)


def profile(value):
    require(type(value) is dict, "Profile must be an object")
    answer = {}
    for rank, count in value.items():
        require(type(rank) is str and rank.isascii() and rank.isdigit()
                and str(int(rank)) == rank and int(rank) > 0,
                "Canonical positive profile rank required")
        require(type(count) is int and count > 0, "Positive integer profile count required")
        answer[int(rank)] = count
    return answer


def difference(new, old):
    return {r: new.get(r, 0) - old.get(r, 0)
            for r in sorted(new.keys() | old.keys()) if new.get(r, 0) != old.get(r, 0)}


def signed(paid_delta, target_delta):
    return difference(target_delta, paid_delta)


def string_keys(value):
    return {str(k): v for k, v in sorted(value.items())}


def validate_coefficient_claim(actual, expected):
    require(canonical(string_keys(actual)) == canonical(string_keys(expected)),
            "Derived coefficient boundary mismatch")


def validate_bracket(left, right):
    require(0 < left < right < 1 and right-left <= F(1, 10**10),
            "Strict interior bracket width")


def coefficients():
    primary = read_json(ROOT / "PROFILES.json")
    oracle = read_json(ROOT / "ORACLE-PROFILES.json")
    extracted = {}
    for level in ("local", "complete"):
        by_version = {}
        for version in ("old", "new"):
            p = primary[version + "_local"] if level == "local" else primary["complete"][version]
            o = oracle[version + "_" + level]
            by_version[version] = {}
            for kind in ("paid", "targets"):
                a, b = profile(p[kind]), profile(o[kind])
                require(a == b, "Independent receipt profile disagreement")
                by_version[version][kind] = a
        pd = difference(by_version["new"]["paid"], by_version["old"]["paid"])
        td = difference(by_version["new"]["targets"], by_version["old"]["targets"])
        extracted[level] = {"paid": pd, "targets": td, "gain": signed(pd, td)}
    for kind in ("paid", "targets", "gain"):
        require(extracted["complete"][kind] == {r: 19*c for r, c in extracted["local"][kind].items()},
                "Complete/local factor19 mismatch")
    c = extracted["local"]["gain"]
    validate_coefficient_claim(c, {1: -6, 3: 3, 4: -3, 5: 3, 8: 6, 9: -6})
    validate_coefficient_claim(extracted["complete"]["gain"], {r: 19*n for r, n in c.items()})
    return extracted, by_version, c


def prime_log_coefficients(c, weighted):
    answer = {}
    for rank, coefficient in c.items():
        n = rank
        prime = 2
        while prime <= n:
            while n % prime == 0:
                answer[prime] = answer.get(prime, 0) + coefficient * (rank if weighted else 1)
                n //= prime
            prime += 1
    return {p: n for p, n in sorted(answer.items()) if n}


def analytic_identities(c):
    require(all(n % 3 == 0 for n in c.values()), "Normalization divisibility")
    a = {r: n // 3 for r, n in c.items()}
    require(sum(a.values()) == -1 and sum(r*n for r, n in a.items()) == 0,
            "Taylor constant/first-moment identities")
    require(sum((r-1)*n for r, n in a.items()) == 1, "Taylor linear identity")
    breaks = (1, 3, 4, 5, 8, 9)
    expected = ((2, -1), (-1, 0), (3, -1), (-2, 0), (-18, 2))
    rows = []
    for left, right, want in zip(breaks, breaks[1:], expected):
        active = {r: n for r, n in a.items() if r > left}
        intercept, slope = sum(r*n for r, n in active.items()), -sum(active.values())
        require((intercept, slope) == want, "Kernel Peano coefficient identity")
        rows.append({"interval": [left, right], "intercept": intercept, "slope": slope})
    require(rows[0]["intercept"] + 2*rows[0]["slope"] == 0, "Kernel switch at2")
    for row in rows[1:]:
        left, right = row["interval"]
        require(row["intercept"] + row["slope"]*F(left+right, 2) < 0,
                "Kernel strict negative interval")
    p0, p1 = prime_log_coefficients(a, False), prime_log_coefficients(a, True)
    require(p0 == {2: 4, 3: -3, 5: 1}, "I0 logarithm identity")
    require(p1 == {2: 40, 3: -33, 5: 5}, "L1 logarithm identity")
    lower = F(2, 3) + F(26, 67)
    require(lower == F(212, 201) and lower > 1, "Exact strict log lower bound")
    numerator, denominator = 2**40 * 5**5, 3**33
    require(denominator - numerator == 2123086729755523 and numerator < denominator,
            "Strict L1 endpoint integer inequality")
    return {"normalized_coefficients": string_keys(a), "kernel": rows,
            "kernel_sign_change": 2, "coefficient_sum": -1, "first_rank_moment": 0,
            "I0_equals": "1-log(80/27)", "log80over27_strict_lower_bound": str(lower),
            "I0_strict_upper_bound": str(1-lower),
            "L1_equals": "log(2^40*5^5/3^33)",
            "L1_ratio_numerator": numerator, "L1_ratio_denominator": denominator,
            "L1_denominator_minus_numerator": denominator-numerator,
            "whole_domain_argument": "Proper-integral Taylor factorization; one kernel sign change gives I<0 and I'<0, so L=1+sI strictly decreases from1 to a negative L1. See PROOF.md."}


def floor_grid(value, grid):
    return F((value.numerator * grid) // value.denominator, grid)


def ceil_grid(value, grid):
    return -floor_grid(-value, grid)


def power_bounds(rank, s):
    require(type(rank) is int and rank >= 1 and F(0) < s < F(1), "Binomial evaluator domain")
    if rank == 1:
        return F(1), F(1)
    x = F(rank-1, rank+1)
    require(0 < x <= F(4, 5), "Frozen rank domain")
    # Positive magnitudes of both binomial series. All recurrence factors are
    # positive and <x; interval rounding preserves each exact term enclosure.
    lo = floor_grid(s*x, WORK_GRID)
    hi = ceil_grid(s*x, WORK_GRID)
    numerator_lo = numerator_hi = F(1)
    sum_lo = sum_hi = F(0)
    for k in range(1, TERMS+1):
        sum_lo += lo
        sum_hi += hi
        if k % 2:
            numerator_lo += lo
            numerator_hi += hi
        else:
            numerator_lo -= hi
            numerator_hi -= lo
        factor = x * (k-s) / (k+1)
        require(0 < factor < x, "Binomial positive decreasing-tail factor")
        lo = floor_grid(lo*factor, WORK_GRID)
        hi = ceil_grid(hi*factor, WORK_GRID)
    # lo/hi now enclose term N+1. The alternating tail has its first sign;
    # the denominator's all-negative remainder is bounded geometrically.
    if TERMS % 2 == 0:
        numerator_hi += hi
    else:
        numerator_lo -= hi
    denominator_lo = 1-sum_hi-hi/(1-x)
    denominator_hi = 1-sum_lo
    require(0 < numerator_lo <= numerator_hi and 0 < denominator_lo <= denominator_hi,
            "Positive quotient denominator enclosure")
    return floor_grid(numerator_lo/denominator_hi, OUTPUT_GRID), ceil_grid(numerator_hi/denominator_lo, OUTPUT_GRID)


def gain_bounds(c, s):
    lo = hi = F(0)
    powers = {}
    for rank, coefficient in sorted(c.items()):
        a, b = power_bounds(rank, s)
        powers[str(rank)] = [str(a), str(b)]
        lo += coefficient*(a if coefficient > 0 else b)
        hi += coefficient*(b if coefficient > 0 else a)
    require(lo <= hi, "Signed interval ordering")
    return {"s": str(s), "g_bounds": [str(floor_grid(lo, OUTPUT_GRID)), str(ceil_grid(hi, OUTPUT_GRID))],
            "complete_gain_bounds": [str(floor_grid(19*lo, OUTPUT_GRID)), str(ceil_grid(19*hi, OUTPUT_GRID))],
            "power_bounds": powers}, lo, hi


def boundary_controls(complete, c):
    expected = {r: 19*n for r, n in c.items()}
    controls = []
    candidates = []
    wrong_sign = dict(expected)
    wrong_sign[3] *= -1
    candidates.append(("wrong_signed_rank3_coefficient", wrong_sign))
    for name, paid_change, target_change in (
            ("old_rank9_target_instead_of_new_rank8", {}, {8: -19, 9: 19}),
            ("unpaid_carrier_first_leg", {1: -19}, {})):
        paid = dict(complete["new"]["paid"])
        targets = dict(complete["new"]["targets"])
        for r, n in paid_change.items():
            paid[r] += n
        for r, n in target_change.items():
            targets[r] += n
        wrong = signed(difference(paid, complete["old"]["paid"]),
                       difference(targets, complete["old"]["targets"]))
        candidates.append((name, wrong))
    for name, wrong in candidates:
        require(wrong != expected, "Counterfactual coefficient guard failed")
        rejection = None
        try:
            validate_coefficient_claim(wrong, expected)
        except ValueError as exc:
            rejection = str(exc)
        require(rejection == "Derived coefficient boundary mismatch", "Coefficient boundary control did not reject")
        rank = next(r for r in sorted(wrong.keys() | expected.keys()) if wrong.get(r, 0) != expected.get(r, 0))
        controls.append({"control": name, "rejected_at": "derived complete coefficient boundary",
                         "observed_error": rejection,
                         "witness": {"rank": rank, "actual_coefficient": wrong.get(rank, 0),
                                     "expected_coefficient": expected.get(rank, 0)}})
    require(sum(c.values()) != 0 and sum(r*n for r, n in c.items()) == 0,
            "Interior versus endpoint distinction")
    rejection = None
    try:
        validate_bracket(F(99999999999, 10**11), F(1))
    except ValueError as exc:
        rejection = str(exc)
    require(rejection == "Strict interior bracket width", "Endpoint1 bracket control did not reject")
    controls.append({"control": "endpoint_one_is_not_the_interior_root", "g0": sum(c.values()), "g1": 0,
                     "observed_error": rejection,
                     "rejected_at": "strict open-domain root bracket"})
    return controls


def compute():
    authenticate()
    extracted, complete, c = coefficients()
    identities = analytic_identities(c)
    require(BRACKET is not None, "Frozen rational bracket not configured")
    left, right = BRACKET
    validate_bracket(left, right)
    lrow, llo, lhi = gain_bounds(c, left)
    rrow, rlo, rhi = gain_bounds(c, right)
    require(lhi < 0 < rlo, "Independent binomial strict bracket signs")
    sqrt_row, sqrt_lo, sqrt_hi = gain_bounds(c, F(1, 2))
    selected_row, selected_lo, selected_hi = gain_bounds(c, F(1246061, 1250000))
    require(sqrt_hi < 0 and selected_lo > 0, "Tariff comparison sanity signs")
    return {"schema_version": 1, "status": "PASS_CONDITIONAL_RELATIVE_TARIFF",
            "checkpoint_sha256": PINS,
            "local_paid_delta": string_keys(extracted["local"]["paid"]),
            "local_target_delta": string_keys(extracted["local"]["targets"]),
            "local_gain_coefficients": string_keys(c),
            "complete_gain_coefficients": string_keys(extracted["complete"]["gain"]),
            "complete_factor": 19, "analytic_identities": identities,
            "arithmetic": {"method": "positive quotient of generalized binomial enclosures",
                           "terms": TERMS, "work_grid": WORK_GRID, "output_grid": OUTPUT_GRID,
                           "maximum_x": "4/5", "numerator_tail": "alternating next-term bound",
                           "denominator_tail": "next-term upper bound divided by1-x"},
            "threshold_bracket": [str(left), str(right)], "bracket_width": str(right-left),
            "bracket_evaluations": [lrow, rrow],
            "sqrt_tariff": sqrt_row, "source_claimed_power_relative_comparison": selected_row,
            "controls": boundary_controls(complete, c),
            "limits": ["The whole-domain sign theorem uses the proper-integral argument in PROOF.md; finite identities and strict endpoint arithmetic are checked here.",
                       "All conclusions compare two frozen formal invoices under retained native/interface/tariff premises.",
                       "The selected power is a relative-comparison point, not an admitted kappa or positive complete-margin claim.",
                       "No scalar/native endpoint, physical caller, erasure, ordinary funding, compiler, outer admission or frontier change is certified.",
                       "Counterfactual controls corrupt coefficient/invoice claims; they are not valid cheaper programs."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        path = ROOT / "RELATIVE-ORACLE.json"
        require(path.is_file(), "Retained receipt RELATIVE-ORACLE.json is required")
        retained = read_json(path)
        require(canonical(retained) == canonical(result), "Retained receipt mismatch")
        print("PASS independent binomial relative-tariff receipt")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        sys.exit(1)
