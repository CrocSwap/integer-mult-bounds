#!/usr/bin/env python3
"""Nilpotent Schur extension: bounded exact corroboration, not a general proof.

ssafwann with substantial OpenAI Codex (gpt-6-astra) assistance. Apache-2.0.
Matrix helpers adapted from ssafwann PR5256, exact head c72d6ff431cf5c979f5010018d8eba0c15577bce.
Sector construction: Nick Petalas PR4746. Factor transport: MatShep PR4762 /
codyw912 PR4735. Stabilizer method: Nick Petalas PR4915. No runtime imports
from those packages; the written argument in README.md is the general proof.
"""
from itertools import product
from math import prod
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


def schur(p, d, q):
    r = tuple(row[d:] for row in p[:d])
    c = tuple(row[:d] for row in p[d:])
    tail = tuple(row[d:] for row in p[d:])
    return add(tail, mul(c, r, q), q, -1)



def scale(a, c, q):
    return tuple(tuple(c*x % q for x in row) for row in a)


def columns(a):
    return list(zip(*a))


def from_columns(cs, rows):
    return tuple(zip(*cs)) if cs else zero(rows, 0)


def diag(*blocks):
    n = sum(len(b) for b in blocks)
    out, offset = [], 0
    for b in blocks:
        out.extend((0,)*offset + row + (0,)*(n-offset-len(b)) for row in b)
        offset += len(b)
    return tuple(out)


def solve(a, v, q):
    reduced, pivots = rref(tuple(row+(x,) for row, x in zip(a, v)), q, len(a[0]))
    require(not any(not any(row[:-1]) and row[-1] for row in reduced), 'no lift')
    result = [0]*len(a[0])
    for i, j in enumerate(pivots):
        result[j] = reduced[i][-1]
    return tuple(result)


def extend(cs, candidates, rows, q):
    added = []
    for c in candidates:
        if rank(from_columns(cs+added+[c], rows), q) > len(cs)+len(added):
            added.append(c)
    return added


def nilpotent(h, q):
    d = len(h)
    require(d > 0 and all(len(row) == d for row in h), 'square H')
    power = eye(d)
    for _ in range(d):
        power = mul(power, h, q)
    return power == zero(d, d)


def factors(h, pads, q):
    require(nilpotent(h, q), 'nilpotent family')
    require(len(pads) == 4 and all(isinstance(s, int) and s >= 0 for s in pads),
            'nonnegative four-sector padding')
    d = len(h)
    w = add(eye(d), h, q, -1)
    cs = columns(h)
    # Use only independent columns when selecting a complement to im H.
    independent = []
    for c in cs:
        independent += extend(independent, [c], d, q)
    nc = extend(independent, columns(eye(d)), d, q)
    n = from_columns(nc, d)
    ts = (scale(w, -1, q), w, w, h)
    out = []
    for j, t in enumerate(ts):
        x = tuple(row + (n[i] if j == 3 else ()) + (0,)*pads[j]
                  for i, row in enumerate(t))
        out.append((x, eye(d)+zero(len(x[0])-d, d)))
    return out, n


def split_pair(fs, q, require_sharp=True):
    d = len(fs[0][0])
    pi = tuple(sum((x[i] for x, _ in fs), ()) for i in range(d))
    inc = sum((y for _, y in fs), ())
    require(mul(pi, inc, q) == eye(d), 'split identity')
    basis = tuple(a+b for a, b in zip(inc, kernel(pi, q)))
    inv = inverse(basis, q)
    sector = sum(((j,)*len(y) for j, (_, y) in enumerate(fs)), ())
    pair = []
    for support in ((1, 3), (2, 3)):
        p0 = tuple(tuple(int(i == j and sector[i] in support)
                         for j in range(len(inc))) for i in range(len(inc)))
        p = mul(mul(inv, p0, q), basis, q)
        require(tuple(row[:d] for row in p[:d]) == eye(d), 'identity pivot')
        pair.append(p)
    p, t = pair
    require(mul(p, p, q) == p and mul(t, t, q) == t, 'full idempotents')
    pq = mul(p, t, q)
    require(pq == mul(t, p, q), 'full commuting pair')
    s, u = schur(p, d, q), schur(t, d, q)
    require(mul(s, s, q) == s and mul(u, u, q) == u, 'residual idempotents')
    if require_sharp:
        require(rank(add(mul(s, u, q), mul(u, s, q), q, -1), q) == 2*d,
                'sharp commutator')
    return basis, s, u, tuple(row[:d] for row in pq[:d])


