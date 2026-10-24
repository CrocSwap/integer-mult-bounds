#!/usr/bin/env python3
"""Exact finite corroboration of general-H ordered Schur primary gluing.

Mihir Srivastava with substantial OpenAI Codex assistance. Apache-2.0.
Standalone implementation; predecessor proof credit is in README.md.
"""
from dataclasses import dataclass
from itertools import product
import hashlib
import json


class CheckError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise CheckError(message)


@dataclass(frozen=True)
class Field:
    q: int

    def add(self, a, b):
        return a ^ b if self.q == 4 else (a + b) % self.q

    def neg(self, a):
        return a if self.q == 4 else (-a) % self.q

    def mul(self, a, b):
        if self.q != 4:
            return a * b % self.q
        value = 0
        while b:
            if b & 1:
                value ^= a
            b >>= 1
            a <<= 1
            if a & 4:
                a ^= 7  # F4 = F2[t]/(t^2+t+1), not integers modulo 4.
        return value

    def inv(self, a):
        require(a != 0, "zero field inverse")
        return next(b for b in range(1, self.q) if self.mul(a, b) == 1)


@dataclass(frozen=True)
class Matrix:
    field: Field
    rows: int
    cols: int
    data: tuple

    def __add__(self, other):
        require((self.field, self.rows, self.cols) ==
                (other.field, other.rows, other.cols), "addition shape")
        return mat(self.field, self.rows, self.cols,
                   lambda i, j: self.field.add(self.data[i][j], other.data[i][j]))

    def __neg__(self):
        return mat(self.field, self.rows, self.cols,
                   lambda i, j: self.field.neg(self.data[i][j]))

    def __sub__(self, other):
        return self + (-other)

    def __matmul__(self, other):
        require(self.field == other.field and self.cols == other.rows, "product shape")
        out = [[0] * other.cols for _ in range(self.rows)]
        f = self.field
        for i in range(self.rows):
            for k in range(self.cols):
                a = self.data[i][k]
                if a:
                    for j, b in enumerate(other.data[k]):
                        if b:
                            out[i][j] = f.add(out[i][j], f.mul(a, b))
        return mat(f, self.rows, other.cols, lambda i, j: out[i][j])

    def sub(self, r0, r1, c0, c1):
        return mat(self.field, r1-r0, c1-c0, lambda i, j: self.data[r0+i][c0+j])

    def power(self, exponent):
        require(self.rows == self.cols and exponent >= 0, "power domain")
        result = eye(self.field, self.rows)
        for _ in range(exponent):
            result = result @ self
        return result


def mat(f, n, m, value=lambda i, j: 0):
    return Matrix(f, n, m, tuple(tuple(value(i, j) for j in range(m)) for i in range(n)))


def eye(f, n):
    return mat(f, n, n, lambda i, j: int(i == j))


def hcat(*blocks):
    f, n = blocks[0].field, blocks[0].rows
    require(all(b.field == f and b.rows == n for b in blocks), "horizontal shape")
    data = [sum((list(b.data[i]) for b in blocks), []) for i in range(n)]
    return mat(f, n, sum(b.cols for b in blocks), lambda i, j: data[i][j])


def vcat(*blocks):
    f, m = blocks[0].field, blocks[0].cols
    require(all(b.field == f and b.cols == m for b in blocks), "vertical shape")
    data = sum((list(b.data) for b in blocks), [])
    return mat(f, len(data), m, lambda i, j: data[i][j])


def rref(a):
    f = a.field
    rows = [list(r) for r in a.data]
    pivots = []
    for col in range(a.cols):
        row = next((i for i in range(len(pivots), a.rows) if rows[i][col]), None)
        if row is None:
            continue
        p = len(pivots)
        rows[p], rows[row] = rows[row], rows[p]
        inv = f.inv(rows[p][col])
        rows[p] = [f.mul(inv, x) for x in rows[p]]
        for i in range(a.rows):
            if i != p and rows[i][col]:
                scale = f.neg(rows[i][col])
                rows[i] = [f.add(x, f.mul(scale, y)) for x, y in zip(rows[i], rows[p])]
        pivots.append(col)
        if len(pivots) == a.rows:
            break
    return mat(f, a.rows, a.cols, lambda i, j: rows[i][j]), pivots


