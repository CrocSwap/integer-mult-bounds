"""Exact binary charts and Gaussian convolution, independently implemented.

Gareth Davidson, with OpenAI Codex assistance. Apache-2.0.
No predecessor executable code is imported.
"""
from collections import Counter
import hashlib
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def linear(columns, x):
    out = 0
    while x:
        bit = x & -x
        out ^= columns[bit.bit_length() - 1]
        x ^= bit
    return out


def transpose(columns, n):
    return tuple(sum(((q >> j) & 1) << i for i, q in enumerate(columns)) for j in range(n))


def rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            p = vector.bit_length() - 1
            if p in pivots:
                vector ^= pivots[p]
            else:
                pivots[p] = vector
                break
    return len(pivots)


def orthonormal(columns, ambient):
    require(all(type(q) is int and 0 < q < (1 << ambient) for q in columns), 'axis range/type')
    require(all((a & b).bit_count() % 2 == (i == j)
                for i, a in enumerate(columns) for j, b in enumerate(columns)), 'Gram identity')


def projector(columns, ambient):
    # The image of every physical coordinate vector under U U^t.
    return tuple(linear(columns, sum(((q >> j) & 1) << i for i, q in enumerate(columns)))
                 for j in range(ambient))


def multiply(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def rotate(a, exponent):
    return (a, (-a[1], a[0]), (-a[0], -a[1]), (a[1], -a[0]))[exponent % 4]


def convolution(axes, sign=1):
    """Literal product of (1+si)I+(1-si)X_q; common denominator 2^len(axes)."""
    require(sign in (-1, 1) and type(sign) is int, 'C direction')
    state = {0: (1, 0)}
    for q in axes:
        out = {}
        for x, value in state.items():
            for y, factor in ((x, (1, sign)), (x ^ q, (1, -sign))):
                a, b = multiply(value, factor)
                c, d = out.get(y, (0, 0))
                out[y] = (a + c, b + d)
        state = out
    return state


def closed_kernel(axes, sign=1):
    """Independent subset formula, using only integer powers and rotations."""
    prefactor = (1, 0)
    for _ in axes:
        prefactor = multiply(prefactor, (1, sign))
    out = {linear(axes, z): rotate(prefactor, -sign * z.bit_count())
           for z in range(1 << len(axes))}
    require(len(out) == (1 << len(axes)), 'dependent convolution axes')
    return out


def rebased(axes, change):
    return tuple(linear(axes, v) for v in change)


def defect(change):
    n = len(change)
    orthonormal(change, n)
    rows = transpose(change, n)
    return sum((((r.bit_count() - 1) // 2) & 1) << i for i, r in enumerate(rows))


def orthogonal_matrices(n):
    # Exhaust every ordered orthonormal basis, with no random nomination.
    vectors = [x for x in range(1, 1 << n) if x.bit_count() & 1]

    def extend(columns, candidates):
        if len(columns) == n:
            yield tuple(columns)
            return
        for q in candidates:
            yield from extend(columns + [q], [v for v in candidates if not ((q & v).bit_count() & 1)])

    yield from extend([], vectors)


def census():
    result = []
    for n in range(1, 7):
        basis = tuple(1 << i for i in range(n))
        wanted = {s: convolution(basis, s) for s in (-1, 1)}
        matrices = preserving = permutations = coefficient_checks = 0
        masks = Counter()
        stream = hashlib.sha256()
        first_failure = None
        for columns in orthogonal_matrices(n):
            matrices += 1
            delta = defect(columns)
            masks[delta] += 1
            preserving += delta == 0
            permutations += all(x.bit_count() == 1 for x in columns)
            stream.update(canonical([columns, delta]) + b'\n')
            for sign in (-1, 1):
                actual = convolution(columns, sign)
                require(len(actual) == (1 << n), 'orthogonal support')
                for x, amplitude in actual.items():
                    factor = -1 if (delta & x).bit_count() & 1 else 1
                    require(amplitude == tuple(factor * a for a in wanted[sign][x]), 'phase-defect theorem')
                    coefficient_checks += 1
                require((actual == wanted[sign]) == (delta == 0), 'exact preservation iff')
            if delta and first_failure is None:
                first_failure = dict(columns=columns, defect=delta)
        result.append(dict(dimension=n, matrices=matrices, preserving=preserving,
                           permutations=permutations, coefficient_checks=coefficient_checks,
                           defect_histogram=dict(sorted(masks.items())), stream_sha256=stream.hexdigest(),
                           first_failure=first_failure))
    require([r['matrices'] for r in result] == [1, 2, 6, 48, 720, 23040], 'complete small orthogonal census')
    require([r['preserving'] for r in result] == [1, 2, 6, 24, 120, 1440], 'small refinement stabilizers')
    return result
