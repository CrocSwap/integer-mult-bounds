"""SEPPAYS sepcheck.py (own code): CARRIER-TREE SEPARATION class test + exact decoder from it.
Lifetimes = owned INIT..CLEAR.  Edges: owned k read by owned p (ADD p += l*k) => p is k's parent.
Class CT: every lifetime GTD w.r.t. its outputs (no intake after its first read-out); non-roots never output into publics and
are read by exactly one parent lifetime; the read graph is a forest.  A_k = meet of k's intake charts before its LAST read-out
(roots: all intakes).  A*_g = meet over the tree.  Row of root m = (sum of its FA weights, eff(final content)).
Theorem [P]: if eff(content of root) is cold at A*_g, price(row) <= dim B - dim(B cap A*) <= sum_{k in tree} cost_k."""
from eng import *
from fa import eff, price, gfa
from f2mass import rank2

def meet(charts):
    A = None
    for C in charts: A = C if A is None else (A & C)
    return A if A is not None else None

def analyse(n, P, F, meta, ops):
    fa = gfa(n, P, F, meta, ops)
    R = Run(n, P, F, **meta)
    life = {}; L = []
    for i, op in enumerate(ops):
        if op[0] == 'INIT':
            life[op[1]] = len(L); L.append(dict(reg=op[1], cost=0, intakes=[], outs=[], reads=[], first_out=None, path=[op[2]]))
        elif op[0] == 'CLEAR':
            del life[op[1]]
        elif op[0] == 'MOVE' and op[1] in life:
            C = R.reg[op[1]][0]
            if C <= op[2]: L[life[op[1]]]['cost'] += fdim(op[2]) - fdim(C)
        elif op[0] == 'ADD':
            _, d, lam, e = op
            if d in life: L[life[d]]['intakes'].append((i, R.reg[d][0], e))
            if e in life:
                lf = L[life[e]]
                if d in life: lf['reads'].append((i, life[d], R.reg[d][0]))
                else: lf['outs'].append((i, d, R.reg[e][0]))
                if lf['first_out'] is None: lf['first_out'] = i
        R.ADD(*op[1:]) if op[0] == 'ADD' else getattr(R, op[0])(*op[1:])
    # FA rows per lifetime (gfa emits rows in lifetime order of CLEAR/flush; recompute by replay to merge)
    rows = merge_rows(n, P, F, meta, ops)
    T = len(P); finX = {t: R.reg[('X', t)][1] for t in range(T)}
    gtd = all(lf['first_out'] is None or all(i < lf['first_out'] for i, _, _ in lf['intakes']) for lf in L)
    parent = {}
    ok_forest = True
    for k, lf in enumerate(L):
        ps = {p for _, p, _ in lf['reads']}
        if len(ps) > 1: ok_forest = False
        if ps:
            if lf['outs'] and any(w for w in [rows[k][0]]): ok_forest = False
            parent[k] = ps.pop()
    roots = [k for k in range(len(L)) if k not in parent]
    def subtree(k):
        out = [k]
        for c, p in parent.items():
            if p == k: out += subtree(c)
        return out
    res = dict(L=L, rows=rows, gtd=gtd, forest=ok_forest, fa=fa, groups=[])
    if not (gtd and ok_forest): return res
    for m in roots:
        g = subtree(m); As = []
        for k in g:
            lf = L[k]
            last = max((i for i, _, _ in lf['reads']), default=None)
            As += [C for i, C, _ in lf['intakes'] if last is None or i < last]
        A = meet(As) if As else frozenset([0])
        w, c = rows[m]
        e = eff(c, finX, F)
        cold = all(all(not dot(v, P[s]) for v in A) for s in e)
        pr = price(set(w), set(e), P)
        cost = sum(L[k]['cost'] for k in g)
        res['groups'].append(dict(root=m, members=g, cold=cold, price=pr, cost=cost, single_cold=None))
    return res

def merge_rows(n, P, F, meta, ops):
    """global FA with weights summed per lifetime (no flush split): row_k = (total weight given to k, final content of k)"""
    R = Run(n, P, F, **meta)
    W = {k: {} for k in R.reg}; life = {}; rows = []
    def addw(Wd, k, v):
        nv = F.add(Wd.get(k, F.c(0)), v)
        if nv == 0: Wd.pop(k, None)
        else: Wd[k] = nv
    for op in ops:
        if op[0] == 'INIT':
            R.INIT(op[1], op[2]); W[op[1]] = {}; life[op[1]] = len(rows); rows.append(None)
        elif op[0] == 'CLEAR':
            r = op[1]; rows[life[r]] = (dict(W[r]), dict(R.reg[r][1])); del W[r]; del life[r]; R.CLEAR(r)
        elif op[0] == 'MOVE':
            R.MOVE(op[1], op[2])
        else:
            _, d, lam, e = op
            om = {}
            if d[0] == 'X': om[d[1]] = lam
            for t, v in W[d].items(): addw(om, t, -lam * v)
            for t, v in om.items(): addw(W[e], t, v)
            R.ADD(d, lam, e)
    return rows