def rank(a):
    return len(rref(a)[1])


def columns(a, indices):
    return mat(a.field, a.rows, len(indices), lambda i, j: a.data[i][indices[j]])


def kernel(a):
    reduced, pivots = rref(a)
    free = [j for j in range(a.cols) if j not in pivots]
    pos = {p: i for i, p in enumerate(pivots)}
    return mat(a.field, a.cols, len(free),
               lambda i, j: a.field.neg(reduced.data[pos[i]][free[j]]) if i in pos
               else int(i == free[j]))


def solve(a, b):
    require(a.rows == b.rows and b.cols == 1, "solve shape")
    reduced, pivots = rref(hcat(a, b))
    require(a.cols not in pivots, "inconsistent linear system")
    positions = {p: i for i, p in enumerate(pivots)}
    return mat(a.field, a.cols, 1,
               lambda i, j: reduced.data[positions[i]][a.cols] if i in positions else 0)


def inverse(a):
    require(a.rows == a.cols, "inverse shape")
    reduced, pivots = rref(hcat(a, eye(a.field, a.rows)))
    require(pivots == list(range(a.rows)), "singular inverse")
    return reduced.sub(0, a.rows, a.cols, 2*a.cols)


def extend(base, candidates, target):
    chosen = base
    for j in range(candidates.cols):
        if chosen.cols == target:
            break
        trial = hcat(chosen, columns(candidates, [j]))
        if rank(trial) == trial.cols:
            chosen = trial
    require(chosen.cols == target, "basis extension failed")
    return chosen


def complement(a):
    basis = columns(a, rref(a)[1])
    full = extend(basis, eye(a.field, a.rows), a.rows)
    return full.sub(0, a.rows, basis.cols, a.rows)


def direct_sum(*blocks):
    f = blocks[0].field
    n, m = sum(b.rows for b in blocks), sum(b.cols for b in blocks)
    data = [[0] * m for _ in range(n)]
    r = c = 0
    for b in blocks:
        for i in range(b.rows):
            for j in range(b.cols):
                data[r+i][c+j] = b.data[i][j]
        r += b.rows
        c += b.cols
    return mat(f, n, m, lambda i, j: data[i][j])


def linear_map(f, n, m, action):
    basis = eye(f, m)
    output = [action(columns(basis, [j])) for j in range(m)]
    return hcat(*output) if output else mat(f, n, 0)


def full_factor(a, padding=0):
    f, d = a.field, a.rows
    extra = complement(a)
    x = hcat(a, extra, mat(f, d, padding))
    y = vcat(eye(f, d), mat(f, extra.cols+padding, d))
    return x, y


def rank_factor(a, padding=0):
    basis = columns(a, rref(a)[1])
    coeff = linear_map(a.field, basis.cols, a.cols, lambda v: solve(basis, a @ v))
    return hcat(basis, mat(a.field, a.rows, padding)), vcat(coeff, mat(a.field, padding, a.cols))


def fitting(h):
    d, f = h.rows, h.field
    w = eye(f, d)-h
    wd = w.power(d)
    c = columns(wd, rref(wd)[1])
    one = kernel(wd)
    basis = hcat(c, one)
    require(rank(basis) == d, "Fitting basis not direct")
    split = inverse(basis) @ h @ basis
    dc = c.cols
    require(split.sub(0, dc, dc, d) == mat(f, dc, d-dc), "Fitting cross block")
    require(split.sub(dc, d, 0, dc) == mat(f, d-dc, dc), "Fitting cross block")
    hc, h1 = split.sub(0, dc, 0, dc), split.sub(dc, d, dc, d)
    require(rank(eye(f, dc)-hc) == dc, "complement W not invertible")
    require((eye(f, d-dc)-h1).power(d) == mat(f, d-dc, d-dc), "primary W not nilpotent")
    return basis, hc, h1


