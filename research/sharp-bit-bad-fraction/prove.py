"""Sharper bad-class charge for the binding bit supplier of PR 458.

PR 458's complex kernel raises the complex root above the bit root, so the
balanced assembly binds on the bit moment. That moment still charges every
paid edge the round envelope 10^-16 * 32 m^2. The source theorem gives the
smaller charge (2 m^3/2^80) * (6 N (N-1) + 3 N + 6 (N-1)) with N = 2 m.
The histogram, complex root and six-level assembly are unchanged.
"""
import importlib.util
from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "research" / "five-stage-gen4-banks"

# PR 458 EXPECTED.json bit profile. Same hosted histogram as PR 454.
PROFILE = {
    1: 217576,
    2: 93392,
    3: 24064,
    4: 31112,
    5: 8624,
    6: 5664,
    7: 5168,
    8: 792,
    35: 8,
    56: 440,
}
M = 78
W = 9600
DEFICIT = 3264
PUBLISHED_BIT = Q("10205262550350024303/8000000000000000000000")
PUBLISHED_COMPLEX = Q("1297203880559577927527/1000000000000000000000000")
PUBLISHED_KAPPA = Q("1274032589159993/1000000000000000000")
LEAF = Q(384599, 10**10)
ETA = BETA = GRID = Q(1, 10**18)
CHARGED_COEFFICIENT_BITS = 1024
PRIME = 1 << 80


def load(name):
    spec = importlib.util.spec_from_file_location(name, PKG / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gaussian_children(m):
    """Proved fallback count from notes/three-stage-cover-bit.tex, N = 2 m."""
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
    # One rank-one child contributes m^{a-1}/W. `children` of them on the bad fraction
    # of every edge contribute (children * edges * fraction) * m^{a-1} / W.
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


def kappa_of(outer, bit_lower, complex_lower):
    assert bit_lower < (1 - BETA) * complex_lower
    cap = min(bit_lower, (1 - BETA) * complex_lower) - Q(1, 10**24)
    saving = LEAF
    for _ in range(6):
        nxt = (1 - cap) * cap + cap * saving
        gap = min(cap - nxt, 1 - nxt - cap, 1 - nxt - cap * (1 - saving), 1 - cap)
        assert saving < nxt < cap < 1 - nxt and gap > 0
        cutoff = max(-((-36) // (gap * gap)), -((-2 * (4 + CHARGED_COEFFICIENT_BITS)) // gap))
        assert cutoff * gap * gap >= 36 and cutoff * gap >= 2 * (4 + CHARGED_COEFFICIENT_BITS)
        saving = nxt
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
    assert M * W - mass == DEFICIT
    assert max(PROFILE) < M and 2 * max(PROFILE) ** 3 < M ** 3

    children = gaussian_children(M)
    inherited_children = 32 * M * M
    inherited_fraction = Q(1, 10**16)
    sharp_fraction = Q(2 * M**3, PRIME)
    assert children < inherited_children
    assert 2 * M**3 * 10**16 < PRIME
    assert sharp_fraction < inherited_fraction
    assert children * sharp_fraction < inherited_children * inherited_fraction

    inherited_hi = moment.moment(PROFILE, M, W, PUBLISHED_BIT, True)[1]
    replay_hi = moment_charge(moment, PROFILE, PUBLISHED_BIT, inherited_children, inherited_fraction)[1]
    assert inherited_hi == replay_hi
    inherited = moment.certify(PROFILE, M, W, True)
    assert Q(inherited["lower"]) == PUBLISHED_BIT
    assert kappa_of(outer, PUBLISHED_BIT, PUBLISHED_COMPLEX) == PUBLISHED_KAPPA

    lower = certify(moment, PROFILE, children, sharp_fraction)
    assert lower > PUBLISHED_BIT
    assert lower < (1 - BETA) * PUBLISHED_COMPLEX
    cross_hi = other.moment(M, W, list(PROFILE.items()), lower)[1]
    fallback_hi = other.moment(M, W, [(1, children * edges)], lower)[1]
    assert cross_hi + fallback_hi * sharp_fraction < 1

    kappa = kappa_of(outer, lower, PUBLISHED_COMPLEX)
    assert lower == Q("127565782172928582023/100000000000000000000000")
    assert kappa == Q("25480651841761/20000000000000000")
    assert kappa > PUBLISHED_KAPPA
    print("PASS sharp bit bad-class charge")
    print("children", children, "inherited", inherited_children)
    print("fraction", sharp_fraction)
    print("bit_lower", lower)
    print("kappa", kappa)
    print("gain", kappa - PUBLISHED_KAPPA)


if __name__ == "__main__":
    main()
