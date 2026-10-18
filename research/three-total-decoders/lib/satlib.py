"""Small exact SAT encodings (python-sat, CaDiCaL): rank factorisations over F2 of the three blocks of an admissible B.
build_ranks: all B with rank B[R_j,A_j] <= rs[j] (used to enumerate the optima of tied_min).
cost_leq:    one CNF 'cost <= K' (per block a factorisation with c_j active columns, total active <= K); returns a B or None.
Adapted from fprime/enumB.py and fprime/costsat2.py of the working cards (see NOTICE.md)."""
from pysat.solvers import Cadical153
from pysat.formula import IDPool
from pysat.card import CardEnc, EncType


def _inc(P, Q):
    return lambda t, s: t != s and sum(a * b for a, b in zip(P[t], Q[s])) == 0


def _factor(cl, pool, P, Q, j, c, R, A, Bv, tag=''):
    for t in R:
        for s in A:
            target = Bv(t, s)
            ands = []
            for k in range(c):
                x = pool.id(('X', j, t, k)); y = pool.id(('Y', j, k, s)); z = pool.id(('Z', j, t, s, k))
                cl += [[-z, x], [-z, y], [z, -x, -y]]; ands.append(z)
            if not ands:
                if target is True: cl.append([])
                elif target is not False: cl.append([-target])
                continue
            acc = ands[0]
            for z in ands[1:]:
                n = pool.id(('C', j, t, s, z)); cl += [[-n, acc, z], [-n, -acc, -z], [n, -acc, z], [n, acc, -z]]; acc = n
            if target is True: cl.append([acc])
            elif target is False: cl.append([-acc])
            else: cl += [[-acc, target], [acc, -target]]


def build_ranks(P, Q, rs):
    v = len(P); pool = IDPool(); cl = []; inc = _inc(P, Q)
    def Bv(t, s):
        if t == s: return True
        if inc(t, s): return pool.id(('B', t, s))
        return False
    for j, r in enumerate(rs):
        R = [t for t in range(v) if P[t][j]]; A = [s for s in range(v) if Q[s][j]]
        _factor(cl, pool, P, Q, j, r, R, A, Bv)
    bvars = {(t, s): pool.id(('B', t, s)) for t in range(v) for s in range(v) if inc(t, s)}
    return cl, bvars


def enumerate_B(P, Q, rs, limit=10 ** 6):
    """All distinct B (as set of (t,s) off-diagonal ones) with block ranks <= rs, by blocking clauses on the B variables."""
    cl, bv = build_ranks(P, Q, rs); s = Cadical153(bootstrap_with=cl); out = []
    while len(out) < limit and s.solve():
        m = set(l for l in s.get_model() if l > 0)
        out.append(sorted(k for k, x in bv.items() if x in m))
        s.add_clause([-x if x in m else x for x in bv.values()])
    return out


def cost_leq(P, Q, K):
    v = len(P); pool = IDPool(); cl = []; inc = _inc(P, Q); act = []
    def Bv(t, s):
        if t == s: return True
        if inc(t, s): return pool.id(('B', t, s))
        return False
    for j in range(3):
        R = [t for t in range(v) if P[t][j]]; A = [s for s in range(v) if Q[s][j]]
        c = min(len(R), len(A), K)
        e = [pool.id(('e', j, k)) for k in range(c)]; act += e
        for k in range(c - 1): cl.append([-e[k + 1], e[k]])
        for t in R:
            for k in range(c): cl.append([-pool.id(('X', j, t, k)), e[k]])
        _factor(cl, pool, P, Q, j, c, R, A, Bv)
    card = CardEnc.atmost(lits=act, bound=K, top_id=pool.top, encoding=EncType.seqcounter)
    s = Cadical153(bootstrap_with=cl + card.clauses)
    if not s.solve(): return None
    m = set(l for l in s.get_model() if l > 0)
    return [[1 if t == u else (1 if inc(t, u) and pool.id(('B', t, u)) in m else 0) for u in range(v)] for t in range(v)]
