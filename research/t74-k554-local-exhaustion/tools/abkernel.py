"""Relocation/compensation search across A, B and early tails for deleting A or B reads: full A+cut+B+tail map exact,
target rows of the A+cut+B map unchanged (dirt), frame-cost oracle over A+B+tails, exact pricing.
usage: abkernel.py WORD JOBS maxterms K tl ; JOBS = [[["A",i],...], ...]"""
import os, sys, json, time, signal
from fractions import Fraction as Q
from collections import defaultdict
from ortools.sat.python import cp_model
import _paths
import harness as H, frames as F
from word import inline
from writeback import write_back
from akernel import Orc, amap, norm, coef
from model import cone_caps
V = 112

def compile_AB(w, ed):
    """ed: delete=[('A',i)|('B',i)], insert=[(('A'|'B'),pos,gate)], tail=[(j,gate)]"""
    w2 = dict(w)
    for sec in ('A', 'B'):
        S = w[sec]; dele = {i for s, i in ed.get('delete', []) if s == sec}; at = {}
        for s, p, g in ed.get('insert', []):
            if s == sec: at.setdefault(p, []).append(list(g[:-1]) + [list(g[-1])])
        out = []
        for i, e in enumerate(S):
            out.extend(at.get(i, []))
            if i in dele: continue
            out.append(list(e[:-1]) + [list(e[-1]) if e[-1] is not None else []])
        out.extend(at.get(len(S), []))
        w2[sec] = out
    C = [list(g) for g in w['cleanup']]; early = [[i, list(U)] for i, U in w['early_cleanup']]; ins = []
    for j, g in ed.get('tail', []):
        C.append(list(g[:-1]) + [[]]); ins.append((j, len(C) - 1))
    for j, ci in sorted(ins): early.insert(j, [ci, []])
    w2['cleanup'] = C; w2['early_cleanup'] = early
    return w2

def fullseq(w):
    return list(w['A']) + [list(g) for g in w['cut']] + list(w['B']) + [w['cleanup'][i] for i, U in w['early_cleanup']]

def price(P, ed, base_full, timeout=300):
    w1 = compile_AB(P.base, ed)
    rows = amap(fullseq(w1))
    if any(rows.get(q, {q: 1}) != base_full.get(q, {q: 1}) for q in set(rows) | set(base_full)): return dict(status='inexact')
    signal.signal(signal.SIGALRM, H._alarm); signal.alarm(timeout)
    try:
        caps, comp = cone_caps(w1)
        ent = set(map(int, w1['start_extra'])); low = set(map(int, w1['helper_final']))
        if any(e[2] in ent | low for e in comp): return dict(status='compensation-touches-residual')
        g = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=caps, cut_equality=True)
        r = F.optimal_frames(inline(w1, True), P.costs, check_literal=False, graph=g)
    except F.Infeasible: return dict(status='infeasible')
    except H.Timeout: return dict(status='timeout')
    except Exception as e: return dict(status='err:' + repr(e)[:80])
    finally: signal.alarm(0)
    return dict(status='ok' if r['certified'] else 'uncertified', delta=r['cost'] - P.base_cost, profile=dict(sorted(r['profile'].items())))

