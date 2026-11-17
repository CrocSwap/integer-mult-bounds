"""Emit a rank-minimal common-query stream with minimum persistent cache.

The executable domain is at most 24 requests on 1..8 sources over one of
the listed prime fields. The accompanying proof has no such finite bounds.
"""

import argparse
import json
from pathlib import Path

PRIMES = (2, 3, 5, 7, 11)
MAX_DIMENSION = 8
MAX_REQUESTS = 24


def need(condition, message):
    if not condition:
        raise ValueError(message)


def validate(problem):
    need(type(problem) is dict, "problem must be an object")
    need(set(problem) == {"prime", "dimension", "rows"}, "unexpected keys")
    prime, dimension, rows = (problem[k] for k in ("prime", "dimension", "rows"))
    need(type(prime) is int and prime in PRIMES, "unsupported prime")
    need(type(dimension) is int and 1 <= dimension <= MAX_DIMENSION, "dimension")
    need(type(rows) is list and len(rows) <= MAX_REQUESTS, "request count")
    for row in rows:
        need(type(row) is list and len(row) == dimension, "row shape")
        need(all(type(x) is int and 0 <= x < prime for x in row), "coefficient")
    return prime, dimension, rows


def rref(rows, columns, prime):
    matrix = [list(row) for row in rows]
    pivots = []
    for column in range(columns):
        candidates = [i for i in range(len(pivots), len(matrix)) if matrix[i][column]]
        if not candidates:
            continue
        pivot = len(pivots)
        index = candidates[0]
        matrix[pivot], matrix[index] = matrix[index], matrix[pivot]
        scale = pow(matrix[pivot][column], -1, prime)
        matrix[pivot] = [x * scale % prime for x in matrix[pivot]]
        for index in range(len(matrix)):
            if index != pivot:
                factor = matrix[index][column]
                matrix[index] = [(a - factor * b) % prime
                                 for a, b in zip(matrix[index], matrix[pivot])]
        pivots.append(column)
    return matrix, pivots


def basis(rows, dimension, prime):
    matrix, pivots = rref(rows, dimension, prime)
    return matrix[:len(pivots)]


def kernel(rows, columns, prime):
    matrix, pivots = rref(rows, columns, prime)
    result = []
    for free in range(columns):
        if free not in pivots:
            vector = [0] * columns
            vector[free] = 1
            for index, pivot in enumerate(pivots):
                vector[pivot] = -matrix[index][free] % prime
            result.append(vector)
    return result


def combination(coefficients, rows, dimension, prime):
    return [sum(c * row[j] for c, row in zip(coefficients, rows)) % prime
            for j in range(dimension)]


def intersection(left, right, dimension, prime):
    equations = [[row[j] for row in left] + [-row[j] % prime for row in right]
                 for j in range(dimension)]
    relations = kernel(equations, len(left) + len(right), prime)
    rows = [combination(v[:len(left)], left, dimension, prime) for v in relations]
    return basis(rows, dimension, prime)


def coordinates(row, spanning, dimension, prime):
    columns = len(spanning)
    equations = [[v[j] for v in spanning] + [row[j]] for j in range(dimension)]
    reduced, pivots = rref(equations, columns, prime)
    need(all(any(line[:columns]) or line[-1] == 0 for line in reduced),
         "row is outside the supplied span")
    result = [0] * columns
    for index, pivot in enumerate(pivots):
        result[pivot] = reduced[index][-1]
    need(combination(result, spanning, dimension, prime) == row, "coordinate residual")
    return result


def inverse_row_operation(operation, prime):
    kind, *args = operation
    if kind == "scale":
        return [kind, args[0], pow(args[1], -1, prime)]
    if kind == "add":
        return [kind, args[0], args[1], -args[2] % prime]
    need(kind == "swap", "noninvertible reduction operation")
    return operation[:]


