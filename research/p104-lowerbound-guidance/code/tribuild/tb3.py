# TRIBUILD tb3: numeric FRAME-LEVEL scout of the TRIANGLE witness (scout only, not a claim).
# Frame: k=3g stages (class t%3), hubs j=0,1,2 on stages of class != j, leaves per stage (list), T thins (rank-1, dense) at the END.
# Unknowns: host rows A_t,B_t on E_t; thin vectors a_i,b_i in R^n.  Equations: P + I = 0 (P = thins * P_h), |det K_tt| >= detmin.
import os, sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'): os.environ[v]='1'
import numpy as np
from scipy.optimize import least_squares
def setup(g, leaves, T):
    k = 3*g; n = 3 + sum(leaves); E = []; off = 3
    for t in range(k):
        E.append([j for j in range(3) if j != t % 3] + list(range(off, off+leaves[t]))); off += leaves[t]
    return k, n, E
def unpack(x, n, E, T):
    i = 0; st = []
    for m in E:
        L = len(m); A = np.zeros((n, 2)); B = np.zeros((n, 2))
        A[m] = x[i:i+2*L].reshape(L, 2); B[m] = x[i+2*L:i+4*L].reshape(L, 2); i += 4*L; st.append((A, B))
    th = [(x[i+2*n*j:i+2*n*j+n], x[i+2*n*j+n:i+2*n*j+2*n]) for j in range(T)]
    return st, th
def res(x, n, E, T, detmin):
    st, th = unpack(x, n, E, T); P = np.eye(n); pen = []
    for A, B in st:
        P = (np.eye(n) + A@B.T)@P; pen.append(max(0, detmin - abs(np.linalg.det(2*np.eye(2) + B.T@A))))
        pen.append(max(0, detmin - abs(np.linalg.det(np.eye(2) + B.T@A))))   # V_t invertible
    for a, b in th: P = (np.eye(n) + np.outer(a, b))@P
    return np.r_[(P + np.eye(n)).ravel(), 10*np.array(pen), 1e-3*max(0, np.linalg.norm(x) - 60)]
if __name__ == '__main__':
    g = int(sys.argv[1]); T = int(sys.argv[2]); leaves = list(map(int, sys.argv[3].split(','))); trials = int(sys.argv[4]); seed = int(sys.argv[5])
    k, n, E = setup(g, leaves, T); assert len(leaves) == k
    N = sum(4*len(m) for m in E) + 2*n*T; rng = np.random.default_rng(seed); best = 9e9
    for tr in range(trials):
        r = least_squares(res, rng.normal(size=N), args=(n, E, T, .3), method='trf', max_nfev=4000, xtol=1e-15, ftol=1e-15, gtol=1e-15)
        v = np.abs(res(r.x, n, E, T, .3)).max(); best = min(best, v)
        if v < 1e-10: break
    print(f'g{g} k{k} n{n} T{T} leaves {leaves} d1 {sum(leaves)} (LC bound k+T={k+T}): best max-residual {best:.3e} after {tr+1} trials', flush=True)
