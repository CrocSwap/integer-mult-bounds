"""Exact Gaussian-dyadic vectors; no predecessor implementation is imported.

Conventions follow the credited native Clifford sources in README.md.
Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from functools import lru_cache

DIM = 512


def need(ok, message):
    if not ok:
        raise ValueError(message)


def vector(real, imag=None, exponent=0):
    real = tuple(real)
    imag = tuple(imag) if imag is not None else (0,) * len(real)
    need(len(real) == len(imag) == DIM and exponent >= 0, "vector dimensions")
    if not any(real) and not any(imag):
        return ZERO
    while exponent and all(x % 2 == 0 for x in real + imag):
        real = tuple(x // 2 for x in real)
        imag = tuple(x // 2 for x in imag)
        exponent -= 1
    return real, imag, exponent


ZERO = ((0,) * DIM, (0,) * DIM, 0)
ONE = ((1,) * DIM, (0,) * DIM, 0)


def rotate(a, b, phase):
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            high = value.bit_length() - 1
            if high not in pivots:
                pivots[high] = value
                break
            value ^= pivots[high]
    return len(pivots)


def transpose(rows):
    return tuple(sum(((rows[j] >> i) & 1) << j for j in range(9)) for i in range(9))


def inverse(rows):
    aug = [x | (1 << (9 + i)) for i, x in enumerate(rows)]
    for i in range(9):
        pivot = next((j for j in range(i, 9) if (aug[j] >> i) & 1), None)
        need(pivot is not None, "invertible binary map")
        aug[i], aug[pivot] = aug[pivot], aug[i]
        for j in range(9):
            if j != i and (aug[j] >> i) & 1:
                aug[j] ^= aug[i]
    return tuple(x >> 9 for x in aug)


def monomial_key(record, axes=9):
    """Reduce identity spectators, checking every discarded coordinate."""
    need(set(record) == {"matrix_rows", "quadratic_rows", "linear_Z4", "offset", "phase"},
         "monomial schema")
    rows, quad, linear = (record[k] for k in ("matrix_rows", "quadratic_rows", "linear_Z4"))
    need(len(rows) == len(quad) == len(linear) == axes, "monomial axes")
    need(all(type(x) is int for x in rows + quad + linear), "integer monomial")
    need(all(0 <= x < 2**axes for x in rows + quad) and all(0 <= x < 4 for x in linear),
         "monomial coefficient range")
    need(0 <= record["offset"] < DIM and 0 <= record["phase"] < 4, "monomial constants")
    need(all(x < DIM for x in rows[:9] + quad[:9]), "no low/high coupling")
    need(rows[9:] == [1 << i for i in range(9, axes)]
         and not any(quad[9:] + linear[9:]), "identity spectators")
    need(rank(rows[:9]) == 9, "invertible monomial")
    return tuple(rows[:9]), tuple(quad[:9]), tuple(linear[:9]), record["offset"], record["phase"]


@lru_cache(256)
def table(key):
    rows, quad, linear, offset, phase = key
    result = []
    for x in range(DIM):
        dest = offset ^ sum(((x & row).bit_count() % 2) << i for i, row in enumerate(rows))
        angle = phase + sum(linear[i] for i in range(9) if (x >> i) & 1)
        # Old core stores symmetric Q; wrapper recipes store an upper triangle.
        # Both conventions read each strict-upper pair exactly once.
        angle += 2 * sum((quad[i] & x & ~((1 << (i + 1)) - 1)).bit_count()
                         for i in range(9) if (x >> i) & 1)
        result.append((dest, angle % 4))
    need(len({dest for dest, _ in result}) == DIM, "monomial permutation")
    return tuple(result)


def mono(value, key, adjoint=False):
    re, im, exponent = value
    rr, ii = [0] * DIM, [0] * DIM
    for x, (dest, angle) in enumerate(table(key)):
        if adjoint:
            rr[x], ii[x] = rotate(re[dest], im[dest], -angle)
        else:
            rr[dest], ii[dest] = rotate(re[x], im[x], angle)
    return vector(rr, ii, exponent)


def line(value, axis, sign=1, normalize=True):
    need(0 < axis < DIM and sign in (-1, 1), "line parameters")
    re, im, exponent = value
    rr, ii = [], []
    for x in range(DIM):
        a, b, c, d = re[x], im[x], re[x ^ axis], im[x ^ axis]
        rr.append(a - sign*b + c + sign*d)
        ii.append(b + sign*a + d - sign*c)
    return vector(rr, ii, exponent + int(normalize))


def recipe(value, record, axes=9):
    r = record["rank"]
    need(type(r) is int and 0 <= r <= 9, "child rank")
    if r:
        value = mono(value, monomial_key(record["right"], axes))
        for j in range(r):
            value = line(value, 1 << j)
    else:
        need(record["right"] is None, "rank-zero recipe")
    return mono(value, monomial_key(record["left"], axes))


def diagonal(value, quad, linear, sign=1):
    key = (tuple(1 << i for i in range(9)), tuple(quad),
           tuple((sign*x) % 4 for x in linear), 0, 0)
    return mono(value, key)


def permute(value, rows):
    return mono(value, (tuple(rows), (0,) * 9, (0,) * 9, 0, 0))


def frame(axes):
    """T_U applied to the constant vector, using the stored ordered basis."""
    r = len(axes)
    need(rank(axes) == r and all(0 < x < DIM for x in axes), "independent frame")
    if r in (0, 9):
        return ONE  # I and the full coordinate C-product both fix constants.
    ext = list(axes)
    for axis in (1 << i for i in range(9)):
        if rank(ext + [axis]) > len(ext):
            ext.append(axis)
    g = transpose(ext)
    gi = inverse(g)
    columns = transpose(gi)
    quad = tuple((1 << i) ^ sum(((columns[i] & columns[j]).bit_count() % 2) << j
                               for j in range(9)) for i in range(9))
    linear = tuple((quad[i] >> i) & 1 for i in range(9))
    # Circuit: K^-1, F_r, K; K is P(G) followed by D(Q).
    value = permute(diagonal(ONE, quad, linear, -1), gi)
    for j in range(r):
        value = line(value, 1 << j)
    value = diagonal(permute(value, g), quad, linear)
    need(sum(x*x for x in value[0] + value[1]) == DIM * 2**(2*value[2]),
         "frame preserves squared norm")
    return value


def scaled(value, coefficient):
    n, d = coefficient.numerator, coefficient.denominator
    need(d > 0 and d & (d-1) == 0, "dyadic coefficient")
    return vector((n*x for x in value[0]), (n*x for x in value[1]),
                  value[2] + d.bit_length()-1)


def plus(left, right):
    exponent = max(left[2], right[2])
    shifts = exponent-left[2], exponent-right[2]
    return vector(((a << shifts[0]) + (b << shifts[1]) for a, b in zip(left[0], right[0])),
                  ((a << shifts[0]) + (b << shifts[1]) for a, b in zip(left[1], right[1])),
                  exponent)
