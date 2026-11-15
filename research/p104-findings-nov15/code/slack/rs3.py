#!/usr/bin/env python3
"""SLACK rs3.py = CALLEROPEN rs2.py with INTERVAL lines (stage tuple, count, support).
CALLEROPEN rs2.py [N]: same model as rootsearch.py (units, product -I, HOST pair invariant, supports in masks, PREFIX
COMMUTATION before/after every stage, optional crossing idle lines) with an ANALYTIC Jacobian.  Solver scipy least_squares
(trf), fixed number of random starts per row (stopping rule).  solved = max|residual| < 1e-10."""
import sys, json
import numpy as np
from scipy.optimize import least_squares
class Model:
    def __init__(s, n, order, t, lines=()):
        s.n = n; units = []; stages = []
        for it in order:
            if it[0] == 'S': stages.append((len(units), list(it[1]))); units += [list(it[1]), list(it[1])]
            else: units.append(list(range(n)) if len(it) == 1 else list(it[1]))
        s.units = units; s.stages = stages; s.N = N = len(units)
        s.idx = []; off = 0
        for sup in units: s.idx.append((off, np.array(sup))); off += 2 * len(sup)
        s.lidx = []
        for spec in lines:          # (stage tuple, count, support or None = intersection of the stage masks)
            st_, c, S = spec
            if S is None: S = sorted(set.intersection(*[set(stages[a][1]) for a in st_]))
            for _ in range(c): s.lidx.append((tuple(st_), None, off, np.array(sorted(S)))); off += 2 * len(S)
        s.dim = off; s.tk = t if isinstance(t, (list, tuple)) else [t] * len(stages)
    def unpack(s, z):
        X = np.zeros((s.N, s.n)); Y = np.zeros((s.N, s.n))
        for i, (o, sup) in enumerate(s.idx):
            k = len(sup); X[i, sup] = z[o:o + k]; Y[i, sup] = z[o + k:o + 2 * k]
        return X, Y
    def fj(s, z):
        n, N = s.n, s.N; X, Y = s.unpack(z); I = np.eye(n)
        T = [I - 2 * np.outer(X[i], Y[i]) for i in range(N)]
        pref = [I]
        for i in range(N): pref.append(T[i] @ pref[-1])
        rows = []; jac = []
        def blank(m): return np.zeros((m, s.dim))
        # 1 isotropy
        r = np.sum(X * Y, axis=1); J = blank(N)
        for i, (o, sup) in enumerate(s.idx):
            k = len(sup); J[i, o:o + k] = Y[i, sup]; J[i, o + k:o + 2 * k] = X[i, sup]
        rows.append(r); jac.append(J)
        # product and prefixes: d(A_{u}) where A_u = T_{u-1}..T_0 ; dA_u/dunit i (i<u) = Suf(u,i) dT_i pref_i
        def dprod(u, sel_r=None, sel_c=None):
            """Jacobian of pref[u] entries (restricted rows/cols) w.r.t. all unit params."""
            R_ = np.arange(n) if sel_r is None else sel_r; C_ = np.arange(n) if sel_c is None else sel_c
            Jm = np.zeros((len(R_) * len(C_), s.dim))
            suf = I.copy()   # T_{u-1}..T_{i+1}
            for i in range(u - 1, -1, -1):
                o, sup = s.idx[i]; k = len(sup)
                a = suf[np.ix_(R_, sup)]                    # S[:, a] rows R_
                yP = (Y[i] @ pref[i])[C_]                    # (y^T P)[c]
                Sx = (suf @ X[i])[R_]; Pb = pref[i][np.ix_(sup, C_)]
                # d/dx_i[a]: -2 S[r,a] yP[c] ; d/dy_i[b]: -2 Sx[r] P[b,c]
                Jm[:, o:o + k] = (-2 * a[:, None, :] * yP[None, :, None]).reshape(len(R_) * len(C_), k)
                Jm[:, o + k:o + 2 * k] = (-2 * Sx[:, None, None] * Pb.T[None, :, :]).reshape(len(R_) * len(C_), k)
                suf = suf @ T[i]
            return Jm
        rows.append((pref[N] + I).ravel()); jac.append(dprod(N))
        for st, (u0, mask) in enumerate(s.stages):
            p, q = u0, u0 + 1; a = Y[p] @ X[q]; b = Y[q] @ X[p]
            J = blank(1); op, sp = s.idx[p]; oq, sq = s.idx[q]; kp = len(sp); kq = len(sq)
            # d(a b): a = Y[p].X[q], b = Y[q].X[p]
            J[0, op + kp:op + 2 * kp] += b * X[q, sp]; J[0, oq:oq + kq] += b * Y[p, sq]
            J[0, oq + kq:oq + 2 * kq] += a * X[p, sq]; J[0, op:op + kp] += a * Y[q, sp]
            rows.append(np.array([a * b - s.tk[st]])); jac.append(J)
            inm = np.zeros(n, bool); inm[mask] = True; Zi = np.where(inm)[0]; Zo = np.where(~inm)[0]
            if len(Zo):
                for u in (u0, u0 + 2):
                    rows.append(pref[u][np.ix_(Zi, Zo)].ravel()); jac.append(dprod(u, Zi, Zo))
                    rows.append(pref[u][np.ix_(Zo, Zi)].ravel()); jac.append(dprod(u, Zo, Zi))
        byb = {}
        for li, (a_, b_, o, S) in enumerate(s.lidx):
            k = len(S); phi = np.zeros(n); gam = np.zeros(n); phi[S] = z[o:o + k]; gam[S] = z[o + k:o + 2 * k]
            byb.setdefault(a_, []).append((o, S, phi, gam))
            ua = sum(([s.stages[a][0], s.stages[a][0] + 1] for a in a_), [])
            for u in ua:
                ou, su = s.idx[u]; ku = len(su)
                J = blank(1); J[0, ou + ku:ou + 2 * ku] = phi[su]; J[0, o:o + k] = Y[u, S]; rows.append(np.array([Y[u] @ phi])); jac.append(J)
                J = blank(1); J[0, ou:ou + ku] = gam[su]; J[0, o + k:o + 2 * k] = X[u, S]; rows.append(np.array([gam @ X[u]])); jac.append(J)
        for key, Ls in byb.items():
            for i, (oi, Si, phi_i, gam_i) in enumerate(Ls):
                for j, (oj, Sj, phi_j, gam_j) in enumerate(Ls):
                    J = blank(1); J[0, oj:oj + len(Sj)] += gam_i[Sj]; J[0, oi + len(Si):oi + 2 * len(Si)] += phi_j[Si]
                    rows.append(np.array([gam_i @ phi_j - (i == j)])); jac.append(J)
        return np.concatenate(rows), np.vstack(jac)
