"""Pivot kernel search with frame-aware free slots in B and in early-cleanup tails, exactness over B+tails,
and the target-dirt constraint (B-only change on target rows must vanish).
usage: fc3.py WORD JOBS maxterms K tl ; JOBS = [[q, [dels], [[lo,hi],...] windows in seq coordinates (B then tails)], ...]"""
import os, sys, json, gzip, time, bisect, collections
from fractions import Fraction as Q
from collections import defaultdict
from ortools.sat.python import cp_model
import _paths
import harness as H, frames as F
from word import inline, span
from writeback import write_back
V = 112

def solve(P, ed, caps=None):
    w1 = H.compile_edits(P.base, ed)
    g = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=caps or P.caps, cut_equality=True)
    r = F.optimal_frames(inline(w1, True), P.costs, check_literal=False, graph=g)
    return write_back(w1, g, r['assign']), r

class Oracle:
    """gate timelines over B followed by early-cleanup tails (seq coordinates)."""
    def __init__(self, w):
        n = 2 * V + w['report']['R']
        cur = [frozenset((0, p)) for p in w['ports']] + [frozenset((0,))] * (n - V)
        for r, vecs in w['start_extra'].items(): cur[int(r)] = span(tuple(vecs))
        for e in w['A']:
            T = span(tuple(e[-1]))
            for r in (e[1:3] if e[0] == 'add' else e[1:2]): cur[r] = T
        self.start = list(cur); self.g = defaultdict(list)
        seq = [(e, e[-1]) for e in w['B']] + [(w['cleanup'][i], U) for i, U in w['early_cleanup']]
        for i, (e, U) in enumerate(seq):
            T = span(tuple(U))
            for r in (e[1:3] if e[0] == 'add' else e[1:2]):
                self.g[r].append((i, cur[r], T)); cur[r] = T
        self.pos = {r: [x[0] for x in gl] for r, gl in self.g.items()}
    def opts(self, y, p):
        gl = self.g.get(y, []); ps = self.pos.get(y, [])
        k = bisect.bisect_left(ps, p)
        fr = gl[k - 1][2] if k > 0 else self.start[y]
        o = {fr}
        if k < len(gl) and gl[k][2] != fr: o.add(gl[k][2])
        return o
    def free(self, x, q, p): return bool(self.opts(x, p) & self.opts(q, p))

