#!/usr/bin/env python3
"""Exact finite evidence for the E8 Gram-class floor in README.md.

Standard library only. Supports and all design prices use integer dot products
and binary submatrix ranks. The ray census supplies the finite data in the proof.
"""
import itertools
import json
import os
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))


DATA = os.path.join(HERE, "data", "designs.json")


def require(cond, msg):
    # Not `assert`, so the checks survive python -O.
    if not cond:
        raise SystemExit("FAIL: " + msg)


def ok(name, detail=""):
    print("PASS %s%s" % (name, (": " + detail) if detail else ""))


def parity(x):
    return bin(x).count("1") & 1


def f2_rank(rows):
    basis = []
    for x in rows:
        for b in basis:
            x = min(x, x ^ b)
        if x:
            basis.append(x)
    return len(basis)


def f2_inverse(rows, n):
    """Inverse of an n x n F2 matrix given as n row bit-masks."""
    aug = [(rows[i], 1 << i) for i in range(n)]
    for c in range(n):
        piv = next((i for i in range(c, n) if (aug[i][0] >> c) & 1), None)
        require(piv is not None, "singular F2 matrix")
        aug[c], aug[piv] = aug[piv], aug[c]
        for i in range(n):
            if i != c and (aug[i][0] >> c) & 1:
                aug[i] = (aug[i][0] ^ aug[c][0], aug[i][1] ^ aug[c][1])
    return [aug[i][1] for i in range(n)]


def det_q(m):
    """Exact determinant of an integer matrix (Bareiss fraction-free elimination)."""
    n = len(m)
    a = [[int(x) for x in row] for row in m]
    sign, prev = 1, 1
    for k in range(n - 1):
        if a[k][k] == 0:
            sw = next((i for i in range(k + 1, n) if a[i][k] != 0), None)
            if sw is None:
                return 0
            a[k], a[sw] = a[sw], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * a[k][k] - a[i][k] * a[k][j]
                require(numerator % prev == 0, "exact Bareiss division")
                a[i][j] = numerator // prev
        prev = a[k][k]
    return sign * a[n - 1][n - 1]


