"""Compatible-direction cliques in the GL_{2m}(F_q) flag model (lower Borel B, Bruhat-transposition cost).

At m = 2 a 2-step session geodesic y -> x -> zy has x in the middle, so two cost-1 neighbours u, w of x are
compatible iff delta(u,w) = z (z = (1 3)(2 4), the interchange H <-> D). In the abelian shear model the largest
pairwise-compatible set is m = 2. This script computes it exactly in the full flag model.
Usage: python3 flag_model_cliques.py q      (q = 2 or 3; standard library only)
"""
import itertools, sys


def max_clique(n_nodes, adj):
    """Bron-Kerbosch with pivoting; adj: list of neighbour sets. Returns one maximum clique."""
    best = []

    def bk(r, p, x):
        nonlocal best
        if not p and not x:
            if len(r) > len(best):
                best = list(r)
            return
        if len(r) + len(p) <= len(best):
            return
        u = max(p | x, key=lambda v: len(adj[v] & p))
        for v in list(p - adj[u]):
            bk(r + [v], p & adj[v], x & adj[v])
            p = p - {v}
            x = x | {v}
    bk([], set(range(n_nodes)), set())
    return best

q = int(sys.argv[1]); n = 4

def rank(M):
    M = [list(r) for r in M]; r = 0; rows = len(M); cols = len(M[0]) if rows else 0
    for c in range(cols):
        p = next((i for i in range(r, rows) if M[i][c] % q), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; inv = pow(M[r][c], q - 2, q)
        M[r] = [(v * inv) % q for v in M[r]]
        for i in range(rows):
            if i != r and M[i][c] % q:
                f = M[i][c]; M[i] = [(a - f * b) % q for a, b in zip(M[i], M[r])]
        r += 1
    return r

def mat_inv(M):
    A = [list(r) + [int(i == j) for j in range(n)] for i, r in enumerate(M)]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c] % q)
        A[c], A[p] = A[p], A[c]; inv = pow(A[c][c], q - 2, q)
        A[c] = [(v * inv) % q for v in A[c]]
        for i in range(n):
            if i != c and A[i][c] % q:
                f = A[i][c]; A[i] = [(a - f * b) % q for a, b in zip(A[i], A[c])]
    return [r[n:] for r in A]

def mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(n)) % q for j in range(n)] for i in range(n)]

def weyl(h):
    """Permutation w with h in B w B, B lower triangular: invariants rank h[:i, j:]."""
    r = lambda i, j: rank([row[j:] for row in h[:i]]) if i > 0 and j < n else 0
    w = {}
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            d = r(i, j - 1) - r(i - 1, j - 1) - r(i, j) + r(i - 1, j)
            if d == 1: w[i - 1] = j - 1
    return tuple(w[i] for i in range(n))

def canon(g):
    """Canonical form of the coset B g: the flag span(g_1) < span(g_1,g_2) < ... as reduced row echelon prefixes."""
    key = []
    for k in range(1, n + 1):
        M = [list(r) for r in g[:k]]
        # RREF
        r = 0
        for c in range(n):
            p = next((i for i in range(r, k) if M[i][c] % q), None)
            if p is None: continue
            M[r], M[p] = M[p], M[r]; inv = pow(M[r][c], q - 2, q)
            M[r] = [(v * inv) % q for v in M[r]]
            for i in range(k):
                if i != r and M[i][c] % q:
                    f = M[i][c]; M[i] = [(a - f * b) % q for a, b in zip(M[i], M[r])]
            r += 1
        key.append(tuple(map(tuple, M)))
    return tuple(key)

# Hecke transposition cost on S_4 (lower Borel has the same simple reflections and lengths).
def length(w): return sum(1 for i in range(n) for j in range(i + 1, n) if w[i] > w[j])
def compose(a, b): return tuple(a[b[i]] for i in range(n))  # (a*b)(i) = a(b(i))
simple = [tuple(list(range(i)) + [i + 1, i] + list(range(i + 2, n))) for i in range(n - 1)]
def times_s(x, s):
    xs = compose(x, s)
    return {xs} if length(xs) > length(x) else {xs, x}
def reduced_word(w):
    word = []; w = tuple(w)
    while length(w) > 0:
        for i, s in enumerate(simple):
            ws = compose(w, s)
            if length(ws) < length(w): word.append(i); w = ws; break
    return word[::-1]
transp = []
for i, j in itertools.combinations(range(n), 2):
    t = list(range(n)); t[i], t[j] = j, i; transp.append(tuple(t))
def times_cell(X, t):
    cur = set(X)
    for i in reduced_word(t):
        nxt = set()
        for x in cur: nxt |= times_s(x, simple[i])
        cur = nxt
    return cur
ident = tuple(range(n)); cost = {ident: 0}; frontier = {ident}; k = 0
while len(cost) < 24:
    k += 1; new = set()
    for x in frontier:
        for t in transp:
            new |= times_cell({x}, t)
    frontier = {w for w in new if w not in cost}
    for w in frontier: cost[w] = k
z = (2, 3, 0, 1)
print("q =", q, " c(z) =", cost[z], " cost-1 cells:", sorted(w for w in cost if cost[w] == 1) == sorted(transp))

# Enumerate flags as cosets B g; neighbours of the base flag x = B.
flags = {}
gens = []
for i in range(n):
    for j in range(n):
        if i != j:
            e = [[int(a == b) for b in range(n)] for a in range(n)]; e[i][j] = 1; gens.append(e)
d = [[int(a == b) for b in range(n)] for a in range(n)]; d[0][0] = 2 % q or 1; gens.append(d)
stack = [[[int(a == b) for b in range(n)] for a in range(n)]]
while stack:
    g0 = stack.pop()
    for s in gens:
        g = mul(g0, s); key = canon(g)
        if key not in flags: flags[key] = g; stack.append(g)
for rows in []:
    g = [list(r) for r in rows]
    if rank(g) < n: continue
    key = canon(g)
    if key not in flags: flags[key] = g
print("flags:", len(flags))
base = [[int(i == j) for j in range(n)] for i in range(n)]
nbrs = [g for g in flags.values() if cost[weyl(mul(g, mat_inv(base)))] == 1]
print("cost-1 neighbours of the base flag:", len(nbrs))
adj = [set() for _ in nbrs]
inv = [mat_inv(g) for g in nbrs]
n_edges = 0
for a in range(len(nbrs)):
    for b in range(a + 1, len(nbrs)):
        if weyl(mul(nbrs[b], inv[a])) == z or weyl(mul(nbrs[a], inv[b])) == z:
            adj[a].add(b)
            adj[b].add(a)
            n_edges += 1
cl = max_clique(len(nbrs), adj)
print("compatible pairs:", n_edges, " max pairwise-compatible set:", len(cl), " (abelian model: 2)")
