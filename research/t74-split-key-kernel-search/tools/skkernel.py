"""Split-key compensation search (generalises PR1957 abkernel.py).

abkernel admits only compensating reads x += lam*y where y holds a multiple of the deleted read's source value v.
Here the admissible keys are a small linearly dependent family K = {v, k_1, ..., k_m}: every value held by the deleted
read's source or target register over the whole (deleted) word, and every value added into either of them.  Writing every key in a basis e_b of span(K), the exact
identity  sum_j lam_j col_j (x) key_j = d (x) v  splits into one column equation per basis element:
    sum_j lam_j coord_j[b] col_j = coord_v[b] d      (final rows and B-target rows, as in abkernel).
Values and columns are those of the deleted word.  The model is first order: an insert writing register x may not
precede (or share a position with) an insert reading x.  Candidates are priced by the PR1957 frame-cost oracle on the
deleted word; every solution is re-priced exactly (abkernel.price: full A+cut+B+tail map exact, compensation
outside the residual registers, exact optimal frames).
usage: skkernel.py WORD JOBS maxterms K tl   JOBS = [[["B",i]], ...] (one deleted read per job)
environment: SK_CANDCAP (per-insert oracle cap as a multiple of the budget, default 1), SK_NOBUD=1 (drop the summed
oracle budget; diagnostic only), SK_WORKERS (CP-SAT workers, default 4), OUT_DIR (per-job JSON output directory).
Ian Libanio with AI assistance (Anthropic Claude); builds on PR1957 (Rohan Arun) abkernel.py. Apache-2.0.
"""
import os, sys, json, time
from fractions import Fraction as Q
from collections import defaultdict
from ortools.sat.python import cp_model
from pathlib import Path
PR1957_TOOLS = Path(__file__).resolve().parents[2] / 't74-k554-local-exhaustion' / 'tools'
sys.path.insert(0, str(PR1957_TOOLS))
import _paths  # noqa: F401
import harness as H, frames as F
from word import inline
from writeback import write_back
from akernel import Orc, amap, norm, coef
from abkernel import compile_AB, fullseq, price
V = 112
CANDCAP = float(os.environ.get('SK_CANDCAP', '1'))
NOBUD = os.environ.get('SK_NOBUD') == '1'


def rowspace_basis(vecs):
    """rational row reduction; returns (basis list of dicts, coords function)."""
    piv = []  # list of (pivot_key, vec) in reduced form
    def reduce(v):
        v = dict(v); co = {}
        for bi, (pk, pv) in enumerate(piv):
            if v.get(pk):
                f = v[pk] / pv[pk]; co[bi] = co.get(bi, 0) + f
                for k, x in pv.items():
                    v[k] = v.get(k, 0) - f * x
                    if not v[k]: del v[k]
        return v, co
    for v in vecs:
        r, _ = reduce(v)
        if r: piv.append((min(r), r))
    def coords(v):
        r, co = reduce(v); assert not r, 'not in span'
        return co
    return piv, coords