def adapt_active(x, y, basis, ac, a1):
    """Explicit full-rank factor basis from Y, preimage lifts and ker X."""
    f, d, dc = x.field, x.rows, ac.rows
    xu, yu = inverse(basis) @ x, y @ basis
    nc, n1 = complement(ac), complement(a1)
    lifted = []
    for first, a, extra in ((0, ac, nc), (dc, a1, n1)):
        block = columns(yu, list(range(first, first+a.rows)))
        for j in range(extra.cols):
            target = mat(f, d, 1, lambda i, k: extra.data[i-first][j]
                         if first <= i < first+a.rows else 0)
            block = hcat(block, solve(xu, target))
        lifted.append(block)
    core = hcat(*lifted)
    require(rank(core) == core.cols, "factor core dependency")
    result = extend(core, kernel(xu), x.cols)
    require(rank(result) == x.cols, "active factor basis singular")
    return result


def construct_intertwiner(h, factors, drop_correction=False):
    f, d = h.field, h.rows
    require(d >= 1 and h.cols == d, "H domain")
    w = eye(f, d)-h
    products = (-w, w, w, h)
    for j, ((x, y), a) in enumerate(zip(factors, products)):
        require(x @ y == a, "sector product")
        if j:
            require(rank(x) == rank(y) == d, "sharp active ranks")
    basis, hc, h1 = fitting(h)
    dc, d1 = hc.rows, h1.rows
    wc, w1 = eye(f, dc)-hc, eye(f, d1)-h1
    n0, n1 = complement(hc), complement(w1)
    a0, a1 = n0.cols, n1.cols
    x00, y00 = factors[0]
    xu = inverse(basis) @ x00
    tail00 = kernel(xu.sub(0, dc, 0, x00.cols))
    b00 = hcat(y00 @ basis.sub(0, d, 0, dc), tail00)
    require(rank(b00) == x00.cols, "sector00 Fitting split singular")
    x1 = (xu @ tail00).sub(dc, d, 0, tail00.cols)
    b10 = adapt_active(*factors[1], basis, wc, w1)
    b01 = adapt_active(*factors[2], basis, wc, w1)
    b11 = adapt_active(*factors[3], basis, hc, h1)
    sizes = [x.cols for x, _ in factors]
    pads = (sizes[1]-d-a1, sizes[2]-d-a1, sizes[3]-d-a0)
    z00 = sizes[0]-dc
    require(min(z00, *pads) >= 0, "negative capacity")
    iwc, ih1 = inverse(wc), inverse(h1)
    correction = inverse(eye(f, d1)+w1) @ x1
    lengths = [dc, dc, dc, a0, d1, a1, d1, a1, z00, *pads]
    m = sum(lengths)

    def unpack(v):
        out, offset = [], 0
        for length in lengths:
            out.append(v.sub(offset, offset+length, 0, 1))
            offset += length
        return out

    def embed(v):
        x, y, z, t, xb, b, yb, c, u, p10, p01, p11 = unpack(v)
        shift = mat(f, d1, 1) if drop_correction else correction @ u
        xx, yy = xb-shift, yb-shift
        zz = -(ih1 @ (x1 @ u+w1 @ xx+n1 @ b+w1 @ yy+n1 @ c))
        v00 = vcat(x+y+iwc @ (hc @ z+n0 @ t), u)
        return vcat(b00 @ v00, b10 @ vcat(x, xx, b, p10),
                    b01 @ vcat(y, yy, c, p01), b11 @ vcat(z, t, zz, p11))

    def canonical(v, which):
        x, y, z, t, xb, b, yb, c, u, p10, p01, p11 = unpack(v)
        zero_c, zero_1, zero_a = mat(f, dc, 1), mat(f, d1, 1), mat(f, a1, 1)
        if which == 0:
            head = [hc @ (x-z)-n0 @ t, zero_c, wc @ (z-x)-n0 @ t, t]
            middle = [xb+w1 @ yb+n1 @ c, b, zero_1, zero_a]
            tail = [mat(f, z00, 1), p10, mat(f, pads[1], 1), p11]
        else:
            head = [zero_c, hc @ (y-z)-n0 @ t, wc @ (z-y)-n0 @ t, t]
            middle = [zero_1, zero_a, yb+w1 @ xb+n1 @ b, c]
            tail = [mat(f, z00, 1), mat(f, pads[0], 1), p01, p11]
        return vcat(*(head+middle+tail))

    embedding = linear_map(f, sum(sizes), m, embed)
    sc = linear_map(f, m, m, lambda v: canonical(v, 0))
    tc = linear_map(f, m, m, lambda v: canonical(v, 1))
    return embedding, sc, tc, (dc, d1, a0, a1, z00, *pads)


