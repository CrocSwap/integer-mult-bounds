# TRIBUILD tb0: numeric sanity scout for LEAF-CHANNEL [P]:  dim(ker(P_h+I) cap U_leaf) <= min(sum a_t, 2k - sum a_t) <= k
# for a host-only stage product V_t = I + A_t B_t^T (A_t,B_t n x 2, rows on E_t), K_tt = 2I + B_t^T A_t invertible.
# Scout: minimise the m smallest singular values of (P_h+I)|U  (n x d1) with a barrier keeping |det K_tt| >= detmin.
# m = k+1 must FAIL (stall), m <= k may succeed.  Also cross-checks dim S = dim(ker K_hh cap ker Acal_H) at the optimum.
import os, sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'): os.environ[v]='1'
import numpy as np
from scipy.optimize import least_squares
def chart(k, h, f):
    # h hubs on every stage (hub chart) + f leaves per stage
    n = h + f*k; E = [list(range(h)) + [h+f*t+i for i in range(f)] for t in range(k)]; return n, E, list(range(h, n))
def tri(g, f):
    k = 3*g; n = 3 + f*k; E = []
    for t in range(k):
        c = t % 3; hubs = [j for j in range(3) if j != c]   # hub j lives on classes != j  (two classes each)
        E.append(hubs + [3+f*t+i for i in range(f)])
    return k, n, E, list(range(3, n))
def mats(x, n, E):
    out = []; i = 0
    for m in E:
        L = len(m); A = np.zeros((n, 2)); B = np.zeros((n, 2))
        A[m] = x[i:i+2*L].reshape(L, 2); B[m] = x[i+2*L:i+4*L].reshape(L, 2); i += 4*L; out.append((A, B))
    return out
def scout(n, E, U, m, trials, seed, detmin=0.3):
    rng = np.random.default_rng(seed); N = sum(4*len(e) for e in E); k = len(E)
    def res(x):
        P = np.eye(n); pen = []
        for A, B in mats(x, n, E):
            P = (np.eye(n) + A@B.T)@P; pen.append(10*max(0, detmin - abs(np.linalg.det(2*np.eye(2) + B.T@A))))
        M = (P + np.eye(n))[:, U]; sv = np.linalg.svd(M, compute_uv=False)
        sc = np.linalg.norm(P) + 1
        return np.r_[sv[len(U)-m:]/sc, pen, 1e-3*max(0, np.linalg.norm(x) - 40)]
    best = (9e9, None)
    for _ in range(trials):
        r = least_squares(res, rng.normal(size=N), method='trf', max_nfev=3000)
        v = np.linalg.norm(res(r.x))
        if v < best[0]: best = (v, r.x)
        if v < 1e-10: break
    return best
if __name__ == '__main__':
    seed = int(sys.argv[1]); trials = int(sys.argv[2])
    tests = []
    for k in (2, 3):
        n, E, U = chart(k, 2, 2)
        for m in range(1, k+2): tests.append((f'2hub+2leaf k{k} d1{len(U)} want dimS>={m} (bound {k})', n, E, U, m))
    k, n, E, U = tri(1, 2)
    for m in range(1, k+2): tests.append((f'tri g1 2leaf k{k} d1{len(U)} want dimS>={m} (bound {k})', n, E, U, m))
    for name, n, E, U, m in tests:
        v, x = scout(n, E, U, m, trials, seed)
        print(f'{name}: best {v:.3e}', flush=True)
