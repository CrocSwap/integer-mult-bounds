"""SEPPAYS fa.py (own code): global future attribution (G2C form) on eng.Run op lists; rows -> decoder; exact identity check;
hot-intake census (owned intake whose effective content is hot at the owned chart)."""
from eng import *
from f2mass import rank2

def eff(c, finX, F):
    e = {k[1]: v for k, v in c.items() if k[0] == 'y'}
    for k, v in c.items():
        if k[0] == 'x':
            for kk, vv in finX[k[1]].items():
                if kk[0] == 'y':
                    e[kk[1]] = F.add(e.get(kk[1], F.c(0)), -v * vv if F.p == 0 else (v * vv) % 2)
    return {a: b for a, b in e.items() if b != 0}

def price(D, S, P):
    if not D or not S: return 0
    return rank2([sum(1 << j for j in S if dot(P[t], P[j])) for t in D])

def gfa(n, P, F, meta, ops):
    R = Run(n, P, F, **meta)
    W = {k: {} for k in R.reg}; rows = []; intakes = []
    def addw(Wd, k, v):
        nv = F.add(Wd.get(k, F.c(0)), v)
        if nv == 0: Wd.pop(k, None)
        else: Wd[k] = nv
    for op in ops:
        if op[0] == 'INIT':
            R.INIT(op[1], op[2]); W[op[1]] = {}
        elif op[0] == 'CLEAR':
            r = op[1]; rows.append((dict(W[r]), dict(R.reg[r][1]), R.reg[r][0])); del W[r]; R.CLEAR(r)
        elif op[0] == 'MOVE':
            r, D = op[1], op[2]; C = R.reg[r][0]
            if r[0] not in 'XYH' and D < C:
                out = {t: v for t, v in W[r].items() if P[t] not in D}
                if out:
                    rows.append((out, dict(R.reg[r][1]), C))
                    for t in out: del W[r][t]
            R.MOVE(r, D)
        else:
            _, d, lam, e = op
            om = {}
            if d[0] == 'X': om[d[1]] = lam
            for t, v in W[d].items(): addw(om, t, -lam * v)
            for t, v in om.items(): addw(W[e], t, v)
            if d[0] not in 'XYH': intakes.append((d, R.reg[d][0], {k: lam * v for k, v in R.reg[e][1].items()}, e))
            R.ADD(d, lam, e)
    T = len(P)
    finX = {t: R.reg[('X', t)][1] for t in range(T)}
    # identity over all symbols
    idfail = 0
    for t in range(T):
        lhs = dict(R.reg[('X', t)][1]); 
        for k, v in R.start[('X', t)][1].items(): lhs[k] = F.add(lhs.get(k, F.c(0)), -v if F.p == 0 else v)
        lhs = {k: v for k, v in lhs.items() if v != 0}
        rhs = {}
        terms = [(W[p].get(t, 0), R.reg[p][1]) for p in R.reg] + [(w.get(t, 0), c) for (w, c, C) in rows]
        for a, c in terms:
            if a == 0: continue
            for k, v in c.items(): rhs[k] = F.add(rhs.get(k, F.c(0)), a * v)
        rhs = {k: v for k, v in rhs.items() if v != 0}
        idfail += lhs != rhs
    effs = [(w, eff(c, finX, F), C) for (w, c, C) in rows]
    Rec = R.rec(); oddfail = 0
    for t in range(T):
        for s in range(T):
            if not dot(P[t], P[s]): continue
            val = F.c(0)
            for w, e, C in effs: val = F.add(val, w.get(t, F.c(0)) * e.get(s, F.c(0)))
            oddfail += val != Rec[t][s]
    psum = sum(price(set(w), set(e), P) for w, e, C in effs)
    hot = 0
    for (d, C, c, e) in intakes:
        ec = eff(c, finX, F)
        if any(any(dot(v, P[s]) for v in C) for s in ec): hot += 1
    return dict(R=R, rows=effs, idfail=idfail, oddfail=oddfail, psum=psum, hot=hot, nintake=len(intakes))
