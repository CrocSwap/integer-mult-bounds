"""A-section kernel search: delete A read(s) and compensate inside A (A map unchanged), frame-cost-aware.
usage: akernel.py WORD JOBS maxterms K tl   (JOBS = [[a_idx,...], ...] reads sharing one source value)"""
import os, sys, json, time, bisect, signal
from fractions import Fraction as Q
from collections import defaultdict
from ortools.sat.python import cp_model
import _paths
import harness as H, frames as F
from word import inline, span
from writeback import write_back
from costorc import dim, INF
V = 112; PR = 2147483629
coef = lambda g: Q(g[3], g[4]) if g[0] == 'add' else Q(g[2], g[3])

def compile_A(w, ed):
    A = w['A']; dele = set(ed.get('delete', [])); at = {}
    for p, g in ed.get('insert', []): at.setdefault(p, []).append(list(g[:-1]) + [list(g[-1])])
    out = []
    for i, e in enumerate(A):
        out.extend(at.get(i, []))
        if i in dele: continue
        out.append(list(e[:-1]) + [list(e[-1]) if e[-1] is not None else []])
    out.extend(at.get(len(A), []))
    w2 = dict(w); w2['A'] = out; return w2

def amap(seq):
    from exchange import coef_mod
    rows = {}
    for e in seq:
        for q in (e[1:3] if e[0] == 'add' else e[1:2]): rows.setdefault(q, {q: 1})
        c = coef_mod(e); t = e[1]
        if e[0] == 'scale': rows[t] = {k: x * c % PR for k, x in rows[t].items()}
        else:
            d = rows[t]
            for k, x in rows[e[2]].items():
                y = (d.get(k, 0) + c * x) % PR
                if y: d[k] = y
                else: d.pop(k, None)
    return rows

class Orc:
    """frame timeline over A + B + tails (A positions 0..NA-1, B positions NA.., tails after)."""
    def __init__(self, w, c):
        n = 2 * V + w['report']['R']; self.c = c
        cur = [frozenset((0, p)) for p in w['ports']] + [frozenset((0,))] * (n - V)
        for r, vecs in w['start_extra'].items(): cur[int(r)] = span(tuple(vecs))
        self.start = list(cur); self.g = defaultdict(list)
        seq = [(e, e[-1]) for e in w['A']] + [(e, e[-1]) for e in w['B']] + [(w['cleanup'][i], U) for i, U in w['early_cleanup']]
        for i, (e, U) in enumerate(seq):
            T = span(tuple(U))
            for r in (e[1:3] if e[0] == 'add' else e[1:2]):
                self.g[r].append((i, cur[r], T)); cur[r] = T
        self.pos = {r: [x[0] for x in gl] for r, gl in self.g.items()}
        full = frozenset(range(512)); R = w['report']['R']
        ends = [full] * V + [frozenset(x for x in range(512) if (x & p).bit_count() % 2 == 0) for p in w['ports']] + [full] * R
        for r, vecs in w['helper_final'].items(): ends[int(r)] = span(tuple(vecs))
        self.ends = ends
    def info(self, y, p):
        gl = self.g.get(y, []); ps = self.pos.get(y, []); k = bisect.bisect_left(ps, p)
        Fr = gl[k - 1][2] if k > 0 else self.start[y]
        N = gl[k][2] if k < len(gl) else self.ends[y]
        return Fr, N
    def zc(self, F0, N, T):
        if T == F0: return 0
        if not (F0 <= T) or not (T <= N): return INF
        if T == N: return 0
        a = dim(T) - dim(F0); k = dim(N) - dim(F0); return self.c[a] + self.c[k - a] - self.c[k]
    def cost(self, x, y, p):
        Fx, Nx = self.info(x, p); Fy, Ny = self.info(y, p); U = span(tuple(Fx | Fy)); best = INF
        for T in {Fx, Fy, Nx, Ny, U}:
            if Fx <= T and Fy <= T: best = min(best, self.zc(Fx, Nx, T) + self.zc(Fy, Ny, T))
        return best

def solve(P, w1, caps):
    g = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=caps, cut_equality=True)
    r = F.optimal_frames(inline(w1, True), P.costs, check_literal=False, graph=g)
    return g, r

def price(P, ed, base_rows, timeout=240):
    w1 = compile_A(P.base, ed)
    rows = amap(w1['A'])
    if any(rows.get(q, {q: 1}) != base_rows.get(q, {q: 1}) for q in set(rows) | set(base_rows)): return dict(status='inexact')
    signal.signal(signal.SIGALRM, H._alarm); signal.alarm(timeout)
    try:
        g, r = solve(P, w1, P.caps)
    except F.Infeasible as e: return dict(status='infeasible')
    except H.Timeout: return dict(status='timeout')
    except Exception as e: return dict(status='err:' + repr(e)[:80])
    finally: signal.alarm(0)
    return dict(status='ok' if r['certified'] else 'uncertified', delta=r['cost'] - P.base_cost, profile=dict(sorted(r['profile'].items())))

def norm(row):
    if not row: return None, None
    k0 = min(row); a = row[k0]; return tuple(sorted((k, v / a) for k, v in row.items())), a

