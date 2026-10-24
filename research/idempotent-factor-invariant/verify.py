#!/usr/bin/env python3
"""Exact factor-invariant corroboration. GPT-6.1 Sol assistance; Apache-2.0.

No predecessor code is imported. No files, subprocesses or network are used.
"""
from functools import lru_cache
from itertools import product
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


class Field:
    """Prime fields and F4=F2[x]/(x^2+x+1)."""

    def __init__(self, q):
        require(q in (2, 3, 4, 5), "unsupported field")
        self.q = q
        if q == 4:
            self.add = tuple(tuple(a ^ b for b in range(q)) for a in range(q))
            self.mul = tuple(tuple(self.four_mul(a, b) for b in range(q)) for a in range(q))
            self.neg = tuple(range(q))
        else:
            self.add = tuple(tuple((a+b) % q for b in range(q)) for a in range(q))
            self.mul = tuple(tuple((a*b) % q for b in range(q)) for a in range(q))
            self.neg = tuple((-a) % q for a in range(q))
        self.inv = (0,) + tuple(next(b for b in range(1, q) if self.mul[a][b] == 1)
                               for a in range(1, q))

    @staticmethod
    def four_mul(a, b):
        result = 0
        for bit in range(2):
            if b & (1 << bit):
                result ^= a << bit
        return result ^ 7 if result & 4 else result


