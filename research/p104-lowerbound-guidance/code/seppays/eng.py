"""SEPPAYS eng.py (own code): exact run engine for the PINNED model (port-general).
Charts: F2-subspaces of F2^n as frozensets of ints.  Values: dict sym->coef over GF(2) (ints mod 2) or Q (Fraction).
Registers: ('X',t) target public (chart contains q_t), ('Y',s) source public (chart within q_s^perp), ('H',j) helper public
(token h_j), ('O',k) owned (start 0, INIT/CLEAR, cost = sum of ascents).  ADD d += lam*e needs chart(d) <= chart(e), d != e.
Publics only ascend.  Owned moves must be nested.  pinned(): helpers end = token, Y_s end = y_s, X_t end = x_t + y-part only."""
from fractions import Fraction as Fr
import random

dot = lambda a, b: bin(a & b).count('1') & 1
def span(vs):
    S = {0}
    for v in vs:
        if v not in S: S |= {x ^ v for x in S}
    return frozenset(S)
fdim = lambda F: len(F).bit_length() - 1
def perp(vs, n):
    return frozenset(x for x in range(1 << n) if all(not dot(x, v) for v in vs))
def subspaces_containing(C, n, within=None):
    """all subspaces D with C <= D (<= within)"""
    U = within if within is not None else frozenset(range(1 << n))
    out = {C}; frontier = [C]
    while frontier:
        nf = []
        for D in frontier:
            for v in U:
                if v not in D:
                    E = span(list(D) + [v])
                    if E <= U and E not in out: out.add(E); nf.append(E)
        frontier = nf
    return list(out)

class Field:
    def __init__(s, p): s.p = p   # p=2 -> GF(2); p=0 -> Q
    def c(s, x): return (int(x) % 2) if s.p == 2 else Fr(x)
    def add(s, a, b): return (a + b) % 2 if s.p == 2 else a + b

class Run:
    def __init__(s, n, P, F, nh=0, Xch=None, Ych=None, Hch=None):
        s.n, s.P, s.F = n, P, F
        s.reg = {}; s.start = {}; s.ops = []; s.cost = 0; s.bad = []; s.owned = set()
        for t, q in enumerate(P):
            s.reg[('X', t)] = [Xch[t] if Xch else span([q]), {('x', t): F.c(1)}]
            s.reg[('Y', t)] = [Ych[t] if Ych else frozenset([0]), {('y', t): F.c(1)}]
        for j in range(nh):
            s.reg[('H', j)] = [Hch[j] if Hch else frozenset([0]), {('h', j): F.c(1)}]
        s.start = {k: (v[0], dict(v[1])) for k, v in s.reg.items()}
        for t, q in enumerate(P):
            assert q in s.reg[('X', t)][0] and all(not dot(v, q) for v in s.reg[('Y', t)][0])
    def ispub(s, r): return r[0] in 'XYH'
    def INIT(s, r, C):
        assert r not in s.reg; s.reg[r] = [C, {}]; s.owned.add(r); s.ops.append(('INIT', r, C))
    def CLEAR(s, r):
        assert r in s.owned; del s.reg[r]; s.owned.discard(r); s.ops.append(('CLEAR', r))
    def MOVE(s, r, D):
        C = s.reg[r][0]
        if s.ispub(r):
            if not C <= D: s.bad.append(('pub-descend', len(s.ops)))
            if r[0] == 'Y' and any(dot(v, s.P[r[1]]) for v in D): s.bad.append(('Y-hot', len(s.ops)))
        else:
            if not (C <= D or D <= C): s.bad.append(('nest', len(s.ops)))
            if C <= D: s.cost += fdim(D) - fdim(C)
        s.reg[r][0] = D; s.ops.append(('MOVE', r, D))
    def ADD(s, d, lam, e):
        lam = s.F.c(lam)
        if d == e or not s.reg[d][0] <= s.reg[e][0]: s.bad.append(('add', len(s.ops), d, e))
        cd, ce = s.reg[d][1], s.reg[e][1]
        for k, v in list(ce.items()):
            nv = s.F.add(cd.get(k, s.F.c(0)), lam * v)
            if nv == 0: cd.pop(k, None)
            else: cd[k] = nv
        s.ops.append(('ADD', d, lam, e))
    def rec(s):
        """odd/even receipts: Rec[t][s'] = y_s' coefficient of final X_t"""
        T = len(s.P)
        return [[s.reg[('X', t)][1].get(('y', u), 0) for u in range(T)] for t in range(T)]
    def pinned(s):
        T = len(s.P); errs = []
        for k, (C, c) in s.reg.items():
            if k[0] == 'H' and c != {('h', k[1]): s.F.c(1)}: errs.append(k)
            if k[0] == 'Y' and c != {('y', k[1]): s.F.c(1)}: errs.append(k)
            if k[0] == 'X' and any(sym[0] != 'y' and not (sym == ('x', k[1]) and v == 1) for sym, v in c.items()): errs.append(k)
            if k[0] == 'X' and c.get(('x', k[1])) != 1: errs.append(k)
        if s.owned: errs.append('owned-alive')
        return errs

def replay(n, P, F, init_meta, ops):
    """re-execute an op list from scratch (independent legality / value check)"""
    R = Run(n, P, F, **init_meta)
    for op in ops:
        getattr(R, op[0])(*op[1:])
    return R
