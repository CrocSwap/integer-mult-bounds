"""Construct exact minimum-width factors over dyadic Hamilton quaternions.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Hurwitz rounding and Euclidean reduction are classical. See CREDITS.md.
"""

from fractions import Fraction as F

ZERO = (F(0),) * 4
ONE = (F(1), F(0), F(0), F(0))


def add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def scale(a, q):
    return tuple(q*x for x in a)


def multiply(a, b):
    w, x, y, z = a
    t, u, v, r = b
    return (w*t-x*u-y*v-z*r, w*u+x*t+y*r-z*v,
            w*v-x*r+y*t+z*u, w*r+x*v-y*u+z*t)


def norm(a):
    return sum(x*x for x in a)


def inverse(a):
    n = norm(a)
    if not n:
        raise ValueError('zero quaternion inverse')
    return (a[0]/n, -a[1]/n, -a[2]/n, -a[3]/n)


def hurwitz(a):
    return all(x.denominator == 1 for x in a) or all(x.denominator == 2 for x in a)


def dyadic(a):
    return all(x.denominator & (x.denominator-1) == 0 for x in a)


def matrix(value, predicate):
    if (not isinstance(value, (list, tuple)) or not value
            or not isinstance(value[0], (list, tuple)) or not value[0]):
        raise ValueError('nonempty rectangular matrix required')
    width = len(value[0]); result = []
    for row in value:
        if not isinstance(row, (list, tuple)) or len(row) != width:
            raise ValueError('ragged matrix')
        new = []
        for entry in row:
            if (not isinstance(entry, (list, tuple)) or len(entry) != 4
                    or any(type(x) not in (int, F) for x in entry)):
                raise ValueError('four exact rational coordinates required')
            q = tuple(F(x) for x in entry)
            if not predicate(q):
                raise ValueError('coefficient outside the declared order')
            new.append(q)
        result.append(new)
    return result


def nearest_hurwitz(value):
    """Choose the nearer integer or uniform half-integer lattice point."""
    candidates = []
    for offset in (F(0), F(1, 2)):
        rounded = []
        for x in value:
            y = x-offset+F(1, 2)
            rounded.append(F(y.numerator // y.denominator)+offset)
        candidates.append(tuple(rounded))
    return min(candidates, key=lambda q: norm(sub(value, q)))


def identity(size):
    return [[ONE if i == j else ZERO for j in range(size)] for i in range(size)]


def reduce_hurwitz(value):
    """Return U A=E, U V=V U=I, with E in row echelon form."""
    e = matrix(value, hurwitz); m, n = len(e), len(e[0])
    u, v = identity(m), identity(m)
    pivot = 0; pivots = []; steps = []

    def swap(i, j):
        if i == j:
            return
        e[i], e[j] = e[j], e[i]; u[i], u[j] = u[j], u[i]
        for row in v:
            row[i], row[j] = row[j], row[i]
        steps.append(('swap', i, j))

    for col in range(n):
        first = next((i for i in range(pivot, m) if norm(e[i][col])), None)
        if first is None:
            continue
        swap(pivot, first)
        while True:
            i = next((i for i in range(pivot+1, m) if norm(e[i][col])), None)
            if i is None:
                break
            before = norm(e[pivot][col])
            q = nearest_hurwitz(multiply(e[i][col], inverse(e[pivot][col])))
            e[i] = [sub(a, multiply(q, b)) for a, b in zip(e[i], e[pivot])]
            u[i] = [sub(a, multiply(q, b)) for a, b in zip(u[i], u[pivot])]
            for row in v:
                row[pivot] = add(row[pivot], multiply(row[i], q))
            after = norm(e[i][col])
            if after > before/2:
                raise ArithmeticError('Euclidean norm bound failed')
            steps.append(('reduce', i, pivot, col, q, before, after))
            if after:
                swap(pivot, i)
        pivots.append(col); pivot += 1
        if pivot == m:
            break
    return dict(echelon=e, left_transform=u, inverse_transform=v,
                rank=pivot, pivots=pivots, steps=steps)


def factor_dyadic(value):
    a = matrix(value, dyadic)
    exponent = max(x.denominator.bit_length()-1 for row in a for entry in row for x in entry)
    cleared = [[scale(q, 1 << exponent) for q in row] for row in a]
    result = reduce_hurwitz(cleared)
    r = result['rank']
    result.update(input_scale=exponent,
                  left=[row[:r] for row in result['inverse_transform']],
                  right=[[scale(q, F(1, 1 << exponent)) for q in row]
                         for row in result['echelon'][:r]])
    return result
