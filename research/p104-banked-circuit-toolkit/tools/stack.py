#!/usr/bin/env python3
"""BANK stack: exact witnesses for screened hits, applied greedily with exact checks.
usage: stack.py WORD CIRCUIT|- OUTPREFIX hits1.json [hits2.json ...]"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import *
from exval import exact_values
import nest

p = 33554393

def solve_witness(net, EV, t, F, C):
    dt_kids = [m for m, row in net.forms.items() if t in row]
    U = dt_kids
    # descendants of t (exact, BFS)
    kids = {}
    for k, row in net.forms.items():
        for d in row:
            if d >= 0: kids.setdefault(d, []).append(k)
    desc = set(); st = [t]
    while st:
        x = st.pop()
        if x in desc: continue
        desc.add(x); st += kids.get(x, [])
    def avail(X):
        if X is None: return []
        L = [~r for r in range(len(net.init)) if net.init[r] == X]
        return L + [k for k, (a, b) in net.moves.items() if b == X and k not in desc]
    aF, aC = avail(F), avail(C)
    def ev(x): return {~x: Q(1)} if x < 0 else EV[x]
    cols = [('g', m, EV[m], Q(1)) for m in U] + [('w', x, ev(x), Q(-1)) for x in aF] + [('d', x, ev(x), Q(1)) for x in aC]
    n = len(net.init); N = len(cols)
    M = np.zeros((n + 1, N), dtype=np.int64)
    for j, (_, _, v, s) in enumerate(cols):
        for i, c in v.items(): M[i, j] = fmod(c * s, p)
    for j, m in enumerate(U): M[n, j] = fmod(net.forms[m][t], p)
    rhs = np.zeros(n + 1, dtype=np.int64); rhs[n] = 1
    A = np.concatenate([M, rhs[:, None]], axis=1) % p; r = 0; piv = []
    for c in range(N):
        nz = np.flatnonzero(A[r:, c]) if r <= n else []
        if not len(nz): continue
        i = r + nz[0]; A[[r, i]] = A[[i, r]]; A[r] = A[r] * pow(int(A[r, c]), -1, p) % p
        col = A[:, c].copy(); col[r] = 0; nzr = np.flatnonzero(col)
        A[nzr] = (A[nzr] - np.outer(col[nzr], A[r])) % p
        piv.append(c); r += 1
        if r > n: break
    if A[r:, N].any(): return None
    # exact solve on pivot columns
    sel = piv
    rows = {}
    for jj, j in enumerate(sel):
        _, _, v, s = cols[j]
        for i, c in v.items(): rows.setdefault(i, {})[jj] = c * s
    rows['n'] = {jj: net.forms[cols[j][1]][t] for jj, j in enumerate(sel) if cols[j][0] == 'g'}
    k = len(sel); R = [[rw.get(jj, Q(0)) for jj in range(k)] + [Q(1) if i == 'n' else Q(0)] for i, rw in rows.items() if rw]
    sol = {}; r = 0
    for c in range(k):
        i = next((i for i in range(r, len(R)) if R[i][c]), None)
        if i is None: return None
        R[r], R[i] = R[i], R[r]; f = R[r][c]; R[r] = [v / f for v in R[r]]
        for i2 in range(len(R)):
            if i2 != r and R[i2][c]:
                g = R[i2][c]; R[i2] = [a - g * b for a, b in zip(R[i2], R[r])]
        r += 1
    if any(R[i][k] for i in range(r, len(R))): return None
    for c in range(k): sol[c] = R[c][k]
    gamma, sender, receiver = {}, {}, {}
    for jj, j in enumerate(sel):
        val = sol.get(jj, Q(0))
        if not val: continue
        kind, x = cols[j][0], cols[j][1]
        {'g': gamma, 'w': sender, 'd': receiver}[kind][x] = val
    if not gamma: return None
    # exact identity check: sum gamma val(h_m) = W - D
    lhs = {}
    for m, g in gamma.items(): axpy(lhs, EV[m], g)
    for x, w in sender.items(): axpy(lhs, ev(x), -w)
    for x, d in receiver.items(): axpy(lhs, ev(x), d)
    if lhs: return None
    if sum(g * net.forms[m][t] for m, g in gamma.items()) == 0: return None
    lead = max(gamma, key=lambda m: (abs(gamma[m]) > 0, -m))
    return lead, gamma, sender, receiver

if __name__ == '__main__':
    W = load(sys.argv[1]); dim = [len(f) for f in W['frames']]
    net0 = fold(W)
    net = net0 if sys.argv[2] == '-' else load_circuit(sys.argv[2])
    hits = []
    for f in sys.argv[4:]: hits += json.load(open(f))
    hits.sort(key=lambda r: (-r['dS'], -(r['rt'] + r['rj'])))
    EV0 = exact_values(net0); T0 = {r: EV0[net0.first + r] for r in range(len(net0.init))}
    applied = []; tried = set()
    cache = {}
    def cur(d):
        if d not in cache:
            nn = net if d == 'forward' else transpose(net); cache[d] = (nn, exact_values(nn))
        return cache[d]
    for h in hits:
        key = (h['dir'], h['t'])
        if key in tried: continue
        nn, EV = cur(h['dir'])
        if h['t'] not in nn.moves: continue
        U = [m for m, row in nn.forms.items() if h['t'] in row]
        if not U or any(m >= nn.first or nn.moves[m] != (nn.moves[h['t']][1], h['C']) for m in U): continue
        wit = solve_witness(nn, EV, h['t'], h['F'], h['C'])
        if wit is None: continue
        lead, gamma, sender, receiver = wit
        Fc = h['F'] if h['F'] is not None else h['C']   # F None: Y local at C -> W = 0 (sender empty)
        try:
            new = apply(net, h['dir'], h['t'], lead, Fc, gamma, sender, receiver); schedule(new)
        except AssertionError as e:
            print('reject', key, e); continue
        if any(nest.trank(W['frames'], *ab) in (None, 0) for ab in new.moves.values()): print('reject nonnested', key); continue
        EVn = exact_values(new)
        if any(EVn[new.first + r] != T0[r] for r in T0): print('reject terminals', key); continue
        tried.add(key); net = new; cache = {}
        hh = hist(net, dim); pr, _ = price_net(W, net, dim, 18)
        applied.append(dict(dir=h['dir'], t=h['t'], lead=lead, F=Fc, dS=h['dS'],
                            gamma={str(k): str(v) for k, v in gamma.items()}, sender={str(k): str(v) for k, v in sender.items()},
                            receiver={str(k): str(v) for k, v in receiver.items()}))
        print('APPLIED', h['dir'], h['t'], 'lead', lead, 'F', Fc, 'dS', h['dS'], 'paid', sum(hh.values()),
              'S', pr['S'], 'kappa', pk.kstr(pr['kappa'], 16), flush=True)
        json.dump(applied, open(sys.argv[3] + '.json', 'w'))
        dump_circuit(net, sys.argv[3] + '.json.gz')
