#!/usr/bin/env python3
"""Literal check of PR #4601 (petalas) on a noncommutative local algebra and further local rings.

#4601 (head 4b2322fc): over a finite product R of local K-algebras (non-units a proper two-sided ideal J, no
commutativity assumed), for invertible 2 x 2 targets M in the two-role alphabet
    paid factors P(u, y) = I + u y^T (u in R^2, y in K^2), free maps GL_2(K) anywhere,
    delta_R(M) = min_{T in GL_2(K)} dim_K((M T - I) K^2),
it proves  cost_R(M) <= 2 iff cost_D(Mbar) <= 2,  and  cost_R(M) = max(delta_R(M), cost_D(Mbar)),  D = R/J.
Its census enumerates (F2[e]/e^2)^k, k <= 3 (commutative).

Independent literal check (no pivot test, no imported predecessor code): costs are computed from the definition as
the least c with M in S_c, S_0 = GL_2(K), S_c = S_{c-1} P GL_2(K). Because g P(u,y) g^-1 = P(g u, g^-T y), it
suffices to multiply right-coset representatives of S_{c-1} by every paid factor. Paid factors are restricted to
invertible ones: M_2 of a finite ring is finite, hence Dedekind-finite, so a product is invertible only if every
factor is. Residue costs over D are computed the same way over D. Rings, all with k = 1:
  * T4 = F4[e; Frobenius]/e^2 over K = F2: (a + b e)(c + d e) = ac + (ad + b c^2) e; NONCOMMUTATIVE local, D = F4;
  * F2[x]/x^3 (K = F2, D = F2), F3[e]/e^2 (K = F3, D = F3);
  * F2[e]/e^2, whose cost histogram must reproduce #4601's published k = 1 histogram [6, 54, 36, 0].
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from itertools import product
import json
import sys

GF4_MUL = [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 3, 1], [0, 3, 1, 2]]   # 2 = w, 3 = w + 1, w^2 = w + 1


def need(condition, message):
    if not condition:
        raise AssertionError(message)


class Ring:
    def __init__(self, name, elems, add, mul, p, scalar, coords, residue):
        self.name, self.p = name, p
        self.elems = list(elems)
        self.index = {e: i for i, e in enumerate(self.elems)}
        n = len(self.elems)
        self.add = [[self.index[add(a, b)] for b in self.elems] for a in self.elems]
        self.mul = [[self.index[mul(a, b)] for b in self.elems] for a in self.elems]
        self.zero, self.one = self.index[scalar(0)], self.index[scalar(1)]
        self.scalar = [self.index[scalar(k)] for k in range(p)]
        self.neg = [next(j for j in range(n) if self.add[i][j] == self.zero) for i in range(n)]
        self.coords = [coords(e) for e in self.elems]
        self.residue = [residue(e) for e in self.elems]
        self.units = {i for i in range(n) if any(self.mul[i][j] == self.one and self.mul[j][i] == self.one
                                                 for j in range(n))}

    def mat_mul(self, x, y):
        a, m = self.add, self.mul
        return (a[m[x[0]][y[0]]][m[x[1]][y[2]]], a[m[x[0]][y[1]]][m[x[1]][y[3]]],
                a[m[x[2]][y[0]]][m[x[3]][y[2]]], a[m[x[2]][y[1]]][m[x[3]][y[3]]])

    def invertible(self, x):
        """v -> x v is a right-linear self-map of the finite module R^2; it is invertible iff injective, and its
        inverse is again left multiplication by a matrix, so x is invertible iff the kernel is zero."""
        a, m, z = self.add, self.mul, self.zero
        return not any(a[m[x[0]][v1]][m[x[1]][v2]] == z and a[m[x[2]][v1]][m[x[3]][v2]] == z
                       for v1, v2 in self.nonzero_vectors)

    def setup(self):
        n = len(self.elems)
        self.ident = (self.one, self.zero, self.zero, self.one)
        self.nonzero_vectors = [v for v in product(range(n), repeat=2) if v != (self.zero, self.zero)]
        self.gl = [x for x in product(range(n), repeat=4) if self.invertible(x)]
        self.glset = set(self.gl)
        s = self.scalar
        self.free = [g for g in (tuple(s[v] for v in t) for t in product(range(self.p), repeat=4)) if g in self.glset]
        self.paid = []
        for u1, u2 in product(range(n), repeat=2):
            for y1, y2 in product(range(self.p), repeat=2):
                if (y1, y2) == (0, 0):
                    continue
                m = self.mul
                f = (self.add[self.one][m[u1][s[y1]]], m[u1][s[y2]], m[u2][s[y1]], self.add[self.one][m[u2][s[y2]]])
                if f in self.glset:
                    self.paid.append(f)
        return self

    def costs(self, max_cost=4):
        cost = {g: 0 for g in self.free}
        layer = set(self.free)
        for c in range(1, max_cost + 1):
            reps = {min(self.mat_mul(x, g) for g in self.free) for x in layer}
            new = set()
            for x in reps:
                for f in self.paid:
                    t = self.mat_mul(x, f)
                    for g in self.free:
                        h = self.mat_mul(t, g)
                        if h not in cost:
                            cost[h] = c
                            new.add(h)
            layer = {h for h, v in cost.items() if v <= c}
            if len(cost) == len(self.gl):
                break
        return cost

    def delta(self, x):
        best = 2
        for t in self.free:
            mt = self.mat_mul(x, t)
            cols = []
            for j in range(2):
                e1 = self.add[mt[j]][self.neg[self.one if j == 0 else self.zero]]
                e2 = self.add[mt[2 + j]][self.neg[self.one if j == 1 else self.zero]]
                cols.append(self.coords[e1] + self.coords[e2])
            best = min(best, rank_mod(cols, self.p))
        return best



def rank_mod(rows, p):
    rows, r = [list(x) for x in rows], 0
    for c in range(len(rows[0])):
        piv = next((i for i in range(r, len(rows)) if rows[i][c] % p), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = pow(rows[r][c], p - 2, p)
        rows[r] = [v * inv % p for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] % p:
                f = rows[i][c]
                rows[i] = [(a - f * b) % p for a, b in zip(rows[i], rows[r])]
        r += 1
    return r


def gf4_bits(a):
    return (a & 1, a >> 1 & 1)


def rings():
    t4 = Ring("F4[e;Frob]/e^2 over F2", product(range(4), repeat=2),
              lambda x, y: (x[0] ^ y[0], x[1] ^ y[1]),
              lambda x, y: (GF4_MUL[x[0]][y[0]], GF4_MUL[x[0]][y[1]] ^ GF4_MUL[x[1]][GF4_MUL[y[0]][y[0]]]),
              2, lambda k: (k, 0), lambda e: gf4_bits(e[0]) + gf4_bits(e[1]), lambda e: (e[0],))
    f4 = Ring("F4 over F2", product(range(4), repeat=1), lambda x, y: (x[0] ^ y[0],),
              lambda x, y: (GF4_MUL[x[0]][y[0]],), 2, lambda k: (k,), lambda e: gf4_bits(e[0]), lambda e: e)

    def trunc(p, length):
        def mul(x, y):
            out = [0] * length
            for i in range(length):
                for j in range(length - i):
                    out[i + j] = (out[i + j] + x[i] * y[j]) % p
            return tuple(out)
        return Ring("F%d[x]/x^%d" % (p, length), product(range(p), repeat=length),
                    lambda x, y: tuple((a + b) % p for a, b in zip(x, y)), mul, p,
                    lambda k: (k,) + (0,) * (length - 1), lambda e: e, lambda e: (e[0],))

    def field(p):
        return Ring("F%d" % p, product(range(p), repeat=1), lambda x, y: ((x[0] + y[0]) % p,),
                    lambda x, y: (x[0] * y[0] % p,), p, lambda k: (k,), lambda e: e, lambda e: e)
    return [(t4, f4), (trunc(2, 3), field(2)), (trunc(3, 2), field(3)), (trunc(2, 2), field(2))]


def main():
    out = {}
    for big, small in rings():
        big.setup()
        small.setup()
        if big.name.startswith("F4[e"):
            x, y = big.index[(2, 0)], big.index[(0, 1)]
            need(big.mul[x][y] != big.mul[y][x], "T4 is noncommutative")
        need(all((big.residue[i] != (0,)) == (i in big.units) for i in range(len(big.elems))), "local: units by residue")
        need(all(big.mul[a][j] not in big.units and big.mul[j][a] not in big.units
                 for j in range(len(big.elems)) if j not in big.units for a in range(len(big.elems))),
             "non-units form a two-sided ideal")
        cost_r, cost_d = big.costs(), small.costs()
        need(len(cost_r) == len(big.gl) and len(cost_d) == len(small.gl), "every invertible target reached")
        res_index = {e: i for i, e in enumerate(small.elems)}
        hist, bad, residue_only_wrong = [0] * 4, 0, 0
        for m, c in cost_r.items():
            mbar = tuple(res_index[big.residue[v]] for v in m)
            hist[c] += 1
            cd = cost_d[mbar]
            bad += (c != max(big.delta(m), cd)) + ((c <= 2) != (cd <= 2))
            residue_only_wrong += c != cd
        need(bad == 0, "#4601 formula and two-factor invariance on every target of %s" % big.name)
        need(residue_only_wrong > 0, "failure control: the residue cost alone is wrong on some targets")
        out[big.name] = {"invertible_targets": len(big.gl), "cost_histogram_0_3": hist,
                         "targets_where_delta_raises_cost": residue_only_wrong,
                         "free": len(big.free), "paid_invertible_factors": len(big.paid)}
    need(out["F2[x]/x^2"]["cost_histogram_0_3"] == [6, 54, 36, 0], "#4601 published k = 1 histogram")
    out["F2[e]/e^2 (= F2[x]/x^2) control"] = out.pop("F2[x]/x^2")
    print(json.dumps({"status": "PASS_PR4601_LITERAL_LOCAL_CHECK", "rings": out, "new_kappa_claimed": False},
                     indent=1))


if __name__ == "__main__":
    sys.exit(main())
