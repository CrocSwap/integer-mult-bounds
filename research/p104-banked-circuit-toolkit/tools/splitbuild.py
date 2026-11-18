#!/usr/bin/env python3
"""Exact builder for split.py hits (generalised #7697 split).  usage: splitbuild.py WORD CIRCUIT HITS.jsonl OUTPREFIX
Each accepted split must pass: schedule, nesting of all paid edges, EXACT mains == fold(WORD), every helper (incl. fresh) identity."""
import sys, os, json
import numpy as np
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import *
from exval import exact_values
import search2 as S2, hub2 as H2, nest
from split import left_kernel
p = S2.p

def vmod(d, n):
    a = np.zeros(n, dtype=np.int64)
    for i, c in d.items(): a[i] = fmod(c, p)
    return a

def build_split(W, net, h, mains):
    n = len(net.init); C, E, X = h['C'], h['E'], h['X']
    G = sorted(r for r in range(n) if r not in mains and net.init[r] == E and net.final[r] == X)
    Gs = set(G); ng = [i for i in range(n) if i not in Gs]
    EV = exact_values(net); EVt = exact_values(transpose(net))
    order = schedule(net); pos = {k: i for i, k in enumerate(order)}
    kids = defaultdict(list)
    for k, row in net.forms.items():
        for d in row:
            if d >= 0: kids[d].append(k)
    def desc(x):
        s = set(); st = [x]
        while st:
            y = st.pop()
            if y in s: continue
            s.add(y); st += kids.get(y, [])
        return s
    arr = [k for k, (a, b) in net.moves.items() if b == C]
    dep = sorted([k for k, (a, b) in net.moves.items() if a == C], key=lambda k: pos[k])
    Dp = dep[h['cut']:]; D = set()
    for k in Dp: D |= desc(k)
    A = [~r for r in range(n) if net.init[r] == C] + [k for k in arr if k not in D]
    val = lambda a: {~a: Q(1)} if a < 0 else EV[a]
    Av = np.array([vmod(val(a), n) for a in A]); Jv = np.array([vmod(EVt[k], n) for k in Dp])
    cL = left_kernel(Av[:, ng]); cV = left_kernel(Jv[:, ng])
    Gi = np.array(G)
    Lg = (cL @ Av[:, Gi]) % p; Vg = (cV @ Jv[:, Gi]) % p; Pm = (Lg @ Vg.T) % p
    idx = np.argwhere(Pm)
    if not len(idx): return None
    i, j = idx[0]
    a = [H2.ratrec(int(x)) for x in cL[i]]; c = [H2.ratrec(int(x)) for x in cV[j]]
    if any(x is None for x in a + c): return None
    ell = {}
    for ai, t in zip(a, A):
        if ai: axpy(ell, val(t), ai)
    vv = {}
    for ci, k in zip(c, Dp):
        if ci: axpy(vv, EVt[k], ci)
    if any(i_ not in Gs for i_ in ell) or any(i_ not in Gs for i_ in vv): return None
    s = sum(ell.get(r, 0) * vv.get(r, 0) for r in G)
    if not s: return None
    c = [ci / s for ci in c]; vv = {k: x / s for k, x in vv.items()}       # ell(v) = 1
    r = next(rr for rr in G if ell.get(rr))
    newn = n; first = net.first
    # input substitution x_j in terms of u
    sub = {}
    for jj in G:
        if jj == r: continue
        e = {~jj: Q(1)}
        if vv.get(jj): e[~r] = vv[jj]
        sub[~jj] = e
    er = {}
    if vv.get(r): er[~r] = vv[r]
    for jj in G:
        if jj != r and ell.get(jj): er[~jj] = er.get(~jj, 0) - ell[jj] / ell[r]
    sub[~r] = {k: x for k, x in er.items() if x}
    forms = {}
    for k, row in net.forms.items():
        hit = row.keys() & sub.keys()
        if hit:
            new = {t: x for t, x in row.items() if t not in hit}
            for t in hit: axpy(new, sub[t], row[t])
            forms[k] = new
        else: forms[k] = dict(row)
    lform = {t: ai for ai, t in zip(a, A) if ai}     # ell(x) as a form at C (prefix tokens)
    inj = {~newn: Q(1)}; axpy(inj, lform, Q(-1))
    for ci, k in zip(c, Dp):
        if ci: axpy(forms[k], inj, ci)
    oldT = {jj: forms[first + jj] for jj in G}
    ly = {}
    for jj in G:
        if ell.get(jj): axpy(ly, oldT[jj], ell[jj])
    for jj in G:
        if jj == r: continue
        nf = dict(oldT[jj])
        if vv.get(jj): axpy(nf, ly, -vv[jj])
        forms[first + jj] = nf
    forms[first + r] = dict(lform)
    forms[first + newn] = ly
    init = list(net.init) + [C]; final = list(net.final) + [X]; final[r] = C
    return Net(first, init, final, dict(net.moves), forms), r

if __name__ == '__main__':
    W = load(sys.argv[1]); dim = [len(x) for x in W['frames']]; fr = W['frames']
    net = load_circuit(sys.argv[2])
    hits = [json.loads(l) for l in open(sys.argv[3]) if l.strip()]
    hits.sort(key=lambda h: -h['gain'])
    hd = W['hosted']; mains = set(W['live']) | {r + 112 for r in W['live']} | set(hd['X2']) | set(hd['Y2'])
    ref = fold(W); EVr = exact_values(ref)
    pr0, _ = price_net(W, net, dim, 18); print('base', pk.kstr(pr0['kappa'], 16), flush=True)
    for h in hits:
        tr = h.get('dir') == 'transpose' or h['E'] == 127
        nn = transpose(net) if tr else net
        mainsT = mains
        try:
            res = build_split(W, nn, h, mainsT)
        except (AssertionError, StopIteration) as e:
            print('fail', h['C'], repr(e)); continue
        if res is None: print('nobuild', h['C']); continue
        new, r = res
        new = transpose(new) if tr else new
        try: schedule(new)
        except AssertionError as e: print('sched', h['C'], e); continue
        if any(nest.trank(fr, *ab) in (None, 0) for ab in new.moves.values()): print('nonnested', h['C']); continue
        EVn = exact_values(new)
        okm = all(EVn[new.first + m] == EVr[ref.first + m] for m in mains)
        okh = all(EVn[new.first + q] == {q: Q(1)} for q in range(len(new.init)) if q not in mains)
        if not (okm and okh): print('output mismatch', h['C'], okm, okh); continue
        net = new; pr, _ = price_net(W, net, dim, 18)
        print('APPLIED split C=%d E=%d X=%d retired %d -> width %d kappa %s' % (h['C'], h['E'], h['X'], r, len(net.init), pk.kstr(pr['kappa'], 16)), flush=True)
        dump_circuit(net, sys.argv[4] + '.json.gz')
