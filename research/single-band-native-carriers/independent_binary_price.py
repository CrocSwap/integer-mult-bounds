"""Reprice both binary words from the raw tapes using rational log and exp series."""

from collections import Counter
from fractions import Fraction
from functools import cache


GRID = 1 << 112


def grid_bounds(lower, upper):
    lo = lower * GRID
    hi = upper * GRID
    return Fraction(lo.__floor__(), GRID), Fraction(hi.__ceil__(), GRID)


@cache
def log_ratio(z):
    """Enclose 2 atanh(z) by its positive series and a geometric tail."""
    assert 0 <= z <= Fraction(1, 3)
    z2 = z * z
    term = z
    total = Fraction(0)
    for j in range(45):
        total += term / (2 * j + 1)
        term *= z2
    return grid_bounds(2 * total, 2 * (total + term / (91 * (1 - z2))))


@cache
def log_rank(rank):
    """Reduce the argument to [1,2] before evaluation."""
    k = rank.bit_length() - 1
    radix = 1 << k
    low, high = log_ratio(Fraction(rank - radix, rank + radix))
    log2low, log2high = log_ratio(Fraction(1, 3))
    return low + k * log2low, high + k * log2high


def small_exp(x):
    """Use the first 32 terms and bound all later term ratios by x/33."""
    assert 0 <= x <= 1
    term = total = Fraction(1)
    for j in range(1, 32):
        term *= x / j
        total += term
    next_term = term * x / 32
    return grid_bounds(total, total + next_term / (1 - x / 33))


@cache
def rank_price(rank, exponent):
    low, high = log_rank(rank)
    assert exponent >= 0
    a, _ = small_exp(low * exponent / 16)
    _, b = small_exp(high * exponent / 16)
    return grid_bounds(a**16, b**16)


def raw_moments(graph, caller):
    ports = caller["ports"]
    dims = {int(idx): frame["dim"] for idx, frame in graph["frames"].items()}
    targets = Counter()
    paid = Counter()
    local = sum(row[0] == "LOCAL" for row in caller["events"])
    for row in caller["diagonal"]:
        targets[1 + caller["body_rank"] * len(row["stages"])] += ports
    for src, dst in zip(graph["start"][2 * ports :], graph["final"][2 * ports :], strict=True):
        targets[abs(dims[dst] - dims[src])] += local
    for row in graph["program"]:
        if row[0] == "MOVE":
            paid[abs(dims[row[3]] - dims[row[2]])] += local
    for row in caller["events"]:
        if row[0] == "QUERY":
            paid[1] += ports
        elif row[0] == "IDLE_ONE":
            paid[len(row[2]) * caller["body_rank"]] += ports
    assert targets.total() == 18_906 and paid.total() == 104_904
    return targets, paid


def mass(histogram, exponent, upper):
    return sum(count * rank_price(rank, exponent)[upper] for rank, count in histogram.items())


def independent_prices(graph, caller):
    targets, paid = raw_moments(graph, caller)
    profiles = (
        (128, 16, Fraction(2_039, 2**19), Fraction(13, 32), Fraction(1, 10_000)),
        (228, 15, Fraction(17_108_907_955, 2**42), Fraction(31, 64), Fraction(1311, 10**13)),
    )
    floors = []
    for v, keep, saving, w, required in profiles:
        t, z = 1 - saving, Fraction(19, 64)
        target = mass(targets, t, 0)
        alpha = mass(paid, t, 1) / target
        gamma = mass(paid, t + z, 1) / (rank_price(12, z)[0] * target)
        lam = rank_price(keep, w)[1] * mass(targets, t - w, 1) / target
        surplus = 1 - alpha**v - 2 * gamma**v - lam**v
        assert surplus > required
        if v == 228:
            upper_target = mass(targets, t, 1)
            lower_base = mass(paid, t, 0) / upper_target
            old_drop = rank_price(16, w)[0] * mass(targets, t - w, 0) / upper_target
            assert lower_base**v + old_drop**v > 1
        floors.append((surplus * 10**18).__floor__())
    crossing_limit(targets, paid)
    return tuple(floors)


def crossing_limit(targets, paid):
    """Bind the monotonicity proof to every signed coefficient of the literal word."""
    signed = {
        r: targets[r] - paid[r] for r in targets.keys() | paid.keys() if targets[r] != paid[r]
    }
    expected = dict(enumerate((-48972, -44892, -1980, -900, -1044, -2916, -480), 1))
    expected.update({8: 14520, 64: 444, 127: 222})
    for low in range(14, 57, 7):
        expected[low] = -444
        expected[low + 1] = 444
    assert signed == expected
    upper = Fraction("0.0038901152866")
    assert mass(paid, 1 - upper, 0) > mass(targets, 1 - upper, 1)
    signed_rate_floor = Fraction("0.00389011527141") + Fraction(4, 10**14)
    five_bit_floor = (5 / (upper - signed_rate_floor)).__floor__() + 1
    installed_floor = (
        19 / (Fraction(17108907955, 2**42) - Fraction("0.003890115271496"))
    ).__floor__() + 1
    assert (five_bit_floor, installed_floor) == (330033003301, 1455682013917)
    print("PASS_BINARY_RANK_EXPONENT_FLOORS", five_bit_floor, installed_floor)


if __name__ == "__main__":
    from strong_binary import caller, graph

    print("PASS_INDEPENDENT_BINARY_SURPLUS_X_1E18", *independent_prices(graph(), caller()))