def matrix_program(target, prime):
    """Factor T=L^-1 diag(I_r,0) R^-1 into in-place row instructions."""
    size = len(target)
    matrix = [row[:] for row in target]
    left, right = [], []
    rank = 0
    for pivot in range(size):
        candidates = [(i, j) for i in range(pivot, size)
                      for j in range(pivot, size) if matrix[i][j]]
        if not candidates:
            break
        i, j = candidates[0]
        matrix[pivot], matrix[i] = matrix[i], matrix[pivot]
        left.append(["swap", pivot, i])
        for row in matrix:
            row[pivot], row[j] = row[j], row[pivot]
        right.append(["swap", pivot, j])
        factor = pow(matrix[pivot][pivot], -1, prime)
        matrix[pivot] = [x * factor % prime for x in matrix[pivot]]
        left.append(["scale", pivot, factor])
        for i in range(size):
            if i != pivot and matrix[i][pivot]:
                factor = -matrix[i][pivot] % prime
                matrix[i] = [(a + factor * b) % prime
                             for a, b in zip(matrix[i], matrix[pivot])]
                left.append(["add", i, pivot, factor])
        for j in range(size):
            if j != pivot and matrix[pivot][j]:
                factor = -matrix[pivot][j] % prime
                for i in range(size):
                    matrix[i][j] = (matrix[i][j] + factor * matrix[i][pivot]) % prime
                right.append(["add", pivot, j, -factor % prime])
        rank += 1
    diagonal = [[int(i == j and i < rank) for j in range(size)] for i in range(size)]
    need(matrix == diagonal, "two-sided reduction residual")
    return right + [["clear", i] for i in range(rank, size)] + [
        inverse_row_operation(op, prime) for op in reversed(left)]


def cut_spaces(rows, dimension, prime):
    cuts = []
    for index in range(len(rows) + 1):
        past = basis(rows[:index], dimension, prime)
        future = basis(rows[index:], dimension, prime)
        shared = intersection(past, future, dimension, prime)
        cuts.append({"past_rank": len(past), "future_rank": len(future),
                     "basis": shared})
    return cuts


def transition(old, new, request, cache_width, dimension, prime):
    size = cache_width + 1
    matrix = [[0] * size for _ in range(size)]
    for i, row in enumerate(new):
        coeff = coordinates(row, old + [request], dimension, prime)
        matrix[i][:len(old)] = coeff[:-1]
        matrix[i][-1] = coeff[-1]
    matrix[-1][-1] = 1
    return matrix_program(matrix, prime)


def compile_stream(problem):
    prime, dimension, rows = validate(problem)
    cuts = cut_spaces(rows, dimension, prime)
    rank = cuts[-1]["past_rank"]
    width = max(len(cut["basis"]) for cut in cuts)
    stages = []
    for index, request in enumerate(rows):
        old, new = cuts[index]["basis"], cuts[index + 1]["basis"]
        acquire = cuts[index + 1]["past_rank"] > cuts[index]["past_rank"]
        prepare = []
        if not acquire:
            coeff = coordinates(request, old, dimension, prime)
            prepare = [["add", width, j, value] for j, value in enumerate(coeff) if value]
        stages.append({"acquire": acquire, "prepare": prepare,
                       "transition": transition(old, new, request, width, dimension, prime)})
    need(sum(stage["acquire"] for stage in stages) == rank, "acquisition count")
    need(all(len(cut["basis"]) == cut["past_rank"] + cut["future_rank"] - rank
             for cut in cuts), "cut dimension identity")
    return {"schema": "causal-query-cache-stock/1", "problem": problem,
            "queries": rank, "cache_width": width, "bank_fields": width + 1,
            "initial_clear": list(range(width + 1)), "cuts": cuts, "stages": stages}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    args = parser.parse_args()
    need(args.problem.stat().st_size <= 65536, "problem exceeds 64 KiB")
    problem = json.loads(args.problem.read_text())
    print(json.dumps(compile_stream(problem), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
