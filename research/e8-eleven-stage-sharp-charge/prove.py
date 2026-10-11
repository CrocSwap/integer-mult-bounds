"""Sharper bad-class charge on the binding bit supplier of PR 450.

PR 450's eleven-stage cross-copy hosted word binds on the bit moment: its bit
root 1.349563e-3 sits strictly below (1 - 10^-18) times its complex root
1.437532e-3. That bit moment still charges every paid edge the inherited round
envelope 10^-16 * 32 m^2 rank-one children (engines/moment.py, bad=True). The
source theorem in notes/three-stage-cover-bit.tex proves the smaller charge
(2 m^3 / 2^80) * (6 N (N - 1) + 3 N + 6 (N - 1)) with N = 2 m, the form PR 461
applied to PR 458. Here it is applied to the current leader's word. The bit
histogram, live width, complex root, bootstrap and six-level outer assembly
are exactly PR 450's; only the bad-class term inside the bit moment changes.

Run from the repository root:  python3 -B research/e8-eleven-stage-sharp-charge/prove.py
"""
import importlib.util
from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINES = ROOT / "research" / "five-stage-gen4-banks"   # moment, base_two_moment and outer: byte-identical to PR 450's pinned engines

# PR 450 research/e8-eleven-stage-cross-copy, eleven/stacked_mixed/RESULT.json (head e36181b4).
PROFILE = {1: 27060, 2: 11132, 3: 3036, 4: 3465, 5: 1188, 6: 462, 7: 154, 8: 99, 14: 1, 56: 184}
M = 78            # 1 + 7 * 11
W = 1200          # live families, 2 K V with K = 5, V = 120
DEFICIT = 408     # T (2 K V - 72 L) with T = 1, L = 11
ALLOW = 28416     # external_row_allowance
CHARGED_TWO = 512 # charged_two_level_coefficient_bits
PUBLISHED_BIT = Q("674781707224226878971/500000000000000000000000")
PUBLISHED_COMPLEX = Q("718766148669433/500000000000000000")
PUBLISHED_KAPPA = Q("269548909542967/200000000000000000")
LEAF = Q(384599, 10 ** 10)
ETA = BETA = GRID = Q(1, 10 ** 18)
PRIME = 1 << 80

EXPECTED_BIT = Q("1349563417453477963841/1000000000000000000000000")
EXPECTED_KAPPA = Q("269548910142353/200000000000000000")


