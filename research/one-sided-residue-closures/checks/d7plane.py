# D7 plane fact (SC-A2), exact rational arithmetic, no sympy: the 32 directions served by a D7 8-set (formF.pkl, from annon.py)
# lie in no plane with a third of them; a plane through two of them holds 0 or 2 of the 112+8 E8 lines (never 1, never >=3).
import pickle, itertools, sys
from fractions import Fraction
from math import lcm
import p112 as p
def rref(M):
    M = [[Fraction(x) for x in r] for r in M]; piv = []; r = 0
    for c in range(len(M[0])):
        k = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if k is None: continue
        M[r], M[k] = M[k], M[r]; M[r] = [x / M[r][c] for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0: M[i] = [a - M[i][c] * b for a, b in zip(M[i], M[r])]
        piv.append(c); r += 1
        if r == len(M): break
    return M[:r], piv
def rank(M): return len(rref(M)[1])
def nullvec(M):
    R, piv = rref(M); free = [c for c in range(len(M[0])) if c not in piv]
    assert len(free) == 1, len(free)
    f = free[0]; v = [Fraction(0)] * len(M[0]); v[f] = Fraction(1)
    for row, c in zip(R, piv): v[c] = -row[f]
    L = lcm(*[x.denominator for x in v]); return [int(x * L) for x in v]
D = pickle.load(open('formF.pkl', 'rb'))['A']
F, ms = max(D.items(), key=lambda t: len(t[1]))
n4 = sum(1 for i in range(112) if p.PL[i] in F)
H = []
for gm in ms:
    perp = [p.P[i] for i in range(112) if not gm >> i & 1]
    H.append(nullvec([list(p.LINES[i]) for i in perp]))
E8 = [list(l) for l in p.LINES]
c3 = {}; cE = {}
for a, b in itertools.combinations(range(len(H)), 2):
    assert rank([H[a], H[b]]) == 2
    t = sum(1 for c in range(len(H)) if c not in (a, b) and rank([H[a], H[b], H[c]]) == 2)
    e = sum(1 for l in E8 if rank([H[a], H[b], l]) == 2)
    c3[t] = c3.get(t, 0) + 1; cE[e] = cE.get(e, 0) + 1
print('4-flat holds %d lines of P112; directions served: %d; third served directions in a plane: %s; E8 lines in a plane: %s' % (n4, len(H), c3, cE))
ok = n4 == 8 and len(H) == 32 and c3 == {0: 496} and set(cE) <= {0, 2}
print(('PASS' if ok else 'FAIL') + ' D7 plane fact: no plane contains three of the 32 directions; each plane through two holds 0 or 2 E8 lines (%s)' % cE)
sys.exit(0 if ok else 1)
