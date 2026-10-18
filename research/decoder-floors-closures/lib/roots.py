"""Root-system line sets and exact F2 / clique helpers (standard library only).
Lines are given by integer vectors: E8 with doubled coordinates (so the inner product is 4x the usual one: roots have norm 8), D_n with norm 2.
Only zero patterns of the Gram matrix are used by the F2 / frame checks; the decoder checks (frame120, Lemma OC) use exact Fractions with the
proper scale (the E8 helpers below return the 'real' scaling through `real_dot`)."""
import itertools
from fractions import Fraction as Fr

def dot(a, b): return sum(x * y for x, y in zip(a, b))

def e8_roots2():
    """E8 roots with coordinates doubled: +-2e_i +-2e_j and (+-1)^8 with an even number of minus signs (240 vectors)."""
    R = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (2, -2):
            for sj in (2, -2):
                r = [0] * 8; r[i] = si; r[j] = sj; R.append(tuple(r))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0: R.append(tuple(s))
    return R

def dn_roots(n):
    R = []
    for i, j in itertools.combinations(range(n), 2):
        for si in (1, -1):
            for sj in (1, -1):
                r = [0] * n; r[i] = si; r[j] = sj; R.append(tuple(r))
    return R

def lines(R):
    """one representative per +-pair, in first-occurrence order"""
    seen = set(); L = []
    for r in R:
        if tuple(-x for x in r) in seen: continue
        seen.add(r); L.append(r)
    return L

def orth_sub(L, vs): return [r for r in L if all(dot(r, x) == 0 for x in vs)]

E8 = lines(e8_roots2())                       # 120 lines, doubled coordinates
_r0 = E8[0]; _r1 = next(r for r in E8 if dot(r, _r0) in (4, -4))
E7 = orth_sub(E8, [_r0])                      # 63 lines
E6 = orth_sub(E8, [_r0, _r1])                 # 36 lines
D4 = lines(dn_roots(4)); D5 = lines(dn_roots(5)); D6 = lines(dn_roots(6))
UNITS = {'D4': (D4, 4), 'D5': (D5, 5), 'D6': (D6, 6), 'E6': (E6, 6), 'E7': (E7, 7), 'E8': (E8, 8)}

def gram(L): return [[dot(a, b) for b in L] for a in L]

def b0rows(L):
    """dense pairing B = J + Abar as row bitmasks: B_ts = 1 iff t = s or the lines t, s are orthogonal"""
    G = gram(L); v = len(L)
    return [sum(1 << s for s in range(v) if s == t or G[t][s] == 0) for t in range(v)]

def rank_f2(rows):
    basis = []
    for r in rows:
        x = r
        for b in basis: x = min(x, x ^ b)
        if x: basis.append(x)
    return len(basis)

def blk(Brows, R, A):
    """rank over F2 of the submatrix B[R, A]"""
    return rank_f2([sum(1 << i for i, s in enumerate(A) if Brows[t] >> s & 1) for t in R])

def colspace_basis(rows):
    """reduced echelon basis (bitmasks over the column index) of the span of the given rows"""
    basis = []; piv = []
    for r in rows:
        x = r
        for b, p in zip(basis, piv):
            if x >> p & 1: x ^= b
        if x:
            p = x.bit_length() - 1
            for i in range(len(basis)):
                if basis[i] >> p & 1: basis[i] ^= x
            basis.append(x); piv.append(p)
    return basis

def span_vectors(basis):
    """all nonzero vectors of the F2 span as (coefficient mask, vector) pairs"""
    h = len(basis); out = []
    for co in range(1, 1 << h):
        w = 0
        for i in range(h):
            if co >> i & 1: w ^= basis[i]
        out.append((co, w))
    return out

def orth_graph(L):
    G = gram(L); v = len(L)
    return [sum(1 << s for s in range(v) if s != t and G[t][s] == 0) for t in range(v)]

def maximal_cliques(adj):
    """Bron-Kerbosch with pivoting on bitmask adjacency; yields clique bitmasks"""
    def bk(R, P, X):
        if not P and not X:
            yield R; return
        # pivot: vertex of P|X maximising |P & N(u)|
        best = -1; piv = 0; PX = P | X; m = PX
        while m:
            low = m & -m; i = low.bit_length() - 1; m ^= low
            c = bin(P & adj[i]).count('1')
            if c > best: best = c; piv = i
        cand = P & ~adj[piv]
        while cand:
            low = cand & -cand; i = low.bit_length() - 1; cand ^= low
            yield from bk(R | low, P & adj[i], X & adj[i])
            P &= ~low; X |= low
    yield from bk(0, (1 << len(adj)) - 1, 0)

def popcount(x): return bin(x).count('1')
def bits(x):
    out = []
    while x:
        low = x & -x; out.append(low.bit_length() - 1); x ^= low
    return out

# Fraction linear algebra
def rank_q(rows):
    M = [[Fr(x) for x in r] for r in rows]; r = 0
    if not M: return 0
    for c in range(len(M[0])):
        piv = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; pv = M[r][c]; M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        r += 1
    return r

def nullspace_q(rows, ncols):
    """basis of {x : rows . x = 0} over Q"""
    M = [[Fr(x) for x in r] for r in rows]; pivs = []; r = 0
    for c in range(ncols):
        piv = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; pv = M[r][c]; M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        pivs.append(c); r += 1
    free = [c for c in range(ncols) if c not in pivs]; out = []
    for f in free:
        x = [Fr(0)] * ncols; x[f] = Fr(1)
        for i, c in enumerate(pivs): x[c] = -M[i][f]
        out.append(x)
    return out
