"""G2CLUSTER gfa.py (own code): GLOBAL future attribution = FA with weights on EVERY register (owned included) + flush.
Forward sweep. Every register r carries W_r (vector over targets). ADD d += lam*s:  W_s += lam*([d==X_t] e_t - W_d)  (d, s any kind).
Owned descent C -> C' (C' < C): labels t of W_r with q_t not in C' are FLUSHED: emit row (W_out, content now, C); W_r -= W_out.
Owned CLEAR: emit row (W_r, content, chart).  Invariant: X(tau)-X(0) = sum_r W_r r(tau) + sum emitted rows  (exact telescoping).
=> odd receipts = sum_rows w_r c_r^T (effective contents), public finals vanish on odd cells (chart invariant + cold finals)."""
import sys
sys.path.insert(0, 'code/uphase')
from fattr import *

def gfa(prog, init, P):
    CH = Charts(P)
    reg = {k: [f, dict(c)] for k, (f, c) in init.items()}
    start = {k: dict(c) for k, (f, c) in init.items()}
    W = {k: {} for k in init}
    owned = {}; L = []; rows = []; bad = []
    isX = lambda r: isinstance(r, tuple) and r[0] == 'X'
    def addv(a, c, b):
        for k, v in b.items():
            a[k] = a.get(k, 0) + c * v
            if a[k] == 0: del a[k]
    for i, op in enumerate(prog):
        t = op[0]
        if t == 'INIT':
            r, f = op[1], op[2]; reg[r] = [f, {}]; W[r] = {}; owned[r] = len(L)
            L.append(dict(reg=r, path=[f], cost=0, intakes=[], outs=[], rows=[], cold=True, flushes=0, events=[]))
        elif t == 'MOVE':
            r, f = op[1], op[2]; a = reg[r][0]
            if r in owned:
                lf = L[owned[r]]
                if not (a <= f or f <= a): bad.append(('nest', i))
                lf['cost'] += abs(fdim(f) - fdim(a)); lf['path'].append(f)
                if f < a:
                    out = {tt: v for tt, v in W[r].items() if P[tt] not in f}
                    if out:
                        rows.append((owned[r], out, dict(reg[r][1]), a, 'flush')); lf['rows'].append(len(rows) - 1); lf['flushes'] += 1
                        for tt in out: del W[r][tt]
                lf['events'].append(('M', f))
            elif not a <= f: bad.append(('public-descends', i))
            reg[r][0] = f
        elif t == 'ADD':
            d, lam, s = op[1], Fr(op[2]), op[3]
            if reg[d][0] != reg[s][0]: bad.append(('frame', i))
            C = reg[d][0]
            om = {}
            if isX(d): om[d[1]] = lam
            for tt, v in W[d].items(): om[tt] = om.get(tt, 0) - lam * v
            for k, v in om.items():
                if v == 0: continue
                W[s][k] = W[s].get(k, 0) + v
                if W[s][k] == 0: del W[s][k]
            if d in owned:
                lf = L[owned[d]]
                lf['intakes'].append(C); lf['events'].append(('I', C)); lf.setdefault('raw', []).append((C, {k: lam * v for k, v in reg[s][1].items()}))
            if s in owned:
                L[owned[s]]['outs'].append(C); L[owned[s]]['events'].append(('O', C))
            addv(reg[d][1], lam, reg[s][1])
        elif t == 'CLEAR':
            r = op[1]; lf = L[owned[r]]
            rows.append((owned[r], dict(W[r]), dict(reg[r][1]), reg[r][0], 'clear')); lf['rows'].append(len(rows) - 1)
            del owned[r]; del reg[r]; del W[r]
    fin = {k: dict(v[1]) for k, v in reg.items()}
    res = dict(bad=bad, L=L, rows=rows, W=W, fin=fin, start=start)
    # exact identity over all symbols
    nb = 0
    for X in [k for k in init if isX(k)]:
        tt = X[1]; lhs = dict(fin[X]); addv(lhs, -1, start[X]); rhs = {}
        for p, w in W.items():
            if tt in w: addv(rhs, w[tt], fin[p])
        for (_, w, c, C, _) in rows:
            if tt in w: addv(rhs, w[tt], c)
        nb += lhs != rhs
    res['identity_fail'] = nb
    res['viol_pub'] = sum(1 for p, w in W.items() for tt in w if P[tt] not in reg[p][0])
    res['viol_row'] = sum(1 for (_, w, c, C, _) in rows for tt in w if P[tt] not in C)
    # effective coldness of every owned intake (needs the finals, so done after the sweep)
    for lf in L:
        lf['cold'] = True
        for (C, c) in lf.get('raw', []):
            _, cold, _ = CH.info(C)
            if any(s_ not in cold for s_ in eff(c, fin)): lf['cold'] = False
    return res

def eff(c, fin):
    """effective y-content: c|y - sum_s c[x_s] final(X_s)|y"""
    e = {k[1]: v for k, v in c.items() if k[0] == 'y'}
    for k, v in c.items():
        if k[0] == 'x':
            for kk, vv in fin[('X', k[1])].items():
                if kk[0] == 'y': e[kk[1]] = e.get(kk[1], 0) - v * vv
    return {a: b for a, b in e.items() if b != 0}

def odd_check(res, P, n):
    fin, start = res['fin'], res['start']; nb = 0
    effs = [(w, eff(c, fin)) for (_, w, c, C, _) in res['rows']]
    for t in range(n):
        rec = dict(fin[('X', t)])
        for k, v in start[('X', t)].items(): rec[k] = rec.get(k, 0) - v
        for s in range(n):
            if not dot(P[t], P[s]): continue
            val = sum((w.get(t, 0) * e.get(s, 0) for w, e in effs), Fr(0))
            nb += val != rec.get(('y', s), 0)
    return nb, effs

def nri_bound(lf, w):
    """NRI lemma bound: Bl = span(labels of w), A = meet of intake charts"""
    A = None
    for C in lf['intakes']: A = C if A is None else A & C
    if A is None: A = frozenset([0])
    return A
