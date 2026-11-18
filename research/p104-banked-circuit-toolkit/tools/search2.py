#!/usr/bin/env python3
"""BANK search v2 (mod-p screen, general gamma, causal re-check).
usage: search2.py WORD CIRCUIT|- DIR OUT.json [minDS]
hit = (t, C, F, dS): exists gamma over readers U of t with gamma.alpha != 0 and
sum gamma_m val(h_m) in V_F + V_C, V_X = values of tokens available at X that are not descendants of t."""
import sys, os, json
import numpy as np
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import *

p = 33554393

def rref(rows, n):
    """returns (piv list, B array k x n) fully reduced."""
    rows = list(rows); M = np.zeros((len(rows), n), dtype=np.int64); piv = []; k = 0
    for v in rows:
        v = v % p
        if k:
            cv = v[piv]; ix = np.flatnonzero(cv)
            if len(ix): v = (v - (cv[ix] @ M[ix]) % p) % p
        nz = np.flatnonzero(v)
        if not len(nz): continue
        c = int(nz[0]); v = v * pow(int(v[c]), -1, p) % p
        if k:
            col = M[:k, c]; idx = np.flatnonzero(col)
            if len(idx): M[idx] = (M[idx] - np.outer(col[idx], v)) % p
        M[k] = v; piv.append(c); k += 1
    return piv, M[:k]

def red(V, piv, B):
    if not piv: return V % p
    if V.ndim == 1:
        cv = V[piv]; ix = np.flatnonzero(cv)
        return (V - (cv[ix] @ B[ix]) % p) % p if len(ix) else V % p
    CV = V[:, piv]; ix = np.flatnonzero(CV.any(axis=0))
    return (V - (CV[:, ix] @ B[ix]) % p) % p if len(ix) else V % p

def kernel_hits_alpha(R, alpha):
    """R: m x n residuals mod p. Is there gamma with gamma R = 0 and gamma.alpha != 0 ?  returns gamma or None."""
    m = R.shape[0]
    A = np.concatenate([R % p, np.eye(m, dtype=np.int64)], axis=1)   # row ops track gamma
    n = R.shape[1]; r = 0
    for c in range(n):
        if r == m: break
        nz = np.flatnonzero(A[r:, c])
        if not len(nz): continue
        i = r + nz[0]; A[[r, i]] = A[[i, r]]
        A[r] = A[r] * pow(int(A[r, c]), -1, p) % p
        for k in range(m):
            if k != r and A[k, c]: A[k] = (A[k] - A[k, c] * A[r]) % p
        r += 1
    for k in range(r, m):
        g = A[k, n:]
        if int(g @ alpha % p): return g
    return None

def run(net, dim, tag, minDS, shard=0, nsh=1, log=None):
    order = schedule(net); V = values(net, p, order); n = len(net.init)
    kids = defaultdict(list)
    for k, row in net.forms.items():
        for d in row:
            if d >= 0: kids[d].append(k)
    desc = {}
    for k in reversed(order):
        b = 1 << k if k < net.first else 0
        for m in kids[k]: b |= desc[m]
        desc[k] = b
    toks = defaultdict(list); tv = {}
    for r in range(n):
        e = np.zeros(n, dtype=np.int64); e[r] = 1; toks[net.init[r]].append(~r); tv[~r] = e
    for k, (a, b) in net.moves.items(): toks[b].append(k); tv[k] = V[k]
    def supbits(v): return int.from_bytes(np.packbits((v != 0)[::-1]).tobytes(), 'big') >> ((-n) % 8)
    sup = {t: supbits(v) for t, v in tv.items()}
    chsup = {X: 0 for X in toks}
    for X, L in toks.items():
        for t in L: chsup[X] |= sup[t]
    stat = {X: rref([tv[x] for x in L], n) for X, L in toks.items()}
    rk = lambda m: abs(dim[net.moves[m][1]] - dim[net.moves[m][0]])
    out = []; nok = 0; import time; t0 = time.time()
    for ti, (t, (A, B)) in enumerate(sorted(net.moves.items())):
        if ti % nsh != shard: continue
        if ti % 500 < nsh: print('prog', ti, len(out), round(time.time() - t0), file=sys.stderr, flush=True)
        U = kids[t]
        if not U or any(m >= net.first for m in U): continue
        Cs = {net.moves[m] for m in U}
        if len(Cs) != 1 or next(iter(Cs))[0] != B: continue
        C = next(iter(Cs))[1]; nok += 1
        dt = desc[t]; base = rk(t) + rk(U[0])
        aC = [x for x in toks[C] if x < 0 or not (dt >> x) & 1]
        pC, BC = rref([tv[x] for x in aC], n)
        alpha = np.array([fmod(net.forms[m][t], p) for m in U], dtype=np.int64)
        Hm = np.array([V[m] for m in U]); RC = red(Hm, pC, BC)
        supU = 0
        for m in U: supU |= sup[m]
        supC = 0
        for x in aC: supC |= sup[x]
        g = kernel_hits_alpha(RC, alpha)
        if g is not None:
            out.append(dict(t=t, C=C, F=None, dS=base, rt=rk(t), rj=rk(U[0]), rnew=0, nU=len(U), causal=True))
            if log: log.write(json.dumps(dict(out[-1], dir=tag)) + '\n'); log.flush()
            continue
        for F in toks:
            if F == B or F == C: continue
            rn = abs(dim[C] - dim[F])
            if base - rn < minDS: continue
            if len(U) == 1:
                if supU & ~(chsup[F] | supC): continue
            elif not (chsup[F] & supU): continue
            pF, BF = stat[F]
            # static screen: reduce H and BC rows by V_F, then by reduced V_C
            R1 = red(Hm, pF, BF); C1 = red(BC, pF, BF) if len(pC) else BC
            pc2, BC2 = rref(list(C1), n); R2 = red(R1, pc2, BC2)
            if kernel_hits_alpha(R2, alpha) is None: continue
            aF = [x for x in toks[F] if x < 0 or not (dt >> x) & 1]
            causal = len(aF) == len(toks[F])
            if not causal:
                pF2, BF2 = rref([tv[x] for x in aF], n)
                R1 = red(Hm, pF2, BF2); C1 = red(BC, pF2, BF2) if len(pC) else BC
                pc2, BC2 = rref(list(C1), n); causal = kernel_hits_alpha(red(R1, pc2, BC2), alpha) is not None
            if causal:
                out.append(dict(t=t, C=C, F=F, dS=base - rn, rt=rk(t), rj=rk(U[0]), rnew=rn, nU=len(U), causal=True))
                if log: log.write(json.dumps(dict(out[-1], dir=tag)) + '\n'); log.flush()
    print(tag, 'eligible t', nok, 'hits', len(out), file=sys.stderr)
    return out

if __name__ == '__main__':
    W = load(sys.argv[1]); dim = [len(f) for f in W['frames']]
    net = fold(W) if sys.argv[2] == '-' else load_circuit(sys.argv[2])
    d = sys.argv[3]; minDS = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    sh, nsh = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (0, 1)
    res = run(net if d == 'forward' else transpose(net), dim, d, minDS, sh, nsh, open(sys.argv[4] + 'l', 'w'))
    for r in res: r['dir'] = d
    res.sort(key=lambda r: (-r['dS'], -r['rt'] - r['rj']))
    json.dump(res, open(sys.argv[4], 'w'))
    print(d, 'hits', len(res), 'distinct t', len({r['t'] for r in res}))
    print(Counter((r['dS'], r['rt'], r['rj'], r['rnew']) for r in res).most_common(30))
    for r in res[:15]: print(r)
