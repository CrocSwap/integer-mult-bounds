"""Exact power-sum enclosures and finite hypotheses for README's proof."""
from fractions import Fraction as Q
from functools import lru_cache

SCALE = 1 << 160


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceildiv(a, b):
    return -(-a // b)


def atanh_log(z):
    """Enclose 2 atanh(z) by 64 rational terms and a geometric tail."""
    need(Q(0) <= z <= Q(1, 3), "log range reduction")
    count = 64
    total = sum((2 * z ** (2 * j + 1) / (2 * j + 1) for j in range(count)), Q(0))
    tail = 2 * z ** (2 * count + 1) / ((2 * count + 1) * (1 - z * z))
    return total, total + tail


@lru_cache(None)
def log_interval(rank):
    need(type(rank) is int and 1 <= rank <= 48, "log rank domain")
    k = rank.bit_length() - 1
    l2, u2 = atanh_log(Q(1, 3))
    lr, ur = atanh_log(Q(rank - (1 << k), rank + (1 << k)))
    lower, upper = (k * l2 + lr) * SCALE, (k * u2 + ur) * SCALE
    return lower.numerator // lower.denominator, ceildiv(upper.numerator, upper.denominator)


def exp_interval(lower, upper):
    """Outward integer Taylor recurrence, with all omitted terms bounded."""
    need(0 <= lower <= upper <= 4 * SCALE, "exp domain")
    term_lo = term_hi = sum_lo = sum_hi = SCALE
    count = 100
    for j in range(1, count + 1):
        term_lo = term_lo * lower // (SCALE * j)
        term_hi = ceildiv(term_hi * upper, SCALE * j)
        sum_lo += term_lo
        sum_hi += term_hi
    # First omitted term; subsequent ratios are at most 4/(count+2).
    first = ceildiv(term_hi * upper, SCALE * (count + 1))
    tail = ceildiv(first * (count + 2), count - 2)
    return sum_lo, sum_hi + tail


def power_interval(rank, power):
    need(Q(0) <= power <= Q(1), "power domain")
    lo, hi = log_interval(rank)
    return exp_interval(lo * power.numerator // power.denominator,
                        ceildiv(hi * power.numerator, power.denominator))


def sum_interval(delta, power):
    lo = hi = 0
    for rank, coefficient in delta.items():
        a, b = power_interval(rank, power)
        lo += coefficient * (a if coefficient >= 0 else b)
        hi += coefficient * (b if coefficient >= 0 else a)
    return lo, hi


def hinge_certificate(delta):
    need(all(type(r) is int and 1 <= r <= 48 and type(n) is int for r, n in delta.items()), "delta domain")
    need(sum(r * n for r, n in delta.items()) == 0, "equal rank mass")
    need(sum(delta.values()) > 0, "positive small-power limit")
    knots = [0] + sorted(delta)
    values = [sum(n * min(r, t) for r, n in delta.items()) for t in knots]
    need(values[0] == values[-1] == 0, "hinge endpoints")
    crossings = [i for i in range(len(knots) - 1) if values[i] > 0 > values[i + 1]]
    need(len(crossings) == 1, "one hinge crossing")
    i = crossings[0]
    need(all(v > 0 for v in values[1:i + 1]) and all(v < 0 for v in values[i + 1:-1]), "hinge sign order")
    crossing = Q(knots[i]) + Q(values[i] * (knots[i + 1] - knots[i]), values[i] - values[i + 1])
    low, high = Q(289994, 1000000), Q(289995, 1000000)
    low_value, high_value = sum_interval(delta, low), sum_interval(delta, high)
    need(low_value[0] > 0 and high_value[1] < 0, "crossover bracket signs")
    return dict(knots=knots, values=values, hinge_crossing=str(crossing),
                crossover_interval=[str(low), str(high)], interval_scale=SCALE,
                power_sum_at_lower=list(low_value), power_sum_at_upper=list(high_value),
                conclusion="unique crossing in (0,1); new cost exceeds old below, is smaller above")