def transport(x, y, x0, y0, q):
    """Construct gY=Y0, X0g=X, rather than compare rank fingerprints."""
    d, r = len(x), len(y)
    require(rank(x, q) == d and rank(y, q) == d, 'active factor ranks')
    require(rank(x0, q) == d and rank(y0, q) == d and len(y0) == r,
            'target factor ranks')
    t = mul(x, y, q)
    require(t == mul(x0, y0, q), 'equal products')
    b, b0 = columns(y), columns(y0)
    b += extend(b, columns(kernel(x, q)), r, q)
    b0 += extend(b0, columns(kernel(x0, q)), r, q)
    image = []
    for c in columns(t):
        image += extend(image, [c], d, q)
    for v in extend(image, columns(eye(d)), d, q):
        b.append(solve(x, v, q))
        b0.append(solve(x0, v, q))
    require(len(b) == r and len(b0) == r, 'transport bases')
    g = mul(from_columns(b0, r), inverse(from_columns(b, r), q), q)
    require(rank(g, q) == r and mul(g, y, q) == y0 and mul(x0, g, q) == x,
            'factor intertwiner')
    return g


def residual_transport(fs, target, q):
    m, s, t, h = split_pair(fs, q)
    m0, s0, t0, h0 = split_pair(target, q)
    require(h == h0, 'fixed H')
    g = diag(*(transport(x, y, x0, y0, q)
               for (x, y), (x0, y0) in zip(fs, target)))
    change = mul(mul(inverse(m0, q), g, q), m, q)
    d = len(h)
    k = tuple(row[d:] for row in change[d:])
    require(change == diag(eye(d), k) and rank(k, q) == len(k), 'header transport')
    require(mul(k, s, q) == mul(s0, k, q) and mul(k, t, q) == mul(t0, k, q),
            'whole residual ordered intertwiner')


def model(h, n, q):
    """Explicit (x,y,z,t) action; independently compared to literal Schur."""
    d, a = len(h), len(n[0])
    w = add(eye(d), h, q, -1)
    z = zero(d, d)
    nn = scale(n, -1, q)
    s = tuple(h[i]+z[i]+scale(h, -1, q)[i]+nn[i] for i in range(d))
    s += zero(d, 3*d+a)
    s += tuple(scale(w, -1, q)[i]+z[i]+w[i]+nn[i] for i in range(d))
    s += tuple((0,)*(3*d)+row for row in eye(a))
    t = zero(d, 3*d+a)
    t += tuple(z[i]+h[i]+scale(h, -1, q)[i]+nn[i] for i in range(d))
    t += tuple(z[i]+scale(w, -1, q)[i]+w[i]+nn[i] for i in range(d))
    t += tuple((0,)*(3*d)+row for row in eye(a))
    return s, t


