"""Exact interface codec for a scoped refined native chain.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The literal matrix and one-step interface are credited to #5444/#5323.
No physical or reversible-machine implementation is claimed.
"""
from math import prod


MAX_DEPTH = 8
U = (((1, 1), (12, 1), (0, -1), (16, -1)), 2, 2)
V = (((0, 1), (8, 1), (2, -1), (6, -1)), 3, 2)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact_int(value):
    return type(value) is int


def nearest(numerator, denominator=52):
    """Nearest integer, with exact half ties away from zero."""
    require(exact_int(numerator) and exact_int(denominator)
            and denominator > 0, "invalid rounding operands")
    magnitude = (2 * abs(numerator) + denominator) // (2 * denominator)
    return magnitude if numerator >= 0 else -magnitude


def project(matrix, vector):
    require(len(vector) == len(matrix), "wrong vector dimension")
    return [sum(row[j] * value for row, value in zip(matrix, vector))
            for j in range(8)]


def lift(matrix, vector):
    require(len(vector) == 8, "wrong mode dimension")
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def kernel(matrix, vector):
    quotient = [nearest(value) for value in project(matrix, vector)]
    correction = lift(matrix, quotient)
    return [a - b for a, b in zip(vector, correction)]


def scalar_step(s, value):
    return value - nearest(s + 56 * value)


def quotient_interval(s):
    lower = -((26 + s) // 4)
    upper = (26 - s) // 4
    values = [q for q in range(lower, upper + 1)
              if nearest(s + 56 * q) == q]
    require(values and len(values) <= 13, "invalid scalar inverse interval")
    require(values == list(range(values[0], values[-1] + 1)),
            "nonconsecutive scalar inverse interval")
    return values[0], values[-1]


def total_interval(s, depth):
    require(exact_int(s) and exact_int(depth) and 1 <= depth <= MAX_DEPTH,
            "unsupported scalar interval")
    lower = upper = 0
    for _ in range(depth):
        low_q = quotient_interval(s + 56 * upper)
        high_q = quotient_interval(s + 56 * lower)
        lower, upper = upper + low_q[0], lower + high_q[1]
    return lower, upper


def validate_shear(matrix, shear):
    terms, source, coefficient = shear
    require(exact_int(source) and 0 <= source < len(matrix), "invalid source")
    require(exact_int(coefficient) and coefficient % 2 == 0,
            "frame must be identity modulo two")
    require(len(terms) <= len(matrix), "oversized shear")
    indices = [i for i, _ in terms]
    require(len(set(indices)) == len(indices), "duplicate shear coordinate")
    require(all(exact_int(i) and 0 <= i < len(matrix) and exact_int(v)
                for i, v in terms), "invalid shear terms")
    require(all(i != source or v == 0 for i, v in terms),
            "shear is not the declared unimodular transvection")
    require(all(sum(matrix[i][j] * v for i, v in terms) == 0
                for j in range(8)), "frame does not preserve native modes")


def apply_shear(vector, shear, inverse=False):
    terms, source, coefficient = shear
    result = list(vector)
    scale = coefficient * vector[source] * (-1 if inverse else 1)
    for index, value in terms:
        result[index] += scale * value
    return result


def validate_chain(matrix, depth, frames):
    require(exact_int(depth) and 1 <= depth <= MAX_DEPTH,
            "unsupported chain depth")
    require(len(frames) == depth - 1, "wrong number of frames")
    for shear in frames:
        validate_shear(matrix, shear)


def forward(matrix, vector, frames):
    depth = len(frames) + 1
    validate_chain(matrix, depth, frames)
    require(len(vector) == len(matrix) and all(map(exact_int, vector)),
            "input must be an exact integer vector")
    result = kernel(matrix, [2 * value for value in vector])
    for shear in frames:
        result = kernel(matrix, apply_shear(result, shear))
    return result


def parity_options(matrix, output):
    masks = [sum((value & 1) << j for j, value in enumerate(row))
             for row in matrix]
    return [mask for mask in range(256)
            if all((mask & row).bit_count() % 2 == (value & 1)
                   for row, value in zip(masks, output))]


def parity_interval(interval, parity):
    lower, upper = interval
    first = lower + ((parity - lower) & 1)
    return first, max(0, (upper - first) // 2 + 1)


def blocks(matrix, output, depth):
    require(len(output) == len(matrix) and all(map(exact_int, output)),
            "output must be an exact integer vector")
    intervals = [total_interval(s, depth) for s in project(matrix, output)]
    result = []
    for mask in parity_options(matrix, output):
        cells = [parity_interval(interval, (mask >> j) & 1)
                 for j, interval in enumerate(intervals)]
        count = prod(size for _, size in cells)
        if count:
            result.append((mask, cells, count))
    return result


def max_states(depth):
    require(exact_int(depth) and 1 <= depth <= MAX_DEPTH, "unsupported depth")
    length = 13 ** depth
    return (length ** 8 + 14 * length ** 4 + 1) // 16


def fiber_count(matrix, output, depth):
    return sum(count for _, _, count in blocks(matrix, output, depth))


def unrank_total(matrix, output, depth, tag):
    require(exact_int(tag) and tag >= 0, "invalid recovery tag")
    for _, cells, count in blocks(matrix, output, depth):
        if tag >= count:
            tag -= count
            continue
        total = [0] * 8
        for j in range(7, -1, -1):
            first, size = cells[j]
            tag, index = divmod(tag, size)
            total[j] = first + 2 * index
        require(tag == 0, "unconsumed recovery tag")
        return total
    raise ValueError("recovery tag exceeds the actual output fiber")


def rank_total(matrix, output, depth, total):
    offset = 0
    mask = sum((value & 1) << j for j, value in enumerate(total))
    for candidate, cells, count in blocks(matrix, output, depth):
        if candidate != mask:
            offset += count
            continue
        rank = 0
        for value, (first, size) in zip(total, cells):
            delta = value - first
            require(delta % 2 == 0 and 0 <= delta // 2 < size,
                    "total quotient outside its scalar interval")
            rank = rank * size + delta // 2
        return offset + rank
    raise ValueError("total quotient fails the output parity syndrome")


def decode(matrix, output, frames, tag):
    depth = len(frames) + 1
    validate_chain(matrix, depth, frames)
    total = unrank_total(matrix, output, depth, tag)
    s = project(matrix, output)
    states = [total]
    for _ in range(depth):
        states.append([scalar_step(a, b) for a, b in zip(s, states[-1])])
    require(states[-1] == [0] * 8, "scalar endpoint does not close")
    current = list(output)
    for i in range(depth - 1, -1, -1):
        q = [a - b for a, b in zip(states[i], states[i + 1])]
        current = [a + b for a, b in zip(current, lift(matrix, q))]
        if i:
            current = apply_shear(current, frames[i - 1], inverse=True)
    require(all(value % 2 == 0 for value in current), "input is not integral")
    result = [value // 2 for value in current]
    require(forward(matrix, result, frames) == list(output),
            "decoded input fails literal native replay")
    return result


def encode(matrix, vector, frames):
    output = forward(matrix, vector, frames)
    initial_modes = project(matrix, vector)
    final_modes = project(matrix, output)
    differences = [2 * a - b for a, b in zip(initial_modes, final_modes)]
    require(all(value % 56 == 0 for value in differences),
            "mode difference is not an integer quotient")
    total = [value // 56 for value in differences]
    tag = rank_total(matrix, output, len(frames) + 1, total)
    return output, tag
