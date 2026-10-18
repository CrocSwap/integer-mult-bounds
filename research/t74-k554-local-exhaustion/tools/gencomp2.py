"""General read-relocation search: delete B read(s) (t += c s), compensate with inserted reads x += lam*y at positions
where y holds a multiple of the deleted read's source value, restricted to frame-free slots. Exact over B+tails;
target-row B-only change must vanish.  usage: gencomp.py WORD JOBS maxterms K tl ; JOBS=[[dels...],...] (single source value)"""
import os, sys, json, time
from fractions import Fraction as Q
from collections import defaultdict
from ortools.sat.python import cp_model
import _paths
import harness as H
from fc3 import solve, Oracle
from costorc import CostOracle, INF
V = 112
coef = lambda g: Q(g[3], g[4]) if g[0] == 'add' else Q(g[2], g[3])

def norm(row):
    if not row: return None, None
    k0 = min(row); a = row[k0]
    return tuple(sorted((k, v / a) for k, v in row.items())), a

def value_windows(seq, nreg):
    """per normalized value: list of (y, start, end, alpha) with y holding alpha*value on positions [start,end) (position = before gate)."""
    rows = {}
    def get(x): return rows.get(x, {x: Q(1)})
    cur_start = [0] * nreg; cur_key = [None] * nreg
    out = defaultdict(list)
    for x in range(nreg): cur_key[x] = norm({x: Q(1)})
    for i, g in enumerate(seq):
        t = g[1]
        if g[0] == 'add':
            a = dict(get(t)); c = coef(g)
            for k, v in get(g[2]).items():
                a[k] = a.get(k, 0) + c * v
                if not a[k]: del a[k]
        else:
            a = {k: v * coef(g) for k, v in get(t).items()}
        rows[t] = a
        nk = norm(a)
        if nk != cur_key[t]:
            key, al = cur_key[t]
            if key is not None: out[key].append((t, cur_start[t], i + 1, al))
            cur_key[t] = nk; cur_start[t] = i + 1
    L = len(seq)
    for x in range(nreg):
        key, al = cur_key[x]
        if key is not None: out[key].append((x, cur_start[x], L + 1, al))
    return out, rows

