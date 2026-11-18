#!/usr/bin/env python3
"""Exact builder for hub2 hits.  usage: hubbuild.py WORD CIRCUIT HITS.jsonl OUTPREFIX
Applies hits greedily (best G first); each must pass schedule() + EXACT terminal equality; prices with PRICEKIT."""
import sys, os, json
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import *
from exval import exact_values
from fsolve import esolve
import nest


def find_u_k1(EV, EVt, nonR, VP, RQ, at, desc, net, n):
    """k=1: u in V_P with u in span(h_x) + RQ + V_X for every non-R need x (mod-p kernel intersection, ratrec, exact)."""
    import numpy as np, hub2 as H2
    from hub2 import vec_mod
    pm = H2.p
    Pm = [vec_mod(EVt[y], n) for y in VP]; m = len(Pm)
    Cb = np.eye(m, dtype=np.int64)          # current c-space basis (rows)
    for x in nonR:
        X = net.moves[x][1] if x < net.first else None
        dx = set() if os.environ.get("BANK_NODESC") else desc(x)
        B = [y for y in RQ if y not in dx] + ([y for y in at(X) if y not in dx] if X is not None else [])
        rows = [(Cb[i] @ np.array(Pm)) % pm for i in range(len(Cb))] + [vec_mod(EV[x], n)] + [vec_mod(EVt[y], n) for y in B]
        ker = H2.kernel(rows, len(Cb))
        if not ker: return None
        Cb = np.array([(k @ Cb) % pm for k in ker]) % pm
        Cb = np.array([r for r in Cb if r.any()])
        if not len(Cb): return None
    rng = np.random.default_rng(7)
    for _ in range(4):
        c = (rng.integers(1, pm, size=len(Cb)) @ Cb) % pm
        j = int(np.flatnonzero(c)[0]); c = c * pow(int(c[j]), -1, pm) % pm
        cq = [H2.ratrec(int(v)) for v in c]
        if any(v is None for v in cq): continue
        u = {}
        for y, cv in zip(VP, cq):
            if cv: axpy(u, EVt[y], cv)
        if u: return u
    return None

def _fail(k):
    if os.environ.get("BANK_DBG"): print("fail@", k, flush=True)
    return None

