"""Real cyclic inverses stabilized by one dirty scalar.

Integer-grid reference: exact rational coefficients, nearest rounding with
ties away from zero, no fixed-tape or fast coefficient-preparation claim.
"""
from fractions import Fraction


def need(condition, message):
    if not condition:
        raise ValueError(message)


def nearest(value):
    """Round a rational to an integer; odd under sign reversal."""
    value = Fraction(value)
    numerator, denominator = value.numerator, value.denominator
    sign = -1 if numerator < 0 else 1
    return sign * ((2 * abs(numerator) + denominator) // (2 * denominator))


def factor_word(coefficients, direction=1):
    """Return shears for diag((I-C)^-1, det(I-C)), C_ij=b_i[i-j=d]."""
    need(type(direction) is int and direction in (-1, 1), "direction")
    need(len(coefficients) > 0, "nonempty cyclic factor")
    need(all(type(b) in (int, Fraction) for b in coefficients), "rational coefficients")
    coefficients = tuple(Fraction(b) for b in coefficients)
    need(all(abs(b) <= Fraction(1, 2) for b in coefficients), "half-stable coefficients")
    length = len(coefficients)
    order = tuple(range(length)) if direction == 1 else tuple(range(length - 1, -1, -1))
    prefixes = []
    product = Fraction(1)
    for index in order:
        product *= coefficients[index]
        prefixes.append(product)
    delta = 1 - product
    scale = 1 / delta
    pivot, helper = order[-1], length
    word = [(order[j], order[j - 1], coefficients[order[j]]) for j in range(1, length)]
    # Chronological L(-t), U(delta-1), L(1), U(t-1) scales the pair by (t,delta).
    word.extend(((helper, pivot, -scale), (pivot, helper, delta - 1),
                 (helper, pivot, Fraction(1)), (pivot, helper, scale - 1)))
    word.extend((index, pivot, prefix) for index, prefix in zip(order[:-1], prefixes[:-1]))
    return tuple(word)


def compile_factors(factors):
    need(len(factors) > 0, "nonempty ordered product")
    words = tuple(factor_word(coefficients, direction) for coefficients, direction in factors)
    length = len(factors[0][0])
    need(all(len(coefficients) == length for coefficients, _ in factors), "common length")
    return words


def run_word(data, helper, word, inverse=False):
    """Mutate borrowed storage directly, using no copied payload array."""
    length = len(data)
    sequence = reversed(word) if inverse else iter(word)
    sign = -1 if inverse else 1
    for destination, source, coefficient in sequence:
        value = helper[0] if source == length else data[source]
        increment = sign * nearest(coefficient * value)
        if destination == length:
            helper[0] += increment
        else:
            data[destination] += increment


def run_pipeline(data, helper, words, inverse=False):
    for word in reversed(words) if inverse else words:
        run_word(data, helper, word, inverse)


def admit(source, target, data, helper, factors, sign):
    need(type(sign) is int and sign in (-1, 1), "sign")
    need(all(type(v) is list for v in (source, target, data, helper)), "list storage")
    need(len({id(v) for v in (source, target, data, helper)}) == 4, "distinct storage")
    length = len(source)
    need(length > 0 and len(target) == len(data) == length and len(helper) == 1, "storage lengths")
    need(all(type(x) is int for v in (source, target, data, helper) for x in v), "integer-grid data")
    words = compile_factors(factors)
    need(len(factors[0][0]) == length, "factor/storage length")
    return words


def add_product(source, target, data, helper, factors, sign=1):
    """Add sign*(F(data+source)-F(data)); restore data/helper/source exactly."""
    words = admit(source, target, data, helper, factors, sign)
    run_pipeline(data, helper, words)
    for j in range(len(data)):
        target[j] -= sign * data[j]
    run_pipeline(data, helper, words, inverse=True)
    for j in range(len(data)):
        data[j] += source[j]
    run_pipeline(data, helper, words)
    for j in range(len(data)):
        target[j] += sign * data[j]
    run_pipeline(data, helper, words, inverse=True)
    for j in range(len(data)):
        data[j] -= source[j]
    return {"factor_executions": 4 * len(words),
            "coordinate_updates": 4 * sum(map(len, words)) + 4 * len(data),
            "borrowed_array_words": len(data), "borrowed_scalar_words": 1}


def error_bound(factor_count):
    """Absolute increment error in grid units; exact-coefficient contract."""
    need(type(factor_count) is int and factor_count >= 1, "positive factor count")
    return 10 * ((1 << factor_count) - 1)