def run(P, q, dels, wins, maxterms, K, tl, out, lamr=8, strict_free=True):
    w = P.base; B = w['B']; Cl = w['cleanup']; NB = len(B)
    tails = [Cl[i] for i, U in w['early_cleanup']]; seq = B + tails; L = len(seq)
    w2, r = solve(P, dict(delete=dels)); ddel = r['cost'] - P.base_cost
    orc = Oracle(w2); ds = sorted(dels)
    def to2(p): return p - sum(1 for t in ds if t < p)
    inwin = lambda p: any(a <= p < b for a, b in wins)
    coef = lambda g: Q(g[3], g[4]) if g[0] == 'add' else Q(g[2], g[3])
    def back(stop):
        """backward sensitivities from end of seq[:stop]; returns generator over positions"""
        pass
    # full sensitivities (B+tails) and B-only sensitivities
    colsF, colsB = {}, {}
    SF = lambda x: colsF.get(x, {x: Q(1)}); SB = lambda x: colsB.get(x, {x: Q(1)})
    d, dB = {}, {}
    lastkey = {}; cand = []
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
    nreg = 2 * V + w['report']['R']
    for i in range(L, -1, -1):
        g = seq[i] if i < L else None
        if g is None: pass
        elif i in dset:
            t = g[1]; c = coef(g)
            for k, v in SF(t).items(): d[k] = d.get(k, 0) + c * v
            if i < NB:
                for k, v in SB(t).items(): dB[k] = dB.get(k, 0) + c * v
        else:
            step(colsF, SF, g)
            if i < NB: step(colsB, SB, g)
        if inwin(i):
            p2 = to2(i) if i < NB else i - len(ds)
            for x in range(nreg):
                if x == q: continue
                if strict_free and not orc.free(x, q, p2): continue
                vf = SF(x); vb = {k: v for k, v in SB(x).items() if V <= k < 2 * V} if i < NB else {}
                key = (tuple(sorted(vf.items())), tuple(sorted(vb.items())), i < NB)
                if lastkey.get(x) == key: continue
                lastkey[x] = key; cand.append((x, i, dict(vf), vb))
    d = {k: v for k, v in d.items() if v}; dB = {k: v for k, v in dB.items() if v and V <= k < 2 * V}
    rowsF = set(d); rowsB = set(dB)
    for x, p, vf, vb in cand: rowsF |= set(vf); rowsB |= set(vb)
    den = 1
    for x, p, vf, vb in cand:
        for val in list(vf.values()) + list(vb.values()): den = max(den, val.denominator)
    for val in list(d.values()) + list(dB.values()): den = max(den, val.denominator)
    SC = 2 * den
    m = cp_model.CpModel(); lam = []; z = []
    for j in range(len(cand)):
        l = m.NewIntVar(-lamr, lamr, ''); b = m.NewBoolVar(''); m.Add(l == 0).OnlyEnforceIf(b.Not()); m.Add(l != 0).OnlyEnforceIf(b); lam.append(l); z.append(b)
    byF = defaultdict(list); byB = defaultdict(list)
    for j, (x, p, vf, vb) in enumerate(cand):
        for rr, val in vf.items(): byF[rr].append((j, val))
        for rr, val in vb.items(): byB[rr].append((j, val))
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
    m.Add(sum(z) <= maxterms); m.Minimize(sum(z))
    nb = sum(1 for c in cand if c[1] < NB)
    print('q', q, 'dels', dels, 'ddel', ddel, 'cand', len(cand), '(B %d, tail %d)' % (nb, len(cand) - nb), 'd', len(d), 'dB', len(dB), 'shape', ok, flush=True)
    res = []
    if ok:
        for it in range(K):
            s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.num_workers = 2
            st = s.Solve(m)
            if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): print('stop', s.StatusName(st), flush=True); break
            supp = [j for j in range(len(cand)) if s.Value(z[j])]
            terms = [(cand[j][0], cand[j][1], Q(s.Value(lam[j]), 2)) for j in supp]
            m.Add(sum(z[j] for j in supp) <= len(supp) - 1)
            ed = dict(delete=list(dels), insert=[], tail=[], prepend=[])
            for x, p, l in terms:
                gte = ['add', x, q, l.numerator, l.denominator, []]
                if p < NB: ed['insert'].append((p, gte))
                else: ed['tail'].append((p - NB, gte))
            ed['insert'].sort(key=lambda t: t[0]); ed['tail'].sort(key=lambda t: t[0])
            rr = P.price(ed, timeout=240)
            res.append(dict(terms=[(x, p, str(l)) for x, p, l in terms], status=rr.get('status'), delta=rr.get('delta'), profile=rr.get('profile'), ed=ed))
            print(it, len(terms), [(x, p, str(l)) for x, p, l in terms], rr.get('status'), rr.get('delta'), flush=True)
    json.dump(res, open(out, 'w'), indent=1)
    return res

if __name__ == '__main__':
    word = sys.argv[1]; P = H.Pricer(word)
    jobs = json.loads(sys.argv[2]); maxterms, K, tl = int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
    strict = (sys.argv[6] != 'loose') if len(sys.argv) > 6 else True
    for q, dels, wins in jobs:
        run(P, q, dels, wins, maxterms, K, tl, os.path.join(os.environ.get('OUT_DIR', '.'), 'fc3-%d-%s%s.json') % (q, '-'.join(map(str, dels)), '' if strict else '-loose'), strict_free=strict)
