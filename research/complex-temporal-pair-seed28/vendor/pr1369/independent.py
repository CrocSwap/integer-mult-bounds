"""Exact one-coordinate temporal gauge pricing for a frozen scalar word."""

from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dyadic_parts(value):
    value = Fraction(value)
    numerator, denominator = abs(value.numerator), value.denominator
    need(numerator > 0 and denominator & (denominator - 1) == 0,
         "coefficient must be a nonzero dyadic")
    trailing = (numerator & -numerator).bit_length() - 1
    return numerator >> trailing, trailing - (denominator.bit_length() - 1)


def add_price(value):
    odd, exponent = dyadic_parts(value)
    return 1 + odd.bit_length() + odd.bit_count() + abs(exponent) - int(odd == 1 and exponent == 0)


def two_power(exponent):
    return Fraction(2 ** exponent, 1) if exponent >= 0 else Fraction(1, 2 ** -exponent)


def incident_adds(events, helper):
    found = []
    for index, event in enumerate(events):
        if event[0] != "scalar" or event[1][0] != "add":
            continue
        op = event[1]
        sign = int(op[1] == ["L", helper]) - int(op[2] == ["L", helper])
        if sign:
            found.append((index, Fraction(op[3], op[4]), sign))
    need(bool(found), "eligible helper has no incident ADD")
    return found


def objective(terms, schedule):
    need(len(terms) == len(schedule), "complete schedule length")
    previous = 0
    result = 0
    for (_, coefficient, sign), exponent in zip(terms, schedule):
        result += abs(exponent - previous)
        result += add_price(coefficient * two_power(sign * exponent)) - add_price(coefficient)
        previous = exponent
    return result + abs(previous)


def optimize(terms):
    """Minimize over Z^m by exact DP and a proved finite interval clamp."""
    breakpoints = [0]
    for _, coefficient, sign in terms:
        _, exponent = dyadic_parts(coefficient)
        breakpoints.append(-sign * exponent)
    low, high = min(breakpoints), max(breakpoints)
    domain = range(low, high + 1)

    # State values include deterministic tie breakers after the exact cost.
    states = {0: (0, 0, 0, ())}
    edge_evaluations = 0
    for _, coefficient, sign in terms:
        following = {}
        for exponent in domain:
            add_delta = add_price(coefficient * two_power(sign * exponent)) - add_price(coefficient)
            choices = []
            for previous, value in states.items():
                edge_evaluations += 1
                choices.append((value[0] + abs(exponent - previous) + add_delta,
                                value[1] + int(exponent != previous),
                                value[2] + abs(exponent),
                                value[3] + (exponent,)))
            following[exponent] = min(choices)
        states = following

    complete = [(value[0] + abs(last), value[1] + int(last != 0), value[2], value[3])
                for last, value in states.items()]
    best = min(complete)
    constant = min((2 * abs(exponent) + sum(
        add_price(coefficient * two_power(sign * exponent)) - add_price(coefficient)
        for _, coefficient, sign in terms), int(exponent != 0), abs(exponent), exponent)
        for exponent in domain)

    schedule = tuple(best[3])
    need(objective(terms, schedule) == best[0], "DP receipt recomputes")
    return {
        "domain": [low, high],
        "domain_size": high - low + 1,
        "incident_adds": len(terms),
        "edge_evaluations": edge_evaluations,
        "delta_real": best[0],
        "transition_scale_macros": best[1],
        "schedule_l1": best[2],
        "constant_delta_real": constant[0],
        "constant_exponent": constant[3],
        "schedule": schedule,
    }


def transform(events, helper, indexed_schedule):
    """Insert every gauge transition and conjugate each incident ADD exactly."""
    terms = incident_adds(events, helper)
    indices = [index for index, _, _ in terms]
    need([index for index, _ in indexed_schedule] == indices,
         "schedule covers every chronological incident ADD exactly once")
    need(all(type(exponent) is int for _, exponent in indexed_schedule), "integer exponents")
    need(events[-1] == ["phase", "done"], "word has terminal cleanup boundary")

    exponent_at = dict(indexed_schedule)
    result, previous = [], 0
    inserted = []
    for index, source_event in enumerate(events):
        event = [source_event[0], list(source_event[1]), *source_event[2:]] if source_event[0] == "scalar" else list(source_event)
        if index in exponent_at:
            current = exponent_at[index]
            if current != previous:
                change = current - previous
                scale = two_power(change)
                pulse = ["scalar", ["scale", ["L", helper], scale.numerator, scale.denominator], event[2]]
                output_index = len(result)
                result.append(pulse)
                inserted.append([index, change, event[2], output_index])
            op = event[1]
            sign = int(op[1] == ["L", helper]) - int(op[2] == ["L", helper])
            coefficient = Fraction(op[3], op[4]) * two_power(sign * current)
            op[3], op[4] = coefficient.numerator, coefficient.denominator
            previous = current
        if index == len(events) - 1 and previous:
            scale = two_power(-previous)
            pulse = ["scalar", ["scale", ["L", helper], scale.numerator, scale.denominator], 1]
            output_index = len(result)
            result.append(pulse)
            inserted.append([index, -previous, 1, output_index])
        result.append(event)
    return result, inserted


def exhaustive(terms, low, high):
    """Tiny independent control used to compare the DP with direct enumeration."""
    import itertools
    return min(objective(terms, schedule)
               for schedule in itertools.product(range(low, high + 1), repeat=len(terms)))