def build(net, EV, h):
    n = len(net.init); e1, e2, P, Qc, T, R_ = h['e1'], h['e2'], h['P'], h['Q'], h['T'], h['R']
    if net.moves.get(e1, (None,))[0] != P or net.moves[e1][1] != Qc or net.moves.get(e2) != (Qc, T): return _fail(1)
    kids = defaultdict(list)
    for k, row in net.forms.items():
        for d in row:
            if d >= 0: kids[d].append(k)
    memo = {}
    def desc(x):
        if x in memo: return memo[x]
        s = set(); st = [x]
        while st:
            y = st.pop()
            if y in s: continue
            s.add(y); st += kids.get(y, [])
        memo[x] = s; return s
    EVt = dict(EV)
    for r in range(n): EVt[~r] = {r: Q(1)}
    def at(X, ex=()):
        return [~r for r in range(n) if net.init[r] == X] + [k for k, (a, b) in net.moves.items() if b == X and k not in ex]
    Ein = [k for k, ab in net.moves.items() if ab == (P, Qc)]; others = [e for e in Ein if e != e1]
    Redges = [k for k, ab in net.moves.items() if ab == (Qc, R_)]
    RQ = at(Qc, set(Ein)); VP = [x for x in at(P) if x not in desc(e1)]
    needs = [x for x in net.forms if net.chart_of_node(x) == Qc and x != e2]
    nonR = [x for x in needs if x not in Redges]
    # step 2: U from non-R needs
    sol2 = {}; U = []; Ulift = []
    for x in nonR:
        X = net.moves[x][1] if x < net.first else None
        tk0 = [('q', y) for y in RQ if y not in desc(x)]
        if X is not None: tk0 += [('v', y) for y in at(X) if y not in desc(x)]
        mp0 = {t: EVt[t[1]] for t in tk0}; mp0.update({('U', i): U[i] for i in range(len(U))})
        s = esolve(EV[x], tk0 + [('U', i) for i in range(len(U))], mp0, n)
        if s is not None:
            s2 = {}
            for t, c in s.items():
                if t[0] == 'U':
                    for (tg, y), c2 in Ulift[t[1]].items(): s2[('p', y)] = s2.get(('p', y), 0) + c * c2
                else: s2[t] = s2.get(t, 0) + c
            sol2[x] = {t: c for t, c in s2.items() if c}; continue
        tk = tk0 + [('p', y) for y in VP]
        s = esolve(EV[x], tk, {t: EVt[t[1]] for t in tk}, n)
        if s is None: return _fail(2)
        sol2[x] = s; u = {}
        for (tg, y), c in s.items():
            if tg == 'p': axpy(u, EVt[y], c)
        if u: U.append(u); Ulift.append({t: c for t, c in s.items() if t[0] == 'p'})
    if len(U) > len(others):
        if len(others) != 1: return _fail(3)
        u = find_u_k1(EV, EVt, nonR, VP, RQ, at, desc, net, n)
        if u is None: return _fail(3)
        U = [u]; sol2 = {}
        for x in nonR:
            X = net.moves[x][1] if x < net.first else None
            tk0 = [('q', y) for y in RQ if y not in desc(x)]
            if X is not None: tk0 += [('v', y) for y in at(X) if y not in desc(x)]
            mp0 = {t: EVt[t[1]] for t in tk0}; mp0[('U', 0)] = u
            s = esolve(EV[x], tk0 + [('U', 0)], mp0, n)
            if s is None: return _fail(12)
            fu = esolve(u, VP, EVt, n)
            s2 = {}
            for t, c in s.items():
                if t[0] == 'U':
                    for y, c2 in fu.items(): s2[('p', y)] = s2.get(('p', y), 0) + c * c2
                else: s2[t] = s2.get(t, 0) + c
            sol2[x] = {t: c for t, c in s2.items() if c}
    Ut = {('U', i): U[i] for i in range(len(U))}
    # step 3: w1 and G
    exR = desc(e1) | desc(e2)
    for x in Redges: exR |= desc(x)
    VR = [y for y in at(R_) if y not in exR]
    Svecs = [EV[x] for x in Redges] + [EV[e2]]
    w1 = None
    # try w1 candidates: S-vector components in V_P (solve s = p + a + v with p in V_P)
    for s_ in Svecs:
        tk = [('p', y) for y in VP] + [('q', y) for y in RQ] + list(Ut) + [('v', y) for y in VR]
        mp = {t: (Ut[t] if t[0] == 'U' else EVt[t[1]]) for t in tk}
        sol = esolve(s_, tk, mp, n)
        if sol is None: return _fail(4)
        w = {}
        for t, c in sol.items():
            if t[0] == 'p': axpy(w, EVt[t[1]], c)
        if w: w1 = w; break
    cands = []
    try:
        import numpy as np, hub2 as H2
        from hub2 import vec_mod
        pm = H2.p
        Sm = [vec_mod(v, n) for v in Svecs]
        Bm = [(-vec_mod(EVt[y], n)) % pm for y in VP]; Rm = [(-vec_mod(EVt[y], n)) % pm for y in VR]
        for ker in H2.kernel(Sm + Bm + Rm, len(Sm))[:6]:
            if not ker.any(): continue
            j = int(np.flatnonzero(ker)[0]); lam = ker * pow(int(ker[j]), -1, pm) % pm
            lq = [H2.ratrec(int(x)) for x in lam]
            if any(x is None for x in lq): continue
            wv = {}
            for i, c in enumerate(lq):
                if c: axpy(wv, Svecs[i], c)
            sol = esolve(wv, [('p', y) for y in VP] + [('v', y) for y in VR], {('p', y): EVt[y] for y in VP} | {('v', y): EVt[y] for y in VR}, n)
            if sol is None: continue
            w = {}
            for t, c in sol.items():
                if t[0] == 'p': axpy(w, EVt[t[1]], c)
            if w: cands.append(w)
    except ImportError:
        pass                      # numpy absent: the exact fallback below (w1 from the S vectors) is used
    except Exception as ex:
        print('kernel fail', ex)
    cands += [w1] if w1 is not None else []
    cands = cands or [None]
    # if dS = m+1 we may need w1 in S: try also w1 = each S vector's V_P part combined; fall back to search over S basis combos
    best = None
    for w in cands + [None]:
        G = []; gsol = {}
        ok = True
        for i, s_ in enumerate(Svecs):
            tk = [('q', y) for y in RQ] + list(Ut) + [('v', y) for y in VR] + ([('w', 0)] if w else [])
            mp = {t: (Ut[t] if t[0] == 'U' else (w if t[0] == 'w' else EVt[t[1]])) for t in tk}
            sol = esolve(s_, tk, mp, n)
            if sol is None: ok = False; break
            g = {}
            for t, c in sol.items():
                if t[0] in ('q', 'U'): axpy(g, mp[t], c)
            gsol[i] = sol
            if g and esolve(g, [('G', j) for j in range(len(G))], {('G', j): G[j] for j in range(len(G))}, n) is None: G.append(g)
        if ok and len(G) <= len(Redges): best = (w, G); break
    if best is None: return _fail(5)
    w1, G = best
    forms = dict(net.forms); moves = dict(net.moves); newv = {}
    # carriers P->Q
    for i, e in enumerate(others):
        if i < len(U):
            fm = esolve(U[i], VP, EVt, n)
            if fm is None: return _fail(6)
            forms[e] = fm; newv[e] = U[i]
        else: forms[e] = {}; newv[e] = {}
    moves[e1] = (P, R_)
    if w1:
        fm = esolve(w1, VP, EVt, n)
        if fm is None: return _fail(7)
        forms[e1] = fm; newv[e1] = w1
    else: forms[e1] = {}; newv[e1] = {}
    EVn = dict(EVt); EVn.update(newv)
    Qtok = RQ + [e for e in others]
    # Redges carry G
    for j, x in enumerate(Redges):
        g = G[j] if j < len(G) else {}
        fm = esolve(g, [y for y in Qtok if y not in desc(x)], EVn, n) if g else {}
        if fm is None: return _fail(8)
        forms[x] = fm; newv[x] = g
    EVn.update(newv)
    # non-R needs: send Q-part; receiver adds V_X part
    for x in nonR:
        X = net.moves[x][1] if x < net.first else None
        s = sol2[x]; gx = {}; vx = {}
        for (tg, y), c in s.items():
            if tg in ('q', 'p'): axpy(gx, EVt[y], c)
            else: vx[y] = c
        fm = esolve(gx if X is not None else EV[x], [y for y in Qtok if y not in desc(x)], EVn, n)
        if fm is None: return _fail(9)
        forms[x] = fm
        if X is not None:
            newv[x] = gx; EVn[x] = gx
            rec = {x: Q(1)}; axpy(rec, vx, Q(1))
            for k2, row in list(forms.items()):
                if k2 != x and x in row and net.chart_of_node(k2) == X:
                    new = {i: v for i, v in row.items() if i != x}; axpy(new, rec, row[x]); forms[k2] = new
    # e2 from R
    Rtok = [e1] + Redges + VR
    fm = esolve(EV[e2], Rtok, EVn, n)
    if fm is None: return _fail(10)
    moves[e2] = (R_, T); forms[e2] = fm
    # R readers of Redges tokens: recover old values
    for x in Redges:
        rec = esolve(EV[x], [e1] + Redges + VR, EVn, n)
        if rec is None: return _fail(11)
        for k2, row in list(forms.items()):
            if x in row and net.chart_of_node(k2) == R_ and k2 != e2:
                new = {i: v for i, v in row.items() if i != x}; axpy(new, rec, row[x]); forms[k2] = new
    for e in list(moves):
        if e in others and not forms[e] and not any(e in r for r in forms.values()): del moves[e]; del forms[e]
    return Net(net.first, net.init, net.final, moves, forms)

