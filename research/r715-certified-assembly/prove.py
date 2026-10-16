"""Certified assembly of the R715 bit profile with PR 458's complex root.

The paid-children histogram is the one recomputed in PR 463's tape audit:
m = 78, W = 1200, deficit 408, max child 56. The moment below uses the
inherited bad-class envelope first, then the sharp charge from
notes/three-stage-cover-bit.tex. The complex root is PR 458's. Residuals
stay whole.
"""
import importlib.util
from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "research" / "five-stage-gen4-banks"

PROFILE = {
    1: 26914,
    2: 11799,
    3: 2642,
    4: 3569,
    5: 1254,
    6: 906,
    7: 630,
    8: 99,
    42: 1,
    56: 63,
}
M = 78
W = 1200
DEFICIT = 408
PUBLISHED_BIT = Q("642564369945714399381/500000000000000000000000")
PUBLISHED_COMPLEX = Q("1297203880559577927527/1000000000000000000000000")
# PR 462, the previous whole-residual leader.
FRONTIER = Q("159311871398197/125000000000000000")
LEAF = Q(384599, 10**10)
ETA = BETA = GRID = Q(1, 10**18)
CHARGED_COEFFICIENT_BITS = 1664
PRIME = 1 << 80


def load(name):
    spec = importlib.util.spec_from_file_location(name, PKG / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gaussian_children(m):
    n = 2 * m
    return 6 * n * (n - 1) + 3 * n + 6 * (n - 1)


def moment_charge(moment, histogram, saving, children, fraction):
    lo = hi = Q(0)
    edges = 0
    for rank, count in histogram.items():
        assert 0 < rank < M and count > 0
        edges += count
        lower_log, upper_log = moment.logarithm(Q(M, rank))
        lower_exp, upper_exp = moment.exponential(saving * lower_log, saving * upper_log)
        weight = Q(rank * count, M * W)
        lo += weight * lower_exp
        hi += weight * upper_exp
    lower_log, upper_log = moment.logarithm(Q(M))
    lower_exp, upper_exp = moment.exponential(saving * lower_log, saving * upper_log)
    weight = Q(children * edges, M * W) * fraction
    lo += weight * lower_exp
    hi += weight * upper_exp
    return moment.floor(lo), moment.ceil(hi)


def certify(moment, histogram, children, fraction):
    edges = sum(histogram.values())
    with localcontext() as ctx:
        ctx.prec = 80
        terms = [
            (Decimal(rank * count) / Decimal(M * W), (Decimal(M) / Decimal(rank)).ln())
            for rank, count in histogram.items()
        ]
        fallback = (
            Decimal(children * edges)
            * Decimal(fraction.numerator)
            / Decimal(fraction.denominator)
            / Decimal(M * W)
        )
        log_m = Decimal(M).ln()
        lo = Decimal(0)
        hi = Decimal("0.003")
        for _ in range(240):
            mid = (lo + hi) / 2
            value = sum(weight * (mid * log_ratio).exp() for weight, log_ratio in terms)
            value += fallback * (mid * log_m).exp()
            if value < 1:
                lo = mid
            else:
                hi = mid
        proposal = int((lo * Decimal(10) ** 24).to_integral_value(rounding=ROUND_FLOOR))
    lower = Q(proposal, 10**24)
    while moment_charge(moment, histogram, lower, children, fraction)[1] >= 1:
        lower -= Q(1, 10**24)
    assert moment_charge(moment, histogram, lower, children, fraction)[1] < 1
    upper = lower + Q(1, 10**24)
    assert moment_charge(moment, histogram, upper, children, fraction)[0] > 1
    return lower


def bootstrap(bit_lower, complex_lower, charged_bits):
    assert bit_lower < (1 - BETA) * complex_lower
    cap = min(bit_lower, (1 - BETA) * complex_lower) - Q(1, 10**24)
    saving = LEAF
    for _ in range(6):
        nxt = (1 - cap) * cap + cap * saving
        gap = min(cap - nxt, 1 - nxt - cap, 1 - nxt - cap * (1 - saving), 1 - cap)
        assert saving < nxt < cap < 1 - nxt and gap > 0
        cutoff = max(-((-36) // (gap * gap)), -((-2 * (4 + charged_bits)) // gap))
        assert cutoff * gap * gap >= 36 and cutoff * gap >= 2 * (4 + charged_bits)
        saving = nxt
    return saving


def kappa_of(outer, bit_lower, complex_lower):
    saving = bootstrap(bit_lower, complex_lower, CHARGED_COEFFICIENT_BITS)
    # A larger finite coefficient charge still has a finite cutoff.
    bootstrap(bit_lower, complex_lower, 10**6)
    q = saving * (1 - 2 * ETA)
    margin = (1 - ETA) * q / (1 + q)
    ticks = margin / GRID
    kappa = GRID * ((ticks.numerator - 1) // ticks.denominator)
    bridge = {
        "semantic": {"C0": {"base": 2, "exponent": 210000}, "strict_literal_gap": 1},
        "rows": {"degree_gap": Q(10**6) - Q(51 * 20161, 25)},
    }
    assembly = outer.assembly(saving, complex_lower, bridge, kappa, eta=ETA, beta=BETA)
    assert len(assembly["strict_constraints"]) == 47
    assert min(assembly["strict_constraints"].values()) > 0
    try:
        outer.assembly(saving, complex_lower, bridge, kappa + GRID, eta=ETA, beta=BETA)
    except AssertionError:
        pass
    else:
        raise AssertionError("adjacent grid point admitted")
    return kappa


def main():
    moment = load("moment")
    other = load("base_two_moment")
    outer = load("outer")
    mass = sum(rank * count for rank, count in PROFILE.items())
    edges = sum(PROFILE.values())
    assert mass == 93192
    assert M * W - mass == DEFICIT
    assert max(PROFILE) == 56 and 2 * 56**3 < M**3

    inherited_children = 32 * M * M
    inherited_fraction = Q(1, 10**16)
    children = gaussian_children(M)
    sharp_fraction = Q(2 * M**3, PRIME)
    assert children * sharp_fraction < inherited_children * inherited_fraction

    inherited_hi = moment.moment(PROFILE, M, W, PUBLISHED_BIT, True)[1]
    replay_hi = moment_charge(moment, PROFILE, PUBLISHED_BIT, inherited_children, inherited_fraction)[1]
    assert inherited_hi == replay_hi
    inherited = moment.certify(PROFILE, M, W, True)
    assert Q(inherited["lower"]) == PUBLISHED_BIT
    inherited_kappa = kappa_of(outer, PUBLISHED_BIT, PUBLISHED_COMPLEX)
    assert inherited_kappa > FRONTIER

    lower = certify(moment, PROFILE, children, sharp_fraction)
    assert lower > PUBLISHED_BIT
    assert lower < (1 - BETA) * PUBLISHED_COMPLEX
    cross_hi = other.moment(M, W, list(PROFILE.items()), lower)[1]
    fallback_hi = other.moment(M, W, [(1, children * edges)], lower)[1]
    assert cross_hi + fallback_hi * sharp_fraction < 1
    kappa = kappa_of(outer, lower, PUBLISHED_COMPLEX)
    assert inherited_kappa == Q("641739651875561/500000000000000000")
    assert lower == Q("642564371409803769573/500000000000000000000000")
    assert kappa == Q("1283479306671789/1000000000000000000")
    assert kappa > inherited_kappa
    print("PASS R715 assembly")
    print("inherited_kappa", inherited_kappa)
    print("bit_lower", lower)
    print("kappa", kappa)
    print("gain_over_462", kappa - FRONTIER)


if __name__ == "__main__":
    main()