def run(model, starts, seed=1, scale=0.7, nfev=600):
    rng = np.random.default_rng(seed); best = 1e9; hits = 0; zb = None
    f = lambda z: model.fj(z)[0]; jf = lambda z: model.fj(z)[1]
    for _ in range(starts):
        z0 = rng.normal(size=model.dim) * scale
        try: r = least_squares(f, z0, jac=jf, method='trf', xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=nfev)
        except Exception: continue
        c = float(np.max(np.abs(r.fun)))
        if c < best: best, zb = c, r.x
        hits += c < 1e-10
    return hits, best, zb
def two_arm(L, nh, grow=2, outer_own=2, rho=2, nl=None, extra_thin=0):
    nl = L // 2 if nl is None else nl; nr = L - nl; hubs = list(range(nh)); nxt = nh; left = []; cur = []
    for k in range(nl):
        c = outer_own if k == 0 else grow; cur = cur + list(range(nxt, nxt + c)); nxt += c; left.append(sorted(hubs + cur))
    cur = []; right = []
    for k in range(nr):
        c = outer_own if k == 0 else grow; cur = cur + list(range(nxt, nxt + c)); nxt += c; right.append(sorted(hubs + cur))
    n = nxt + extra_thin; th = n + rho - 2 * L
    return n, [('S', m) for m in left] + [('T',)] * th + [('S', m) for m in right[::-1]], th
if __name__ == '__main__':
    # Jacobian self-check
    n, o, th = two_arm(4, 2); m = Model(n, o, -0.5, ((0, 1, 2),)); z = np.random.default_rng(0).normal(size=m.dim)
    r0, J = m.fj(z); e = 1e-6; Jn = np.zeros_like(J)
    for i in range(m.dim):
        zz = z.copy(); zz[i] += e; Jn[:, i] = (m.fj(zz)[0] - r0) / e
    print('jacobian check max err', np.max(np.abs(J - Jn)), 'scale', np.max(np.abs(J)))
