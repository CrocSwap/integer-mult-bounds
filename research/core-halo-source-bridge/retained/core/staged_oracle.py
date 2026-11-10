"""Independent exact rational interpreter for retained staged sparse semantics.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
This interpreter never calls a producer's page builder or rounded observer and
never supplies a physical payload. Quantized diagonal blocks are recomputed by
independent pivoted inversion. All truncations are toward zero at their actual
stage boundaries, including the forward lift's coefficient pre-rounding.
"""
from fractions import Fraction as Q
from independent_numerics import ceil_div, inverse, multiply, need


def quantize(value, precision):
    value = Q(value)
    numerator = (abs(value.numerator) << precision) // value.denominator
    return Q(-numerator if value < 0 else numerator, 1 << precision)


def padded(matrix, block):
    n, extent = len(matrix), ceil_div(len(matrix), block) * block
    return tuple(tuple(matrix[i][j] if i < n and j < n else Q(i == j)
                       for j in range(extent)) for i in range(extent))


def one_pass(matrix, rhs, block, precision):
    n = len(matrix)
    need(n == len(rhs) and n % block == 0, "whole physical row blocks")
    need(all(not matrix[i][j] or i // block - 1 <= j // block <= i // block
             for i in range(n) for j in range(n)), "actual lower bidiagonal block support")
    returned = []
    for start in range(0, n, block):
        rows = range(start, start + block)
        diagonal = inverse(tuple(tuple(matrix[i][j] for j in rows) for i in rows))
        diagonal = tuple(tuple(quantize(value, precision) for value in row) for row in diagonal)
        residual = tuple(tuple(rhs[i]) for i in rows)
        if start:
            preceding = tuple(tuple(quantize(matrix[i][j], precision)
                                    for j in range(start - block, start)) for i in rows)
            term = multiply(preceding, tuple(returned[-block:]))
            residual = tuple(tuple(quantize(x - y, precision) for x, y in zip(row, product))
                             for row, product in zip(residual, term))
        returned.extend(tuple(quantize(value, precision) for value in row)
                        for row in multiply(diagonal, residual))
    return tuple(returned)


def solve(lower, upper, rhs, block, precision):
    n = len(lower)
    need(len(upper) == len(rhs) == n and n > 0, "nonempty exact staged solve")
    columns = len(rhs[0])
    need(all(len(row) == columns and all((Q(x) * (1 << precision)).denominator == 1 for x in row)
             for row in rhs), "all current rows on the common grid")
    extent = ceil_div(n, block) * block
    first = one_pass(padded(lower, block), tuple(tuple(row) for row in rhs)
                     + ((Q(),) * columns,) * (extent - n), block, precision)
    reversed_upper = tuple(tuple(reversed(row)) for row in reversed(padded(upper, block)))
    second = one_pass(reversed_upper, tuple(reversed(first)), block, precision)
    return tuple(reversed(second))[:n]


def first_inverse(window, rhs):
    current = list(solve(window.shear_lower, window.shear_upper, rhs,
                         window.block, window.precision))
    js = tuple(i for i, value in enumerate(window.j_mask) if value)
    solved = solve(window.f_lower, window.f_upper, tuple(current[i] for i in js),
                   window.block, window.precision)
    for index, value in zip(js, solved):
        current[index] = value
    return tuple(current)


def supplied_action(matrix, rhs, block, precision):
    size, columns = len(matrix), len(rhs[0])
    need(size == len(rhs) and size > 0, "complete supplied E action")
    need(all(not x or abs(2 * i - (2 * j + 1)) <= block
             for i, row in enumerate(matrix) for j, x in enumerate(row)),
         "actual unrounded interleaved lift support")
    rounded = tuple(tuple(quantize(x, precision) for x in row) for row in matrix)
    extent = 2 * size
    nilpotent = tuple(tuple(-rounded[i // 2][j // 2] if i % 2 == 0 and j % 2 == 1 else Q()
                           for j in range(extent)) for i in range(extent))
    lower = tuple(tuple(Q(i == j) + (nilpotent[i][j] if i // block > j // block else Q())
                        for j in range(extent)) for i in range(extent))
    upper = tuple(tuple(Q(i == j) + (nilpotent[i][j] if i // block <= j // block else Q())
                        for j in range(extent)) for i in range(extent))
    lifted = tuple(row for value in rhs for row in ((Q(),) * columns, tuple(value)))
    result = solve(lower, upper, lifted, block, precision)
    need(tuple(result[2 * i + 1] for i in range(size)) == tuple(tuple(row) for row in rhs),
         "staged forward lift preserves source rows exactly")
    return tuple(result[2 * i] for i in range(size))
