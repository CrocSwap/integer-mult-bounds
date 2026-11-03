"""Approximate dyadic channels with exact dirty restoration. Apache-2.0."""

from fractions import Fraction as Q
from itertools import combinations

MAX_DIM = 4
MAX_BITS = 64


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum((x * y for x, y in zip(row, col)), Q(0))
             for col in zip(*b)] for row in a]


def infinity_norm(a):
    return max(sum(map(abs, row), Q(0)) for row in a)


def inverse(a):
    n = len(a)
    work = [list(row) + unit for row, unit in zip(a, identity(n))]
    for col in range(n):
        pivot = next((i for i in range(col, n) if work[i][col]), None)
        if pivot is None:
            return None
        work[col], work[pivot] = work[pivot], work[col]
        scale = work[col][col]
        work[col] = [x / scale for x in work[col]]
        for row in range(n):
            if row != col:
                scale = work[row][col]
                work[row] = [x - scale * y
                             for x, y in zip(work[row], work[col])]
    result = [row[n:] for row in work]
    need(multiply(a, result) == identity(n), "inverse invariant")
    return result


def validate_cut(cut):
    need(isinstance(cut, (list, tuple)) and 1 <= len(cut) <= MAX_DIM,
         "cut row limit")
    need(all(isinstance(row, (list, tuple)) for row in cut), "cut rows")
    width = len(cut[0])
    need(len(cut) <= width <= MAX_DIM, "cut column limit")
    need(all(len(row) == width for row in cut), "rectangular cut")
    for row in cut:
        for value in row:
            need(type(value) in (int, Q), "exact cut coefficient")
            q = Q(value)
            need(q.denominator & (q.denominator - 1) == 0,
                 "dyadic cut coefficient")
            need(abs(q.numerator) <= 4096 and q.denominator <= 4096,
                 "cut coefficient limit")
    return [[Q(x) for x in row] for row in cut]


def right_inverse(cut):
    rows, cols = len(cut), len(cut[0])
    for selected in combinations(range(cols), rows):
        block = [[row[j] for j in selected] for row in cut]
        inv = inverse(block)
        if inv is not None:
            result = [[Q(0)] * rows for _ in range(cols)]
            for j, row in zip(selected, inv):
                result[j] = row
            need(multiply(cut, result) == identity(rows), "right inverse")
            return result
    raise ValueError("cut lacks full rational row rank")


def round_dyadic(value, bits):
    need(type(value) in (int, Q), "exact rounding input")
    need(type(bits) is int and 0 <= bits <= MAX_BITS, "rounding bit limit")
    scaled = Q(value) * (1 << bits)
    nearest = (2 * scaled.numerator + scaled.denominator) // (2 * scaled.denominator)
    return Q(nearest, 1 << bits)


def normalize(cut, epsilon):
    cut = validate_cut(cut)
    need(type(epsilon) in (int, Q), "exact error tolerance")
    epsilon = Q(epsilon)
    need(Q(1, 1 << 32) <= epsilon <= Q(1, 2), "error tolerance limit")
    right = right_inverse(cut)
    rows = len(cut)
    scale = rows * infinity_norm(cut)
    bits = next((b for b in range(MAX_BITS + 1)
                 if scale / (1 << (b + 1)) <= epsilon), None)
    need(bits is not None, "precision budget exhausted")
    rounded = [[round_dyadic(x, bits) for x in row] for row in right]
    response = multiply(cut, rounded)
    error = [[x - Q(i == j) for j, x in enumerate(row)]
             for i, row in enumerate(response)]
    bound = scale / (1 << (bits + 1))
    need(infinity_norm(error) <= bound <= epsilon, "normalization error")
    return {"cut": cut, "right": right, "rounded": rounded,
            "bits": bits, "response": response, "bound": bound}


def coefficient_word(dst, src, coefficient):
    """Restore src exactly; use only signed unit ADD and SCALE 2 or 1/2."""
    need(type(dst) is int and type(src) is int and 0 <= dst < 12
         and 0 <= src < 12 and dst != src, "distinct bounded shear roles")
    need(type(coefficient) in (int, Q), "exact shear coefficient")
    coefficient = Q(coefficient)
    denom = coefficient.denominator
    need(denom & (denom - 1) == 0, "dyadic shear coefficient")
    numerator = abs(coefficient.numerator)
    bits = denom.bit_length() - 1
    length = numerator.bit_length()
    need(bits <= MAX_BITS and length <= 160, "shear coefficient limit")
    if numerator == 0:
        return []
    sign = 1 if coefficient > 0 else -1
    word = [("scale", src, Q(1, 2)) for _ in range(bits)]
    for level in range(length):
        if numerator & (1 << level):
            word.append(("add", dst, src, sign))
        if level + 1 < length:
            word.append(("scale", src, Q(2)))
    balance = bits - length + 1
    factor = Q(2) if balance >= 0 else Q(1, 2)
    word.extend(("scale", src, factor) for _ in range(abs(balance)))
    expected = numerator.bit_count() + 2 * max(bits, length - 1)
    need(len(word) == expected, "coefficient word count")
    return word


def channel_word(cut, rounded):
    rows, cols = len(cut), len(cut[0])
    word = []
    for phase in range(4):
        matrix = rounded if phase % 2 == 0 else cut
        dst_start = rows if phase % 2 == 0 else rows + cols
        src_start = 0 if phase % 2 == 0 else rows
        sign = 1 if phase < 2 else -1
        for i, row in enumerate(matrix):
            for j, coefficient in enumerate(row):
                word.extend(coefficient_word(dst_start + i, src_start + j,
                                             sign * coefficient))
    return word


def execute(word, state):
    values = list(map(Q, state))
    for event in word:
        if event[0] == "scale":
            values[event[1]] *= event[2]
        else:
            _, dst, src, sign = event
            values[dst] += sign * values[src]
    return values
