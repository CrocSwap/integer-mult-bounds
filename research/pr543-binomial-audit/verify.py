#!/usr/bin/env python3
"""Audit the pinned PR543 bit moment without logarithms or exponentials.

Prepared for 0x-chad with substantial OpenAI assistance. Apache-2.0.
See README.md for the enclosure proof, attribution, and limits.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BITS = 192
TAIL_BITS = 160
MAX_TERMS = 16384
SEED = 71
GRID = Q(1, 10**24)
EXPECTED = "research/e8-bit-r420/EXPECTED.json"
ASSEMBLY = "research/community-k492-audit/pr626/replay/ASSEMBLY.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(n, d):
    return -(-n // d)


def power_bounds(m, r, a, *, max_terms=MAX_TERMS):
    """Enclose (m/r)**a using positive binomial terms and integer rounding.

    With z=1-r/m, t[0]=1 and t[n]=t[n-1]*z*(a+n-1)/n.
    For 0<=a<=1 the subsequent term ratios are <=z, so the tail after
    t[n] is <=t[n]*z/(1-z). No floating-point operation is used.
    """
    require(type(m) is int and type(r) is int and 0 < r <= m,
            "power domain requires integer 0 < r <= m")
    require(isinstance(a, Q) and 0 <= a <= 1,
            "power domain requires rational 0 <= a <= 1")
    require(type(max_terms) is int and max_terms > 0, "positive term limit required")
    if r == m or a == 0:
        return Q(1), Q(1), 0
    scale = 1 << BITS
    threshold = 1 << (BITS - TAIL_BITS)
    p, q = a.numerator, a.denominator
    term_lo = term_hi = sum_lo = sum_hi = scale
    for n in range(1, max_terms + 1):
        numerator = (m - r) * (p + (n - 1) * q)
        denominator = m * n * q
        term_lo = term_lo * numerator // denominator
        term_hi = ceil_div(term_hi * numerator, denominator)
        sum_lo += term_lo
        sum_hi += term_hi
        tail_hi = ceil_div(term_hi * (m - r), r)
        if tail_hi <= threshold:
            return Q(sum_lo, scale), Q(sum_hi + tail_hi, scale), n
    raise ArithmeticError("binomial tail unresolved within term limit")


def moment(profile, m, live, a, *, surcharge=True):
    require(type(live) is int and live > 0 and bool(profile), "invalid moment stock")
    low = high = Q(0)
    powers = {}
    for r, count in sorted(profile.items()):
        require(type(r) is int and 0 < r < m and type(count) is int and count > 0,
                "improper child")
        lo, hi, n = power_bounds(m, r, a)
        powers[r] = (lo, hi, n)
        weight = Q(r * count, m * live)
        low += weight * lo
        high += weight * hi
    if surcharge:
        # (32*m*m*E) rank-one calls, exceptional fraction 10^-16,
        # and the same 1/(m*live) normalization as every ordinary child.
        if 1 not in powers:
            powers[1] = power_bounds(m, 1, a)
        lo, hi, _ = powers[1]
        weight = Q(32 * m * sum(profile.values()), 10**16 * live)
        low += weight * lo
        high += weight * hi
    return low, high, {str(r): n for r, (_, _, n) in powers.items()}


def residual(bounds):
    return [str(bounds[0] - 1), str(bounds[1] - 1)]


def algebraic_controls():
    """Check rational powers by integer-power comparisons, not another series."""
    cases = [(1, 1, Q(0)), (64, 64, Q(1, 71)), (64, 1, Q(0)),
             (64, 1, Q(1)), (64, 1, Q(1, 2)), (64, 1, Q(1, 3)),
             (9, 4, Q(1, 2)), (64, 63, Q(1, 71)), (64, 1, Q(70, 71))]
    rng = random.Random(SEED)
    while len(cases) < 71:
        m = rng.randrange(2, 65)
        r = rng.randrange(1, m + 1)
        q = rng.randrange(2, 72)
        case = (m, r, Q(rng.randrange(1, q), q))
        if case not in cases:
            cases.append(case)
    result = []
    for m, r, a in cases:
        lo, hi, n = power_bounds(m, r, a)
        # Raising positive endpoints to q preserves their order. The target
        # rational power is bracketed iff lo**q <= (m/r)**p <= hi**q.
        target = Q(m, r) ** a.numerator
        require(lo ** a.denominator <= target <= hi ** a.denominator,
                f"algebraic enclosure failed: {(m, r, str(a))}")
        result.append({"m": m, "r": r, "a": str(a), "terms": n})
    return result


def rejection_controls():
    cases = [("zero_rank", lambda: power_bounds(64, 0, Q(1, 2))),
             ("rank_above_dimension", lambda: power_bounds(64, 65, Q(1, 2))),
             ("negative_exponent", lambda: power_bounds(64, 1, Q(-1, 71))),
             ("exponent_above_one", lambda: power_bounds(64, 1, Q(72, 71))),
             ("nonrational_exponent", lambda: power_bounds(64, 1, "1/2")),
             ("noninteger_count", lambda: moment({1: Q(3, 2)}, 64, 1, Q(1, 2))),
             ("zero_count", lambda: moment({1: 0}, 64, 1, Q(1, 2))),
             ("unresolved_tail", lambda: power_bounds(64, 1, Q(1, 2), max_terms=1))]
    rejected = []
    for name, run in cases:
        try:
            run()
        except (ValueError, ArithmeticError):
            rejected.append(name)
        else:
            raise ValueError(f"invalid control accepted: {name}")
    return rejected


def audit():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for path, digest in sources["files"].items():
        require(sha256((ROOT / path).read_bytes()).hexdigest() == digest,
                f"source hash mismatch: {path}")
    expected = json.loads((ROOT / EXPECTED).read_text())["nine"]
    assembly = json.loads((ROOT / ASSEMBLY).read_text())
    profile = {int(r): n for r, n in expected["profile"].items()}
    live = expected["bit"]["live"]
    # PR510/463 global_k.py: compressed odd-stage dimension m=1+7*L.
    m = 1 + 7 * 9
    mass = sum(r * n for r, n in profile.items())
    require(mass == expected["bit"]["rank_mass"], "rank mass mismatch")
    require(m * live - mass == 32 * (2 * 4 * 120 - 9 * 8 * 9), "deficit mismatch")
    lower = Q(expected["bit_lower"])
    upper = lower + GRID
    require(Q(assembly["bit_lower"]) == lower, "consumed bit endpoint mismatch")
    require(assembly["surcharge_model"]["bit"] is True, "bit surcharge not consumed")
    require(assembly["bit_supplier"]["commit"] == sources["supplier_commit"],
            "supplier commit mismatch")
    recorded = [row for row in assembly["moments"] if row["side"] == "bit"]
    require([(Q(row["endpoint"]), row["accept"], row["surcharge"]) for row in recorded]
            == [(lower, True, True), (upper, False, True)], "consumed bracket mismatch")

    at_lower = moment(profile, m, live, lower)
    at_upper = moment(profile, m, live, upper)
    require(at_lower[1] < 1 < at_upper[0], "claimed strict root bracket failed")
    no_surcharge = moment(profile, m, live, upper, surcharge=False)
    require(no_surcharge[1] < 1, "omitted surcharge control did not separate")

    # Same call count, rank mass, maximum child and surcharge; different moment.
    changed = dict(profile)
    changed[1] -= 1
    changed[42] -= 1
    changed[2] += 1
    changed[41] = changed.get(41, 0) + 1
    require(sum(changed.values()) == sum(profile.values())
            and sum(r * n for r, n in changed.items()) == mass
            and max(changed) == max(profile), "redistribution invariants failed")
    redistributed = moment(changed, m, live, lower)
    require(redistributed[0] > 1, "rank-mass-only control did not reject")

    # A finite sum without its positive tail is not an upper enclosure.
    # At a=1 the complete binomial sum has the exact value m/r=64.
    degree = 1 + SEED % 13
    z = Q(63, 64)
    partial = sum((z**n for n in range(degree + 1)), Q(0))
    require(partial < 64, "tailless upper bound control did not fail")
    controls = algebraic_controls()
    rejected = rejection_controls()
    return {
        "status": "PASS_PR543_BINOMIAL_MOMENT",
        "base_commit": sources["base_commit"],
        "supplier_commit": sources["supplier_commit"],
        "assignment_seed": SEED,
        "precision_bits": BITS,
        "tail_bound_bits": TAIL_BITS,
        "maximum_terms_per_power": MAX_TERMS,
        "dimension": m,
        "live": live,
        "paid_profile": {str(r): n for r, n in sorted(profile.items())},
        "paid_calls": sum(profile.values()),
        "rank_mass": mass,
        "deficit": m * live - mass,
        "exceptional_rank_one_calls": 32 * m * m * sum(profile.values()),
        "exceptional_fraction": "1/10000000000000000",
        "root_bracket": {
            "lower": str(lower), "upper": str(upper),
            "at_lower_minus_one": residual(at_lower),
            "at_upper_minus_one": residual(at_upper),
            "lower_terms_by_rank": at_lower[2], "upper_terms_by_rank": at_upper[2],
        },
        "negative_controls": {
            "next_grid_without_surcharge_minus_one": residual(no_surcharge),
            "same_mass_and_calls_1_plus_42_to_2_plus_41_minus_one": residual(redistributed),
            "tailless_upper_counterexample": {
                "base": "64", "exponent": "1", "degree": degree,
                "false_upper": str(partial), "exact_value": "64",
            },
        },
        "algebraic_controls": controls,
        "rejected_inputs": rejected,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the recomputed exact certificate")
    args = parser.parse_args()
    result = audit()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE / "certificate.json").read_text())
        require(result == expected, "committed certificate differs from recomputation")
        print(result["status"])
        print("Strict adjacent 10^-24 endpoints; 71 algebraic controls; "
              "3 mathematical controls; 8 rejected inputs.")


if __name__ == "__main__":
    main()
