"""ARF inv.py (own code): fixed-Q Z/4 invariants of P104. Exact integer arithmetic.
(1) q(x)=x^T Q x mod 4 on F2^104 equals -wt(L^T x) mod 4 (L = 104x9 labels)  [checked on random x + proved in ARF.md]
(2) Gauss sums / Brown invariants for P104, every frame, sub-port-sets.
(3) canonical spaces: Pi (pure quadratic monomials), R(2) radical, universal tau-form."""
import sys, os, itertools, numpy as np, cmath
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../orbitlp'))
from geo import Q, LAB, frames
n = 104
L = np.array([[int(c) for c in format(x, '09b')] for x in LAB])
rng = np.random.default_rng(0)
# (1)
for _ in range(2000):
    x = rng.integers(0, 2, n)
    assert (x @ Q @ x) % 4 == (-(((L.T @ x) % 2).sum())) % 4
print('[C] q(x)=x^TQx mod 4 == -wt(L^T x) mod 4 on 2000 random x: OK; all labels wt%4==3:', all(bin(v).count('1') % 4 == 3 for v in LAB))
def gauss_sub(P):
    """Gauss sum of q restricted to F2^P = 2^{|P|-rk} * sum_{z in span l_P} i^{-wt z}; return (|G|^2 as exponent of 2, Brown mod 8 or None)"""
    B = L[list(P)] % 2
    # span basis
    basis = []
    for v in B:
        v = int(''.join(map(str, v)), 2)
        for b in basis: v = min(v, v ^ b)
        if v: basis.append(v)
    span = [0]
    for b in basis: span = span + [s ^ b for s in span]
    S = sum(1j ** ((-bin(z).count('1')) % 4) for z in span)
    S = complex(round(S.real), round(S.imag))
    rk = len(basis)
    if abs(S) < 1e-9: return rk, None, 0
    ang = cmath.phase(S) / (2 * cmath.pi) * 8
    return rk, int(round(ang)) % 8, abs(S) ** 2
print('P104: rank', gauss_sub(range(n)))
F = frames(); res = {}
for f in F:
    r = gauss_sub(f); res[r[:2]] = res.get(r[:2], 0) + 1
print('frames (rank, Brown):', res)
# frame label structure
f = F[0]; print('frame0 labels', [format(LAB[i], '09b') for i in f])
# (3) Pi: e_t -> (l_ti l_tj)_{i<j}
pairs = list(itertools.combinations(range(9), 2))
Pi = np.array([[L[t, i] * L[t, j] for (i, j) in pairs] for t in range(n)]).T  # 36 x n
def rkF2(M):
    M = [int(''.join(str(int(c) % 2) for c in r), 2) for r in M]; basis = []
    for v in M:
        for b in basis: v = min(v, v ^ b)
        if v: basis.append(v)
    return len(basis)
print('rank Pi (36 x 104):', rkF2(Pi), ' rank [L^T;Pi]:', rkF2(np.concatenate([L.T, Pi])))
print('rank of Gram Pi Pi^T:', rkF2(Pi @ Pi.T), ' rank L^T L:', rkF2(L.T @ L), ' rank Pi L:', rkF2(Pi @ L))
