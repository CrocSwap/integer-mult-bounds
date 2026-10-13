"""Exact integer rows with a common binary denominator.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
No Fraction or predecessor interpreter is used in this engine.
"""

from math import gcd


def need(ok, message):
    if not ok:
        raise ValueError(message)


def normalized(values, exponent):
    need(type(exponent) is int and exponent >= 0, "bad binary exponent")
    values = {k: n for k, n in values.items() if n}
    if not values:
        return {}, 0
    if exponent:
        removable = min(exponent, min((abs(n) & -abs(n)).bit_length()-1 for n in values.values()))
        if removable:
            values = {k: n >> removable for k, n in values.items()}
            exponent -= removable
    return values, exponent


def plus(left, right, sign=1):
    a, ea = left
    b, eb = right
    e = max(ea, eb)
    values = {k: n << (e-ea) for k, n in a.items()}
    for k, n in b.items():
        values[k] = values.get(k, 0) + sign*(n << (e-eb))
    return normalized(values, e)


def multiply(row, numerator, denominator):
    need(denominator != 0, "zero multiplier denominator")
    divisor = gcd(numerator, denominator)
    numerator, denominator = numerator // divisor, denominator // divisor
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    need(denominator > 0 and denominator & (denominator-1) == 0, "non-dyadic multiplier")
    values, e = row
    return normalized({k: numerator*n for k, n in values.items()}, e+denominator.bit_length()-1)


def primitive(step, state):
    tag, target = step[:2]
    row, e = state[target]
    if tag == "clear":
        state[target] = {}, 0
    elif tag == "copy":
        source, se = state[step[2]]
        state[target] = dict(source), se
    elif tag == "add" or tag == "subtract":
        state[target] = plus(state[target], state[step[2]], 1 if tag == "add" else -1)
    elif tag == "double":
        state[target] = normalized(row, e-1) if e else ({k: 2*n for k, n in row.items()}, 0)
    elif tag == "halve":
        state[target] = normalized(row, e+1)
    elif tag == "negate":
        state[target] = {k: -n for k, n in row.items()}, e
    else:
        raise ValueError("unknown primitive")
    return state[target][1]


def macro(op, state):
    tag, target = op[0], tuple(op[1])
    if tag == "clear":
        return {}, 0
    if tag == "copy":
        values, e = state[tuple(op[2])]
        return dict(values), e
    if tag == "scale":
        return multiply(state[target], op[2], op[3])
    need(tag == "add", "unknown macro")
    return plus(state[target], multiply(state[tuple(op[2])], op[3], op[4]))


def witness(row):
    values, exponent = row
    need(exponent > 0, "no fractional witness required")
    column = min(k for k, n in values.items() if n % 2)
    return {"input_column": column, "odd_numerator": values[column], "denominator_exponent": exponent}