_VW = None
def run(P, dels, maxterms, K, tl, out, lamr=8, restrict_x=None, verbose=True, budget=None):
    w = P.base; B = w['B']; Cl = w['cleanup']; NB = len(B)
    tails = [Cl[i] for i, U in w['early_cleanup']]; seq = B + tails; L = len(seq)
    nreg = 2 * V + w['report']['R']
    # value of deleted read sources
    global _VW
    if _VW is None or _VW[0] is not P: _VW = (P, value_windows(seq, nreg)[0])
    vw = _VW[1]
    # source value at deletion time: recompute rows up to deletion
    rows = {}
    def get(x): return rows.get(x, {x: Q(1)})
    srcval = {}
    for i, g in enumerate(seq):
        if i in dels: srcval[i] = dict(get(g[2]))
        t = g[1]
        if g[0] == 'add':
            a = dict(get(t)); c = coef(g)
            for k, v in get(g[2]).items():
                a[k] = a.get(k, 0) + c * v
                if not a[k]: del a[k]
        else: a = {k: v * coef(g) for k, v in get(t).items()}
        rows[t] = a
        if i > max(dels): break
    keys = {norm(srcval[i])[0] for i in dels}
    assert len(keys) == 1, 'deleted reads must share a source value'
    key = keys.pop(); alpha0 = {i: norm(srcval[i])[1] for i in dels}
    wins = [x for x in vw[key]]          # (y, a, b, alpha)
    w2, r = solve(P, dict(delete=dels)); ddel = r['cost'] - P.base_cost
    orc = CostOracle(w2, P.costs.c); ds = sorted(dels)
    bud = (-ddel - 1) if budget is None else budget
    def to2(p): return p - sum(1 for t in ds if t < p)
    # position -> list of (y, alpha) holding the value
    holders = defaultdict(list)
    for y, a, b, al in wins:
        for p in range(a, min(b, L + 1)):
            holders[p].append((y, al))
    colsF, colsB = {}, {}
    SF = lambda x: colsF.get(x, {x: Q(1)}); SB = lambda x: colsB.get(x, {x: Q(1)})
    d, dB = {}, {}
    seen = {}; cand = []
    dset = set(dels)
    def step(cols, Sf, g):
        if g[0] == 'add':
            t, s = g[1], g[2]; c = coef(g); a = dict(Sf(s))
            for k, v in Sf(t).items():
                a[k] = a.get(k, 0) + c * v
                if not a[k]: del a[k]
            cols[s] = a
        else:
            x = g[1]; cols[x] = {k: v * coef(g) for k, v in Sf(x).items()}
    for i in range(L, -1, -1):
        g = seq[i] if i < L else None
        if g is None: pass
        elif i in dset:
            t = g[1]; c = coef(g) * alpha0[i]
            for k, v in SF(t).items(): d[k] = d.get(k, 0) + c * v
            if i < NB:
                for k, v in SB(t).items():
                    if V <= k < 2 * V: dB[k] = dB.get(k, 0) + c * v
        else:
            step(colsF, SF, g)
            if i < NB: step(colsB, SB, g)
        if i in holders:
            p2 = to2(i) if i < NB else i - len(ds)
            for y, al in holders[i]:
                if i in dset: continue
                xs = range(nreg) if restrict_x is None else restrict_x
                for x in xs:
                    if x == y: continue
                    cst = orc.cost(x, y, p2)
                    if cst > bud: continue
                    vf = SF(x); vb = {k: v for k, v in SB(x).items() if V <= k < 2 * V} if i < NB else {}
                    kk = (x, y, tuple(sorted(vf.items())), tuple(sorted(vb.items())), i < NB)
                    if kk in seen and seen[kk] <= cst: continue
                    seen[kk] = cst
                    cand.append((x, y, i, al, {k: v * al for k, v in vf.items()}, {k: v * al for k, v in vb.items()}, cst))
    d = {k: v for k, v in d.items() if v}; dB = {k: v for k, v in dB.items() if v}
    rowsF = set(d); rowsB = set(dB)
    for c_ in cand: rowsF |= set(c_[4]); rowsB |= set(c_[5])
    den = 1
    for c_ in cand:
        for val in list(c_[4].values()) + list(c_[5].values()): den = max(den, val.denominator)
    for val in list(d.values()) + list(dB.values()): den = max(den, val.denominator)
    SC = 2 * den
    m = cp_model.CpModel(); lam = []; z = []
    for j in range(len(cand)):
        l = m.NewIntVar(-lamr, lamr, ''); b = m.NewBoolVar(''); m.Add(l == 0).OnlyEnforceIf(b.Not()); m.Add(l != 0).OnlyEnforceIf(b); lam.append(l); z.append(b)
    byF = defaultdict(list); byB = defaultdict(list)
    for j, c_ in enumerate(cand):
        for rr, val in c_[4].items(): byF[rr].append((j, val))
        for rr, val in c_[5].items(): byB[rr].append((j, val))
    ok = True
    for rr in rowsF:
        rhs = d.get(rr, Q(0)) * 2 * SC; terms = [lam[j] * int(val * SC) for j, val in byF.get(rr, [])]
        if not terms:
            if rhs: ok = False
            continue
        m.Add(sum(terms) == int(rhs))
    for rr in rowsB:
        rhs = dB.get(rr, Q(0)) * 2 * SC; terms = [lam[j] * int(val * SC) for j, val in byB.get(rr, [])]
        if not terms:
            if rhs: ok = False
            continue
        m.Add(sum(terms) == int(rhs))
    m.Add(sum(z) <= maxterms)
    m.Add(sum(z[j] * cand[j][6] for j in range(len(cand))) <= bud)
    m.Minimize(sum(z[j] * (cand[j][6] + 50) for j in range(len(cand))))
    if verbose: print('dels', dels, [B[i][:5] for i in dels], 'ddel', ddel, 'holders-wins', len(wins), 'cand', len(cand), 'd', len(d), 'dB', len(dB), 'shape', ok, flush=True)
    res = []
    if ok and ddel < 0:
        for it in range(K):
            s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.num_workers = 2
            st = s.Solve(m)
            if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): print('stop', s.StatusName(st), flush=True); break
            supp = [j for j in range(len(cand)) if s.Value(z[j])]
            terms = [(cand[j][0], cand[j][1], cand[j][2], Q(s.Value(lam[j]), 2)) for j in supp]
            estc = sum(cand[j][6] for j in supp)
            m.Add(sum(z[j] for j in supp) <= len(supp) - 1)
            ed = dict(delete=list(dels), insert=[], tail=[], prepend=[])
            for x, y, p, l in terms:
                gte = ['add', x, y, l.numerator, l.denominator, []]
                if p < NB: ed['insert'].append((p, gte))
                else: ed['tail'].append((p - NB, gte))
            ed['insert'].sort(key=lambda t: t[0]); ed['tail'].sort(key=lambda t: t[0])
            rr = P.price(ed, timeout=240)
            res.append(dict(terms=[(x, y, p, str(l)) for x, y, p, l in terms], status=rr.get('status'), delta=rr.get('delta'), profile=rr.get('profile'), ed=ed))
            print(it, len(terms), 'est', estc, [(x, y, p, str(l)) for x, y, p, l in terms], rr.get('status'), rr.get('delta'), flush=True)
    if out: json.dump(dict(ddel=ddel, ncand=len(cand), res=res), open(out, 'w'), indent=1)
    return ddel, res

if __name__ == '__main__':
    word = sys.argv[1]; P = H.Pricer(word)
    jobs = json.loads(sys.argv[2]); maxterms, K, tl = int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
    import time as _t
    for dels in jobs:
        t0 = _t.time()
        try:
            ddel, res = run(P, dels, maxterms, K, tl, os.path.join(os.environ.get('OUT_DIR', '.'), 'gc2-%s.json') % '-'.join(map(str, dels)))
        except Exception as e:
            print('ERR', dels, repr(e)[:100], flush=True); continue
        best = min([r['delta'] for r in res if r.get('delta') is not None], default=None)
        print('SUMMARY', dels, 'ddel', ddel, 'nsol', len(res), 'best', best, '%.1fs' % (_t.time() - t0), flush=True)
