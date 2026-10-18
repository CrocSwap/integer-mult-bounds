"""Exact binary affine and formal group-algebra arithmetic; no search code.

Gareth Davidson, with substantial OpenAI Codex assistance. Apache-2.0.
Rows are bit vectors. Products are ordinary left-to-right matrix products:
the rightmost factor acts first. All acceptance checks survive Python -O.
"""
from functools import lru_cache


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return tuple(1 << i for i in range(n))


def parity(v):
    return v.bit_count() & 1


def apply(a, v):
    return sum(parity(row & v) << i for i, row in enumerate(a))


def mul(a, b):
    out = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length() - 1]
            row ^= bit
        out.append(value)
    return tuple(out)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


def reduced(rows, n):
    a = list(rows)
    pivots = []
    for j in range(n):
        pos = next((i for i in range(len(pivots), len(a)) if a[i] >> j & 1), None)
        if pos is None:
            continue
        k = len(pivots)
        a[k], a[pos] = a[pos], a[k]
        for i in range(len(a)):
            if i != k and a[i] >> j & 1:
                a[i] ^= a[k]
        pivots.append(j)
    return a, pivots


def kernel(a, n):
    rows, pivots = reduced(a, n)
    out = []
    for j in range(n):
        if j not in pivots:
            out.append((1 << j) | sum(((rows[i] >> j) & 1) << p for i, p in enumerate(pivots)))
    return out


def solve(a, b, n):
    rows, pivots = reduced([row | (((b >> i) & 1) << n) for i, row in enumerate(a)], n)
    if any(row == 1 << n for row in rows):
        return None
    return sum(((rows[i] >> n) & 1) << p for i, p in enumerate(pivots))


@lru_cache(maxsize=None)
def linear_factors(a):
    """Construct rank(a-I) transvections by enlarging the fixed space each step."""
    n = len(a)
    need(rank(a) == n, "invertible linear part")
    identity, current, factors = eye(n), a, []
    while current != identity:
        delta = tuple(x ^ y for x, y in zip(current, identity))
        v = next(1 << j for j in range(n) if apply(delta, 1 << j))
        u = apply(delta, v)
        fixed = kernel(delta, n)
        # f vanishes on Fix(current) and u, with f(v)=1.
        constraints = fixed + [u, v]
        f = solve(constraints, 1 << (len(constraints) - 1), n)
        need(f is not None and parity(f & u) == 0 and parity(f & v) == 1, "separating functional")
        t = tuple(row ^ (f if (u >> i) & 1 else 0) for i, row in enumerate(identity))
        new = mul(t, current)
        need(rank(tuple(x ^ y for x, y in zip(new, identity))) == rank(delta) - 1,
             "fixed-space descent")
        factors.append(t)
        current = new
    return tuple(factors)


def affine(a, b=0):
    n = len(a)
    return tuple(row | (((b >> i) & 1) << n) for i, row in enumerate(a))


def homogeneous(g):
    return tuple(g) + (1 << len(g),)


def amul(g, h):
    need(len(g) == len(h), "address dimensions")
    return mul(homogeneous(g), homogeneous(h))[:-1]


def displacement(g):
    return rank(tuple(row ^ (1 << i) for i, row in enumerate(g)))


def affine_factors(g):
    n, mask = len(g), (1 << len(g)) - 1
    a = tuple(row & mask for row in g)
    b = sum((row >> n) << i for i, row in enumerate(g))
    linear = linear_factors(a)
    c = solve(tuple(row ^ (1 << i) for i, row in enumerate(a)), b, n)
    if c is not None:
        return tuple(affine(t, apply(t, c) ^ c) for t in linear)
    return (affine(eye(n), b),) + tuple(affine(t) for t in linear)


def validate_factors(g, factors):
    product = eye(len(g))
    for t in factors:
        need(displacement(t) == 1, "paid affine displacement")
        need(amul(t, t) == eye(len(g)), "paid map must be an involution")
        product = amul(product, t)
    need(product == g, "complete affine endpoint")
    need(len(factors) == displacement(g), "attaining paid length")


def encode(g):
    return sum(row << (i * (len(g) + 1)) for i, row in enumerate(g))


def decode(code, n):
    return tuple((code >> (i * (n + 1))) & ((1 << (n + 1)) - 1) for i in range(n))


def linear_maps(n):
    for code in range(1 << (n * n)):
        a = tuple((code >> (i * n)) & ((1 << n) - 1) for i in range(n))
        if rank(a) == n:
            yield a


def projectors(r):
    for x in range(1, 1 << r):
        for y in range(1, 1 << r):
            if parity(x & y):
                yield tuple(y if (x >> i) & 1 else 0 for i in range(r))


def group_units(n):
    """Every rank-one homogeneous affine displacement, without duplicates."""
    identity = eye(n)
    for u in range(1, 1 << n):
        for f in range(1, 1 << (n + 1)):
            if parity(u & f) == 0:
                yield tuple(row ^ (f if (u >> i) & 1 else 0) for i, row in enumerate(identity))


def representation(nmat, g):
    """Image of I+([g]-1)N under the homogeneous representation."""
    r, m = len(nmat), len(g) + 1
    delta = tuple(row ^ (1 << i) for i, row in enumerate(homogeneous(g)))
    out = []
    for i in range(r):
        for a in range(m):
            row = 1 << (i * m + a)
            for j in range(r):
                if (nmat[i] >> j) & 1:
                    row ^= delta[a] << (j * m)
            out.append(row)
    return tuple(out)


def ring_eye(r, n):
    one = eye(n)
    return [[{one} if i == j else set() for j in range(r)] for i in range(r)]


def ring_call(nmat, g):
    r, one = len(nmat), eye(len(g))
    out = ring_eye(r, len(g))
    for i in range(r):
        for j in range(r):
            if nmat[i] >> j & 1:
                out[i][j] ^= {one}
                out[i][j] ^= {g}
    return out


def ring_mul(a, b):
    r = len(a)
    out = [[set() for _ in range(r)] for _ in range(r)]
    for i in range(r):
        for j in range(r):
            value = out[i][j]
            for k in range(r):
                for g in a[i][k]:
                    for h in b[k][j]:
                        gh = amul(g, h)
                        if gh in value:
                            value.remove(gh)
                        else:
                            value.add(gh)
    return out


def ring_image(a, n):
    r, m = len(a), n + 1
    out = [0] * (r * m)
    for i in range(r):
        for j in range(r):
            block = [0] * m
            for g in a[i][j]:
                for k, row in enumerate(homogeneous(g)):
                    block[k] ^= row
            for k, row in enumerate(block):
                out[i * m + k] ^= row << (j * m)
    return tuple(out)
