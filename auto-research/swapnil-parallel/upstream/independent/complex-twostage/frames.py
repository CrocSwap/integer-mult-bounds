"""Binary frame labels of the complex producer over F2^h with the dot product, and the residual checks.

Label of a node (a subspace of F2^h, h = points): an input triple t -> <t>; a node whose >= 2 triples share a common
pair -> span of their indicator vectors; otherwise the coordinate space of the covered points.
A frame change U -> V is a valid whole-residual child iff U, V are nested and the residual (larger ∩ smaller^perp)
is nondegenerate and nonalternating (has an orthonormal basis). The checker verifies, for every active node,
  - the label itself as the entry residual from the low frame 0 (also: the copied-centre COPY transform L -> 0),
  - its complement in F = F2^h as the exit residual to the high frame (also: the copied-centre DIRECT move L -> F),
  - every producer edge (argument label -> node label) and piece edge (node label -> t_S^perp).
Two-stage lifts preserve this: stage-one frames are L (x) t, stage-two frames D0 + t (x) L, D0 = t^perp (x) F; for a
weight-3 triple t (t.t = 1, odd weight) the lifted residual R (x) t, resp. t (x) R, is nondegenerate and
nonalternating iff R is (Gram matrix is unchanged; wt(r (x) t) = 3 wt(r) is odd iff wt(r) is).
Usage: python3 frames.py 24   (prints edges checked and bad count)"""
import sys


def echelon(vs):
    b = {}
    for x in vs:
        for p, y in b.items():
            if x & p: x ^= y
        if not x: continue
        p = x & -x
        for q in list(b):
            if b[q] & p: b[q] ^= x
        b[p] = x
    return b
def red(b, x):
    for p, y in b.items():
        if x & p: x ^= y
    return x
def dot(a, b): return bin(a & b).count('1') & 1
def perp_in(V, U):
    """basis of span(V) ∩ U^perp."""
    rows = [(sum(dot(v, u) << j for j, u in enumerate(U)), 1 << i) for i, v in enumerate(V)]
    for col in range(len(U)):
        bit = 1 << col
        idx = next((i for i, (a, _) in enumerate(rows) if a & bit), None)
        if idx is None: continue
        pa, pb = rows.pop(idx)
        rows = [(a ^ pa, b ^ pb) if a & bit else (a, b) for a, b in rows]
    out = []
    for a, b in rows:
        x = 0
        for i, v in enumerate(V):
            if b >> i & 1: x ^= v
        out.append(x)
    return out
def nondeg(B):
    return len(echelon([sum(dot(a, b) << j for j, b in enumerate(B)) for a in B])) == len(B)
def ok_res(R):
    """nondegenerate and nonalternating (some odd-weight vector), i.e. an orthonormal basis exists."""
    return (not R) or (nondeg(R) and any(bin(x).count('1') & 1 for x in R))


class Checker:
    def __init__(s, c): s.c = c; s.h = c.h; s.cache = {}; s.lab = {}
    def tvec(s, i): return sum(1 << p for p in s.c.triples[i])
    def label(s, n):
        if n in s.lab: return s.lab[n]
        c = s.c; sp = c.sup[n]; idx = []
        while sp:
            lo = sp & -sp; idx.append(lo.bit_length() - 1); sp ^= lo
        if len(idx) == 1: B = [s.tvec(idx[0])]
        else:
            common = set(c.triples[idx[0]])
            for i in idx[1:]: common &= set(c.triples[i])
            if len(common) >= 2: B = list(echelon([s.tvec(i) for i in idx]).values()); assert len(B) == len(idx)
            else: X = c.cover(n); B = [1 << p for p in range(s.h) if X >> p & 1]
        B = sorted(echelon(B).values()); s.lab[n] = B; return B
    def edge(s, U, V):
        key = (tuple(U), tuple(V))
        if key not in s.cache:
            bV = echelon(V)
            s.cache[key] = all(red(bV, u) == 0 for u in U) and ok_res(perp_in(V, U))
        return s.cache[key]
    def run(s):
        c = s.c; bad = 0; n_e = 0; F = [1 << p for p in range(s.h)]
        for n in c.active:
            L = s.label(n)
            n_e += 2; bad += (not (nondeg(L) and ok_res(L))) + (not ok_res(perp_in(F, L)))   # entry / exit residuals
            if c.args[n]:
                for a in c.args[n]:
                    n_e += 1; bad += not s.edge(s.label(a), L)
        for S, n, _ in c.pieces:
            n_e += 1; bad += not s.edge(s.label(n), perp_in(F, [sum(1 << p for p in S)]))
        return dict(edges=n_e, bad=bad, labels=len(s.lab))


if __name__ == '__main__':
    from producer import NStar3
    for h in map(int, sys.argv[1:]): print(h, Checker(NStar3(h)).run(), flush=True)
