#!/usr/bin/env python3
"""BANK search v3: batched random-functional screen over all charts F at once, then exact-ish mod-p recheck (search2 logic).
No false negatives in the screen (V_F static superset, functionals annihilate V_F); hits rechecked with causal V_F.
usage: search3.py WORD CIRCUIT|- DIR OUT [minDS] [shard nsh]"""
import sys, os, json, time
import numpy as np
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bank import *
import search2 as S2

ps = 1048573; R = 48
RES = bool(os.environ.get('BANK_RES'))
ONLY = {int(x) for x in os.environ.get('BANK_T', '').split(',') if x}

def batched_hit(A, kC, alpha):
    """A: (nF, R, kC+u) mod ps int64.  Rows y with y Z_C = 0 give L = y Z_H; hit iff alpha not in rowspace(L).
    Returns bool array (nF,)."""
    nF, r, c = A.shape; u = c - kC
    A = np.concatenate([A, np.zeros((nF, 1, c), dtype=np.int64)], axis=1)
    A[:, r, kC:] = alpha % ps
    used = np.zeros((nF, r + 1), dtype=bool); used[:, r] = True     # alpha row never pivots
    ar = np.arange(nF)
    for j in range(c):
        cand = (A[:, :, j] != 0) & ~used
        has = cand.any(axis=1)
        if not has.any(): continue
        pr = np.argmax(cand, axis=1)
        idx = ar[has]; prow = pr[has]
        piv = A[idx, prow, :]                                    # (h, c)
        inv_ = np.array([pow(int(x), -1, ps) for x in piv[:, j]], dtype=np.int64)
        piv = piv * inv_[:, None] % ps
        A[idx, prow, :] = piv
        f = A[idx, :, j].copy(); f[np.arange(len(idx)), prow] = 0
        A[idx] = (A[idx] - f[:, :, None] * piv[:, None, :]) % ps
        used[idx, prow] = True
        if j < kC: pass
    # alpha row is reduced against all pivots; pivots from Z_C columns have nonzero Z_C part -> they can only
    # touch alpha's Z_H part if alpha had a Z_C entry (it doesn't, but elimination at Z_C columns uses rows with
    # Z_C pivot; alpha's Z_C entries stay 0 so those steps leave alpha unchanged).
    return A[:, r, :].any(axis=1)