def run(P, dels, maxterms, K, tl, out, lamr=8):
    w = P.base; A = w['A']; NA = len(A); nreg = 2 * V + w['report']['R']
    base_rows = amap(A)
    # exact rational rows over A: values and windows
    rows = {}; get = lambda x: rows.get(x, {x: Q(1)})
    srcval = {}; cur_key = {x: norm({x: Q(1)}) for x in range(nreg)}; cur_start = {x: 0 for x in range(nreg)}; wins = defaultdict(list)
    for i, g in enumerate(A):
        if i in dels: srcval[i] = dict(get(g[2]))
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
        if key is not None: wins[key].append((x, cur_start[x], NA + 1, al))
    keys = {norm(srcval[i])[0] for i in dels}; assert len(keys) == 1
    key = keys.pop(); alpha0 = {i: norm(srcval[i])[1] for i in dels}
    holders = defaultdict(list)
    for y, a_, b_, al in wins[key]:
        for p in range(a_, min(b_, NA + 1)): holders[p].append((y, al))
    w1 = compile_A(w, dict(delete=dels)); g, r = solve(P, w1, P.caps); ddel = r['cost'] - P.base_cost
    w2 = write_back(w1, g, r['assign']); orc = Orc(w2, P.costs.c); ds = sorted(dels)
    to2 = lambda p: p - sum(1 for t in ds if t < p)
    bud = -ddel - 1
    cols = {}; S = lambda x: cols.get(x, {x: Q(1)})
    d = {}; seen = {}; cand = []
    for i in range(NA, -1, -1):
        gte = A[i] if i < NA else None
        if gte is None: pass
        elif i in dels:
            t = gte[1]; c = coef(gte) * alpha0[i]
            for k, v in S(t).items(): d[k] = d.get(k, 0) + c * v
        elif gte[0] == 'add':
            t, s = gte[1], gte[2]; c = coef(gte); a = dict(S(s))
            for k, v in S(t).items():
                a[k] = a.get(k, 0) + c * v
                if not a[k]: del a[k]
            cols[s] = a
        else:
            x = gte[1]; cols[x] = {k: v * coef(gte) for k, v in S(x).items()}
        if i in holders:
            p2 = to2(i)
            for y, al in holders[i]:
                for x in range(nreg):
                    if x == y or (V <= y < 2 * V and not (V <= x < 2 * V)): continue
                    cst = orc.cost(x, y, p2)
                    if cst > bud: continue
                    vf = S(x); kk = (x, y, tuple(sorted(vf.items())))
                    if kk in seen and seen[kk] <= cst: continue
                    seen[kk] = cst; cand.append((x, y, i, al, {k: v * al for k, v in vf.items()}, cst))
    d = {k: v for k, v in d.items() if v}
    rowsF = set(d)
    for c_ in cand: rowsF |= set(c_[4])
    den = 1
    for c_ in cand:
        for val in c_[4].values(): den = max(den, val.denominator)
    for val in d.values(): den = max(den, val.denominator)
    SC = 2 * den
    m = cp_model.CpModel(); lam = []; z = []
    for j in range(len(cand)):
        l = m.NewIntVar(-lamr, lamr, ''); b = m.NewBoolVar(''); m.Add(l == 0).OnlyEnforceIf(b.Not()); m.Add(l != 0).OnlyEnforceIf(b); lam.append(l); z.append(b)
    by = defaultdict(list)
    for j, c_ in enumerate(cand):
        for rr, val in c_[4].items(): by[rr].append((j, val))
    ok = True
    for rr in rowsF:
        rhs = d.get(rr, Q(0)) * 2 * SC; terms = [lam[j] * int(val * SC) for j, val in by.get(rr, [])]
        if not terms:
            if rhs: ok = False
            continue
        m.Add(sum(terms) == int(rhs))
    m.Add(sum(z) <= maxterms); m.Add(sum(z[j] * cand[j][5] for j in range(len(cand))) <= bud)
    m.Minimize(sum(z[j] * (cand[j][5] + 50) for j in range(len(cand))))
    print('A dels', dels, [A[i][:5] for i in dels], 'ddel', ddel, 'wins', len(wins[key]), 'cand', len(cand), 'd', len(d), 'shape', ok, flush=True)
    res = []
    if ok and ddel < 0:
        for it in range(K):
            s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.num_workers = 2
            st = s.Solve(m)
            if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): print('stop', s.StatusName(st), flush=True); break
            supp = [j for j in range(len(cand)) if s.Value(z[j])]
            terms = [(cand[j][0], cand[j][1], cand[j][2], Q(s.Value(lam[j]), 2)) for j in supp]
            est = sum(cand[j][5] for j in supp)
            m.Add(sum(z[j] for j in supp) <= len(supp) - 1)
            ed = dict(delete=list(dels), insert=sorted([(p, ['add', x, y, l.numerator, l.denominator, []]) for x, y, p, l in terms], key=lambda t: t[0]))
            rr = price(P, ed, base_rows)
            res.append(dict(terms=[(x, y, p, str(l)) for x, y, p, l in terms], est=est, status=rr.get('status'), delta=rr.get('delta'), profile=rr.get('profile'), ed=ed))
            print(it, len(terms), 'est', est, [(x, y, p, str(l)) for x, y, p, l in terms], rr.get('status'), rr.get('delta'), flush=True)
    json.dump(dict(ddel=ddel, res=res), open(out, 'w'), indent=1)
    return ddel, res

if __name__ == '__main__':
    word = sys.argv[1]; P = H.Pricer(word)
    jobs = json.loads(sys.argv[2]); maxterms, K, tl = int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
    for dels in jobs:
        t0 = time.time()
        try: ddel, res = run(P, dels, maxterms, K, tl, os.path.join(os.environ.get('OUT_DIR', '.'), 'ak-%s.json') % '-'.join(map(str, dels)))
        except Exception as e:
            import traceback; traceback.print_exc(); continue
        best = min([r['delta'] for r in res if r.get('delta') is not None], default=None)
        print('SUMMARY', dels, 'ddel', ddel, 'nsol', len(res), 'best', best, '%.1fs' % (time.time() - t0), flush=True)
