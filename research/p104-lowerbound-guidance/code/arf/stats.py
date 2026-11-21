"""ARF stats.py (own code): per-decoder subspace statistics vs fixed-Q spaces (R1 = label code, P2 = Pi-image (28-dim),
R2, Rad2 = R2 ∩ R2^perp). J = all spans U = sum R'_s, V = sum R_t. f = dimU + dimV - rank<U,V> (= n - tau-rank at J=all).
usage: stats.py [npz-or-prefix ...]   (prefix p loads p_W.npy / p_V.npy)"""
import sys, os, itertools, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE + '/../tau48'); os.chdir(HERE + '/../tau48')
ARGS = sys.argv[1:]; sys.argv = sys.argv[:1]
from gibbs import *
L = Lab
def rows_basis(M):
    b = f2basis([toint(r) for r in np.asarray(M) % 2]); return b
def dimI(*Bs):
    return f2rank([x for B in Bs for x in B])
def bits(x): return np.array([(x >> (n - 1 - s)) & 1 for s in range(n)])
def mat(B): return np.array([bits(x) for x in B]).reshape(-1, n)
R1 = rows_basis(L.T)
pairs = list(itertools.combinations(range(9), 2))
P2 = rows_basis(np.array([[L[t, i] * L[t, j] for (i, j) in pairs] for t in range(n)]).T)
R2 = f2basis(R1 + P2)
M2 = mat(R2); G = (M2 @ M2.T) % 2
from e8xy_lib import nullsp
coef = nullsp(G, range(len(R2)), len(R2)); Rad2 = rows_basis((coef @ M2) % 2) if len(coef) else []
print('fixed: dim R1', len(R1), 'P2', len(P2), 'R2', len(R2), 'Rad2', len(Rad2), 'P2∩R1', len(P2) + len(R1) - len(R2),
      'Rad2∩P2', len(Rad2) + len(P2) - dimI(Rad2, P2))
def inter(A, B): return len(A) + len(B) - dimI(A, B)
def st(W, V, tag):
    W = W % 4; V = V % 4
    RB = spaces_B(W, V, Q); RA = spaces_A(W, V, Q)
    U = f2basis([x for t in range(n) for x in RA[t]]); Vv = f2basis([x for t in range(n) for x in RB[t]])
    MU = mat(U); MV = mat(Vv); r = rk(MU @ MV.T) if len(U) and len(Vv) else 0
    f = len(U) + len(Vv) - r
    out = dict(C=cost(W, V, Q), dU=len(U), dV=len(Vv), UV=inter(U, Vv), rUV=r, f=f,
               rUU=rk(MU @ MU.T), rVV=rk(MV @ MV.T),
               U_R1=inter(U, R1), V_R1=inter(Vv, R1), U_P2=inter(U, P2), V_P2=inter(Vv, P2),
               U_R2=inter(U, R2), V_R2=inter(Vv, R2), UV_R2=inter(f2basis(U + Vv), R2), U_Rad=inter(U, Rad2), V_Rad=inter(Vv, Rad2))
    print(tag, ' '.join('%s=%s' % kv for kv in out.items()), flush=True)
    return out
if __name__ == '__main__':
    st(np.load('../orbitlp/e8W.npy'), np.load('../orbitlp/e8V.npy'), 'E8')
    for p in ARGS:
        st(np.load(p + '_W.npy') if os.path.exists(p + '_W.npy') else np.load(p.replace('XX', 'W') + '.npy'),
           np.load(p + '_V.npy') if os.path.exists(p + '_V.npy') else np.load(p.replace('XX', 'V') + '.npy'), os.path.basename(p))
