"""Standalone rational and integer-grid interpreters for finite evidence.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction as Q

from guard import need, validate


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def multiply(left, right):
    columns = transpose(right)
    return [[sum((a * b for a, b in zip(row, column)), Q(0))
             for column in columns] for row in left]


def inverse(matrix):
    size = len(matrix)
    need(1 <= size <= 16, "inverse capacity")
    rows = [list(map(Q, row)) + [Q(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((i for i in range(column, size) if rows[i][column]), None)
        need(pivot is not None, "singular matrix")
        rows[pivot], rows[column] = rows[column], rows[pivot]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for i in range(size):
            if i != column:
                scale = rows[i][column]
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[column])]
    return [row[size:] for row in rows]


def cayley(word, labels, parameter):
    size = len(word) + 1
    need(1 <= size <= 16 and 1 <= labels <= 3, "matrix fixture capacity")
    need(all(type(label) is int and 0 <= label < labels for label in word), "path labels")
    result = []
    for label in range(labels):
        skew = [[Q(0) for _ in range(size)] for _ in range(size)]
        for i, edge in enumerate(word):
            if edge == label:
                skew[i][i + 1], skew[i + 1][i] = Q(1), Q(-1)
        minus = [[Q(i == j) - parameter * skew[i][j] / 2
                  for j in range(size)] for i in range(size)]
        plus = [[Q(i == j) + parameter * skew[i][j] / 2
                 for j in range(size)] for i in range(size)]
        result.append(multiply(inverse(minus), plus))
    return result


def check_matrices(matrices, dimension):
    need(1 <= len(matrices) <= 3, "matrix count")
    identity = [[Q(i == j) for j in range(dimension)] for i in range(dimension)]
    for matrix in matrices:
        need(len(matrix) == dimension and all(len(row) == dimension for row in matrix),
             "matrix shape")
        need(multiply(transpose(matrix), matrix) == identity, "orthogonal matrices required")


def exact_trace(side, matrices, initial):
    values = [list(map(Q, row)) for row in initial]
    trace = []
    for step in side:
        if step.op == "linear":
            new = [sum((Q(c) * values[src][j] for src, c in step.terms), Q(0))
                   for j in range(len(values[0]))]
        else:
            matrix = matrices[step.label]
            if step.direction == -1:
                matrix = transpose(matrix)
            source = values[step.dst if step.op == "apply" else step.src]
            new = [sum((a * b for a, b in zip(row, source)), Q(0)) for row in matrix]
            if step.op == "query":
                new = [old + Q(step.coefficient) * value
                       for old, value in zip(values[step.dst], new)]
        values[step.dst] = new
        trace.append([row[:] for row in values])
    return trace


def trunc(value):
    value = Q(value)
    return value.numerator // value.denominator if value >= 0 else -((-value.numerator) // value.denominator)


def rounded_trace(side, matrices, initial, bits, wrong_inverse=False):
    scale = 1 << bits
    tables = [[[trunc(scale * value) for value in row] for row in matrix]
              for matrix in matrices]
    need(all(Q(value * scale).denominator == 1 for row in initial for value in row),
         "input is not on the working grid")
    values = [[int(value * scale) for value in row] for row in initial]
    trace = []
    for step in side:
        if step.op == "linear":
            new = [trunc(sum((Q(c) * values[src][j] for src, c in step.terms), Q(0)))
                   for j in range(len(values[0]))]
        else:
            matrix = tables[step.label]
            if step.direction == -1 and not wrong_inverse:
                matrix = transpose(matrix)
            source = values[step.dst if step.op == "apply" else step.src]
            dots = [sum(a * b for a, b in zip(row, source)) for row in matrix]
            if step.op == "apply":
                new = [trunc(Q(value, scale)) for value in dots]
            else:
                new = [trunc(old + Q(step.coefficient) * Q(value, scale))
                       for old, value in zip(values[step.dst], dots)]
        values[step.dst] = new
        trace.append([[Q(value, scale) for value in row] for row in values])
    return trace


def checked_traces(program, matrices, initial, bits):
    dimension, roles = len(initial[0]), len(initial)
    validate(program, dimension, roles, len(matrices))
    check_matrices(matrices, dimension)
    return tuple((exact_trace(side, matrices, initial),
                  rounded_trace(side, matrices, initial, bits)) for side in program)