def run(P, dels, maxterms, K, tl, out, lamr=8, base_full=None):
    w = P.base; NA, NC, NB = len(w['A']), len(w['cut']), len(w['B']); NT = len(w['early_cleanup'])
    seq = fullseq(w); L = len(seq); nreg = 2 * V + w['report']['R']
    gidx = lambda s, i: i if s == 'A' else (NA + NC + i if s == 'B' else NA + NC + NB + i)
    dg = {gidx(s, i) for s, i in dels}
    # values over full seq
    rows = {}; get = lambda x: rows.get(x, {x: Q(1)}); srcval = {}
    cur_key = {x: norm({x: Q(1)}) for x in range(nreg)}; cur_start = {x: 0 for x in range(nreg)}; wins = defaultdict(list)
    for i, g in enumerate(seq):
        if i in dg: srcval[i] = dict(get(g[2]))
        t = g[1]
        if g[0] == 'add':
            a = dict(get(t)); c = coef(g)
            for k, v in get(g[2]).items():
                a[k] = a.get(k, 0) + c * v
                if not a[k]: del a[k]
        else: a = {k: v * coef(g) for k, v in get(t).items()}
        rows[t] = a; nk = norm(a)
        if nk != cur_key[t]:
            key, al = cur_key[t]
            if key is not None: wins[key].append((t, cur_start[t], i + 1, al))
            cur_key[t] = nk; cur_start[t] = i + 1
    for x in range(nreg):
        key, al = cur_key[x]
        if key is not None: wins[key].append((x, cur_start[x], L + 1, al))
    keys = {norm(srcval[i])[0] for i in dg}; assert len(keys) == 1
    key = keys.pop(); alpha0 = {i: norm(srcval[i])[1] for i in dg}
    holders = defaultdict(list)
    for y, a_, b_, al in wins[key]:
        for p in range(a_, min(b_, L + 1)): holders[p].append((y, al))
    # deleted-word frames
    w1 = compile_AB(w, dict(delete=dels))
    g = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=P.caps, cut_equality=True)
    r = F.optimal_frames(inline(w1, True), P.costs, check_literal=False, graph=g); ddel = r['cost'] - P.base_cost
    w2 = write_back(w1, g, r['assign']); orc = Orc(w2, P.costs.c)
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
            for k, v in Sf(t).items():
                a[k] = a.get(k, 0) + c * v
                if not a[k]: del a[k]
            cols[s] = a
        else:
            x = g[1]; cols[x] = {k: v * coef(g) for k, v in Sf(x).items()}
    for i in range(L, -1, -1):
        g = seq[i] if i < L else None
        inAB = i < NA + NC + NB
        if g is None: pass
        elif i in dg:
            t = g[1]; c = coef(g) * alpha0[i]
            for k, v in SF(t).items(): d[k] = d.get(k, 0) + c * v
            if inAB:
                for k, v in SB(t).items():
                    if V <= k < 2 * V: dBt[k] = dBt.get(k, 0) + c * v
        else:
            step(colsF, SF, g)
            if inAB: step(colsB, SB, g)
        if i in holders:
            op = orcpos(i)
            if op is None: continue
            sec = 'A' if i < NA else ('B' if i < NA + NC + NB else 'T')
            if sec == 'A' and i == NA: pass
            for y, al in holders[i]:
                for x in range(nreg):
                    if x == y or (V <= y < 2 * V and not (V <= x < 2 * V)): continue
                    cst = orc.cost(x, y, op)
                    if cst > bud: continue
                    vf = SF(x); vb = {k: v for k, v in SB(x).items() if V <= k < 2 * V} if inAB else {}
                    kk = (x, y, tuple(sorted(vf.items())), tuple(sorted(vb.items())))
                    if kk in seen and seen[kk] <= cst: continue
                    seen[kk] = cst; cand.append((x, y, i, al, {k: v * al for k, v in vf.items()}, {k: v * al for k, v in vb.items()}, cst))
    d = {k: v for k, v in d.items() if v}; dBt = {k: v for k, v in dBt.items() if v}
    rowsF = set(d); rowsB = set(dBt)
    for c_ in cand: rowsF |= set(c_[4]); rowsB |= set(c_[5])
    den = 1
    for c_ in cand:
        for val in list(c_[4].values()) + list(c_[5].values()): den = max(den, val.denominator)
    for val in list(d.values()) + list(dBt.values()): den = max(den, val.denominator)
    SC = 2 * den
    m = cp_model.CpModel(); lam = []; z = []
    for j in range(len(cand)):
        l = m.NewIntVar(-lamr, lamr, ''); b = m.NewBoolVar(''); m.Add(l == 0).OnlyEnforceIf(b.Not()); m.Add(l != 0).OnlyEnforceIf(b); lam.append(l); z.append(b)
    byF = defaultdict(list); byB = defaultdict(list)
    for j, c_ in enumerate(cand):
        for rr, val in c_[4].items(): byF[rr].append((j, val))
        for rr, val in c_[5].items(): byB[rr].append((j, val))
    ok = True
    for rset, by, dd in ((rowsF, byF, d), (rowsB, byB, dBt)):
        for rr in rset:
            rhs = dd.get(rr, Q(0)) * 2 * SC; terms = [lam[j] * int(val * SC) for j, val in by.get(rr, [])]
            if not terms:
                if rhs: ok = False
                continue
            m.Add(sum(terms) == int(rhs))
    m.Add(sum(z) <= maxterms); m.Add(sum(z[j] * cand[j][6] for j in range(len(cand))) <= bud)
    m.Minimize(sum(z[j] * (cand[j][6] + 50) for j in range(len(cand))))
    print('dels', dels, 'ddel', ddel, 'wins', len(wins[key]), 'cand', len(cand), 'd', len(d), 'dB', len(dBt), 'shape', ok, flush=True)
    res = []
    if ok and ddel < 0:
        base_full = base_full or amap(seq)
        for it in range(K):
            s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.num_workers = 2
            st = s.Solve(m)
            if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): print('stop', s.StatusName(st), flush=True); break
            supp = [j for j in range(len(cand)) if s.Value(z[j])]
            terms = [(cand[j][0], cand[j][1], cand[j][2], Q(s.Value(lam[j]), 2)) for j in supp]; est = sum(cand[j][6] for j in supp)
            m.Add(sum(z[j] for j in supp) <= len(supp) - 1)
            ed = dict(delete=list(dels), insert=[], tail=[])
            for x, y, gi, l in terms:
                gate = ['add', x, y, l.numerator, l.denominator, []]
                if gi <= NA: ed['insert'].append(('A', gi, gate)) if gi < NA else ed['insert'].append(('B', 0, gate))
                elif gi < NA + NC + NB: ed['insert'].append(('B', gi - NA - NC, gate))
                else: ed['tail'].append((gi - NA - NC - NB, gate))
            rr = price(P, ed, base_full)
            res.append(dict(terms=[(x, y, gi, str(l)) for x, y, gi, l in terms], est=est, status=rr.get('status'), delta=rr.get('delta'), profile=rr.get('profile'), ed=ed))
            print(it, len(terms), 'est', est, [(x, y, gi, str(l)) for x, y, gi, l in terms], rr.get('status'), rr.get('delta'), flush=True)
    json.dump(dict(ddel=ddel, res=res), open(out, 'w'), indent=1)
    return ddel, res

if __name__ == '__main__':
    word = sys.argv[1]; P = H.Pricer(word)
    jobs = json.loads(sys.argv[2]); maxterms, K, tl = int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
    base_full = amap(fullseq(P.base))
    for dels in jobs:
        dels = [tuple(x) for x in dels]; t0 = time.time()
        try: ddel, res = run(P, dels, maxterms, K, tl, os.path.join(os.environ.get('OUT_DIR', '.'), 'abk-%s.json') % '-'.join('%s%d' % x for x in dels), base_full=base_full)
        except Exception as e:
            import traceback; traceback.print_exc(); continue
        best = min([r['delta'] for r in res if r.get('delta') is not None], default=None)
        print('SUMMARY', dels, 'ddel', ddel, 'nsol', len(res), 'best', best, '%.1fs' % (time.time() - t0), flush=True)
