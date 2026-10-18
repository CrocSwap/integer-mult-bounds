"""Independent exact pricing and event transformation for one temporal helper gauge."""
from copy import deepcopy
from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dyadic_parts(value):
    value = Fraction(value)
    numerator, denominator = abs(value.numerator), value.denominator
    need(numerator and denominator & (denominator - 1) == 0, "nonzero dyadic required")
    trailing = (numerator & -numerator).bit_length() - 1
    return numerator >> trailing, trailing - (denominator.bit_length() - 1)


def add_price(value):
    odd, exponent = dyadic_parts(value)
    return 1 + odd.bit_length() + odd.bit_count() + abs(exponent) - int(odd == 1 and exponent == 0)


def power2(exponent):
    return Fraction(2 ** exponent, 1) if exponent >= 0 else Fraction(1, 2 ** -exponent)


def incident_adds(events, helper):
    result = []
    for index, event in enumerate(events):
        if event[0] != "scalar" or event[1][0] != "add":
            continue
        op = event[1]
        sign = int(op[1] == ["L", helper]) - int(op[2] == ["L", helper])
        if sign:
            result.append((index, Fraction(op[3], op[4]), sign))
    need(result, "helper must occur in at least one ADD")
    return result


def objective(terms, schedule):
    need(len(terms) == len(schedule), "schedule covers all incident ADDs")
    previous = result = 0
    for (_, coefficient, sign), exponent in zip(terms, schedule):
        result += abs(exponent - previous)
        result += add_price(coefficient * power2(sign * exponent)) - add_price(coefficient)
        previous = exponent
    return result + abs(previous)


def optimize(terms):
    """Exact layered shortest path over the finite interval of all price breakpoints."""
    breakpoints = [0]
    for _, coefficient, sign in terms:
        _, exponent = dyadic_parts(coefficient)
        breakpoints.append(-sign * exponent)
    low, high = min(breakpoints), max(breakpoints)
    domain = tuple(range(low, high + 1))

    # Each state stores (cost, transition count, schedule L1, lexicographic path).
    states = {0: (0, 0, 0, ())}
    edge_evaluations = 0
    for _, coefficient, sign in terms:
        delta = {k: add_price(coefficient * power2(sign * k)) - add_price(coefficient)
                 for k in domain}
        next_states = {}
        for current in domain:
            choices = []
            for previous, value in states.items():
                edge_evaluations += 1
                choices.append((value[0] + abs(current - previous) + delta[current],
                                value[1] + int(current != previous),
                                value[2] + abs(current), value[3] + (current,)))
            next_states[current] = min(choices)
        states = next_states

    finished = [(value[0] + abs(last), value[1] + int(last != 0), value[2], value[3])
                for last, value in states.items()]
    best = min(finished)
    constants = [(2 * abs(k) + sum(add_price(coefficient * power2(sign * k)) - add_price(coefficient)
                                   for _, coefficient, sign in terms),
                  int(k != 0), abs(k), k) for k in domain]
    constant = min(constants)
    schedule = best[3]
    need(objective(terms, schedule) == best[0], "exact objective replay")
    return {
        "domain": [low, high],
        "domain_size": len(domain),
        "edge_evaluations": edge_evaluations,
        "delta_real": best[0],
        "transition_count": best[1],
        "schedule_l1": best[2],
        "schedule": schedule,
        "constant_delta_real": constant[0],
        "constant_exponent": constant[3],
    }


def transform(events, helper, terms, schedule):
    """Apply the exact changing gauge; retain all original nonscalar and SCALE events."""
    need(len(terms) == len(schedule), "complete schedule")
    indices = [index for index, _, _ in terms]
    need(len(indices) == len(set(indices)), "unique chronological ADD indices")
    need(events[-1] == ["phase", "done"], "terminal cleanup boundary")
    signs = {index: sign for index, _, sign in terms}
    exponents = dict(zip(indices, schedule))
    result, inserted, previous = [], [], 0
    for index, old in enumerate(events):
        event = deepcopy(old)
        if index in exponents:
            current = exponents[index]
            if current != previous:
                change = current - previous
                scale = power2(change)
                pulse = ["scalar", ["scale", ["L", helper], scale.numerator, scale.denominator], event[2]]
                output_index = len(result)
                result.append(pulse)
                inserted.append([index, change, event[2], output_index])
            op = event[1]
            coefficient = Fraction(op[3], op[4]) * power2(signs[index] * current)
            op[3], op[4] = coefficient.numerator, coefficient.denominator
            previous = current
        if index == len(events) - 1 and previous:
            scale = power2(-previous)
            pulse = ["scalar", ["scale", ["L", helper], scale.numerator, scale.denominator], 1]
            output_index = len(result)
            result.append(pulse)
            inserted.append([index, -previous, 1, output_index])
        result.append(event)
    return result, inserted


def small_exhaustive_control():
    """Compare the DP with direct enumeration on a three-ADD control word."""
    from itertools import product
    terms = [(0, Fraction(3, 8), 1), (1, Fraction(5, 4), -1), (2, Fraction(3, 2), 1)]
    result = optimize(terms)
    lo, hi = result["domain"]
    direct = min(objective(terms, path) for path in product(range(lo, hi + 1), repeat=len(terms)))
    need(direct == result["delta_real"], "small exhaustive objective control")
    return result["delta_real"]