def literal_schur(h, factors):
    f, d = h.field, h.rows
    sizes = [x.cols for x, _ in factors]
    n = sum(sizes)
    inc, proj = vcat(*(y for _, y in factors)), hcat(*(x for x, _ in factors))
    require(proj @ inc == eye(f, d), "split identity")
    p0 = direct_sum(*(eye(f, r) if j in (1, 3) else mat(f, r, r) for j, r in enumerate(sizes)))
    q0 = direct_sum(*(eye(f, r) if j in (2, 3) else mat(f, r, r) for j, r in enumerate(sizes)))
    header = hcat(inc, kernel(proj))
    ih = inverse(header)
    p, q = ih @ p0 @ header, ih @ q0 @ header
    require(p @ p == p and q @ q == q and p @ q == q @ p, "commuting idempotents")
    require(p.sub(0, d, 0, d) == q.sub(0, d, 0, d) == eye(f, d), "identity pivots")
    require((p @ q).sub(0, d, 0, d) == h, "compressed H")
    s = p.sub(d, n, d, n)-p.sub(d, n, 0, d) @ p.sub(0, d, d, n)
    t = q.sub(d, n, d, n)-q.sub(d, n, 0, d) @ q.sub(0, d, d, n)
    require(rank(s @ t-t @ s) == 2*d, "literal sharpness")
    return s, t, ih, proj


def check_case(h, factors, drop_correction=False):
    embedding, sc, tc, signature = construct_intertwiner(h, factors, drop_correction)
    s, t, ih, proj = literal_schur(h, factors)
    d, n = h.rows, embedding.rows
    require(proj @ embedding == mat(h.field, d, embedding.cols), "embedding outside ker pi")
    g = (ih @ embedding).sub(d, n, 0, embedding.cols)
    require(rank(g) == g.rows == g.cols, "residual intertwiner singular")
    require(s @ g == g @ sc, "S intertwiner failed")
    require(t @ g == g @ tc, "T intertwiner failed")
    require(sc @ sc == sc and tc @ tc == tc, "canonical idempotents")
    return signature, sc, tc


def make_factors(h, padding=(0, 0, 0, 0), arbitrary00=None):
    w = eye(h.field, h.rows)-h
    return [arbitrary00 if arbitrary00 is not None else rank_factor(-w, padding[0]),
            full_factor(w, padding[1]), full_factor(w, padding[2]), full_factor(h, padding[3])]


def all_matrices(f, n, m):
    for entries in product(range(f.q), repeat=n*m):
        yield mat(f, n, m, lambda i, j: entries[i*m+j])


def scramble(factors, seed):
    result = []
    for slot, (x, y) in enumerate(factors):
        f, r = x.field, x.cols
        g = eye(f, r)
        for j in range(max(0, r-1)):
            a, b = (j, j+1) if (seed+slot+j) % 2 else (j+1, j)
            shear = mat(f, r, r, lambda u, v: int(u == v) if (u, v) != (a, b)
                        else 1+(seed+j+slot) % (f.q-1))
            g = shear @ g
        result.append((x @ inverse(g), g @ y))
    return result


def jordan(f, n, eigenvalue):
    return mat(f, n, n, lambda i, j: eigenvalue if i == j else int(j == i+1))


def rejected(action):
    try:
        action()
    except CheckError:
        return
    raise CheckError("negative control unexpectedly accepted")


