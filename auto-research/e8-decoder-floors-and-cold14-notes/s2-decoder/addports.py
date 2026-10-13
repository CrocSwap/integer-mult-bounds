"""Mixed units: can a non-root port be added?  Bit side: Q-label lam needs an odd F2 label z with <z,u_S>=0 for every
live line S with <lam,L_S> != 0.  Enumerate hyperplane flats (rank-7 sets of roots) -> normals lam."""
import numpy as np, itertools
from geo import *
from collections import Counter
from sympy import Matrix
# hyperplane flats: all subsets of lines spanning a rank-7 space, maximal: generate from 7 independent lines
rng = np.random.default_rng(1)
seen = {}
Lf = L.astype(float)
for trial in range(200000):
    idx = rng.choice(NL, 7, replace=False)
    if np.linalg.matrix_rank(Lf[idx]) < 7: continue
    # normal vector
    M = Matrix(L[idx].tolist()); ns = M.nullspace()[0]
    lam = np.array([int(x) for x in (ns * np.lcm.reduce([int(t.q) for t in ns]))])
    g = np.gcd.reduce(np.abs(lam)); lam //= g
    if lam[np.nonzero(lam)[0][0]] < 0: lam = -lam
    key = tuple(lam)
    if key in seen: continue
    O = [i for i in range(NL) if L[i] @ lam == 0]
    seen[key] = O
print('hyperplane normals found', len(seen))
odd = [z for z in range(1, 512) if bin(z).count('1') % 2 == 1]
types = Counter()
best = {}
for key, O in seen.items():
    lam = np.array(key)
    N = [i for i in range(NL) if L[i] @ lam != 0]
    # min over odd z of |{S in N : <z,u_S>=1}| (lines to puncture); if lam is itself a root line, exclude it
    selfi = LIDX.get(tuple(lam * (2 // max(1, int(np.max(np.abs(lam)))))), None) if False else None
    rootline = [i for i in N if abs(G[i, i]) and np.linalg.matrix_rank(np.vstack([L[i], lam]).astype(float)) == 1]
    Nn = [i for i in N if i not in rootline]
    m = min((sum(lab_dot(z, uint[S]) for S in Nn), z) for z in odd)
    t = (len(O), len(Nn), bool(rootline), m[0])
    types[t] += 1
print(sorted(types.items()))
