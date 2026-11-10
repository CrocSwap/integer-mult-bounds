"""E8 from scratch (doubled coordinates), F2 labels, simple roots and fundamental weights. Standard library only."""
import itertools
from fractions import Fraction as Fr

def build():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (2, -2):
            for sj in (2, -2):
                v = [0] * 8; v[i] = si; v[j] = sj; roots.append(tuple(v))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            roots.append(tuple(s))
    assert len(roots) == 240
    seen = set(); lines = []
    for r in roots:
        if tuple(-x for x in r) in seen:
            continue
        seen.add(r); lines.append(r)
    assert len(lines) == 120
    return roots, lines

ROOTS, LINES = build()
n = 120
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def ip(a, b): return dot(a, b) // 4          # root inner product, norm 2
IP = [[ip(LINES[i], LINES[j]) for j in range(n)] for i in range(n)]
# N[i][j] = 1 iff the root inner product is even (orthogonal or equal); one bitmask row per line
NR = [sum(1 << j for j in range(n) if IP[i][j] % 2 == 0) for i in range(n)]

def rank2(rows):
    b = []
    for v in rows:
        for x in b:
            v = min(v, v ^ x)
        if v:
            b.append(v)
    return len(b)

def rho(S, T):
    """rank over F2 of N[S,T]"""
    if not S or not T:
        return 0
    tm = sum(1 << t for t in T)
    return rank2([NR[s] & tm for s in S])

# simple roots: positive roots (generic functional) that are not a sum of two positive roots
GEN = (1000, 100, 10, 1, 10007, 1009, 101, 11)  # generic integer functional
def func(r): return sum(a * b for a, b in zip(GEN, r))
POS = [r if func(r) > 0 else tuple(-x for x in r) for r in LINES]
POSSET = set(POS)
SIMPLE = [r for r in POS if not any(tuple(a - b for a, b in zip(r, q)) in POSSET for q in POS)]
assert len(SIMPLE) == 8

def solve_dual(vs):
    """rows of Fraction inverse so that columns give vectors w_l with dot(vs[k], w_l)=delta (vs: 8 vectors)"""
    M = [[Fr(x) for x in row] + [Fr(int(i == j)) for j in range(8)] for i, row in enumerate(vs)]
    for c in range(8):
        p = next(i for i in range(c, 8) if M[i][c] != 0); M[c], M[p] = M[p], M[c]
        pv = M[c][c]; M[c] = [x / pv for x in M[c]]
        for i in range(8):
            if i != c and M[i][c] != 0:
                f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[c])]
    inv = [row[8:] for row in M]   # inverse of the matrix with rows vs
    return [[inv[i][l] for i in range(8)] for l in range(8)]

def scale_int(v):
    import math
    den = 1
    for x in v:
        den = den * x.denominator // math.gcd(den, x.denominator)
    return tuple(int(x * den) for x in v)

# fundamental weights w_i with ip(w_i, alpha_j) = delta (simple roots have doubled norm 8: dot/4)
_cols = solve_dual([tuple(Fr(x) for x in s) for s in SIMPLE])   # dot(s_k, col_l) = delta_kl
WEIGHTS = [scale_int(c) for c in _cols]    # proportional to the fundamental weights (ray directions)
for i, w in enumerate(WEIGHTS):
    assert all((dot(SIMPLE[k], w) == 0) == (k != i) for k in range(8))

# F2 labels: label(l) = (1, c_1 mod 2, ..., c_8 mod 2), c_i = coefficient of l on the simple roots
def coeffs(l):
    # coefficient vector solving sum c_i alpha_i = l, via the dual vectors
    out = []
    for i in range(8):
        num = dot(l, _cols[i]); out.append(num)
    return out
LABEL = []
for l in LINES:
    c = coeffs(l)
    assert all(x.denominator == 1 for x in c)
    bits = 1
    for i, x in enumerate(c):
        bits |= (int(x) & 1) << (i + 1)
    LABEL.append(bits)

# the form on F2^9 whose Gram matrix on labels is N: <(a,v),(b,w)> = ab + v^T C w, C the Cartan matrix mod 2
CART = [[ip(SIMPLE[i], SIMPLE[j]) % 2 for j in range(8)] for i in range(8)]
def form(x, y):
    a, b = x & 1, y & 1
    v, w = x >> 1, y >> 1
    s = a & b
    for i in range(8):
        if (v >> i) & 1:
            for j in range(8):
                if (w >> j) & 1:
                    s ^= CART[i][j]
    return s