if __name__ == '__main__':
    W = load(sys.argv[1]); dim = [len(f) for f in W['frames']]; FR = W['frames']
    net = load_circuit(sys.argv[2])
    txt = open(sys.argv[3]).read()
    hits = json.loads(txt) if txt.lstrip().startswith('[') else [json.loads(l) for l in txt.splitlines() if l.strip()]
    hits.sort(key=lambda h: -h['G'])
    net0 = net; EV0 = exact_values(net0); T0 = [EV0[net0.first + r] for r in range(len(net0.init))]
    pr0, _ = price_net(W, net0, dim, 18); print('base', pk.kstr(pr0['kappa'], 16), flush=True)
    applied = []
    for h in hits:
        nn = net if h['dir'] == 'forward' else transpose(net)
        try:
            new = build(nn, exact_values(nn), h)
        except AssertionError as e:
            print('reject', h['e1'], h['e2'], e); continue
        if new is None: print('nobuild', h['e1'], h['e2'], h['R']); continue
        new = new if h['dir'] == 'forward' else transpose(new)
        bad = [k for k, ab in new.moves.items() if nest.trank(FR, *ab) in (None, 0)]
        if bad: print('nonnested/zero', bad[:3]); continue
        try: schedule(new)
        except AssertionError as e: print('sched', h['e1'], h['e2'], e); continue
        EVn = exact_values(new)
        if any(EVn[new.first + r] != T0[r] for r in range(len(T0))): print('terminal mismatch', h['e1'], h['e2']); continue
        net = new; hh = hist(net, dim); pr, _ = price_net(W, net, dim, 18)
        applied.append(h); print('APPLIED', json.dumps(h), 'paid', sum(hh.values()), 'kappa', pk.kstr(pr['kappa'], 16), flush=True)
        dump_circuit(net, sys.argv[4] + '.json.gz'); json.dump(applied, open(sys.argv[4] + '.json', 'w'))
