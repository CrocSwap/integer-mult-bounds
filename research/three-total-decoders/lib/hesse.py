"""Rank-3 decoder configurations built on the Hesse configuration over Q(w), w^2 + w + 1 = 0 (Eisenstein integers a + b w as pairs).
Adapted from the working card g1/hesse.py (module-level search loop removed; the exhaustive evaluation is kit.enum_raw).
A configuration is a list of (point, line) pairs with p.q != 0; incidence p.q = 0 is evaluated in Z[w]."""
import itertools, os, sys, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit

Z = (0, 0); O = (1, 0); W = (0, 1); W2 = (-1, -1)
def add(x, y): return (x[0] + y[0], x[1] + y[1])
def neg(x): return (-x[0], -x[1])
def mul(x, y): a, b = x; c, d = y; return (a * c - b * d, a * d + b * c - b * d)
def dot(p, q):
    s = Z
    for a, b in zip(p, q): s = add(s, mul(a, b))
    return s
def cross(a, b):
    return (add(mul(a[1], b[2]), neg(mul(a[2], b[1]))), add(mul(a[2], b[0]), neg(mul(a[0], b[2]))), add(mul(a[0], b[1]), neg(mul(a[1], b[0]))))
def nz(x): return x != Z
def same(p, q): return all(not nz(x) for x in cross(p, q))
def inc(p, l): return not nz(dot(p, l))

def hesse():
    ws = [O, W, W2]; pts = []
    for k in range(3):
        pts += [(Z, O, neg(ws[k])), (neg(ws[k]), Z, O), (O, neg(ws[k]), Z)]
    lines = []
    for a, b in itertools.combinations(pts, 2):
        l = cross(a, b)
        if not any(same(l, m) for m in lines): lines.append(l)
    xp = list(pts)
    for a, b in itertools.combinations(lines, 2):
        p = cross(a, b)
        if not any(same(p, q) for q in xp): xp.append(p)
    return pts, lines, xp

def evaluate(P, Q, cap=26):
    """Exhaustive minimum of cost over all admissible B: returns (v, f, best); best is None (not evaluated) if f > cap."""
    v = len(P)
    R = [[t for t in range(v) if nz(P[t][j])] for j in range(3)]; A = [[s for s in range(v) if nz(Q[s][j])] for j in range(3)]
    free = [(t, s) for t in range(v) for s in range(v) if t != s and inc(P[t], Q[s]) and any(t in R[j] and s in A[j] for j in range(3))]
    if len(free) > cap: return v, len(free), None
    best, _ = kit.enum_raw(v, R, A, free)
    return v, len(free), best

def transform(M, p): return tuple(dot(r, p) for r in M)

def random_config(rng, xp, pts, lines, v=None):
    """The sampler of the working card: random projective change of coordinates (so the coordinate triangle is generic), points from the
    9 Hesse points or all 21 intersection points, lines from the 12 Hesse lines; pairs (p,l) with p.l != 0 chosen biased towards incidences."""
    if rng.random() < 0.3: M = [[O, Z, Z], [Z, O, Z], [Z, Z, O]]
    else:
        while True:
            M = [[(rng.randint(-2, 2), rng.randint(-1, 1)) for _ in range(3)] for _ in range(3)]
            if nz(dot(M[0], cross(M[1], M[2]))): break
    cof = [cross(M[1], M[2]), cross(M[2], M[0]), cross(M[0], M[1])]
    PP = [transform(M, p) for p in (xp if rng.random() < 0.5 else pts)]
    LL = [transform(cof, l) for l in lines]
    pairs = [(p, l) for p in PP for l in LL if not inc(p, l)]
    v = v or rng.randint(6, 12); P = []; Q = []
    for _ in range(v):
        cand = rng.sample(pairs, min(12, len(pairs)))
        sc = lambda pl: sum(inc(pl[0], q) for q in Q) + sum(inc(p, pl[1]) for p in P) + rng.random()
        p, l = max(cand, key=sc); P.append(p); Q.append(l)
    return P, Q
