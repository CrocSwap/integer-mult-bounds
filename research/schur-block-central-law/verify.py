#!/usr/bin/env python3
"""Block Schur central-action law: exact finite corroboration.

ssafwann with substantial OpenAI Codex assistance. Apache-2.0.
Sector fixtures follow Petalas #4746 and ssafwann #4671; ordered factors
follow Petalas #4597. No predecessor executable is imported.
"""
from itertools import product
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def zero(n, m):
    return tuple((0,) * m for _ in range(n))


def eye(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def add(a, b, q, scale=1):
    require(len(a) == len(b) and all(len(r) == len(s) for r, s in zip(a, b)),
            'addition shape')
    return tuple(tuple((x+scale*y) % q for x, y in zip(r, s))
                 for r, s in zip(a, b))


def mul(a, b, q):
    require(a and b and all(len(row) == len(b) for row in a), 'product shape')
    require(all(len(row) == len(b[0]) for row in b), 'ragged product')
    bt = tuple(zip(*b))
    return tuple(tuple(sum(x*y for x, y in zip(r, c)) % q for c in bt)
                 for r in a)


def block(a, b, c, d):
    return tuple(x+y for x, y in zip(a, b)) + tuple(x+y for x, y in zip(c, d))


def rref(a, q, columns=None):
    m = [list(row) for row in a]
    width = len(m[0]) if m else 0
    pivots = []
    for j in range(width if columns is None else columns):
        pivot = next((i for i in range(len(pivots), len(m)) if m[i][j]), None)
        if pivot is None:
            continue
        k = len(pivots)
        m[k], m[pivot] = m[pivot], m[k]
        inv = pow(m[k][j], -1, q)
        m[k] = [(x*inv) % q for x in m[k]]
        for i in range(len(m)):
            if i != k and m[i][j]:
                t = m[i][j]
                m[i] = [(x-t*y) % q for x, y in zip(m[i], m[k])]
        pivots.append(j)
    return tuple(tuple(row) for row in m), tuple(pivots)


def rank(a, q):
    return len(rref(a, q)[1])


def inverse(a, q):
    n = len(a)
    reduced, pivots = rref(tuple(r+s for r, s in zip(a, eye(n))), q, n)
    require(len(pivots) == n, 'singular matrix')
    return tuple(row[n:] for row in reduced)


def kernel(a, q):
    reduced, pivots = rref(a, q)
    width = len(a[0])
    columns = []
    for j in range(width):
        if j not in pivots:
            v = [0]*width
            v[j] = 1
            for i, p in enumerate(pivots):
                v[p] = -reduced[i][j] % q
            columns.append(tuple(v))
    return tuple(zip(*columns))


def matrices(q, d):
    require(q in (2, 3, 5) and 0 < d <= 3 and q**(d*d) <= 625,
            'census capacity')
    for data in product(range(q), repeat=d*d):
        yield tuple(tuple(data[i*d:(i+1)*d]) for i in range(d))


def complete_factor(t, q):
    """X=[T,N] is onto, Y=[I;0] is injective, XY=T (#4746)."""
    d = len(t)
    x = t
    for j in range(d):
        trial = tuple(row+(int(i == j),) for i, row in enumerate(x))
        if rank(trial, q) > rank(x, q):
            x = trial
    y = eye(d) + zero(len(x[0])-d, d)
    require(rank(x, q) == d and mul(x, y, q) == t, 'factor fixture')
    return x, y


def construct(h, q):
    """A sharp full pair with H prescribed; the 00 sector is padded to d."""
    d = len(h)
    w = add(eye(d), h, q, -1)
    factors = [(add(zero(d, d), w, q, -1), eye(d))]
    factors += [complete_factor(t, q) for t in (w, w, h)]
    x = tuple(sum((factor[0][i] for factor in factors), ()) for i in range(d))
    y = sum((factor[1] for factor in factors), ())
    sizes = tuple(len(factor[1]) for factor in factors)
    require(mul(x, y, q) == eye(d), 'split construction')
    basis = tuple(a+b for a, b in zip(y, kernel(x, q)))
    inv = inverse(basis, q)
    sectors = sum(((j,)*s for j, s in enumerate(sizes)), ())
    p0 = tuple(tuple(int(i == j and sectors[i] in (1, 3))
                     for j in range(len(y))) for i in range(len(y)))
    q0 = tuple(tuple(int(i == j and sectors[i] in (2, 3))
                     for j in range(len(y))) for i in range(len(y)))
    return mul(mul(inv, p0, q), basis, q), mul(mul(inv, q0, q), basis, q)


def schur(p, d, q):
    r = tuple(row[d:] for row in p[:d])
    c = tuple(row[:d] for row in p[d:])
    tail = tuple(row[d:] for row in p[d:])
    return add(tail, mul(c, r, q), q, -1)


def poly(a, coefficients, q):
    out = zero(len(a), len(a))
    for c in reversed(coefficients):
        out = add(mul(out, a, q), eye(len(a)), q, c)
    return out


def minimal_polynomial(a, q):
    """First exact linear dependence of I,A,...,A^d; no root sampling."""
    d = len(a)
    powers = [eye(d)]
    for degree in range(1, d+1):
        powers.append(mul(powers[-1], a, q))
        system = tuple(tuple(p[i][j] for p in powers[:-1]) +
                       (-powers[-1][i][j] % q,)
                       for i in range(d) for j in range(d))
        reduced, pivots = rref(system, q, degree)
        if any(not any(row[:degree]) and row[degree] for row in reduced):
            continue
        require(len(pivots) == degree, 'first dependence uniqueness')
        coefficients = tuple(reduced[i][-1] for i in range(degree)) + (1,)
        require(poly(a, coefficients, q) == zero(d, d), 'annihilator computation')
        return coefficients
    raise ValueError('no minimal polynomial by dimension')


def inspect_pair(p, t, d, q):
    n = len(p)
    require(q in (2, 3, 5) and 1 <= d < n <= 18, 'field/dimension contract')
    require(all(len(row) == n for row in p+t) and len(t) == n, 'square pair')
    require(mul(p, p, q) == p and mul(t, t, q) == t, 'idempotent premise')
    pq = mul(p, t, q)
    require(pq == mul(t, p, q), 'commuting premise')
    require(tuple(row[:d] for row in p[:d]) == eye(d) and
            tuple(row[:d] for row in t[:d]) == eye(d), 'identity pivot premise')
    h = tuple(row[:d] for row in pq[:d])
    s, u = schur(p, d, q), schur(t, d, q)
    m = n-d
    a1 = add(tuple(row[:d] for row in pq[d:]),
             mul(tuple(row[:d] for row in t[d:]), h, q), q, -1)
    a2 = add(tuple(row[:d] for row in p[d:]),
             tuple(row[:d] for row in t[d:]), q, -1)
    a = tuple(x+y for x, y in zip(a1, a2))
    b1 = add(tuple(row[d:] for row in p[:d]), tuple(row[d:] for row in t[:d]), q, -1)
    b2 = add(mul(h, tuple(row[d:] for row in t[:d]), q),
             tuple(row[d:] for row in pq[:d]), q, -1)
    c = add(mul(s, u, q), mul(u, s, q), q, -1)
    delta = add(s, u, q, -1)
    z = mul(delta, delta, q)
    w, j = add(eye(d), h, q, -1), add(h, mul(h, h, q), q, -1)
    ks = block(w, add(zero(d, d), eye(d), q, -1),
               add(zero(d, d), j, q, -1), h)
    kt = block(eye(d), eye(d), zero(d, d), zero(d, d))
    theta = add(add(h, h, q), mul(h, h, q), q, -1)
    theta2 = block(theta, zero(d, d), zero(d, d), theta)
    require(mul(s, s, q) == s and mul(u, u, q) == u, 'residual idempotents')
    require(mul(a, b1+b2, q) == c, 'ordered Schur factorization')
    require(mul(s, a, q) == mul(a, ks, q), 'S action')
    require(mul(u, a, q) == mul(a, kt, q), 'T action')
    require(mul(z, a, q) == mul(a, theta2, q), 'block central intertwiner')
    require(mul(z, s, q) == mul(s, z, q) and mul(z, u, q) == mul(u, z, q),
            'centrality')
    require(mul(c, c, q) == mul(z, add(z, eye(m), q, -1), q), 'C squared')
    mp = minimal_polynomial(theta, q)
    pz = poly(z, mp, q)
    require(mul(pz, c, q) == zero(m, m), 'commutator annihilator')
    require(mul(mul(z, add(z, eye(m), q, -1), q), pz, q) == zero(m, m),
            'whole residual annihilator')
    return {'h': h, 's': s, 't': u, 'a': a, 'c': c, 'z': z,
            'theta': theta, 'mp': mp, 'n': n, 'd': d, 'q': q}


def sharp_checks(data):
    q, d, c, z = (data[k] for k in ('q', 'd', 'c', 'z'))
    require(rank(c, q) == 2*d and rank(data['a'], q) == 2*d, 'sharp fixture')
    powers = [c]
    for _ in range(len(data['mp'])-2):
        powers.append(mul(z, powers[-1], q))
    flat = tuple(tuple(x for row in p for x in row) for p in powers)
    require(rank(flat, q) == len(data['mp'])-1, 'exact restriction minimal polynomial')


def jordan_check(data):
    q, d, c, z, theta = (data[k] for k in ('q', 'd', 'c', 'z', 'theta'))
    rows = []
    for lam in range(q):
        left, right = c, eye(d)
        zl = add(z, eye(len(z)), q, -lam)
        tl = add(theta, eye(d), q, -lam)
        ranks = []
        for _ in range(d+2):
            require(rank(left, q) == 2*rank(right, q), 'doubled Jordan rank sequence')
            ranks.append(rank(left, q))
            left, right = mul(zl, left, q), mul(tl, right, q)
        rows.append(ranks)
    return rows


def exhaustive_nonsharp(n, d):
    free = [(i, j) for i in range(n) for j in range(n) if i >= d or j >= d]
    projectors = []
    for values in product(range(2), repeat=len(free)):
        p = [list(row) for row in eye(n)]
        for (i, j), value in zip(free, values):
            p[i][j] = value
        p = tuple(tuple(row) for row in p)
        if mul(p, p, 2) == p:
            projectors.append(p)
    count, histogram = 0, {}
    for p in projectors:
        for t in projectors:
            if mul(p, t, 2) == mul(t, p, 2):
                data = inspect_pair(p, t, d, 2)
                r = rank(data['c'], 2)
                histogram[r] = histogram.get(r, 0)+1
                count += 1
    return {'n': n, 'd': d, 'pairs': count, 'commutator_ranks': histogram}


def rejected(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError('control accepted: '+label)


def controls(nilpotent, ternary, odd, nonscalar):
    z, c = nilpotent['z'], nilpotent['c']
    out = []
    out.append(rejected(lambda: require(mul(z, c, 2) == zero(len(z), len(z)),
                                       'square-free replacement'), 'drop repeated root'))
    z3 = ternary['z']
    out.append(rejected(lambda: require(poly(z3, ternary['mp'], 3) == zero(len(z3), len(z3)),
                                       'whole-space overclaim'), 'omit endpoint factors'))
    a, h = nonscalar['a'], nonscalar['h']
    bad = block(h, zero(len(h), len(h)), zero(len(h), len(h)), h)
    out.append(rejected(lambda: require(mul(nonscalar['z'], a, 2) == mul(a, bad, 2),
                                       'H in place of Theta'), 'replace Theta by H'))
    h = odd['h']
    bad_theta = add(add(h, h, 5), mul(h, h, 5), 5)
    bad = block(bad_theta, zero(2, 2), zero(2, 2), bad_theta)
    out.append(rejected(lambda: require(mul(odd['z'], odd['a'], 5) == mul(odd['a'], bad, 5),
                                       'wrong odd-field sign'), 'replace minus by plus'))
    identity = inspect_pair(eye(3), eye(3), 1, 2)
    out.append(rejected(lambda: sharp_checks(identity), 'drop sharpness hypothesis'))
    out.append(rejected(lambda: inspect_pair(eye(3), zero(3, 3), 1, 2), 'zero pivot'))
    badp = ((1, 1, 0), (0, 0, 1), (0, 0, 0))
    out.append(rejected(lambda: inspect_pair(badp, eye(3), 1, 2), 'nonidempotent input'))
    p = ((1, 0, 0), (0, 1, 0), (0, 0, 0))
    t = ((1, 0, 0), (0, 0, 0), (0, 1, 1))
    out.append(rejected(lambda: inspect_pair(p, t, 1, 2), 'noncommuting inputs'))
    out.append(rejected(lambda: list(matrices(3, 3)), 'census capacity'))
    return out


def main():
    coverage = []
    for q, d in ((2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (5, 1), (5, 2)):
        count = 0
        for h in matrices(q, d):
            p, t = construct(h, q)
            data = inspect_pair(p, t, d, q)
            require(data['h'] == h, 'prescribed compressed product')
            sharp_checks(data)
            count += 1
        coverage.append({'q': q, 'd': d, 'all_H': count})
    fixtures = []
    for q, h in ((2, ((0, 1, 0), (0, 0, 1), (0, 0, 0))),
                 (3, ((0, 1, 0), (0, 0, 1), (0, 0, 0))),
                 (5, ((0, 1), (1, 1))),
                 (2, ((0, 1), (1, 1)))):
        data = inspect_pair(*construct(h, q), len(h), q)
        sharp_checks(data)
        data['jordan_ranks'] = jordan_check(data)
        data['whole_mp'] = minimal_polynomial(data['z'], q)
        fixtures.append(data)
    extra = [exhaustive_nonsharp(3, 1), exhaustive_nonsharp(4, 2)]
    require([x['pairs'] for x in extra] == [253, 1219], 'credited small-domain sizes')
    require(fixtures[0]['mp'] == (0, 0, 1), 'binary nilpotent fixture')
    require(fixtures[1]['mp'] == (0, 0, 0, 1) and
            fixtures[1]['whole_mp'] == (0, 0, 0, 0, 1), 'ternary endpoint multiplicity')
    failure_controls = controls(*fixtures)
    receipt = {'sharp_H_domains': coverage, 'nonsharp_domains': extra,
               'fixtures': [{k: data[k] for k in ('q', 'd', 'n', 'h', 'theta', 'mp', 'whole_mp', 'jordan_ranks')}
                            for data in fixtures], 'rejected_controls': failure_controls}
    print(json.dumps(receipt, sort_keys=True, indent=2))
    print('PASS_SCHUR_BLOCK_CENTRAL_LAW')


if __name__ == '__main__':
    main()
