# QZBUILD batched residual + finite-difference Jacobian in one vectorised evaluation (own code).
import os
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'): os.environ[v]='1'
import numpy as np
from qzcore import Design, chat, HP

class Sys:
    def __init__(s, d, ns=10, seed=0, wD=1.0):
        s.d = d; rng = np.random.default_rng(seed + 1000)
        s.Ds = rng.uniform(0.4, 1.8, size=(ns, d.k))
        s.X = np.array([[np.prod([D[t] for t in S]) for (S, _) in d.inc] for D in s.Ds])  # (ns, m)
        s.T = np.array([[np.prod([D[t] for t in M]) for M in d.masks] for D in s.Ds])     # (ns, n)
        s.stage_idx = [[e for e in range(d.m) if t in d.inc[e][0]] for t in range(d.k)]
        s.E = [np.array([1.0 if t in M else 0.0 for M in d.masks]) for t in range(d.k)]
        s.wD = wD
        s.nh = np.array(d.nh)
    def res(s, Z):
        """Z: (B, nv) -> (B, nres)"""
        d = s.d; n, m = d.n, d.m; B = Z.shape[0]
        V = Z[:, :n*m].reshape(B, m, n); W = Z[:, n*m:2*n*m].reshape(B, m, n); ab = Z[:, 2*n*m:].reshape(B, -1, 2)
        I = np.eye(n)
        out = [np.einsum('bij,bij->bi', V, W) - 1]
        L = [np.broadcast_to(I, (B, n, n))]
        for h, (i, j) in enumerate(d.hostinc):
            a = ab[:, h, 0][:, None, None]; b = ab[:, h, 1][:, None, None]
            vs, vt, ws, wt = V[:, i], V[:, j], W[:, i], W[:, j]
            o = lambda x, y: x[:, :, None]*y[:, None, :]
            X = I + 2*a*b*(o(vs, ws) + o(vt, wt)) - 2*a*o(vs, wt) - 2*b*(1+a*b)*o(vt, ws)
            L.append(X @ L[-1])
        out.append((L[-1] + I).reshape(B, -1))
        Ls = np.stack(L, 1)  # (B, h+1, n, n)
        Le = Ls[:, s.nh]     # (B, m, n, n)
        Vm = np.linalg.solve(Le, V[..., None])[..., 0]
        Wm = np.einsum('bmji,bmj->bmi', Le, W)
        for (VV, WW) in ((V, W), (Vm, Wm)):
            for t in range(d.k):
                idx = s.stage_idx[t]
                S_ = np.einsum('bei,bej->bij', VV[:, idx], WW[:, idx]) - np.diag(s.E[t])
                G = np.einsum('bei,bfi->bef', WW[:, idx], VV[:, idx]) - np.eye(len(idx))
                out.append(S_.reshape(B, -1)); out.append(G.reshape(B, -1))
            R = np.broadcast_to(I, (B, len(s.Ds), n, n)).copy()
            for e in range(m):
                wR = np.einsum('bi,bsij->bsj', WW[:, e], R)
                R += (s.X[:, e] - 1)[None, :, None, None] * VV[:, e][:, None, :, None] * wR[:, :, None, :]
            R -= s.T[None, :, :, None] * I
            out.append(s.wD * R.reshape(B, -1))
        return np.concatenate(out, 1)
    def fj(s, z, h=1e-7):
        Z = np.vstack([z, z + h*np.eye(len(z))])
        r = s.res(Z)
        return r[0], (r[1:] - r[0]).T / h

def lm(sys, z, it=300, tol=1e-13, lam=1e-3, verbose=False, fix=None):
    """Levenberg-Marquardt; fix = boolean mask of frozen coordinates."""
    r, J = sys.fj(z); f = r @ r
    free = np.ones(len(z), bool) if fix is None else ~fix
    for k in range(it):
        Jf = J[:, free]
        A = Jf.T @ Jf; g = Jf.T @ r
        while True:
            try:
                dz = np.linalg.solve(A + lam*np.diag(np.diag(A) + 1e-12), -g)
            except np.linalg.LinAlgError:
                lam *= 10; continue
            z2 = z.copy(); z2[free] += dz
            r2 = sys.res(z2[None])[0]; f2 = r2 @ r2
            if f2 < f:
                z = z2; lam = max(lam/3, 1e-15); break
            lam *= 4
            if lam > 1e12: return z, np.sqrt(f)
        r, J = sys.fj(z); f = r @ r
        if verbose and k % 20 == 0: print('   it', k, '%.3e' % np.sqrt(f), 'lam %.1e' % lam, flush=True)
        if np.sqrt(f) < tol: break
    return z, np.sqrt(f)
