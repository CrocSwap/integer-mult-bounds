"""Independent dense integer prefixes, inverse prefixes and subwords.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
"""
import hashlib
import json
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    columns = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, col)) for col in columns] for row in a]


def norm(a):
    return max(sum(map(abs, row)) for row in a)


def prefix_step(matrix, factor, op):
    source, target, _, sign = op
    need(source != target, "non-shear instruction")
    width = len(matrix)
    for i in range(2):
        matrix[2*target+i] = [matrix[2*target+i][j] + sign*sum(
            factor[i][k]*matrix[2*source+k][j] for k in range(2)) for j in range(width)]


def inverse_step(matrix, factor, op):
    # If P_new = S P, then P_new^-1 = P^-1 S^-1: update columns.
    source, target, _, sign = op
    for row in matrix:
        for j in range(2):
            row[2*source+j] -= sign*sum(row[2*target+k]*factor[k][j] for k in range(2))


def gauss_inverse(matrix):
    n = len(matrix)
    a = [[Q(v) for v in row]+[Q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next(i for i in range(col, n) if a[i][col])
        a[col], a[pivot] = a[pivot], a[col]
        value = a[col][col]
        a[col] = [x/value for x in a[col]]
        for i in range(n):
            if i != col:
                value = a[i][col]
                a[i] = [x-value*y for x, y in zip(a[i], a[col])]
    return [row[n:] for row in a]


def trace(factors, instructions, sign, arrays, bound):
    width = 2*arrays
    P, inverse = identity(width), identity(width)
    maximum, inverse_maximum = 1, 1
    stream = hashlib.sha256()
    positions = {0, len(instructions)//4, len(instructions)//2, 3*len(instructions)//4, len(instructions)}
    gauss_checks, matrices = 0, [identity(width)] if len(factors) <= 8 else []
    inverses = [identity(width)] if matrices else []
    for j, op in enumerate(instructions, 1):
        factor = factors[op[2]]
        prefix_step(P, factor, op)
        inverse_step(inverse, factor, op)
        np, ni = norm(P), norm(inverse)
        need(np <= bound and ni <= bound, "prefix norm bound")
        maximum, inverse_maximum = max(maximum, np), max(inverse_maximum, ni)
        stream.update(json.dumps([j, np, ni], separators=(',', ':')).encode()+b'\n')
        if j in positions:
            need(gauss_inverse(P) == inverse, "independent inverse-prefix mismatch")
            gauss_checks += 1
        if matrices:
            matrices.append([row[:] for row in P])
            inverses.append([row[:] for row in inverse])
    product = identity(2)
    for factor in factors:
        product = multiply(factor, product)
    endpoint = identity(width)
    for i in range(2):
        for j in range(2):
            endpoint[2+i][j] = sign*product[i][j]
    need(P == endpoint, "ideal product or dirty restoration mismatch")
    need(multiply(P, inverse) == identity(width), "final inverse mismatch")
    subwords, subword_maximum = 0, 1
    if matrices:
        for first in range(len(instructions)):
            direct = identity(width)
            for last in range(first+1, len(instructions)+1):
                op = instructions[last-1]
                prefix_step(direct, factors[op[2]], op)
                need(direct == multiply(matrices[last], inverses[first]), "propagator identity")
                value = norm(direct)
                need(value <= bound*bound, "subword norm bound")
                subword_maximum = max(subword_maximum, value)
                subwords += 1
    return dict(leaf_calls=len(instructions), prefix_maximum=maximum,
                inverse_prefix_maximum=inverse_maximum, prefix_stream_sha256=stream.hexdigest(),
                gaussian_inverse_checks=gauss_checks, subwords_checked=subwords,
                subword_maximum=subword_maximum, all_columns_and_dirty_restoration=True)


def vendor_word(vendor, n, sign):
    """Observe the immutable predecessor dispatcher with its leaf replaced by a recorder."""
    arrays = [[vendor.c.ZERO] for _ in range(2+(n-1).bit_length())]
    ids = {id(a): i for i, a in enumerate(arrays)}
    result = []

    def record(x, y, factor, phases, beta, bits, direction, q, stats):
        result.append((ids[id(x)], ids[id(y)], factor, q))

    saved = vendor.leaf
    try:
        vendor.leaf = record
        vendor.compose(*arrays[:2], list(range(n)), arrays[2:], [vendor.c.ONE], Q(1, 2), 8, 1, sign)
    finally:
        vendor.leaf = saved
    return result
