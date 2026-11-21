"""SEPPAYS gen.py (own code): generator of RESTORATION-RESPECTING (pinned) runs with hot intake, Bennett form F ; G ; F^-1.
F: random ADDs (owned/helpers/Y as destinations and sources; X destination only; X never read), free public ascents,
   owned moves (rare paid ascents).  Owned registers read helpers at any chart => hot intakes.
G: for each X_t, a random combination of sources at charts >= chart(X_t) whose token/x-parts cancel (nullspace), delivered
   into X_t => X_t = x_t + Rec_t.y, token-free (public hot deliveries allowed).
F^-1: reversed ADDs with -lam (publics stay high; owned dest descends freely / owned source climbs if needed).
Since X is never read and G only touches X, every helper / Y / owned content returns exactly => pinned. Verified by replay."""
import random
from fractions import Fraction as Fr
from eng import *

def nullspace(vecs, F):
    """vecs: list of dict sym->coef; return basis of {lam : sum lam_i vecs_i = 0}"""
    syms = sorted({k for v in vecs for k in v})
    m = len(vecs)
    # matrix rows = syms, cols = vecs
    A = [[v.get(k, F.c(0)) for v in vecs] for k in syms]
    piv = []; r = 0
    A = [row[:] for row in A]
    for c in range(m):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None: continue
        A[r], A[p] = A[p], A[r]
        inv = (1 if F.p == 2 else 1 / A[r][c])
        A[r] = [(x * inv) % 2 if F.p == 2 else x * inv for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [((a - f * b) % 2 if F.p == 2 else a - f * b) for a, b in zip(A[i], A[r])]
        piv.append(c); r += 1
    free = [c for c in range(m) if c not in piv]
    basis = []
    for fc in free:
        v = [F.c(0)] * m; v[fc] = F.c(1)
        for i, pc in enumerate(piv):
            v[pc] = (-A[i][fc]) % 2 if F.p == 2 else -A[i][fc]
        basis.append(v)
    return basis

def rand_up(C, n, within, rng):
    cand = [v for v in within if v not in C]
    if not cand: return C
    D = span(list(C) + [rng.choice(cand)])
    return D if D <= within else C

def gen(n, P, F, rng, nh=2, no=2, LF=30, p_up=0.08, lams=None, ych_rand=0.3, deliver_frac=1.0):
    T = len(P); ALL = frozenset(range(1 << n))
    if lams is None: lams = [1] if F.p == 2 else [1, -1, Fr(1, 2), Fr(-1, 2), 2]
    qperp = [perp([q], n) for q in P]
    Ych = [frozenset([0]) if rng.random() > ych_rand else rand_up(frozenset([0]), n, qperp[t], rng) for t in range(T)]
    Xch = [span([q]) for q in P]
    Hch = [frozenset([0]) if rng.random() < 0.6 else rand_up(frozenset([0]), n, ALL, rng) for _ in range(nh)]
    meta = dict(nh=nh, Xch=Xch, Ych=Ych, Hch=Hch)
    R = Run(n, P, F, **meta)
    for k in range(no):
        R.INIT(('O', k), frozenset([0]) if rng.random() < 0.7 else rand_up(frozenset([0]), n, ALL, rng))
    pubs = [r for r in R.reg if r[0] in 'XYH']
    hist = []
    for _ in range(LF):
        u = rng.random()
        if u < 0.25:
            r = rng.choice([p for p in pubs if p[0] == 'H'] or pubs)
            if rng.random() < 0.3: r = rng.choice(pubs)
            within = qperp[r[1]] if r[0] == 'Y' else ALL
            D = rand_up(R.reg[r][0], n, within, rng)
            if D != R.reg[r][0]: R.MOVE(r, D)
        elif u < 0.25 + p_up and no:
            r = ('O', rng.randrange(no)); D = rand_up(R.reg[r][0], n, ALL, rng)
            if D != R.reg[r][0]: R.MOVE(r, D)
        elif u < 0.35 and no:
            r = ('O', rng.randrange(no)); C = R.reg[r][0]
            if fdim(C) > 0:
                subs = [D for D in subspaces_containing(frozenset([0]), n, C) if fdim(D) == fdim(C) - 1]
                R.MOVE(r, rng.choice(subs))
        else:
            dests = [r for r in R.reg if r[0] in 'HOYX']
            srcs = [r for r in R.reg if r[0] in 'HOY']
            d = rng.choice(dests); cands = [e for e in srcs if e != d and R.reg[d][0] <= R.reg[e][0]]
            if not cands: continue
            e = rng.choice(cands); lam = rng.choice(lams)
            R.ADD(d, lam, e); hist.append((d, R.F.c(lam), e))
    # G: deliveries
    for t in range(T):
        if rng.random() > deliver_frac: continue
        X = ('X', t)
        srcs = [e for e in R.reg if e[0] in 'HOY' and R.reg[X][0] <= R.reg[e][0]]
        if not srcs: continue
        toks = [{k: v for k, v in R.reg[e][1].items() if k[0] != 'y'} for e in srcs]
        NS = nullspace(toks, F)
        if not NS: continue
        lam = [F.c(0)] * len(srcs)
        for b in NS:
            c = rng.choice(lams + [0])
            lam = [F.add(a, F.c(c) * x) for a, x in zip(lam, b)]
        for e, l in zip(srcs, lam):
            if l != 0: R.ADD(X, l, e)
    # F^-1
    for (d, lam, e) in reversed(hist):
        if d not in R.reg or e not in R.reg: return None
        if not R.reg[d][0] <= R.reg[e][0]:
            if d[0] == 'O': R.MOVE(d, R.reg[d][0] & R.reg[e][0])
            elif e[0] == 'O': R.MOVE(e, span(list(R.reg[e][0] | R.reg[d][0])))
            else:
                D = span(list(R.reg[e][0] | R.reg[d][0]))
                if e[0] == 'Y' and not D <= qperp[e[1]]: return None
                R.MOVE(e, D)
        R.ADD(d, (-lam) % 2 if F.p == 2 else -lam, e)
    for k in range(no): R.CLEAR(('O', k))
    return R, meta
