"""Implementation B (code-disjoint from lib/jet.py, which it does not import): (J1) as sparse sets of named
variables, Markowitz-style sparse elimination, flows checked by symmetric difference, and an exhaustive Python
minimum-cost enumerator (independent of c/enumall.c).
Written for this package (thakrarsagar, with AI assistance from Claude Opus 5.5). Apache-2.0."""
from itertools import product


def ip(a, b):
    s = 0
    for k in range(3):
        s += a[k] * b[k]
    return s


def sup_of(x):
    return {k for k in range(3) if x[k] != 0}


def the_pool():
    reps = []
    for x in product((-1, 0, 1), repeat=3):
        nz = [c for c in x if c != 0]
        if nz and nz[0] == 1:
            reps.append(x)
    return [(a, b) for a in reps for b in reps if ip(a, b) != 0]


def incidences(L):
    out = []
    for t in range(len(L)):
        for s in range(len(L)):
            if t == s or ip(L[t][0], L[s][1]) != 0:
                continue
            D = sup_of(L[t][0]) & sup_of(L[s][1])
            if D:
                out.append((t, s, frozenset(D)))
    return out


def eq(t, s, D):
    """(J1) row / delta'_t as a set of variable names (unit world: phi = 1 on supports)."""
    return frozenset([('x', t, i) for i in D] + [('y', s, i) for i in D])


def harmonic(L):
    return [t for t in range(len(L)) if len(sup_of(L[t][0]) & sup_of(L[t][1])) == 2]


def unknowns(L):
    return [('x', t, i) for t in range(len(L)) for i in sorted(sup_of(L[t][0]))] + \
           [('y', t, i) for t in range(len(L)) for i in sorted(sup_of(L[t][1]))]


class Sparse:
    def __init__(self, rows):
        active = [set(r) for r in rows if r]
        cols = sorted({c for r in active for c in r})
        self.piv = []
        for c in cols:
            cand = [r for r in active if c in r]
            if not cand:
                continue
            p = min(cand, key=len)
            for r in cand:
                if r is not p:
                    r ^= p
            active = [r for r in active if r is not p and r]
            self.piv.append((c, frozenset(p)))
        self.rank = len(self.piv)

    def member(self, vec):
        v = set(vec)
        for c, p in self.piv:
            if c in v:
                v ^= p
        return not v


def immovable(L):
    S = Sparse([eq(*e) for e in incidences(L)])
    return [t for t in harmonic(L) if S.member(eq(t, t, sup_of(L[t][0]) & sup_of(L[t][1])))]


def flow_ok(L, t, edges):
    """edges: list of (t', s') pairs. True iff every edge is an incidence and the rows sum to delta'_t."""
    acc = set()
    for (a, b) in edges:
        if a == b or ip(L[a][0], L[b][1]) != 0:
            return False
        D = sup_of(L[a][0]) & sup_of(L[b][1])
        if not D:
            return False
        acc ^= eq(a, b, D)
    return acc == set(eq(t, t, sup_of(L[t][0]) & sup_of(L[t][1])))


def lowbit_rank(rows):
    r = 0
    rows = [x for x in rows if x]
    while rows:
        x = rows.pop()
        low = x & -x
        rows = [y ^ x if y & low else y for y in rows]
        rows = [y for y in rows if y]
        r += 1
    return r


def min_cost(L, keep=None):
    """Exhaustive minimum of sum_j rank_F2 B[R_j, A_j] over admissible B (unit diagonal, off-diagonal support
    inside the incidences that meet some block). Returns (min, number of minimisers); if keep is a list, the
    off-diagonal supports of the minimisers are stored in it."""
    v = len(L)
    inc = [(t, s) for (t, s, D) in incidences(L)]
    R = [[t for t in range(v) if L[t][0][j]] for j in range(3)]
    A = [[s for s in range(v) if L[s][1][j]] for j in range(3)]
    best, cnt = None, 0
    for mask in range(1 << len(inc)):
        on = {inc[k] for k in range(len(inc)) if mask >> k & 1}
        c = 0
        for j in range(3):
            rows = []
            for t in R[j]:
                x = 0
                for b, s in enumerate(A[j]):
                    if s == t or (t, s) in on:
                        x |= 1 << b
                rows.append(x)
            c += lowbit_rank(rows)
        if best is None or c < best:
            best, cnt = c, 1
            if keep is not None:
                keep[:] = [on]
        elif c == best:
            cnt += 1
            if keep is not None:
                keep.append(on)
    return best, cnt