def odd_form(h, n, q):
    require(q in (3, 5), 'odd characteristic required')
    d, a = len(h), len(n[0])
    w = add(eye(d), h, q, -1)
    r = add(scale(eye(d), 2, q), h, q, -1)
    ri = inverse(r, q)
    half = pow(2, -1, q)
    hh, rh = scale(h, half, q), scale(r, half, q)
    nn = scale(n, -1, q)
    sc = tuple(hh[i]+hh[i]+nn[i] for i in range(d))
    sc += tuple(rh[i]+rh[i]+n[i] for i in range(d))
    sc += tuple((0,)*(2*d)+row for row in eye(a))
    tc = tuple(hh[i]+scale(hh, -1, q)[i]+n[i] for i in range(d))
    tc += tuple(scale(rh, -1, q)[i]+rh[i]+n[i] for i in range(d))
    tc += tuple((0,)*(2*d)+row for row in eye(a))
    # F maps (u,v,t,c) to (x,y,z,t), using the displayed inverse formula.
    size = 3*d+a
    zrow = tuple((0,)*d+scale(mul(w, ri, q), -1, q)[i]
                 +scale(mul(ri, n, q), -1, q)[i]+eye(d)[i] for i in range(d))
    xrow = add(zrow, tuple(scale(eye(d), half, q)[i]
                           +scale(eye(d), half, q)[i]+(0,)*(a+d)
                           for i in range(d)), q)
    yrow = add(zrow, tuple(scale(eye(d), -half, q)[i]
                           +scale(eye(d), half, q)[i]+(0,)*(a+d)
                           for i in range(d)), q)
    f = xrow+yrow+zrow+tuple((0,)*(2*d)+row+(0,)*d for row in eye(a))
    require(len(f) == size and rank(f, q) == size, 'odd coordinate isomorphism')
    return diag(sc, zero(d, d)), diag(tc, zero(d, d)), f


def check_h(h, pads, q):
    fs, n = factors(h, pads, q)
    basis, s, t, found = split_pair(fs, q)
    require(found == h, 'compressed product')
    d, a = len(h), len(n[0])
    if any(pads):
        minimal, _ = factors(h, (0, 0, 0, 0), q)
        minimal_basis, sm, tm, _ = split_pair(minimal, q)
        # Embed the minimal kernel and append the unused sector coordinates.
        # This checks the full ordered padding decomposition, not just Z.
        embedded, extra, old_offset, offset = [], [], 0, 0
        total = len(basis)
        for j, (_, y) in enumerate(minimal):
            size = len(y)
            embedded += [row[d:] for row in minimal_basis[old_offset:old_offset+size]]
            embedded += list(zero(pads[j], len(sm)))
            for k in range(pads[j]):
                extra.append(tuple(int(i == offset+size+k) for i in range(total)))
            old_offset += size
            offset += size+pads[j]
        v = tuple(row+tail for row, tail in zip(embedded, from_columns(extra, total)))
        change = mul(inverse(basis, q), v, q)
        require(change[:d] == zero(d, total-d), 'padded kernel coordinates')
        change = change[d:]
        sp = diag(sm, zero(pads[0], pads[0]), eye(pads[1]),
                  zero(pads[2], pads[2]), eye(pads[3]))
        tp = diag(tm, zero(pads[0], pads[0]), zero(pads[1], pads[1]),
                  eye(pads[2]), eye(pads[3]))
        require(rank(change, q) == total-d and mul(s, change, q) == mul(change, sp, q)
                and mul(t, change, q) == mul(change, tp, q), 'ordered padding decomposition')
    # Compare the minimal literal Schur pair to the independent coordinate model.
    if not any(pads):
        w = add(eye(d), h, q, -1)
        wi = inverse(w, q)
        v0 = tuple(eye(d)[i]+eye(d)[i]+mul(wi, h, q)[i]+mul(wi, n, q)[i]
                   for i in range(d))
        v = v0 + tuple(eye(d)[i]+(0,)*(2*d+a) for i in range(d))
        v += tuple((0,)*d+eye(d)[i]+(0,)*(d+a) for i in range(d))
        v += tuple((0,)*(2*d)+eye(d)[i]+(0,)*a for i in range(d))
        v += tuple((0,)*(3*d)+row for row in eye(a))
        change = mul(inverse(basis, q), v, q)
        require(change[:d] == zero(d, 3*d+a), 'kernel coordinates')
        change = change[d:]
        sm, tm = model(h, n, q)
        require(rank(change, q) == 3*d+a and mul(s, change, q) == mul(change, sm, q)
                and mul(t, change, q) == mul(change, tm, q), 'literal Schur model')
        if q != 2:
            sc, tc, f = odd_form(h, n, q)
            require(mul(sm, f, q) == mul(f, sc, q)
                    and mul(tm, f, q) == mul(f, tc, q), 'odd core plus common zero')
    if q != 2:
        delta = add(s, t, q, -1)
        z = mul(delta, delta, q)
        hp, zp = eye(d), eye(len(s))
        for _ in range(1, d+2):
            oldrank = rank(hp, q)
            hp, zp = mul(hp, h, q), mul(zp, z, q)
            require(rank(zp, q) == rank(hp, q)+oldrank+pads[1]+pads[2],
                    'whole central Jordan ranks')
        # Powers of Z only see nonzero primary dimensions; also distinguish
        # exactly the claimed size-one blocks at eigenvalue one.
        require(rank(add(z, eye(len(z)), q, -1), q) == len(z)-pads[1]-pads[2],
                'unit padding eigenblocks')
    return s, t