def load(name):
    spec = importlib.util.spec_from_file_location(name, ENGINES / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gaussian_children(m):
    """Fallback count proved in notes/three-stage-cover-bit.tex with N_0 = 2 m."""
    n = 2 * m
    return 6 * n * (n - 1) + 3 * n + 6 * (n - 1)


def moment_charge(moment, histogram, saving, children, fraction):
    """PR 450's exact rational moment with the bad-class term as `children * fraction` rank-one children per edge."""
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
    """Decimal proposes an endpoint; the exact rational engine decides, as in PR 450's certify."""
    edges = sum(histogram.values())
    with localcontext() as ctx:
        ctx.prec = 80
        terms = [(Decimal(rank * count) / Decimal(M * W), (Decimal(M) / Decimal(rank)).ln()) for rank, count in histogram.items()]
        fallback = Decimal(children * edges) * Decimal(fraction.numerator) / Decimal(fraction.denominator) / Decimal(M * W)
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
    lower = Q(proposal, 10 ** 24)
    while moment_charge(moment, histogram, lower, children, fraction)[1] >= 1:
        lower -= Q(1, 10 ** 24)
    assert moment_charge(moment, histogram, lower, children, fraction)[1] < 1
    upper = lower + Q(1, 10 ** 24)
    assert moment_charge(moment, histogram, upper, children, fraction)[0] > 1
    return lower


def ceil(x):
    return -((-x.numerator) // x.denominator)


def kappa_of(outer, bit_lower, complex_lower):
    """PR 450's bootstrap, grid rounding, strict outer assembly and four controls, verbatim in content."""
    assert bit_lower < (1 - BETA) * complex_lower
    s = min(bit_lower, (1 - BETA) * complex_lower) - Q(1, 10 ** 24)
    assert 0 < s < bit_lower
    chain = [LEAF]
    for _ in range(6):
        old = chain[-1]
        a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
        assert old < a < s < 1 - a and gap > 0
        cutoff = max(ceil(36 / gap ** 2), ceil(2 * (4 + CHARGED_TWO) / gap))
        assert cutoff * gap ** 2 >= 36 and cutoff * gap >= 2 * (4 + CHARGED_TWO)
        chain.append(a)
    q = chain[-1] * (1 - 2 * ETA)
    margin = (1 - ETA) * q / (1 + q)
    ticks = margin / GRID
    kappa = GRID * ((ticks.numerator - 1) // ticks.denominator)
    bridge = {"semantic": {"C0": {"base": 2, "exponent": 210000}, "strict_literal_gap": 1},
              "rows": {"degree_gap": Q(10 ** 6) - Q(51 * ALLOW, 25)}}
    assembly = outer.assembly(chain[-1], complex_lower, bridge, kappa, eta=ETA, beta=BETA)
    assert len(assembly["strict_constraints"]) == 47
    assert min(assembly["strict_constraints"].values()) > 0
    for name, kk, ee, bb in [("next_grid", kappa + GRID, ETA, BETA), ("zero_eta", kappa, Q(0), BETA),
                             ("zero_beta", kappa, ETA, Q(0)), ("unit_beta", kappa, ETA, Q(1))]:
        try:
            outer.assembly(chain[-1], complex_lower, bridge, kk, eta=ee, beta=bb)
        except AssertionError:
            continue
        raise AssertionError("control admitted: " + name)
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
    inherited_fraction = Q(1, 10 ** 16)
    sharp_fraction = Q(2 * M ** 3, PRIME)
    assert children < inherited_children
    assert 2 * M ** 3 * 10 ** 16 < PRIME
    assert sharp_fraction < inherited_fraction
    assert children * sharp_fraction < inherited_children * inherited_fraction

    # 1. The inherited envelope reproduces PR 450's published bit root and kappa.
    inherited_hi = moment.moment(PROFILE, M, W, PUBLISHED_BIT, True)[1]
    replay_hi = moment_charge(moment, PROFILE, PUBLISHED_BIT, inherited_children, inherited_fraction)[1]
    assert inherited_hi == replay_hi
    inherited = moment.certify(PROFILE, M, W, True)
    assert Q(inherited["lower"]) == PUBLISHED_BIT
    assert certify(moment, PROFILE, inherited_children, inherited_fraction) == PUBLISHED_BIT
    assert kappa_of(outer, PUBLISHED_BIT, PUBLISHED_COMPLEX) == PUBLISHED_KAPPA

    # 2. The sharp charge on the same histogram.
    lower = certify(moment, PROFILE, children, sharp_fraction)
    assert lower > PUBLISHED_BIT
    assert lower < (1 - BETA) * PUBLISHED_COMPLEX
    cross_hi = other.moment(M, W, list(PROFILE.items()), lower)[1]
    fallback_hi = other.moment(M, W, [(1, children * edges)], lower)[1]
    assert cross_hi + fallback_hi * sharp_fraction < 1
    cross_lo = other.moment(M, W, list(PROFILE.items()), lower + Q(1, 10 ** 24))[0]
    fallback_lo = other.moment(M, W, [(1, children * edges)], lower + Q(1, 10 ** 24))[0]
    assert cross_lo + fallback_lo * sharp_fraction > 1

    kappa = kappa_of(outer, lower, PUBLISHED_COMPLEX)
    assert lower == EXPECTED_BIT
    assert kappa == EXPECTED_KAPPA
    assert kappa > PUBLISHED_KAPPA

    # 3. Controls: a different histogram or the inherited charge must not reproduce the new pair.
    tampered = dict(PROFILE); tampered[56] += 1
    assert certify(moment, tampered, children, sharp_fraction) < lower
    print("PASS sharp bit bad-class charge on PR 450")
    print("children", children, "inherited", inherited_children)
    print("fraction", sharp_fraction, "inherited", inherited_fraction)
    print("bit_lower", lower, format(float(lower), ".18f"))
    print("complex_lower", PUBLISHED_COMPLEX, "(unchanged, slack", format(float((PUBLISHED_COMPLEX - lower) / lower * 100), ".4f"), "percent)")
    print("kappa", kappa, format(float(kappa), ".18f"))
    print("gain", kappa - PUBLISHED_KAPPA)


if __name__ == "__main__":
    main()