def rank_q(vectors):
    """Exact rank over Q of integer vectors (fraction-free elimination with gcd reduction)."""
    m = [[int(x) for x in v] for v in vectors]
    rk = 0
    for c in range(len(m[0]) if m else 0):
        piv = next((r for r in range(rk, len(m)) if m[r][c] != 0), None)
        if piv is None:
            continue
        m[rk], m[piv] = m[piv], m[rk]
        for r in range(len(m)):
            if r != rk and m[r][c] != 0:
                a, b = m[rk][c], m[r][c]
                row = [a * x - b * y for x, y in zip(m[r], m[rk])]
                g = 0
                for x in row:
                    g = gcd(g, x)
                m[r] = [x // g for x in row] if g > 1 else row
        rk += 1
    return rk


def canon(v):
    for x in v:
        if x > 0:
            return tuple(v)
        if x < 0:
            return tuple(-y for y in v)
    raise ValueError("zero vector")


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


class Model:
    """120 root lines of E8 in doubled coordinates (norm 8; <,>/4 in {0,+-1,+-2})."""

    def __init__(self):
        roots = []
        for i in range(8):
            for j in range(i + 1, 8):
                for si in (2, -2):
                    for sj in (2, -2):
                        v = [0] * 8
                        v[i], v[j] = si, sj
                        roots.append(tuple(v))
        for signs in itertools.product((1, -1), repeat=8):
            if signs.count(-1) % 2 == 0:
                roots.append(tuple(signs))
        require(len(roots) == 240, "240 roots")
        self.lines = sorted({canon(v) for v in roots})
        require(len(self.lines) == 120, "120 root lines")
        self.index = {v: i for i, v in enumerate(self.lines)}
        n = 120
        self.n = n
        self.ip = [[dot(self.lines[p], self.lines[q]) for q in range(n)] for p in range(n)]
        for p in range(n):
            for q in range(n):
                require(self.ip[p][q] % 4 == 0 and abs(self.ip[p][q]) <= 8, "ip/4 in {0,+-1,+-2}")
        self.nrow = [0] * n
        for p in range(n):
            b = 0
            for q in range(n):
                if (self.ip[p][q] // 4) % 2 == 0:
                    b |= 1 << q
            self.nrow[p] = b
        self.set_labels()

    def set_labels(self):
        """Factor the rank-nine symmetric mask through a nonsingular block."""
        n = self.n
        # Independent rows of a symmetric matrix select a nonsingular principal block.
        basis, rows_idx = [], []
        for p in range(n):
            x = self.nrow[p]
            for b in basis:
                x = min(x, x ^ b)
            if x:
                basis.append(x)
                rows_idx.append(p)
        self.rank_n = len(rows_idx)
        k = self.rank_n
        self.label = []
        for p in range(n):
            x = 0
            for t, q in enumerate(rows_idx):
                if (self.nrow[p] >> q) & 1:
                    x |= 1 << t
            self.label.append(x)
        block = []
        for a in rows_idx:
            r = 0
            for t, q in enumerate(rows_idx):
                if (self.nrow[a] >> q) & 1:
                    r |= 1 << t
            block.append(r)
        self.G = f2_inverse(block, k)  # row masks of the inverse Gram form

    # --- supports and prices -------------------------------------------------
    def top(self, u, deleted=()):
        """Lines of P not orthogonal to u (u an integer 8-vector)."""
        dele = set(deleted)
        return [p for p in range(self.n) if p not in dele and dot(self.lines[p], u) != 0]

    def price(self, u, w, deleted=()):
        s = self.top(u, deleted)
        t = self.top(w, deleted)
        mask = 0
        for q in t:
            mask |= 1 << q
        return f2_rank([self.nrow[p] & mask for p in s])

    def span_dim(self, lines_subset):
        return f2_rank([self.label[p] for p in lines_subset])

    def deficiency(self, u, deleted=()):
        """a(u; D) = 9 - dim span of labels of T(u) minus D."""
        return self.rank_n - self.span_dim(self.top(u, deleted))

    def line_of(self, v):
        return self.index[canon(v)]

    def design_cost(self, deleted_lines, terms):
        """Exact (c, prices, det M) of a Gram-class design on P = lines minus D."""
        dele = set(deleted_lines)
        prices = [self.price(u, w, dele) for (u, w) in terms]
        m = [[0] * 8 for _ in range(8)]
        for (u, w) in terms:
            for i in range(8):
                for j in range(8):
                    m[i][j] += u[i] * w[j]
        return sum(prices), prices, det_q(m)


def self_checks(M):
    n = M.n
    require(M.rank_n == 9, "rank_F2 N = 9")
    # labels reproduce N: N[p,q] = label(p)^T G label(q)
    for p in range(n):
        gp = 0
        for i in range(9):
            if parity(M.G[i] & M.label[p]):
                gp |= 1 << i
        for q in range(n):
            bit = parity(gp & M.label[q])
            require(bit == ((M.nrow[p] >> q) & 1), "N = L G L^T at (%d,%d)" % (p, q))
    ok("e8-model", "120 lines, rank_F2 N = 9, N = L G L^T on all 14400 pairs")


SIMPLE = [
    None,
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
]


def cartan_inverse():
    c = [[dot(SIMPLE[i], SIMPLE[j]) // 4 for j in range(1, 9)] for i in range(1, 9)]
    # Bourbaki E8 Cartan matrix: chain 1-3-4-5-6-7-8 with node 2 on node 4
    edges = {(1, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (2, 4)}
    for i in range(1, 9):
        for j in range(1, 9):
            want = 2 if i == j else (-1 if (i, j) in edges or (j, i) in edges else 0)
            require(c[i - 1][j - 1] == want, "Cartan entry (%d,%d)" % (i, j))
    # exact inverse by Gauss-Jordan over the rationals
    a = [[Fraction(c[i][j]) for j in range(8)] + [Fraction(1 if i == j else 0) for j in range(8)]
         for i in range(8)]
    for col in range(8):
        piv = next(r for r in range(col, 8) if a[r][col] != 0)
        a[col], a[piv] = a[piv], a[col]
        pv = a[col][col]
        a[col] = [x / pv for x in a[col]]
        for r in range(8):
            if r != col and a[r][col] != 0:
                f = a[r][col]
                a[r] = [x - f * y for x, y in zip(a[r], a[col])]
    inv = [[a[i][8 + j] for j in range(8)] for i in range(8)]
    for i in range(8):
        for j in range(8):
            require(inv[i][j].denominator == 1, "E8 Cartan inverse is integral (det 1)")
    return [[int(x) for x in row] for row in inv]


def fundamental_weights(cinv):
    ws = []
    for i in range(8):
        v = [0] * 8
        for j in range(8):
            for t in range(8):
                v[t] += cinv[i][j] * SIMPLE[j + 1][t]
        ws.append(tuple(v))
    return ws


def wht512(cnt):
    a = list(cnt)
    require(len(a) == 512, "nine-bit Walsh transform")
    for stage in range(9):
        h = 1 << stage
        for i in range(0, 512, 2 * h):
            for j in range(i, i + h):
                x, y = a[j], a[j + h]
                a[j], a[j + h] = x + y, x - y
    return a


def census(M, weights):
    """For each fundamental-weight ray: |T|, cost_1, cost_2.

    cost_a = |T| - max over codimension-a subspaces W of F2^9 of #{p in T: label(p) in W}
    = the fewest lines of T whose deletion can make the labels of T minus D fall in a
    codimension-a subspace.  Counted by characters: #{x in W} = (1/2^a) sum_{h in H} S[h].
    """
    rows = []
    for w in weights:
        t = M.top(w)
        cnt = [0] * 512
        for p in t:
            cnt[M.label[p]] += 1
        s = wht512(cnt)
        best1 = max(s[h] for h in range(1, 512))
        cost1 = len(t) - (len(t) + best1) // 2
        best2 = None
        for h1 in range(1, 512):
            for h2 in range(h1 + 1, 512):
                h3 = h1 ^ h2
                if h3 <= h2:
                    continue
                val = len(t) + s[h1] + s[h2] + s[h3]
                if best2 is None or val > best2:
                    best2 = val
        cost2 = len(t) - best2 // 4
        rows.append((len(t), cost1, cost2))
    return rows


PREDECESSOR_CENSUS = [
    (57, 1, 25), (78, 14, 42), (83, 27, 51), (92, 28, 56),
    (97, 33, 61), (98, 35, 62), (104, 40, 68), (106, 43, 70),
]


def check_census(M):
    cinv = cartan_inverse()
    weights = fundamental_weights(cinv)
    rows = census(M, weights)
    require(sorted(rows) == PREDECESSOR_CENSUS, "census table %r" % (sorted(rows),))
    root_type = [i for i, r in enumerate(rows) if r[0] == 57]
    require(len(root_type) == 1, "one ray type with |T| = 57")
    theta = weights[root_type[0]]
    require(canon(theta) in M.index, "the 57-type fundamental weight is a root")
    require(root_type[0] == 7, "that weight is omega_8, the highest root")
    other = [r for i, r in enumerate(rows) if i != root_type[0]]
    require(all(r[1] >= 14 for r in other), "cost_1 >= 14 off the root type")
    require(rows[root_type[0]][1] == 1 and rows[root_type[0]][2] == 25, "root type costs (1, 25)")
    ok("ray-census", "(|T|, cost_1, cost_2) = %s; only the root type has cost_1 < 14, cost_2 >= 25 everywhere"
       % (sorted(rows),))


def scalar_matrix(terms):
    m = [[0] * 8 for _ in range(8)]
    for (u, w) in terms:
        for i in range(8):
            for j in range(8):
                m[i][j] += u[i] * w[j]
    lam = m[0][0]
    return lam != 0 and all(m[i][j] == (lam if i == j else 0) for i in range(8) for j in range(8))


def check_root_hyperplanes(model):
    """Check every label hyperplane on every root support, with no sampling."""
    for r in range(120):
        support = model.top(model.lines[r])
        orthogonal = [model.lines[p] for p in range(120) if model.ip[p][r] == 0]
        require(len(support) == 57 and len(orthogonal) == 63, "root support sizes")
        require(rank_q(orthogonal) == 7, "orthogonal roots span r-perp")
        singleton = []
        other_sizes = []
        for h in range(1, 512):
            outside = [p for p in support if parity(model.label[p] & h)]
            if outside == [r]:
                singleton.append(h)
            else:
                other_sizes.append(len(outside))
        require(len(singleton) == 1, "unique hyperplane deleting just r")
        require(min(other_sizes) == 24, "all other hyperplanes need at least 24 deletions")
        require(model.deficiency(model.lines[r], [r]) == 1, "deleted root loses one dimension")
    ok("root-hyperplanes", "120 roots x 511 hyperplanes; unique singleton {r}, other costs >= 24; orthogonal rank 7")


def read_designs(model):
    with open(DATA, encoding="utf-8") as stream:
        data = json.load(stream)
    designs = data["designs"]
    require(len(designs) == 25, "one design for every d in 0..24")
    results = {}
    for row in designs:
        d = row["d"]
        require(type(d) is int and 0 <= d <= 24 and d not in results, "distinct valid d")
        require(len(row["D"]) == d and len(row["terms"]) == 8, "certificate sizes")
        vectors = row["D"] + [v for pair in row["terms"] for v in pair]
        require(all(len(v) == 8 and all(type(x) is int for x in v) for v in vectors), "integer 8-vectors")
        deleted = [model.line_of(v) for v in row["D"]]
        require(len(deleted) == len(set(deleted)) == d, "distinct deleted lines")
        terms = [(tuple(u), tuple(w)) for u, w in row["terms"]]
        require(len(terms) == 8, "eight terms")
        require(all(len(u) == len(w) == 8 and any(u) and any(w) for u, w in terms), "term dimensions")
        cost, prices, determinant = model.design_cost(deleted, terms)
        expected = 72 - 2 * min(d, 8)
        require(cost == row["claimed_c"] == expected, "exact attained floor")
        require(determinant != 0, "invertible M")
        results[d] = (cost, prices, determinant)
    ok("designs", "25 exact certificates: c = 72 - 2 min(d,8), d=0..24, all det M != 0")
    return designs, results


def check_controls(model, designs, results):
    terms = [(tuple(u), tuple(w)) for u, w in designs[8]["terms"]]
    simple = [model.line_of(SIMPLE[k]) for k in range(1, 9)]
    require(set(simple) == {model.line_of(v) for v in designs[8]["D"]}, "d=8 deletes the simple roots")
    require(results[8] == (56, [7] * 8, 65536), "d=8 determinant and prices")
    require(not scalar_matrix(terms), "the example has nonscalar M")
    require(112 - results[8][0] == 56 and results[8][0] < 72 - 8, "c >= 72-d is false here")
    same = [(SIMPLE[k], SIMPLE[k]) for k in range(1, 9)]
    cost, prices, determinant = model.design_cost(simple, same)
    require(cost == 64 and prices == [8] * 8 and determinant != 0, "identity pairing costs 64")
    cost, prices, determinant = model.design_cost([], terms)
    require(cost == 72 and prices == [9] * 8 and determinant != 0, "restoring D costs 72")
    singular = [(SIMPLE[1], SIMPLE[1])] * 8
    require(model.design_cost([], singular)[2] == 0, "singular repeated terms rejected")
    require(rank_q([SIMPLE[1], SIMPLE[1]]) == 1, "parallel deficient directions cannot enter a basis twice")
    ok("controls", "identity pairing 64; no deletions 72; singular terms detected; d=8 M is nonscalar")


def main():
    model = Model()
    self_checks(model)
    check_census(model)
    check_root_hyperplanes(model)
    designs, results = read_designs(model)
    check_controls(model, designs, results)
    print("PASS_P104_GRAM_CLASS_EXACT_FLOOR designs=25 root_hyperplanes=61320 no_new_kappa")


if __name__ == "__main__":
    main()
