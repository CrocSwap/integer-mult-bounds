"""SEPPAYS gen2.py (own code): carrier-biased pinned-run generator (hot intake on purpose).
F (forward, recorded): helpers absorb Y's / other helpers at low charts and climb free; owned registers take token copies
(helper snapshots) at low charts, climb (paid), take HOT reads of helpers at high charts and subtract copies.
G: token-cancelling deliveries into X_t from every source at chart >= chart(X_t) (helpers, owned, Y).
F^-1: reversed ADDs; a public<-public reverse ADD that is chart-illegal is done through a paid owned cleaner
(INIT at the source chart, copy, climb to the join, subtract, CLEAR); owned source climbs; owned dest descends free."""
import random
from fractions import Fraction as Fr
from eng import *
from gen import nullspace, rand_up

def gen2(n, P, F, rng, nh=2, no=2, LF=30, p_up=0.1, lams=None):
    T = len(P); ALL = frozenset(range(1 << n))
    if lams is None: lams = [1] if F.p == 2 else [1, -1, Fr(1, 2), Fr(-1, 2), 2]
    qperp = [perp([q], n) for q in P]
    meta = dict(nh=nh, Xch=[span([q]) for q in P], Ych=[frozenset([0])] * T, Hch=[frozenset([0])] * nh)
    R = Run(n, P, F, **meta)
    for k in range(no): R.INIT(('O', k), frozenset([0]))
    H = [('H', j) for j in range(nh)]; O = [('O', k) for k in range(no)]; Y = [('Y', t) for t in range(T)]
    hist = []
    def add(d, l, e):
        R.ADD(d, l, e); hist.append((d, R.F.c(l), e))
    for _ in range(LF):
        u = rng.random()
        if u < 0.2:                                  # Y climbs inside q^perp (free) so helpers can read it higher
            y = rng.choice(Y); D = rand_up(R.reg[y][0], n, qperp[y[1]], rng)
            if D != R.reg[y][0]: R.MOVE(y, D)
        elif u < 0.4 and H:                          # helper climbs (free)
            h = rng.choice(H); D = rand_up(R.reg[h][0], n, ALL, rng)
            if D != R.reg[h][0]: R.MOVE(h, D)
        elif u < 0.4 + p_up and O:                   # owned climbs (paid)
            o = rng.choice(O); D = rand_up(R.reg[o][0], n, ALL, rng)
            if D != R.reg[o][0]: R.MOVE(o, D)
        elif u < 0.55 and O:                         # owned descends (free)
            o = rng.choice(O); C = R.reg[o][0]
            if fdim(C) > 0:
                R.MOVE(o, rng.choice([D for D in subspaces_containing(frozenset([0]), n, C) if fdim(D) == fdim(C) - 1]))
        else:                                        # ADD, biased to carrier patterns
            kind = rng.random()
            if kind < 0.35 and H: d = rng.choice(H); pool = Y + H
            elif kind < 0.8 and O: d = rng.choice(O); pool = H + O + Y
            else: d = rng.choice(H + O + Y) if (H or O) else rng.choice(Y); pool = H + O + Y
            cands = [e for e in pool if e != d and R.reg[d][0] <= R.reg[e][0]]
            if cands: add(d, rng.choice(lams), rng.choice(cands))
    for t in range(T):
        X = ('X', t)
        srcs = [e for e in R.reg if e[0] in 'HOY' and R.reg[X][0] <= R.reg[e][0]]
        if not srcs: continue
        toks = [{k: v for k, v in R.reg[e][1].items() if k[0] != 'y'} for e in srcs]
        NS = nullspace(toks, F)
        lam = [F.c(0)] * len(srcs)
        for b in NS:
            c = rng.choice(lams + [0])
            lam = [F.add(a, F.c(c) * x) for a, x in zip(lam, b)]
        for e, l in zip(srcs, lam):
            if l != 0: R.ADD(X, l, e)
    nc = 0
    for (d, lam, e) in reversed(hist):
        nl = (-lam) % 2 if F.p == 2 else -lam
        if not R.reg[d][0] <= R.reg[e][0]:
            if d[0] == 'O': R.MOVE(d, R.reg[d][0] & R.reg[e][0])
            elif e[0] == 'O': R.MOVE(e, span(list(R.reg[e][0] | R.reg[d][0])))
            else:
                if e[0] in "HX" or (e[0] == "Y" and not span(list(R.reg[e][0] | R.reg[d][0])) <= qperp[e[1]]):
                    c = ('C', nc); nc += 1
                    R.INIT(c, R.reg[e][0]); R.ADD(c, 1, e); R.MOVE(c, span(list(R.reg[e][0] | R.reg[d][0])))
                    R.ADD(d, nl, c); R.CLEAR(c); continue
                R.MOVE(e, span(list(R.reg[e][0] | R.reg[d][0])))
        R.ADD(d, nl, e)
    for k in range(no): R.CLEAR(('O', k))
    return R, meta
