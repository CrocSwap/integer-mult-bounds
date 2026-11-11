"""Bounded exact Gaussian-rational arithmetic for the coefficient construction."""
from fractions import Fraction as Q
from math import gcd, isqrt, lcm

C = tuple[Q, Q]
V = tuple[C, ...]
M = tuple[V, ...]
ZERO: C = (Q(0), Q(0))
ONE: C = (Q(1), Q(0))
MAX_DIM = 8
MAX_HEIGHT = 256
MAX_SQUARE_SUM = 65536


def add(a: C, b: C) -> C:
    return a[0] + b[0], a[1] + b[1]


def neg(a: C) -> C:
    return -a[0], -a[1]


def mul(a: C, b: C) -> C:
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def conj(a: C) -> C:
    return a[0], -a[1]


def scale(a: C, q: Q) -> C:
    return a[0]*q, a[1]*q


def total(values) -> C:
    result = ZERO
    for value in values:
        result = add(result, value)
    return result


def dot(a: V, b: V) -> C:
    assert len(a) == len(b) <= MAX_DIM
    return total(mul(conj(x), y) for x, y in zip(a, b))


def norm2(v: V) -> Q:
    value = dot(v, v)
    assert value[1] == 0 and value[0] >= 0
    return value[0]


def adj(a: M) -> M:
    return tuple(tuple(conj(x) for x in col) for col in zip(*a))


def product(a: M, b: M) -> M:
    assert a and b and len(a[0]) == len(b)
    assert max(len(a), len(b), len(b[0])) <= 2*MAX_DIM
    return tuple(tuple(total(mul(x, y) for x, y in zip(row, col))
                       for col in zip(*b)) for row in a)


def outer(v: V) -> M:
    return tuple(tuple(mul(x, conj(y)) for y in v) for x in v)


def matrix_sum(a: M, b: M) -> M:
    assert len(a) == len(b) and len(a[0]) == len(b[0])
    return tuple(tuple(add(x, y) for x, y in zip(r, s)) for r, s in zip(a, b))


def zero_matrix(rows: int, cols: int) -> M:
    assert 1 <= rows <= 2*MAX_DIM and 1 <= cols <= 2*MAX_DIM
    return tuple(tuple(ZERO for _ in range(cols)) for _ in range(rows))


def validate(a: M) -> None:
    if not isinstance(a, tuple) or not 1 <= len(a) <= MAX_DIM:
        raise ValueError("matrix row capacity")
    if not isinstance(a[0], tuple) or not 1 <= len(a[0]) <= MAX_DIM:
        raise ValueError("matrix column capacity")
    for row in a:
        if not isinstance(row, tuple) or len(row) != len(a[0]):
            raise ValueError("ragged matrix")
        for value in row:
            if not isinstance(value, tuple) or len(value) != 2:
                raise ValueError("Gaussian-rational entry required")
            for part in value:
                if type(part) is not Q:
                    raise ValueError("exact Fraction components required")
                if max(abs(part.numerator).bit_length(), part.denominator.bit_length()) > MAX_HEIGHT:
                    raise ValueError("input height capacity")


def square_pairs(n: int) -> tuple[int, int, int, int]:
    """Two-square representations are preferred, then a bounded four-square search."""
    if type(n) is not int or not 1 <= n <= MAX_SQUARE_SUM:
        raise ValueError("primitive squared-norm capacity")
    pairs = [None]*(n+1)
    for x in range(isqrt(n)+1):
        for y in range(isqrt(n-x*x)+1):
            pairs[x*x+y*y] = (x, y)
    if pairs[n] is not None:
        x, y = pairs[n]
        return x, y, 0, 0
    for k in range(n+1):
        if pairs[k] is not None and pairs[n-k] is not None:
            x, y = pairs[k]
            z, t = pairs[n-k]
            assert x*x+y*y+z*z+t*t == n
            return x, y, z, t
    raise ArithmeticError("four-square exhaustion contradicts Lagrange")


def split_norm(v: V) -> tuple[C, C]:
    """Represent ||v|| squared as two Gaussian-rational squared norms."""
    assert 1 <= len(v) <= MAX_DIM and norm2(v) > 0
    denominator = lcm(*(q.denominator for x in v for q in x))
    integers = tuple(int(q*denominator) for x in v for q in x)
    divisor = gcd(*integers)
    primitive = tuple(x//divisor for x in integers)
    n = sum(x*x for x in primitive)
    a, b, c, d = square_pairs(n)
    factor = Q(divisor, denominator)
    result = ((factor*a, factor*b), (factor*c, factor*d))
    assert sum(norm2((z,)) for z in result) == norm2(v)
    return result


def residuals(a: M) -> tuple[V, ...]:
    validate(a)
    accepted = []
    for column in zip(*a):
        v = tuple(column)
        for previous in accepted:
            coefficient = scale(dot(previous, v), 1/norm2(previous))
            v = tuple(add(x, neg(mul(coefficient, y))) for x, y in zip(v, previous))
        if norm2(v):
            assert all(dot(old, v) == ZERO for old in accepted)
            accepted.append(v)
    return tuple(accepted)


def construct(a: M) -> tuple[tuple[V, ...], tuple[V, ...], tuple[V, ...]]:
    basis = residuals(a)
    columns = []
    rows = []
    for v in basis:
        for z in split_norm(v):
            if z != ZERO:
                g = tuple(scale(mul(x, z), 1/norm2(v)) for x in v)
                row = tuple(dot(g, tuple(col)) for col in zip(*a))
                assert 0 < norm2(g) <= 1
                columns.append(g)
                rows.append(row)
    assert len(basis) <= len(columns) <= 2*len(basis)
    return tuple(columns), tuple(rows), basis
