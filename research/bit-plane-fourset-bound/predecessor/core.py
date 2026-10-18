"""Core data for the bit plane-port step-1 experiment (expBE). Exact integer/F2/rational arithmetic."""
import gzip, hashlib, json
from fractions import Fraction as Q
from pathlib import Path
HERE = Path(__file__).resolve().parent
WORD = HERE.parents[3] / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
assert hashlib.sha256(WORD.read_bytes()).hexdigest() == 'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'
w = json.load(gzip.open(WORD, 'rt'))
live = [tuple(x) for x in w['lines']]
n = len(live)
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def canon(v): return v if next(x for x in v if x) > 0 else tuple(-x for x in v)
roots = set(live) | {tuple(-x for x in q) for q in live}
grown = True
while grown:
    grown = False
    for q in list(roots):
        for x in list(roots):
            y = tuple(int(xi - Q(2 * dot(x, q), dot(q, q)) * qi) for xi, qi in zip(x, q))
            if y not in roots:
                roots.add(y); grown = True
assert len(roots) == 240
liveset = {canon(q) for q in live}
punct = sorted({canon(r) for r in roots} - liveset)
assert len(punct) == 9
LINES = list(live) + punct          # indices 0..110 live (word order), 111..119 punctured
N120 = 120
G = [[dot(a, b) // 2 for b in LINES] for a in LINES]   # Gram, norm-2 convention: diag 2, else 0/+-1

def rank2(vs):
    piv, r = {}, 0
    for v in vs:
        while v:
            h = v.bit_length() - 1
            if h in piv: v ^= piv[h]
            else: piv[h] = v; r += 1; break
    return r

def rankQ(rows):
    """exact rank of an integer matrix (list of lists) by fraction-free Bareiss-like elimination mod big prime x2 + exact fallback."""
    M = [list(r) for r in rows if any(r)]
    if not M: return 0
    # exact Gaussian elimination over Q with Fractions (small matrices) -- use integer Bareiss
    m, k = len(M), len(M[0])
    r = 0; prev = 1
    for c in range(k):
        p = next((i for i in range(r, m) if M[i][c]), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        for i in range(r + 1, m):
            for j in range(c + 1, k):
                M[i][j] = (M[r][c] * M[i][j] - M[i][c] * M[r][j]) // prev
            M[i][c] = 0
        prev = M[r][c]; r += 1
        if r == m: break
    return r

def span_vectors(ports, E):
    out = []
    for a in ports: out.extend(E[a])
    return out

def pair_rank(R, A, E):
    """rational pairing rank between span_Q(E_t: t in R) and span_Q(E_s: s in A) (Theorem C convention, bit side)."""
    X = span_vectors(R, E); Y = span_vectors(A, E)
    if not X or not Y: return 0
    return rankQ([[dot(x, y) for y in Y] for x in X])

def line_E():
    return {i: [LINES[i]] for i in range(N120)}

# ---- F2 labels: B0 = (1+G) mod 2, rank 9 ----
B0 = [[(1 + G[i][j]) % 2 for j in range(N120)] for i in range(N120)]
def _f2_inv(M):
    k = len(M); A = [row[:] + [int(i == j) for j in range(k)] for i, row in enumerate(M)]
    for c in range(k):
        p = next((i for i in range(c, k) if A[i][c]), None)
        if p is None: return None
        A[c], A[p] = A[p], A[c]
        for i in range(k):
            if i != c and A[i][c]: A[i] = [x ^ y for x, y in zip(A[i], A[c])]
    return [row[k:] for row in A]
def _pick_basis():
    import itertools
    # greedy: indices with independent rows, then check principal submatrix invertible; search small
    rows = [sum(B0[i][j] << j for j in range(N120)) for i in range(N120)]
    for combo in itertools.combinations(range(111, 120), 9):
        sub = [[B0[i][j] for j in combo] for i in combo]
        if _f2_inv(sub) is not None: return list(combo)
    raise RuntimeError
IB = _pick_basis()
QF = _f2_inv([[B0[i][j] for j in IB] for i in IB])     # bilinear form on label space: u_s^T QF u_t = B0[s,t]
U = [[B0[t][j] for j in IB] for t in range(N120)]        # label of line t (9 bits)
for s in range(N120):
    for t in range(N120):
        assert sum(U[s][i] * QF[i][j] * U[t][j] for i in range(9) for j in range(9)) % 2 == B0[s][t]
def codeword(y):
    """reader set (all 120 lines) of functional y in F2^9 (coordinates w.r.t. columns IB)."""
    return frozenset(t for t in range(N120) if sum(U[t][i] * y[i] for i in range(9)) % 2)

# ---- E8/2E8 representation ----
def _det(M):
    M = [[Q(x) for x in r] for r in M]; k = len(M); d = Q(1)
    for c in range(k):
        p = next((i for i in range(c, k) if M[i][c]), None)
        if p is None: return 0
        if p != c: M[c], M[p] = M[p], M[c]; d = -d
        d *= M[c][c]
        for i in range(c + 1, k):
            f = M[i][c] / M[c][c]
            for j in range(c, k): M[i][j] -= f * M[c][j]
    return d
def _zbasis():
    import itertools, random
    rnd = random.Random(1)
    idx = list(range(N120))
    while True:
        cand = rnd.sample(idx, 8)
        if abs(_det([[G[i][j] for j in cand] for i in cand])) == 1: return cand
ZB = _zbasis()
def _coords(v):
    # solve v = sum c_i LINES[ZB[i]] via Gram: c = Gram^-1 (dot(v, basis)/2)
    Gm = [[Q(G[i][j]) for j in ZB] for i in ZB]
    rhs = [Q(dot(v, LINES[i]), 2) for i in ZB]
    k = 8; A = [Gm[i] + [rhs[i]] for i in range(k)]
    for c in range(k):
        p = next(i for i in range(c, k) if A[i][c]); A[c], A[p] = A[p], A[c]
        A[c] = [x / A[c][c] for x in A[c]]
        for i in range(k):
            if i != c and A[i][c]: A[i] = [x - A[i][c] * y for x, y in zip(A[i], A[c])]
    c = [A[i][k] for i in range(k)]
    assert all(x.denominator == 1 for x in c)
    return [int(x) % 2 for x in c]
VEC = [sum(b << i for i, b in enumerate(_coords(LINES[t]))) for t in range(N120)]
assert len(set(VEC)) == 120
GB = [[G[ZB[i]][ZB[j]] % 2 for j in range(8)] for i in range(8)]
def Bf(u, v):
    return sum(((u >> i) & 1) & ((v >> j) & 1) & GB[i][j] for i in range(8) for j in range(8)) % 2
for s in range(N120):
    for t in range(N120):
        assert Bf(VEC[s], VEC[t]) == G[s][t] % 2
VIDX = {v: t for t, v in enumerate(VEC)}
