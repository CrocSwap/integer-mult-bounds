"""Separate exact dynamic-program check for the L253 temporal invoice."""
from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dyadic_parts(value):
    value = Fraction(value)
    n, d = abs(value.numerator), value.denominator
    need(n > 0 and d & (d - 1) == 0, "nonzero dyadic coefficient")
    v = (n & -n).bit_length() - 1
    return n >> v, v - (d.bit_length() - 1)


def real_add_price(value):
    odd, exponent = dyadic_parts(value)
    return 1 + odd.bit_length() + odd.bit_count() + abs(exponent) - int(odd == 1 and exponent == 0)


def power_two(exponent):
    return Fraction(2 ** exponent, 1) if exponent >= 0 else Fraction(1, 2 ** -exponent)


def exact_minimum(terms):
    """Minimum over every integer schedule, after an exact tail clamp."""
    breaks = [0]
    for _, coefficient, sign in terms:
        _, exponent = dyadic_parts(coefficient)
        breaks.append(-sign * exponent)
    low, high = min(breaks), max(breaks)
    # Each layer is a usage of L253. The state is the last applied exponent;
    # edge weights are scale work plus the change in the exact ADD lowerer.
    states = {0: 0}
    for _, coefficient, sign in terms:
        next_states = {}
        for exponent in range(low, high + 1):
            changed = real_add_price(coefficient * power_two(sign * exponent))
            delta = changed - real_add_price(coefficient)
            next_states[exponent] = min(value + abs(exponent - previous) + delta
                                        for previous, value in states.items())
        states = next_states
    return min(value + abs(previous) for previous, value in states.items()), [low, high]


def schedule_delta(terms, schedule):
    need(len(terms) == len(schedule), "schedule length")
    previous = 0
    total = 0
    for (_, coefficient, sign), (_, exponent) in zip(terms, schedule):
        total += abs(exponent - previous)
        changed = coefficient * power_two(sign * exponent)
        total += real_add_price(changed) - real_add_price(coefficient)
        previous = exponent
    return total + abs(previous)
