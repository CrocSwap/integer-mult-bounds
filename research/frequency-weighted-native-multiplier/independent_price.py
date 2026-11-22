"""Check both actual transport prices on an independent 192-bit dyadic grid."""

from collections import Counter
from fractions import Fraction as Q
from math import ceil, isqrt
from pathlib import Path
import sys

IMAGE = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(IMAGE))
from upstream import install

install()
from band_product import prepare_native
from installations import BINARY_C, TERMINAL
from strong_complex import load_changed, word

GRID = 1 << 192


def powers(base, exponent):
    assert base > 0 and 0 < exponent < 1
    assert exponent.denominator.bit_count() == 1
    number = Q(base) * GRID
    low, high = number.__floor__(), ceil(number)
    lower_result = upper_result = GRID
    for bit in range(exponent.denominator.bit_length() - 2, -1, -1):
        low = isqrt(low * GRID)
        high = isqrt(high * GRID - 1) + 1
        if exponent.numerator >> bit & 1:
            lower_result = lower_result * low // GRID
            upper_result = ceil(Q(upper_result * high, GRID))
    return Q(lower_result, GRID), Q(upper_result, GRID)


def weighted():
    recipe = prepare_native(TERMINAL)[-1]
    c = recipe.trial
    psi = sum(
        recipe.paid.histogram[r] * share * r * (powers(Q(k, r), c)[0] - 1) / c
        for (r, k), share in recipe.cells.items()
    )
    axes = sum(k * n for k, n in recipe.targets.histogram.items())
    fringe = 10 * axes / ((1 - c) * psi)
    assert psi > Q("184971191.2157") and fringe < Q("7.335168")
    delta = Q(1, 2**128)
    upper = (
        (1 + delta)
        * (1 + Q(4 * 258, 1024 * 306))
        * powers(1024 * 306 * 2048, c)[1]
        * (1 + fringe / 2048 + delta)
        / (1 - delta) ** 4
    )
    lower = powers(2, Q(65081, 524288))[0]
    assert lower - upper > Q("0.00012957")


def rounded_peer():
    raw = word(*load_changed(IMAGE / "inputs"))

    def scales(ports):
        single = Counter(port.rank for port in ports)
        combined = single.copy()
        combined.update({8 * rank: count for rank, count in single.items()})
        return combined

    targets, paid = scales(raw.targets), scales(raw.paid)
    paid[1] -= 1006
    paid[Q(1, 4)] += 1006
    paid[Q(3, 4)] += 1006
    assert (targets.total(), paid.total()) == (105216, 564142)
    c = Q(4286126377, 2**40)
    endpoints = {r: powers(r, 1 - c) for r in (targets | paid)}

    def mass(rows, index):
        return sum(n * endpoints[r][index] for r, n in rows)

    tlo, thi = (mass(targets.items(), i) for i in (0, 1))
    plo, phi = (mass(paid.items(), i) for i in (0, 1))
    assert tlo > phi and plo / thi > Q(99, 100)
    for rank in sorted(paid)[1:]:
        load = mass(((r, n) for r, n in paid.items() if r >= rank), 1)
        cap = mass(((k, n) for k, n in targets.items() if 5 * rank <= 4 * k), 0)
        assert load <= cap * plo / thi
    delta, lower = Q(1, 2**128), 32768
    factor = (
        Q(256, 255)
        * Q(4097, 4096)
        * Q(1028, 1024)
        * powers(1024 * 1224 * lower, c)[1]
        * (1 + Q(64, lower) + delta)
        / ((1 - Q(10, lower)) * (1 - delta) ** 3)
    )
    assert factor**256 < 2**39
    peer = Q(".0038982016137")
    first = 249 * (BINARY_C - Q(11, 8 * 60000)) / 250
    booked = Q((first * 10**18).__floor__() - 1, 10**18)
    second = (249 * (BINARY_C - Q(11, 8 * 960000)) + booked) / 250
    assert peer + Q(5, 10**18) < min(second, c - Q(39, 256 * 20000000))
    assert TERMINAL.kappa - peer == Q(83863, 10**13) and TERMINAL.kappa > c


if __name__ == "__main__":
    if not __debug__:
        raise ValueError("Run with assertions enabled")
    weighted()
    rounded_peer()
    print("PASS_INDEPENDENT_WEIGHTED_AND_QUARTER_PRICES")