def run(P, dels, maxterms, K, tl, out, lamr=8, base_full=None):
    w = P.base; NA, NC, NB = len(w['A']), len(w['cut']), len(w['B'])
    seq = fullseq(w); L = len(seq); nreg = 2 * V + w['report']['R']
    nreg = max(nreg, 1 + max(max(g[1], g[2] if g[0] == 'add' else 0) for g in seq))
    gidx = lambda s, i: i if s == 'A' else (NA + NC + i if s == 'B' else NA + NC + NB + i)
    dg = {gidx(s, i) for s, i in dels}
    rows = {}; get = lambda x: rows.get(x, {x: Q(1)}); srcval = {}
    hist = defaultdict(list)          # register -> [(pos_after, value_dict)]
    addin = defaultdict(list)         # register -> [value of z added into it]
    cur_key = {x: norm({x: Q(1)}) for x in range(nreg)}; cur_start = {x: 0 for x in range(nreg)}; wins = defaultdict(list)
    for x in range(nreg): hist[x].append((0, {x: Q(1)}))
    for i, g in enumerate(seq):
        if i in dg:
            srcval[i] = dict(get(g[2])); continue
        t = g[1]
        if g[0] == 'add':
            addin[t].append(dict(get(g[2])))
            a = dict(get(t)); c = coef(g)
            for k, v in get(g[2]).items():
                a[k] = a.get(k, 0) + c * v
                if not a[k]: del a[k]
        else: a = {k: v * coef(g) for k, v in get(t).items()}
        rows[t] = a; nk = norm(a); hist[t].append((i + 1, dict(a)))
        if nk != cur_key[t]:
            key, al = cur_key[t]
            if key is not None: wins[key].append((t, cur_start[t], i + 1, al))
            cur_key[t] = nk; cur_start[t] = i + 1
    for x in range(nreg):
        key, al = cur_key[x]
        if key is not None: wins[key].append((x, cur_start[x], L + 1, al))
    (i0,) = dg; g0 = seq[i0]; s0 = g0[2]; t0 = g0[1]
    v = srcval[i0]; vkey, alpha0 = norm(v)
    # key family (deleted-word values): v, every value held by the source s0 or the target t0 over the whole word,
    # and every value added into s0 or t0.  One pass; no recursion into further registers.
    fam = [vkey]
    for r in (s0, t0):
        for val in [val for _, val in hist[r]] + addin[r]:
            k, _ = norm(val)
            if k is not None and k not in fam: fam.append(k)
    kv = [dict(k) for k in fam]
    piv, coords = rowspace_basis(kv)
    nb = len(piv)
    kco = [coords(dict(k)) for k in fam]
    vco = kco[0]
    # holders per position: (y, al, key index)
    holders = defaultdict(list)
    for ki, k in enumerate(fam):
        for y, a_, b_, al in wins[k]:
            for p in range(a_, min(b_, L + 1)): holders[p].append((y, al, ki))
    w1 = compile_AB(w, dict(delete=dels))
    gr = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=P.caps, cut_equality=True)
    r = F.optimal_frames(inline(w1, True), P.costs, check_literal=False, graph=gr); ddel = r['cost'] - P.base_cost
    w2 = write_back(w1, gr, r['assign']); orc = Orc(w2, P.costs.c)
    dA = sorted(i for s, i in dels if s == 'A'); dB = sorted(i for s, i in dels if s == 'B')
    def orcpos(gi):
        if gi < NA: return gi - sum(1 for t in dA if t < gi)
        if gi < NA + NC: return None
        if gi < NA + NC + NB: return (NA - len(dA)) + (gi - NA - NC) - sum(1 for t in dB if t < gi - NA - NC)
        return (NA - len(dA)) + (NB - len(dB)) + (gi - NA - NC - NB)
    bud = -ddel - 1
    colsF, colsB = {}, {}; SF = lambda x: colsF.get(x, {x: Q(1)}); SB = lambda x: colsB.get(x, {x: Q(1)})
    d, dBt = {}, {}; seen = {}; cand = []
    def step(cols, Sf, g):
        if g[0] == 'add':
            t, s = g[1], g[2]; c = coef(g); a = dict(Sf(s))
            for k, vv in Sf(t).items():
                a[k] = a.get(k, 0) + c * vv
                if not a[k]: del a[k]
            cols[s] = a
        else:
            x = g[1]; cols[x] = {k: vv * coef(g) for k, vv in Sf(x).items()}
    for i in range(L, -1, -1):
        g = seq[i] if i < L else None
        inAB = i < NA + NC + NB
        if g is None: pass
        elif i in dg:
            t = g[1]; c = coef(g) * alpha0
            for k, vv in SF(t).items(): d[k] = d.get(k, 0) + c * vv
            if inAB:
                for k, vv in SB(t).items():
                    if V <= k < 2 * V: dBt[k] = dBt.get(k, 0) + c * vv
        else:
            step(colsF, SF, g)
            if inAB: step(colsB, SB, g)
        if i in holders:
            op = orcpos(i)
            if op is None: continue
            for y, al, ki in holders[i]:
                for x in range(nreg):
                    if x == y or (V <= y < 2 * V and not (V <= x < 2 * V)): continue
                    cst = orc.cost(x, y, op)
                    if cst > CANDCAP * bud: continue
                    vf = SF(x); vb = {k: vv for k, vv in SB(x).items() if V <= k < 2 * V} if inAB else {}
                    kk = (x, y, ki, tuple(sorted(vf.items())), tuple(sorted(vb.items())))
                    if kk in seen and seen[kk][0] <= cst: continue
                    seen[kk] = (cst, len(cand)); cand.append((x, y, i, al, {k: vv * al for k, vv in vf.items()}, {k: vv * al for k, vv in vb.items()}, cst, ki))
    d = {k: vv for k, vv in d.items() if vv}; dBt = {k: vv for k, vv in dBt.items() if vv}
    # per-basis equations: sum_j lam_j coord_{key_j}[b] col_j = coord_v[b] * d
    eqs = defaultdict(list)  # (b, 'F'|'B', row) -> [(j, coefficient)]
    for j, c_ in enumerate(cand):
        co = kco[c_[7]]
        for b, cb in co.items():
            if not cb: continue
            for rr, val in c_[4].items(): eqs[(b, 'F', rr)].append((j, cb * val))
            for rr, val in c_[5].items(): eqs[(b, 'B', rr)].append((j, cb * val))
    rhs = {}
    for b, cb in vco.items():
        for rr, val in d.items(): rhs[(b, 'F', rr)] = cb * val
        for rr, val in dBt.items(): rhs[(b, 'B', rr)] = cb * val
    allkeys = set(eqs) | set(rhs)
    shape = all(k in eqs for k, val in rhs.items() if val)
    import math
    lcm = 1
    for k in allkeys:
        for _, val in eqs.get(k, []): lcm = lcm * Q(val).denominator // math.gcd(lcm, Q(val).denominator)
        q = Q(rhs.get(k, 0)).denominator; lcm = lcm * q // math.gcd(lcm, q)
    SC = 2 * lcm
    m = cp_model.CpModel(); lam = []; z = []
    for j in range(len(cand)):
        l = m.NewIntVar(-lamr, lamr, ''); b = m.NewBoolVar(''); m.Add(l == 0).OnlyEnforceIf(b.Not()); m.Add(l != 0).OnlyEnforceIf(b); lam.append(l); z.append(b)
    for k in allkeys:
        terms = [lam[j] * int(Q(val) * SC) for j, val in eqs.get(k, [])]
        r_ = Q(rhs.get(k, 0)) * 2 * SC
        assert r_.denominator == 1
        if not terms:
            continue
        m.Add(sum(terms) == int(r_))
    # no insert-insert interaction: an insert writing x at p may not precede an insert reading x
    byx = defaultdict(list)
    for j, c_ in enumerate(cand): byx[c_[0]].append(j)
    for j2, c2 in enumerate(cand):
        ws = [z[j1] for j1 in byx.get(c2[1], []) if cand[j1][2] <= c2[2]]
        if ws: m.Add(sum(ws) == 0).OnlyEnforceIf(z[j2])
    m.Add(sum(z) <= maxterms)
    if not NOBUD: m.Add(sum(z[j] * cand[j][6] for j in range(len(cand))) <= bud)
    # require at least one non-v key (otherwise this is abkernel's family)
    nonv = [z[j] for j in range(len(cand)) if cand[j][7] != 0]
    m.Minimize(sum(z[j] * (cand[j][6] + 50) for j in range(len(cand))))
    keyuse = defaultdict(int)
    for c_ in cand: keyuse[c_[7]] += 1
    print('dels', dels, 'ddel', ddel, 'keys', len(fam), 'basis', nb, 'cand', len(cand), 'per-key', dict(keyuse), 'd', len(d), 'dB', len(dBt), 'shape', shape, flush=True)
    res = []; cp_status = 'SHAPE_INFEASIBLE' if not shape else ('NO_DELETION_GAIN' if ddel >= 0 else 'NOT_RUN')
    if shape and ddel < 0 and cand:
        cp_status = 'SOLUTION_LIMIT'
        base_full = base_full or amap(seq)
        for it in range(K):
            s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.num_workers = int(os.environ.get('SK_WORKERS', '4'))
            st = s.Solve(m)
            if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                cp_status = s.StatusName(st); print('stop', cp_status, flush=True); break
            supp = [j for j in range(len(cand)) if s.Value(z[j])]
            terms = [(cand[j][0], cand[j][1], cand[j][2], Q(s.Value(lam[j]), 2), cand[j][7]) for j in supp]; est = sum(cand[j][6] for j in supp)
            m.Add(sum(z[j] for j in supp) <= len(supp) - 1)
            ed = dict(delete=list(dels), insert=[], tail=[])
            for x, y, gi, l, ki in terms:
                gate = ['add', x, y, l.numerator, l.denominator, []]
                if gi <= NA: ed['insert'].append(('A', gi, gate)) if gi < NA else ed['insert'].append(('B', 0, gate))
                elif gi < NA + NC + NB: ed['insert'].append(('B', gi - NA - NC, gate))
                else: ed['tail'].append((gi - NA - NC - NB, gate))
            rr = price(P, ed, base_full)
            res.append(dict(terms=[(x, y, gi, str(l), ki) for x, y, gi, l, ki in terms], est=est, status=rr.get('status'), delta=rr.get('delta'), profile=rr.get('profile'), ed=ed))
            print(it, len(terms), 'est', est, [(x, y, gi, str(l), ki) for x, y, gi, l, ki in terms], rr.get('status'), rr.get('delta'), flush=True)
    json.dump(dict(ddel=ddel, cp_status=cp_status, keys=[list(map(lambda kv: [kv[0], str(kv[1])], k)) for k in fam], shape=shape, ncand=len(cand), res=res), open(out, 'w'), separators=(',', ':'))
    return ddel, shape, res


if __name__ == '__main__':
    word = sys.argv[1]; P = H.Pricer(word)
    jobs = json.loads(sys.argv[2]); maxterms, K, tl = int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
    base_full = amap(fullseq(P.base))
    for dels in jobs:
        dels = [tuple(x) for x in dels]; t0 = time.time()
        try: ddel, shape, res = run(P, dels, maxterms, K, tl, os.path.join(os.environ.get('OUT_DIR', '.'), 'sk-%s.json') % '-'.join('%s%d' % x for x in dels), base_full=base_full)
        except Exception:
            import traceback; traceback.print_exc(); continue
        best = min([r['delta'] for r in res if r.get('delta') is not None], default=None)
        print('SUMMARY', dels, 'ddel', ddel, 'shape', shape, 'nsol', len(res), 'best', best, '%.1fs' % (time.time() - t0), flush=True)