def run():
    count = {"complete_H": 0, "arbitrary_sector00": 0, "mixed_fixtures": 0, "controls": 0}
    domains = []
    for q, d in ((2, 1), (2, 2), (3, 1), (3, 2), (4, 1), (5, 1)):
        f, local = Field(q), 0
        for h in all_matrices(f, d, d):
            check_case(h, make_factors(h))
            local += 1
        domains.append({"q": q, "d": d, "matrices": local})
        count["complete_H"] += local
    factor_domains = []
    for q, d, r in ((2, 2, 0), (2, 2, 1), (2, 2, 2),
                    (3, 1, 0), (3, 1, 1), (3, 1, 2)):
        f, local = Field(q), 0
        for x in all_matrices(f, d, r):
            for y in all_matrices(f, r, d):
                h = eye(f, d)+x @ y
                factors = make_factors(h, arbitrary00=(x, y))
                check_case(h, scramble(factors, count["arbitrary_sector00"]))
                count["arbitrary_sector00"] += 1
                local += 1
        factor_domains.append({"q": q, "d": d, "r00": r, "pairs": local})
    signatures = []
    for q in (2, 3, 4, 5):
        f = Field(q)
        nonsplit = mat(f, 2, 2, lambda i, j: ((0, 1), (1, 1))[i][j])
        repeated = vcat(hcat(nonsplit, eye(f, 2)), hcat(mat(f, 2, 2), nonsplit))
        for blocks in ((jordan(f, 2, 0), jordan(f, 2, 1)),
                       (nonsplit, jordan(f, 2, 1)),
                       (repeated, jordan(f, 2, 1)),
                       (jordan(f, 2, 2 if q > 2 else 0), jordan(f, 1, 1)),
                       (jordan(f, 1, 0), jordan(f, 3, 1), jordan(f, 1, 0))):
            h0 = direct_sum(*blocks)
            leading = scramble([(eye(f, h0.rows), eye(f, h0.rows))], q)[0][1]
            h = inverse(leading) @ h0 @ leading
            for pad in ((0, 0, 0, 0), (2, 1, 2, 1)):
                result = check_case(h, scramble(make_factors(h, pad), q+sum(pad)))
                signatures.append([q, *result[0]])
                count["mixed_fixtures"] += 1
    f = Field(3)
    h = direct_sum(jordan(f, 1, 0), jordan(f, 2, 1))
    factors = scramble(make_factors(h, (1, 1, 0, 1)), 3)
    rejected(lambda: check_case(h, factors, drop_correction=True))
    count["controls"] += 1
    rejected(lambda: inverse(eye(f, h.rows)-h))
    count["controls"] += 1
    bad = list(factors)
    bad[0] = (-bad[0][0], bad[0][1])
    rejected(lambda: check_case(h, bad))
    count["controls"] += 1
    deficient_h = eye(f, 1)
    bad = make_factors(deficient_h)
    x, y = bad[1]
    bad[1] = (x, mat(f, y.rows, y.cols))
    require(bad[1][0] @ bad[1][1] == mat(f, 1, 1), "control changed product")
    rejected(lambda: check_case(deficient_h, bad))
    count["controls"] += 1
    w = eye(f, 2)-jordan(f, 2, 1)
    rejected(lambda: inverse(hcat(columns(w, rref(w)[1]), kernel(w))))
    count["controls"] += 1
    good, sc, tc, _ = construct_intertwiner(h, factors)
    s, t, ih, _ = literal_schur(h, factors)
    g = (ih @ good).sub(h.rows, good.rows, 0, good.cols)
    padding_index = sc.rows-2  # The one (1,0) padding coordinate in this fixture.
    wrong = sc+mat(f, sc.rows, sc.cols,
                   lambda i, j: f.neg(1) if i == j == padding_index else 0)
    rejected(lambda: require(s @ g == g @ wrong, "wrong scalar padding"))
    count["controls"] += 1
    rejected(lambda: construct_intertwiner(mat(f, 0, 0), [(mat(f, 0, 0), mat(f, 0, 0))]*4))
    count["controls"] += 1
    # Same H and residual dimension alone do not fix the ordered pair.
    scalar_h = mat(f, 1, 1)
    _, s00, _ = check_case(scalar_h, make_factors(scalar_h, (1, 0, 0, 0)))
    _, s10, _ = check_case(scalar_h, make_factors(scalar_h, (0, 1, 0, 0)))
    require(s00.rows == s10.rows and rank(s00) != rank(s10), "profile discriminator failed")
    count["controls"] += 1
    report = {"counts": count, "complete_domains": domains, "factor_domains": factor_domains,
              "mixed_signatures_sha256": hashlib.sha256(json.dumps(signatures).encode()).hexdigest(),
              "scope": "finite full ordered intertwiners, not a proof kernel or supplier replay"}
    print(json.dumps(report, sort_keys=True))
    print("PASS_SCHUR_PRIMARY_GLUING")


if __name__ == "__main__":
    run()