def main():
    W = load(sys.argv[1]); dim = [len(f) for f in W['frames']]
    net = fold(W) if sys.argv[2] == '-' else load_circuit(sys.argv[2])
    d = sys.argv[3]; out_path = sys.argv[4]
    minDS = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    sh, nsh = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (0, 1)
    if d == 'transpose': net = transpose(net)
    t0 = time.time(); order = schedule(net); n = len(net.init)
    Vs = values(net, ps, order); Vp = values(net, S2.p, order)
    kids = defaultdict(list)
    for k, row in net.forms.items():
        for x in row:
            if x >= 0: kids[x].append(k)
    desc = {}
    for k in reversed(order):
        b = 1 << k if k < net.first else 0
        for m in kids[k]: b |= desc[m]
        desc[k] = b
    toks = defaultdict(list)
    for r in range(n): toks[net.init[r]].append(~r)
    for k, (a, b) in net.moves.items(): toks[b].append(k)
    def vec(x, V, p):
        if x < 0:
            e = np.zeros(n, dtype=np.int64); e[~x] = 1; return e
        return V[x]
    charts = sorted(toks); rng = np.random.default_rng(12345)
    Lam = np.zeros((len(charts), R, n))
    S2.p = ps
    for i, F in enumerate(charts):
        piv, B = S2.rref([vec(x, Vs, ps) for x in toks[F]], n)
        lam = rng.integers(0, ps, size=(R, n), dtype=np.int64)
        if piv:
            lam[:, piv] = 0
            lam[:, piv] = (-(lam @ B.T)) % ps
        Lam[i] = lam
    S2.p = 33554393
    print('setup', round(time.time() - t0), file=sys.stderr, flush=True)
    cidx = {F: i for i, F in enumerate(charts)}; cdim = np.array([dim[F] for F in charts])
    rk = lambda m: abs(dim[net.moves[m][1]] - dim[net.moves[m][0]])
    log = open(out_path + 'l', 'w'); out = []; nok = 0; nscr = 0; SF = {}
    for ti, (t, (A_, B_)) in enumerate(sorted(net.moves.items())):
        if ti % nsh != sh: continue
        if ONLY and t not in ONLY: continue
        if ti % 1000 < nsh: print('prog', ti, nok, nscr, len(out), round(time.time() - t0), file=sys.stderr, flush=True)
        if RES:      # re-source: slot t keeps its token, sends W from F instead of its form from A_
            U = [t]; C = B_; B_ = A_; nok += 1; dt = desc[t]; base = rk(t)
            alpha_s = np.array([1], dtype=np.int64)
        else:
            U = kids[t]
            if not U or any(m >= net.first for m in U): continue
            Cs = {net.moves[m] for m in U}
            if len(Cs) != 1 or next(iter(Cs))[0] != B_: continue
            C = next(iter(Cs))[1]; nok += 1; dt = desc[t]; base = rk(t) + rk(U[0])
            alpha_s = np.array([fmod(net.forms[m][t], ps) for m in U], dtype=np.int64)
        aC = [x for x in toks[C] if x < 0 or not (dt >> x) & 1]
        S2.p = ps; pC, BC = S2.rref([vec(x, Vs, ps) for x in aC], n); S2.p = 33554393
        Hm = np.array([Vs[m] for m in U])
        X = np.concatenate([BC, Hm], axis=0)                     # (kC+u, n)
        Sx = np.flatnonzero(X.any(axis=0))
        mask = (base - np.abs(cdim - dim[C]) >= minDS)
        mask[cidx[B_]] = False
        # F = None case (Y local at C) checked by search2 path
        Fi = np.flatnonzero(mask) if not os.environ.get('BANK_FB') else np.array([], dtype=int)
        if len(Fi) and len(pC) + len(U) <= R - 8:
            Z = (Lam[np.ix_(Fi, np.arange(R), Sx)] @ X[:, Sx].T.astype(float)) % ps   # exact: < 2^40 * 1501 < 2^53
            hitm = batched_hit(Z.astype(np.int64), len(pC), alpha_s)
            cand = [charts[i] for i in Fi[hitm]]
        else: cand = [charts[i] for i in Fi]
        if os.environ.get('BANK_FB'): cand = [B_]
        nscr += len(cand)
        # exact-mod-p recheck (search2 logic, reordered: reduce by V_C once per t), causal V_F
        p2 = S2.p
        pC2, BC2 = S2.rref([vec(x, Vp, p2) for x in aC], n)
        alpha2 = np.array([1], dtype=np.int64) if RES else np.array([fmod(net.forms[m][t], p2) for m in U], dtype=np.int64)
        H2 = S2.red(np.array([Vp[m] for m in U]), pC2, BC2)
        if S2.kernel_hits_alpha(H2, alpha2) is not None:
            h = dict(dir=d, t=t, C=C, F=None, dS=base, rt=rk(t), rj=rk(U[0]), rnew=0, nU=len(U))
            out.append(h); log.write(json.dumps(h) + '\n'); log.flush(); continue
        for F in cand:
            aF = [x for x in toks[F] if x < 0 or not (dt >> x) & 1]
            if not aF: continue
            if len(aF) == len(toks[F]):
                if F not in SF: SF[F] = S2.rref([vec(x, Vp, p2) for x in toks[F]], n)
                pF, BF = SF[F]
            else: pF, BF = S2.rref([vec(x, Vp, p2) for x in aF], n)
            pF3, BF3 = S2.rref(list(S2.red(BF, pC2, BC2)), n)
            if S2.kernel_hits_alpha(S2.red(H2, pF3, BF3), alpha2) is None: continue
            rn = abs(dim[C] - dim[F])
            h = dict(dir=d, t=t, C=C, F=F, dS=base - rn, rt=rk(t), rj=rk(U[0]), rnew=rn, nU=len(U))
            out.append(h); log.write(json.dumps(h) + '\n'); log.flush()
    print(d, 'eligible', nok, 'screen-pass', nscr, 'hits', len(out), round(time.time() - t0), file=sys.stderr)
    out.sort(key=lambda r: (-r['dS'], -r['rt'] - r['rj']))
    json.dump(out, open(out_path, 'w'))
    print(d, Counter((r['dS'], r['rt'], r['rj'], r['rnew']) for r in out).most_common(30))

def recheck(net, V, toks, desc, t, U, C, F, n):
    p = S2.p; dt = desc[t]
    def vec(x):
        if x < 0:
            e = np.zeros(n, dtype=np.int64); e[~x] = 1; return e
        return V[x]
    aC = [x for x in toks[C] if x < 0 or not (dt >> x) & 1]
    pC, BC = S2.rref([vec(x) for x in aC], n)
    alpha = np.array([fmod(net.forms[m][t], p) for m in U], dtype=np.int64)
    Hm = np.array([V[m] for m in U])
    if F is None:
        return S2.kernel_hits_alpha(S2.red(Hm, pC, BC), alpha) is not None
    aF = [x for x in toks[F] if x < 0 or not (dt >> x) & 1]
    if not aF: return False
    pF, BF = S2.rref([vec(x) for x in aF], n)
    R1 = S2.red(Hm, pF, BF); C1 = S2.red(BC, pF, BF) if len(pC) else BC
    pc2, BC2 = S2.rref(list(C1), n)
    return S2.kernel_hits_alpha(S2.red(R1, pc2, BC2), alpha) is not None

if __name__ == '__main__':
    main()
