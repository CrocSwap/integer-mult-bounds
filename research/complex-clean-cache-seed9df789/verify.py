#!/usr/bin/env python3
"""Exact interval controls for the clean two-output cache channel lemma."""
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction as Q
from functools import lru_cache
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INTERVAL_PATH = ROOT / "research/complex-local-word-ceiling/ceiling.py"
spec = importlib.util.spec_from_file_location("pinned_ceiling", INTERVAL_PATH)
intervals = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intervals)


def require(ok, message):
    if not ok:
        raise AssertionError(message)


@lru_cache(None)
def power_interval(n, s):
    """Outward interval for n**s, using n**s=n/exp((1-s)*ln(n))."""
    require(type(n) is int and n >= 1 and 0 < s < 1, "power domain")
    delta = 1 - s
    ln_lo, ln_hi = intervals.ln(n)
    exp_lo, exp_hi = intervals.exp(delta * ln_lo, delta * ln_hi)
    return intervals.down(Q(n) / exp_hi), intervals.up(Q(n) / exp_lo)


def add_intervals(*values):
    return sum((v[0] for v in values), Q(0)), sum((v[1] for v in values), Q(0))


def scaled_interval(n, value):
    return n * value[0], n * value[1]


def decimal6(x):
    with localcontext() as ctx:
        ctx.prec = 40
        return format((Decimal(x.numerator) / Decimal(x.denominator)).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP), "f")


def dimensions():
    F = set(range(1, 7))
    H = {1}
    Gs = [
        {1, 7, 8, 9, 10, 11, 12, 13},
        {1, 7, 8, 9, 10, 11, 12, 14},
        {1, 7, 8, 9, 10, 11, 12, 15},
    ]
    a = len(F | H)
    bs = [len(H | G) for G in Gs]
    ds = [len(F | G) for G in Gs]
    require((a, bs, ds) == (6, [8, 8, 8], [13, 13, 13]), "coordinate-span control")
    return a, bs, ds


def main():
    exponents = (Q(9983, 10000), Q(999, 1000))
    expected_triples = sum(1 for a in range(1, 65) for b in range(1, 65)
                           for d in range(1, 65) if d <= a + b)
    require(expected_triples == 220480, "rank-triple census")
    for s in exponents:
        for a in range(1, 65):
            ai = power_interval(a, s)
            for b in range(1, 65):
                ab = add_intervals(ai, power_interval(b, s))
                for d in range(1, min(64, a + b) + 1):
                    require(ab[0] > power_interval(d, s)[1],
                            f"two-port subadditivity rank control failed: {(a, b, d, s)}")

    s = exponents[0]
    p6, p8, p13 = power_interval(6, s), power_interval(8, s), power_interval(13, s)
    direct2 = scaled_interval(2, p13)
    cache2 = add_intervals(scaled_interval(2, p6), scaled_interval(2, p8))
    require(cache2[0] > direct2[1], "two-output control must satisfy cache >= direct")

    a, bs, ds = dimensions()
    direct3 = add_intervals(*(power_interval(d, s) for d in ds))
    cache3 = add_intervals(scaled_interval(2, power_interval(a, s)),
                           *(power_interval(b, s) for b in bs))
    require(cache3[1] < direct3[0], "three-output control must exhibit a cache saving")

    omitted_restore = add_intervals(power_interval(a, s), p8, p8)
    require(omitted_restore[1] < direct2[0],
            "omitting scratch restore should expose the false two-output saving")

    print(
        "PASS_TWO_PORT_CLEAN_CACHE ranks=1..64 triples=220480 alt_s_triples=220480 "
        "positive_control=3_outputs s=9983/10000 "
        f"direct2=[{decimal6(direct2[0])},{decimal6(direct2[1])}] "
        f"cache2=[{decimal6(cache2[0])},{decimal6(cache2[1])}] "
        f"direct3=[{decimal6(direct3[0])},{decimal6(direct3[1])}] "
        f"cache3=[{decimal6(cache3[0])},{decimal6(cache3[1])}] omitted_restore_rejected"
    )


if __name__ == "__main__":
    main()
