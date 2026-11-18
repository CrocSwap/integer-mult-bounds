"""Attaining edit, a mixed-only bank, and rational isolation of the switch."""
from fractions import Fraction
from math import factorial

from word import require


def quotient_dependencies(bank, equations):
    """Chronological elimination modulo the equations, with earlier-bank witnesses."""
    pivots = {}
    for v in equations:
        while v:
            j = v.bit_length() - 1
            if j not in pivots:
                pivots[j] = (v, 0)
                break
            v ^= pivots[j][0]
        else:
            raise ValueError("dependent quotient equations")
    dependencies = []
    for i, token in enumerate(bank):
        v = token.signal
        tags = 1 << i
        while v:
            j = v.bit_length() - 1
            if j not in pivots:
                pivots[j] = (v, tags)
                break
            other, witness = pivots[j]
            v ^= other
            tags ^= witness
        else:
            earlier = [bank[k].clock for k in range(i) if tags >> k & 1]
            dependencies.append((token, earlier))
    return dependencies


def attaining_edit(banks, groups, frames):
    roles = [r for (a, d), block in groups.items()
             if abs(frames[a] - frames[d]) == 6 for r in block]
    require(roles == [341], "rank-six target")
    result = []
    for chart, bank in sorted(banks.items()):
        entries = {token.clock: token for token in bank}
        for token, earlier in quotient_dependencies(bank, [1 << roles[0]]):
            if token.rank == 0:
                continue
            difference = token.signal
            for clock in earlier:
                require(clock < token.clock, "noncausal attaining reconstruction")
                difference ^= entries[clock].signal
            require(difference == 1 << roles[0], "literal rank-six identity")
            result.append({"chart": chart, "clock": token.clock, "rank": token.rank,
                           "earlier_clocks": earlier})
    require(sorted(row["rank"] for row in result) == [1, 4], "complete attained tariff")
    return result


def mixed_example(bank):
    a = 1 << 331
    b = (1 << 332) | (1 << 333)
    token, = [row for row in bank if row.clock == 19881]
    require(token.rank == 1 and token.signal == a ^ b, "mixed bank signal")
    def removed(equations):
        return any(row.clock == token.clock for row, _ in quotient_dependencies(bank, equations))
    require(removed([a, b]) and not removed([a]) and not removed([b]), "genuine cross-group dependence")
    return {"forward_chart": 50, "clock": token.clock, "separate_equations": [[331], [332, 333]]}


def log_interval(base):
    z = Fraction(base - 1, base + 1)
    count = 85
    partial = 2 * sum(z ** (2 * j + 1) / (2 * j + 1) for j in range(count))
    tail = 2 * z ** (2 * count + 1) / ((2 * count + 1) * (1 - z * z))
    scale = 10 ** 28
    return Fraction(int(partial * scale), scale), Fraction(int((partial + tail) * scale) + 1, scale)


def exp_partial(y):
    term = Fraction(1)
    total = term
    for j in range(1, 45):
        term = term * y / j
        total += term
    return total


def power_interval(base, exponent):
    low, high = log_interval(base)
    require(0 <= exponent * low <= exponent * high < 2, "exponential tail domain")
    # From term 45 onwards each ratio is < 2/46, hence the factor two suffices.
    return exp_partial(exponent * low), exp_partial(exponent * high) + Fraction(2 ** 46, factorial(45))


def root_interval():
    left = "0.2517782975220009"
    right = "0.2517782975220010"
    for endpoint, positive in ((left, False), (right, True)):
        t = 1 - Fraction(endpoint)
        low4, high4 = power_interval(4, t)
        low6, high6 = power_interval(6, t)
        require(1 + low4 > high6 if positive else 1 + high4 < low6, "outward root isolation")
    # log_2(5/3) < 37/50 and 6^(37/50) < 34/9 < 1 + 4^(37/50).
    require(2 ** 37 * 3 ** 50 > 5 ** 50 and 6 ** 37 * 9 ** 50 < 34 ** 50,
            "switch inside the certified tariff interval")
    return [left, right]
