"""Independent integer-grid execution of PR628's stated dirty shear schedule.

Data values are pairs of integers in units of 2**-bits. Coefficients remain
exact rational pairs. No producer module or arithmetic helper is imported.
The instruction word is compiled first, then inverted as a flat word.
"""
from fractions import Fraction


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def minus(a, b):
    return a[0] - b[0], a[1] - b[1]


def product(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def conjugate(z):
    return z[0], -z[1]


def nearest(q):
    """Round to an integer, with an exact half rounded toward +infinity."""
    q = Fraction(q)
    quotient, remainder = divmod(q.numerator, q.denominator)
    return quotient + (2 * remainder >= q.denominator)


def rounded_product(coefficient, value):
    return tuple(nearest(q) for q in product(coefficient, value))


def word(factors, source=0, target=1, depth=0):
    """Expand the positive word into (source, target, factor, sign) leaves."""
    if len(factors) == 1:
        return [(source, target, factors[0], 1)]
    middle = len(factors) // 2
    scratch = depth + 2
    b = word(factors[:middle], source, scratch, depth + 1)
    a = word(factors[middle:], scratch, target, depth + 1)
    return b + a + inverse(b) + inverse(a)


def inverse(instructions):
    return [(src, dst, factor, -sign) for src, dst, factor, sign in reversed(instructions)]


def execute_leaf(arrays, instruction, phases, bits, direction):
    src, dst, (inside, b, scale), sign = instruction
    x, y = arrays[src], arrays[dst]
    length, grid = len(x), 1 << bits
    step = -direction if inside else direction
    order = list(range(length))[::step]
    coefficients = [product(b, conjugate(phases[(i + direction) % length]) if inside else phases[i])
                    for i in range(length)]
    power = (grid, 0)
    for position, i in enumerate(order):
        if position:
            x[i] = plus(x[i], rounded_product(coefficients[i], x[order[position - 1]]))
        power = rounded_product(coefficients[i], power)
    denominator = (grid - power[0], -power[1])
    norm = denominator[0] ** 2 + denominator[1] ** 2
    numerator = product(x[order[-1]], conjugate(denominator))
    seed = tuple(nearest(Fraction(v * grid, norm)) for v in numerator)
    power = (grid, 0)
    for i in order:
        power = rounded_product(coefficients[i], power)
        correction = tuple(Fraction(v, grid) for v in power)
        value = plus(x[i], rounded_product(correction, seed))
        multiplier = conjugate(phases[i]) if inside else (-b[0], -b[1])
        multiplier = tuple(v * scale for v in multiplier)
        increment = rounded_product(multiplier, value)
        destination = (i - direction) % length if inside else i
        y[destination] = plus(y[destination], tuple(sign * v for v in increment))
    for position in range(length - 1, 0, -1):
        i, previous = order[position], order[position - 1]
        x[i] = minus(x[i], rounded_product(coefficients[i], x[previous]))


def execute(arrays, factors, phases, bits, direction, sign):
    instructions = word(factors)
    if sign == -1:
        instructions = inverse(instructions)
    for instruction in instructions:
        execute_leaf(arrays, instruction, phases, bits, direction)
    return len(instructions)