def gl(n, q):
    return prod(q**n-q**j for j in range(n))


def split_count(h, pads, q):
    require(nilpotent(h, q), 'nilpotent count family')
    d, a = len(h), len(h)-rank(h, q)
    sizes = [d+s for s in pads]
    sizes[3] += a
    numerator = prod(gl(r, q) for r in sizes)
    denominator = prod(gl(s, q) for s in pads)*q**(a*a+2*a*pads[3])
    require(numerator % denominator == 0, 'integral mass')
    return numerator//denominator


def scalar_census(q, pads):
    h = ((0,),)
    target, _ = factors(h, pads, q)
    sizes = tuple(len(y) for _, y in target)
    n = sum(sizes)
    require(q**(2*n) <= 60000, 'split census capacity')
    vecs = list(product(range(q), repeat=n))
    accepted, splits, legal = 0, 0, 0
    for inc in vecs:
        for pi in vecs:
            if sum(x*y for x, y in zip(inc, pi)) % q != 1:
                continue
            splits += 1
            off, fs, prods = 0, [], []
            for size in sizes:
                x, y = (tuple(pi[off:off+size]),), tuple((v,) for v in inc[off:off+size])
                fs.append((x, y))
                prods.append(mul(x, y, q)[0][0])
                off += size
            if prods != [q-1, 1, 1, 0]:
                continue
            legal += 1
            _, s, t, _ = split_pair(fs, q, require_sharp=False)
            sharp = rank(add(mul(s, t, q), mul(t, s, q), q, -1), q) == 2
            require(sharp == all(rank(x, q) == 1 and rank(y, q) == 1 for x, y in fs),
                    'sector criterion against literal Schur rank')
            if not sharp:
                continue
            residual_transport(fs, target, q)
            accepted += 1
    require(splits == (q**n-1)*q**(n-1), 'complete split inventory')
    require(accepted == split_count(h, pads, q), 'exact fixed-H split mass')
    return {'q': q, 'sectors': sizes, 'all_splits': splits, 'identity_H0_splits': legal,
            'fixed_H_splits': accepted,
            'complete_headers': accepted*gl(n-1, q)}


