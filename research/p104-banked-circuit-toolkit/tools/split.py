#!/usr/bin/env python3
"""BANK split (generalised #7697 chart-595 split).
Helper group G: non-main roles with common entrance E and exit X (normalized identity maps).  At a chart C (E < C < X nested)
pick a cut: injected departures Dp (moves leaving C) and prefix arrivals A (arrivals at C that are not descendants of Dp).
Need ell in span(val A) supported on G inputs, v in span(J_k, k in Dp) supported on G outputs, ell(v) = 1, ell[r] != 0.
Then role r exits at C with ell(x) = u_r, a fresh role n enters at C with g and exits at X; targets: R -> (d, R - d).
usage: split.py WORD CIRCUIT OUT [shard nsh]   (screen, mod p)"""
import sys, os, json, time
import numpy as np
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import *
import search2 as S2
import nest
p = S2.p; KAP = float(os.environ.get("BANK_KAPPA", "0.00373"))  # screen scoring only
f = lambda r: r ** (1 - KAP) if r else 0.0

def left_kernel(M):
    """rows c with c M = 0 (mod p); M: m x q."""
    m = M.shape[0]
    if M.shape[1] == 0: return np.eye(m, dtype=np.int64)
    A = np.concatenate([M % p, np.eye(m, dtype=np.int64)], axis=1); r = 0; q = M.shape[1]
    for c in range(q):
        if r == m: break
        nz = np.flatnonzero(A[r:, c])
        if not len(nz): continue
        i = r + nz[0]; A[[r, i]] = A[[i, r]]; A[r] = A[r] * pow(int(A[r, c]), -1, p) % p
        col = A[:, c].copy(); col[r] = 0; nzr = np.flatnonzero(col)
        A[nzr] = (A[nzr] - np.outer(col[nzr], A[r])) % p
        r += 1
    return A[r:, q:]

def setup(W, net, dim):
    h = W['hosted']; mains = set(W['live']) | {r + 112 for r in W['live']} | set(h['X2']) | set(h['Y2'])
    n = len(net.init)
    order = schedule(net); V = values(net, p, order)
    tn = transpose(net); Vt = values(tn, p)            # Vt[k] = effect of a unit added to form k on all outputs
    kids = defaultdict(list)
    for k, row in net.forms.items():
        for d in row:
            if d >= 0: kids[d].append(k)
    pos = {k: i for i, k in enumerate(order)}
    desc = {}
    for k in reversed(order):
        b = 1 << k if k < net.first else 0
        for m in kids[k]: b |= desc[m]
        desc[k] = b
    groups = defaultdict(list)
    for r in range(n):
        if r not in mains: groups[(net.init[r], net.final[r])].append(r)
    return dict(mains=mains, n=n, V=V, Vt=Vt, pos=pos, desc=desc, groups=groups)

def screen_chart(W, net, dim, S, C, out, log):
    n = S['n']; fr = W['frames']
    arr = [k for k, (a, b) in net.moves.items() if b == C]
    dep = sorted([k for k, (a, b) in net.moves.items() if a == C], key=lambda k: S['pos'][k])
    inputs_here = [r for r in range(n) if net.init[r] == C]
    if not dep or not (arr or inputs_here): return
    for (E, X), G in S['groups'].items():
        if len(G) < 2 or C in (E, X): continue
        if not (nest.nested(fr, E, C) and nest.nested(fr, C, X)): continue
        dE, dC, dX = dim[E], dim[C], dim[X]
        if not (min(dE, dX) < dC < max(dE, dX)): continue
        R = abs(dX - dE); d = abs(dC - dE); gain = f(d) + f(R - d) - f(R)
        Gs = np.array(sorted(G)); mask = np.zeros(n, bool); mask[Gs] = True; ng = np.flatnonzero(~mask)
        for t0 in range(len(dep)):                     # cut: inject into dep[t0:]
            Dp = dep[t0:]; dmask = 0
            for k in Dp: dmask |= S['desc'][k]
            A = [~r for r in inputs_here] + [k for k in arr if not (dmask >> k) & 1]
            if not A: continue
            Av = np.array([(np.eye(1, n, ~a, dtype=np.int64)[0] if a < 0 else S['V'][a]) for a in A])
            cL = left_kernel(Av[:, ng])
            if not len(cL): continue
            Lg = (cL @ Av[:, Gs]) % p                  # ell rows on group coords
            Jv = np.array([S['Vt'][k] for k in Dp])    # effects on outputs (outputs indexed like roles)
            cV = left_kernel(Jv[:, ng])
            if not len(cV): continue
            Vg = (cV @ Jv[:, Gs]) % p
            P_ = (Lg @ Vg.T) % p
            if P_.any():
                h = dict(C=C, E=E, X=X, cut=t0, ndep=len(Dp), nA=len(A), dimL=len(cL), dimV=len(cV), ranks=[R, d, R - d], gain=gain, group=len(G))
                out.append(h); log.write(json.dumps(h) + '\n'); log.flush()
                break                                   # largest cut that works for this group

if __name__ == '__main__':
    W = load(sys.argv[1]); dim = [len(x) for x in W['frames']]
    net = load_circuit(sys.argv[2])
    if os.environ.get('BANK_DIR') == 'transpose': net = transpose(net)
    sh, nsh = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (0, 1)
    S = setup(W, net, dim); out = []; log = open(sys.argv[3] + '.jsonl', 'w'); t0 = time.time()
    charts = sorted({b for a, b in net.moves.values()} | {a for a, b in net.moves.values()})
    for i, C in enumerate(charts):
        if i % nsh != sh: continue
        if os.environ.get('BANK_C') and C != int(os.environ['BANK_C']): continue
        screen_chart(W, net, dim, S, C, out, log)
        if i % 100 < nsh: print('prog', i, len(out), round(time.time() - t0), file=sys.stderr, flush=True)
    print('split screen hits', len(out), Counter(tuple(h['ranks']) for h in out).most_common(10))