def eye(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def tr(a, width=None):
    return tuple(zip(*a)) if a else tuple(() for _ in range(width or 0))


def mm(a, b, f, width=None):
    columns, result = tr(b, width), []
    for row in a:
        out = []
        for col in columns:
            require(len(row) == len(col), "product shape")
            value = 0
            for x, y in zip(row, col):
                value = f.add[value][f.mul[x][y]]
            out.append(value)
        result.append(tuple(out))
    return tuple(result)


def rref(a, width, f):
    require(all(len(row) == width for row in a), "row width")
    require(all(type(x) is int and 0 <= x < f.q for row in a for x in row), "field entry")
    rows, pivots = [list(row) for row in a], []
    for col in range(width):
        found = next((j for j in range(len(pivots), len(rows)) if rows[j][col]), None)
        if found is None:
            continue
        i = len(pivots)
        rows[i], rows[found] = rows[found], rows[i]
        scale = f.inv[rows[i][col]]
        rows[i] = [f.mul[scale][x] for x in rows[i]]
        for j in range(len(rows)):
            if j != i and rows[j][col]:
                coeff = f.neg[rows[j][col]]
                rows[j] = [f.add[x][f.mul[coeff][y]] for x, y in zip(rows[j], rows[i])]
        pivots.append(col)
    return tuple(tuple(row) for row in rows[:len(pivots)]), tuple(pivots)


def space(a, width, f):
    return rref(a, width, f)[0]


def rank(a, width, f):
    return len(space(a, width, f))


def kernel(a, width, f):
    reduced, pivots = rref(a, width, f)
    vectors = []
    for j in range(width):
        if j not in pivots:
            vector = [int(i == j) for i in range(width)]
            for i, pivot in enumerate(pivots):
                vector[pivot] = f.neg[reduced[i][j]]
            vectors.append(tuple(vector))
    return space(vectors, width, f)


def inverse(a, f):
    n = len(a)
    reduced, pivots = rref(tuple(row+unit for row, unit in zip(a, eye(n))), 2*n, f)
    require(pivots == tuple(range(n)), "singular inverse")
    return tuple(row[n:] for row in reduced)


def diag(a, b):
    r, s = len(a), len(b)
    return tuple(row+(0,)*s for row in a) + tuple((0,)*r+row for row in b)


@lru_cache(maxsize=None)
def gl(q, n):
    require(n <= 3 and q**(n*n) <= 20000, "bounded GL domain")
    f, values = Field(q), []
    for entries in product(range(q), repeat=n*n):
        a = tuple(tuple(entries[i*n:(i+1)*n]) for i in range(n))
        if rank(a, n, f) == n:
            values.append((a, inverse(a, f)))
    return tuple(values)


@lru_cache(maxsize=None)
def group(q, r, s):
    return tuple((diag(a, b), diag(ai, bi)) for a, ai in gl(q, r) for b, bi in gl(q, s))


def factor(p, f):
    n = len(p)
    require(mm(p, p, f) == p, "not idempotent")
    pivots = rref(p, n, f)[1]
    x = tuple(tuple(row[j] for j in pivots) for row in p)
    r = len(pivots)
    if not r:
        return x, ()
    selected = rref(tr(x), n, f)[1]
    y = mm(inverse(tuple(x[i] for i in selected), f), tuple(p[i] for i in selected), f)
    require(mm(x, y, f, n) == p and mm(y, x, f, r) == eye(r), "factor identities")
    return x, y


def datum(p, q, f):
    require(len(p) == len(q), "ambient mismatch")
    x, y = factor(p, f)
    z, w = factor(q, f)
    r, s, n = len(y), len(w), len(p)
    t = r+s
    joined, stacked = tuple(a+b for a, b in zip(x, z)), y+w
    m = mm(stacked, joined, f, t)
    return n, r, s, kernel(joined, t, f), space(tr(stacked, n), t, f), m


def transformed(data, g, gi, f):
    n, r, s, k, l, m = data
    t = r+s
    return (n, r, s, space(mm(k, tr(gi), f, t), t, f),
            space(mm(l, tr(gi), f, t), t, f), mm(mm(gi, m, f), g, f))


def signature(data, f):
    return min(transformed(data, g, gi, f) for g, gi in group(f.q, data[1], data[2]))


def complement(initial, target, width, f):
    basis, added = space(initial, width, f), []
    for vector in target:
        candidate = space(basis+(vector,), width, f)
        if len(candidate) > len(basis):
            added.append(vector)
            basis = candidate
    return tuple(added)


def realize(data, f, ambient=None):
    n, r, s, k, l, m = data
    t = r+s
    require(len(m) == t and all(len(row) == t for row in m), "product shape")
    require(tuple(row[:r] for row in m[:r]) == eye(r), "first identity block")
    require(tuple(row[r:] for row in m[r:]) == eye(s), "second identity block")
    k, l = space(k, t, f), space(l, t, f)
    require(not any(x for row in mm(m, tr(k, t), f) for x in row), "kernel not killed")
    im = space(tr(m, t), t, f)
    require(space(l+im, t, f) == l, "product image outside observation image")
    a, b, c = t-len(k), len(l), len(im)
    minimum = a+b-c
    n = n if ambient is None else ambient
    require(n >= minimum and n >= 1, "ambient below bound")
    chosen = complement(k, eye(t), t, f)
    quotient = inverse(tr(k+chosen, t), f)[len(k):]
    lift = complement(im, l, t, f)
    joined = quotient + ((0,)*t,)*(n-a)
    columns = mm(m, tr(chosen, t), f, a)
    stacked = tuple(row+tuple(v[i] for v in lift)+(0,)*(n-minimum)
                    for i, row in enumerate(columns))
    require(mm(stacked, joined, f, t) == m, "constructed product")
    require(kernel(joined, t, f) == k, "constructed kernel")
    require(space(tr(stacked, n), t, f) == l, "constructed observation image")
    p = mm(tuple(row[:r] for row in joined), stacked[:r], f, n)
    q = mm(tuple(row[r:] for row in joined), stacked[r:], f, n)
    require(mm(p, p, f) == p and mm(q, q, f) == q, "constructed idempotents")
    require(rank(p, n, f) == r and rank(q, n, f) == s, "constructed ranks")
    return p, q, minimum


def projectors(q, n, desired):
    require(q**(n*n) <= 65536, "bounded projector census")
    f, result = Field(q), []
    for entries in product(range(q), repeat=n*n):
        p = tuple(tuple(entries[i*n:(i+1)*n]) for i in range(n))
        if mm(p, p, f) == p and rank(p, n, f) == desired:
            result.append(p)
    return result


def direct_key(p, q, f):
    """Normalize P and use its full ambient centralizer, independent of K/L/M."""
    n = len(p)
    x, y = factor(p, f)
    basis = tr(x) + kernel(p, n, f)
    change = tr(basis)
    normalized_q = mm(mm(inverse(change, f), q, f), change, f)
    normalized_p = mm(mm(inverse(change, f), p, f), change, f)
    expected = diag(eye(len(y)), tuple((0,)*(n-len(y)) for _ in range(n-len(y))))
    require(normalized_p == expected, "direct first-projector normalization")
    return min(mm(mm(gi, normalized_q, f), g, f)
               for g, gi in group(f.q, len(y), n-len(y)))


def census(q, n, r, s):
    f = Field(q)
    p = tuple(tuple(int(i == j and i < r) for j in range(n)) for i in range(n))
    direct_group, forward, reverse, active = group(q, r, n-r), {}, {}, {}
    others = projectors(q, n, s)
    for other in others:
        data = datum(p, other, f)
        invariant = signature(data, f)
        direct = min(mm(mm(gi, other, f), g, f) for g, gi in direct_group)
        require(forward.setdefault(invariant, direct) == direct, "invariant merges direct classes")
        require(reverse.setdefault(direct, invariant) == invariant, "invariant splits direct class")
        recovered_p, recovered_q, minimum = realize(data, f)
        require(signature(datum(recovered_p, recovered_q, f), f) == invariant,
                "reconstruction changes orbit")
        require(direct_key(recovered_p, recovered_q, f) == direct,
                "reconstructed pair not directly conjugate")
        pq, qp = mm(p, other, f), mm(other, p, f)
        block = tuple(a+b for a, b in zip(p, pq)) + tuple(a+b for a, b in zip(qp, other))
        direct_active = (rank(tuple(a+b for a, b in zip(p, other)), 2*n, f)
                         + rank(p+other, n, f) - rank(block, 2*n, f))
        require(direct_active == minimum, "direct active-dimension formula")
        require(minimum <= r+s+min(r, s), "active upper bound")
        active[minimum] = active.get(minimum, 0)+1
    return {"field": q, "n": n, "r": r, "s": s, "cases": len(others),
            "orbits": len(forward), "direct_group_order": len(direct_group),
            "factor_group_order": len(group(q, r, s)), "active_dimensions": active}


def rejected(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError("control accepted: "+message)


def controls():
    f = Field(2)
    p = ((1, 0, 0), (0, 0, 0), (0, 0, 0))
    image = ((1, 1, 0), (0, 0, 0), (0, 0, 0))
    d0, di, dd = (datum(p, q, f) for q in (p, image, tr(image)))
    require(d0[5] == di[5] == dd[5], "Gram counterexample")
    require(d0[3] == di[3] and d0[4] != di[4], "image needed")
    require(d0[4] == dd[4] and d0[3] != dd[3], "kernel needed")
    require(len({signature(d, f) for d in (d0, di, dd)}) == 3, "kernel/image omitted")
    ortho = datum(((1, 0), (0, 0)), ((0, 0), (0, 1)), f)
    skew = datum(((1, 1), (0, 0)), ((0, 0), (0, 1)), f)
    require(ortho[3:5] == skew[3:5] and ortho[5] != skew[5], "product needed")
    require(signature(ortho, f) != signature(skew, f), "product omitted")
    deg = datum(((1, 1, 0), (0, 0, 0), (0, 0, 0)),
                ((0, 0, 0), (1, 1, 1), (0, 0, 0)), f)
    require(realize(deg, f)[2] == 3, "sharp active bound")
    rejected(lambda: realize(deg, f, ambient=2), "small ambient")
    rejected(lambda: realize((*deg[:3], ((1, 0),), deg[4], deg[5]), f), "bad kernel")
    rejected(lambda: realize((*deg[:4], (), deg[5]), f), "missing image")
    rejected(lambda: realize((*deg[:5], ((0, 0), (0, 1))), f), "identity block")
    rejected(lambda: factor(((1, 1), (1, 1)), f), "nonidempotent")
    rejected(lambda: rref(((2,),), 1, f), "out-of-field entry")
    require(Field(4).mul[2][2] == 3 and 2*2 % 4 != 3, "extension field arithmetic")
    padded = realize(deg, f, ambient=5)
    require(signature(datum(*padded[:2], f), f) != signature(deg, f), "ambient omitted")
    zero = ((0, 0), (0, 0))
    for pair in ((zero, zero), (zero, ((1, 0), (0, 0)))):
        data = datum(*pair, f)
        recovered = realize(data, f)
        require(datum(*recovered[:2], f)[:3] == data[:3], "rank-zero factor fixture")
    return 11


def sharp_families():
    receipts = []
    for q in (2, 3, 4, 5):
        f = Field(q)
        seed_p = ((1, 1, 0), (0, 0, 0), (0, 0, 0))
        seed_q = ((0, 0, 0), (1, 1, 1), (0, 0, 0))
        for r, s in ((1, 1), (2, 2), (3, 2), (2, 3)):
            p, other = (), ()
            for _ in range(min(r, s)):
                p, other = diag(p, seed_p), diag(other, seed_q)
            for _ in range(abs(r-s)):
                p, other = diag(p, ((int(r > s),),)), diag(other, ((int(s > r),),))
            data = datum(p, other, f)
            minimum = r+s-len(data[3])+len(data[4])-rank(data[5], r+s, f)
            require(minimum == r+s+min(r, s) == len(p), "sharp family formula")
            require(realize(data, f)[2] == minimum, "sharp family reconstruction")
            receipts.append([q, r, s, minimum])
    return receipts


def main():
    cases = ((2, 4, 2, 2), (2, 4, 1, 2), (2, 3, 1, 2), (2, 3, 1, 1),
             (3, 3, 1, 1), (3, 2, 1, 1), (4, 2, 1, 1), (5, 2, 1, 1))
    print(json.dumps({"censuses": [census(*case) for case in cases],
                      "sharp_families": sharp_families(), "controls": controls()}, sort_keys=True))
    print("PASS_IDEMPOTENT_FACTOR_INVARIANT")


if __name__ == "__main__":
    main()