def factor_census(q, d, r, t):
    require(q**(2*d*r) <= 70000, 'factor census capacity')
    xs, ys = [], []
    for values in product(range(q), repeat=d*r):
        x = tuple(tuple(values[i*r:(i+1)*r]) for i in range(d))
        if rank(x, q) == d:
            xs.append(x)
            ys.append(tuple(zip(*x)))
    count = sum(mul(x, y, q) == t for x in xs for y in ys)
    c = d-rank(t, q)
    s = r-d-c
    require(s >= 0, 'factor capacity premise')
    den = gl(s, q)*q**(c*c+2*c*s)
    require(gl(r, q) % den == 0 and count == gl(r, q)//den, 'sector stabilizer count')
    return {'q': q, 'd': d, 'r': r, 'rank_product': d-c, 'pairs': count}


def rejected(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('control failed to reject: '+label)


def main():
    counts = []
    for q, d in ((2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3), (5, 1), (5, 2)):
        count = 0
        for values in product(range(q), repeat=d*d):
            h = tuple(tuple(values[i*d:(i+1)*d]) for i in range(d))
            if nilpotent(h, q):
                check_h(h, (0, 0, 0, 0), q)
                count += 1
        require(count == q**(d*d-d), 'nilpotent inventory cross-check')
        counts.append({'q': q, 'd': d, 'nilpotent_H': count})
    j3 = ((0, 1, 0), (0, 0, 1), (0, 0, 0))
    fixtures = [((0,),), j3, diag(j3, ((0,),))]
    padded = 0
    for q in (2, 3, 5):
        for h in fixtures:
            for pads in ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0),
                         (0, 0, 0, 2), (1, 1, 1, 1)):
                check_h(h, pads, q)
                fs, _ = factors(h, pads, q)
                moved = []
                for x, y in fs:
                    r = len(y)
                    g = [list(row) for row in eye(r)]
                    if r > 1:
                        g[0][-1] = 1
                    g = tuple(tuple(row) for row in g)
                    moved.append((mul(x, inverse(g, q), q), mul(g, y, q)))
                residual_transport(moved, fs, q)
                padded += 1
    census = [scalar_census(3, (0, 0, 0, 0))]
    census += [scalar_census(2, p) for p in ((0, 0, 0, 0), (1, 0, 0, 0),
                                          (0, 1, 0, 0), (0, 0, 0, 1))]
    fc = [factor_census(q, d, r, t) for q, d, r, t in
          ((2, 1, 3, ((0,),)), (3, 1, 3, ((0,),)), (5, 1, 2, ((0,),)),
           (3, 1, 2, ((1,),)), (2, 2, 3, ((0, 1), (0, 0))),
           (2, 2, 4, ((0, 1), (0, 0))))]
    s2, t2 = check_h(((0,),), (0, 0, 0, 0), 2)
    z2 = mul(add(s2, t2, 2, -1), add(s2, t2, 2, -1), 2)
    s3, t3 = check_h(j3, (0, 0, 0, 0), 3)
    z3 = mul(add(s3, t3, 3, -1), add(s3, t3, 3, -1), 3)
    z3cube = mul(mul(z3, z3, 3), z3, 3)
    controls = [
        rejected(lambda: factors(eye(2), (0, 0, 0, 0), 3), 'nonnilpotent H'),
        rejected(lambda: factors(((0, 0),), (0, 0, 0, 0), 3), 'nonsquare H'),
        rejected(lambda: factors(((0,),), (0, 0, 0, -1), 3), 'negative padding'),
        rejected(lambda: odd_form(((0,),), ((1,),), 2), 'division by two'),
        rejected(lambda: require(rank(z2, 2) == 1, 'binary exception'), 'odd Jordan law in F2'),
        rejected(lambda: require(z3cube == zero(len(z3), len(z3)), 'missing chain'), 'omit extended Jordan chain'),
        rejected(lambda: require(split_count(((0,),), (0, 0, 0, 0), 3) == 384,
                                 'missing unipotent denominator'), 'omit q^(a squared)'),
        rejected(lambda: require(split_count(((0,),), (0, 0, 0, 1), 2) == 84,
                                 'missing mixed exponent'), 'omit 2 a s11'),
        rejected(lambda: transport(((0,),), ((1,),), ((0,),), ((1,),), 3), 'non-surjective factor'),
    ]
    print(json.dumps({'nilpotent_domains': counts, 'padded_transport_fixtures': padded,
                      'split_censuses': census, 'factor_censuses': fc,
                      'ternary_J3_whole_Jordan': [4, 3, 1, 1, 1],
                      'rejection_controls': controls}, sort_keys=True))
    print('PASS_SCHUR_NILPOTENT_EXTENSION')


if __name__ == '__main__':
    main()
