#!/usr/bin/env python3
"""Whole-domain relative power-tariff certificate for the frozen PR6375 bills.

Profiles and their two producer engines are authenticated data, never imports.
The numerical proof uses rational arctanh and positive exponential series.
The unique relative crossover is not the author's complete-bill kappa root.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
FROZEN = {
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
    "sources/upstream-PROOF.md": "769e0f87e6b85c557b48135d2d898bb485cf77ce9925540e0a3740e6283f41af"
}
EXPECTED_G = {1: -6, 3: 3, 4: -3, 5: 3, 8: 6, 9: -6}
LOG_TERMS, EXP_DEGREE = 48, 24
WORK_GRID, POWER_GRID = 10 ** 40, 10 ** 30
BRACKET_LOW = Fraction(11712509413, 13421772800)
BRACKET_HIGH = Fraction(5856254707, 6710886400)
CLAIMED_KAPPA = Fraction(3939, 1250000)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON receipt key")
            result[key] = value
        return result
    def bad_constant(value):
        raise ValueError("nonfinite JSON receipt constant: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad_constant)


def authenticated_receipts():
    raw = {}
    for filename, expected in FROZEN.items():
        data = (HERE / filename).read_bytes()
        require(sha256(data).hexdigest() == expected, "frozen source SHA256: " + filename)
        raw[filename] = data
    return strict_json(raw["PROFILES.json"]), strict_json(raw["ORACLE-PROFILES.json"])


def positive_profile(value):
    require(type(value) is dict, "integer rank-profile receipt")
    result = Counter()
    for key, count in value.items():
        require(type(key) is str and key.isdecimal() and str(int(key)) == key and
                1 <= int(key) <= 1000000, "canonical positive rank receipt key")
        require(type(count) is int and 0 < count <= 1000000000, "positive integer profile receipt count")
        result[int(key)] = count
    return result


def cleaned(counter):
    return {rank: count for rank, count in sorted(counter.items()) if count}


def gain(old, new):
    result = Counter(new[1])
    result.subtract(new[0])
    result.subtract(old[1])
    result.update(old[0])
    return cleaned(result)


def parse_pair(receipt, engine, level):
    require(type(receipt) is dict and type(receipt.get("schema_version")) is int and receipt["schema_version"] == 1,
            "typed profile receipt schema")
    if level == "complete":
        records = (receipt["complete"]["old"], receipt["complete"]["new"]) if engine == "primary" else (
            receipt["old_complete"], receipt["new_complete"])
    else:
        records = receipt["old_local"], receipt["new_local"]
    return tuple((positive_profile(record["paid"]), positive_profile(record["targets"])) for record in records)


def require_equal_profiles(first, second):
    for side, (a, b) in enumerate(zip(first, second)):
        for part, (x, y) in enumerate(zip(a, b)):
            for rank in sorted(x.keys() | y.keys()):
                require(x[rank] == y[rank], "complete profile binding mismatch: side%d part%d rank%d" % (side, part, rank))


def bound_coefficients(primary, oracle):
    a = parse_pair(primary, "primary", "complete")
    b = parse_pair(oracle, "oracle", "complete")
    require_equal_profiles(a, b)
    whole_a, whole_b = gain(*a), gain(*b)
    require(whole_a == whole_b and all(type(c) is int and c % 19 == 0 for c in whole_a.values()),
            "exact complete relative coefficients and factor19")
    local = {rank: coefficient // 19 for rank, coefficient in whole_a.items()}
    require(local == EXPECTED_G, "source-bound local relative coefficient vector")
    require(gain(*parse_pair(primary, "primary", "local")) == local and
            gain(*parse_pair(oracle, "oracle", "local")) == local, "independent local/complete coefficient binding")
    return local, whole_a, a


def prime_exponents(coefficients, endpoint):
    result = Counter()
    for rank, coefficient in coefficients.items():
        value, prime = rank, 2
        while prime * prime <= value:
            while value % prime == 0:
                result[prime] += coefficient * rank ** endpoint
                value //= prime
            prime += 1
        if value > 1:
            result[value] += coefficient * rank ** endpoint
    return cleaned(result)


def prime_ratio(exponents):
    numerator, denominator = 1, 1
    for prime, exponent in exponents.items():
        if exponent >= 0:
            numerator *= prime ** exponent
        else:
            denominator *= prime ** (-exponent)
    return Fraction(numerator, denominator)


def global_certificate(coefficients):
    require(all(c % 3 == 0 for c in coefficients.values()), "integer factor3")
    f = {rank: c // 3 for rank, c in coefficients.items()}
    require(sum(f.values()) == -1 and sum(rank*c for rank, c in f.items()) == 0,
            "exact count and linear-rank balance")
    boundaries = [1, 3, 4, 5, 8, 9]
    pieces = []
    expected = [(-1, 2), (0, -1), (-1, 3), (0, -2), (2, -18)]
    for left, right, pair in zip(boundaries, boundaries[1:], expected):
        midpoint = Fraction(left + right, 2)
        active = {rank: c for rank, c in f.items() if rank > midpoint}
        slope, intercept = -sum(active.values()), sum(rank*c for rank, c in active.items())
        require((slope, intercept) == pair, "exact Peano kernel segment")
        pieces.append({"left": left, "right": right, "slope": slope, "intercept": intercept})
    def kernel(x):
        return sum(c * max(Fraction(rank) - x, 0) for rank, c in f.items())
    cuts = [1, 2, 3, 4, 5, 8, 9]
    for left, right in zip(cuts, cuts[1:]):
        a, b, middle = kernel(Fraction(left)), kernel(Fraction(right)), kernel(Fraction(left + right, 2))
        require((a >= 0 and b >= 0 and middle > 0) if right <= 2 else
                (a <= 0 and b <= 0 and middle < 0), "single kernel sign switch at2")
    require(kernel(Fraction(1)) == 1 and kernel(Fraction(2)) == kernel(Fraction(9)) == 0,
            "kernel endpoint values")
    at_zero, at_one = prime_ratio(prime_exponents(f, 0)), prime_ratio(prime_exponents(f, 1))
    require(at_zero == Fraction(80, 27), "exact f'(0) logarithm")
    logarithm_lower = Fraction(2, 3) + Fraction(26, 67)
    require(logarithm_lower == Fraction(212, 201) and logarithm_lower > 1, "strict rational log lower bound")
    require(at_one == Fraction(2 ** 40 * 5 ** 5, 3 ** 33) and at_one < 1, "strict negative L(1)=f'(1) logarithm")
    # The accompanying proof applies Taylor's proper integral identity:
    # f(s)=(s-1)L(s), L=1+sI, I=int_1^9 K(x)x^(s-2)dx.
    # The checked single sign switch implies
    # I(s)-2^s I(0)<0 for s>0 and I'(s)-log(2)I(s)<0.
    # I(0)<0 therefore makes I,I' negative and L strictly decreasing.
    return {"f_coefficients": {str(r): c for r, c in sorted(f.items())},
            "coefficient_sum": -1, "rank_mass": 0, "first_shifted_moment": 1,
            "Peano_kernel_pieces": pieces, "kernel_sign_switch": 2,
            "f_derivative0_log_ratio": str(at_zero), "log_ratio0_strict_lower": str(logarithm_lower),
            "I0_strict_upper": str(1 - logarithm_lower), "L0": "1",
            "L1_negative_log_ratio": {"numerator": str(at_one.numerator), "denominator": str(at_one.denominator)},
            "proper_integral_factorization": "f(s)=(s-1)*(1+s*integral_1^9 K(x)*x^(s-2) dx)",
            "interior_roots": 1, "interior_root_multiplicity": 1,
            "gain_signs": ["negative below the unique interior root", "positive above it up to1", "zero at1"],
            "qualification": "Analytic root count follows the accompanying reviewed Taylor/single-crossing proof, not sampled signs."}


def outward(value, grid, upper=False):
    numerator = value.numerator * grid
    rounded = -((-numerator) // value.denominator) if upper else numerator // value.denominator
    return Fraction(rounded, grid)


def log_atanh(z):
    require(0 <= z <= Fraction(1, 3), "reduced positive logarithm domain")
    square, power, total = z*z, z, Fraction(0)
    for index in range(LOG_TERMS):
        total += power / (2*index + 1)
        power *= square
    lower = 2*total
    return lower, lower + 2*power / ((2*LOG_TERMS + 1)*(1-square))


@lru_cache(None)
def logarithm(rank):
    require(type(rank) is int and rank >= 1, "positive integer power rank")
    exponent = rank.bit_length() - 1
    scale = 1 << exponent
    a, b = log_atanh(Fraction(1, 3))
    c, d = log_atanh(Fraction(rank - scale, rank + scale))
    return outward(exponent*a + c, WORK_GRID), outward(exponent*b + d, WORK_GRID, True)


def exp_positive(value):
    require(0 <= value <= Fraction(1, 4), "small nonnegative exponential domain")
    total, term = Fraction(1), Fraction(1)
    for index in range(1, EXP_DEGREE + 1):
        term *= value / index
        total += term
    following = term * value / (EXP_DEGREE + 1)
    tail = following / (1 - value / (EXP_DEGREE + 2))
    return total, total + tail


def power_bounds(rank, exponent):
    require(0 <= exponent <= 1, "closed tariff exponent domain")
    a, b = logarithm(rank)
    low_argument, high_argument = exponent*a/16, exponent*b/16
    require(0 <= low_argument <= high_argument <= Fraction(1, 4), "complete exponential argument enclosure")
    low = outward(exp_positive(low_argument)[0], WORK_GRID)
    high = outward(exp_positive(high_argument)[1], WORK_GRID, True)
    for _ in range(4):
        low = outward(low*low, WORK_GRID)
        high = outward(high*high, WORK_GRID, True)
    require(0 < low <= high, "ordered positive power bounds")
    return outward(low, POWER_GRID), outward(high, POWER_GRID, True)


def gain_bounds(exponent, coefficients=EXPECTED_G):
    lower, upper = Fraction(0), Fraction(0)
    for rank, coefficient in coefficients.items():
        a, b = power_bounds(rank, exponent)
        lower += coefficient*(a if coefficient >= 0 else b)
        upper += coefficient*(b if coefficient >= 0 else a)
    require(lower <= upper, "ordered signed gain interval")
    return lower, upper


def strict_sign(interval):
    low, high = interval
    if low > 0:
        return 1
    if high < 0:
        return -1
    if low == high == 0:
        return 0
    raise ValueError("undecidable gain interval sign")


def checked_bracket(low, high, required=(-1, 1)):
    require(0 < low < high < 1 and high-low <= Fraction(1, 10**10), "strict rational interior bracket ordering/width")
    intervals = gain_bounds(low), gain_bounds(high)
    signs = tuple(strict_sign(interval) for interval in intervals)
    require(signs == required, "relative root endpoint sign orientation")
    return intervals


def encoded_interval(value):
    return [str(endpoint) for endpoint in value]


def rejected(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError("counterfactual certificate accepted")


def counterfactual_controls(primary, oracle):
    result = {}
    for label in ("missing_carrier_fee", "missing_productive_debit"):
        bad = deepcopy(primary)
        if label == "missing_carrier_fee":
            bad["complete"]["new"]["paid"]["1"] -= 19
        else:
            bad["complete"]["new"]["targets"]["8"] -= 19
            bad["complete"]["new"]["targets"]["9"] += 19
        actual = gain(*parse_pair(bad, "primary", "complete"))
        baseline = gain(*parse_pair(primary, "primary", "complete"))
        rank = next(r for r in sorted(actual.keys() | baseline.keys()) if actual.get(r, 0) != baseline.get(r, 0))
        result[label] = {"kind": "counterfactual invoice coefficients, not a valid cheaper source program",
                         "complete_coefficient_witness": {"rank": rank, "actual": actual.get(rank, 0),
                                                          "expected": baseline.get(rank, 0)},
                         "rejection": rejected(lambda: bound_coefficients(bad, oracle))}
    result["wrong_endpoint_sign_orientation"] = {
        "rejection": rejected(lambda: checked_bracket(BRACKET_LOW, BRACKET_HIGH, required=(1, -1)))}
    return result


def run():
    primary, oracle = authenticated_receipts()
    local, complete, _ = bound_coefficients(primary, oracle)
    analytic = global_certificate(local)
    left, right = checked_bracket(BRACKET_LOW, BRACKET_HIGH)
    square_root = gain_bounds(Fraction(1, 2))
    claimed_exponent = 1 - CLAIMED_KAPPA
    claimed = gain_bounds(claimed_exponent)
    require(strict_sign(square_root) == -1 and strict_sign(claimed) == 1, "source-relative example tariff signs")
    return {"schema_version": 1, "scope": "source-specific exact relative power-tariff crossover, not a raw kappa root",
            "preserved_scientific_files": FROZEN,
            "local_gain_coefficients": {str(r): c for r, c in local.items()},
            "complete_gain_coefficients": {str(r): c for r, c in complete.items()},
            "complete_factor": 19, "analytic_root_count": analytic,
            "interior_bracket": {"lower": str(BRACKET_LOW), "upper": str(BRACKET_HIGH),
                                 "width": str(BRACKET_HIGH - BRACKET_LOW),
                                 "gain_at_lower": encoded_interval(left), "gain_at_upper": encoded_interval(right)},
            "linear_tariff_gain": "0", "count_tariff_gain": "-3",
            "examples": {"square_root": {"exponent": "1/2", "local_gain": encoded_interval(square_root)},
                         "author_claimed_tariff": {"source_claimed_kappa": str(CLAIMED_KAPPA),
                                                  "exponent": str(claimed_exponent),
                                                  "local_gain": encoded_interval(claimed),
                                                  "complete_relative_gain": encoded_interval(tuple(19*x for x in claimed))}},
            "interval_method": {"log_atanh_terms": LOG_TERMS, "log_work_grid": str(WORK_GRID),
                                "positive_exp_degree": EXP_DEGREE, "argument_divisor": 16,
                                "outward_squarings": 4, "power_grid": str(POWER_GRID)},
            "controls": counterfactual_controls(primary, oracle),
            "limits": ["Profile extraction and native/rank-tariff premises remain as stated in the immutable profile evidence.",
                       "A relative bill improvement does not prove source endpoint/native/caller validity or ordinary funding.",
                       "No new multiplication saving, raw kappa crossing, supplier admission or selected-frontier change is claimed."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit fresh certificate JSON without retained-receipt comparison")
    options = parser.parse_args()
    result = run()
    payload = (json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    if options.emit:
        sys.stdout.buffer.write(payload)
    else:
        retained = HERE / "RELATIVE-RESULT.json"
        require(retained.is_file(), "retained RELATIVE-RESULT.json receipt must exist")
        raw = retained.read_bytes()
        parsed = strict_json(raw)
        require(type(parsed) is dict and type(parsed.get("schema_version")) is int and parsed["schema_version"] == 1,
                "typed relative receipt schema")
        require(canonical(parsed) == canonical(result) and raw == payload, "exact typed byte RELATIVE-RESULT.json receipt")
        print("PASS exact relative tariff threshold and retained receipt")
