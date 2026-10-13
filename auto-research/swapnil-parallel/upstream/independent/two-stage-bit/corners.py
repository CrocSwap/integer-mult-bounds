"""Independent corner check for the selected partial-swap projectors of the two-stage bit motif.
Closed forms (G = I - J/9, P_a = G-orthogonal projector on t_a, Q_a = I - P_a):
  aux s1 exit / s2 entrance : I(x)Q_a , Q_a(x)I            rank m-h,     k = h
  data s2 entrance X and Y  : Q_a1 (x) Q_a2                 rank m-2h+1,  k = 2h-1
Part 1 (exact, Fractions): the closed forms equal proj(b)-proj(a) of the label chains.
Part 2 (mod prime, rigorous for invertibility): with ONE random unimodular S0, the k x k corner
(S0^-1 p S0)[L,R] is invertible for EVERY aux a and EVERY data pair (a1,a2). det != 0 mod q
implies det != 0 over Q (all denominators divide 6 and det S0 = 1)."""
import sys, random
from fractions import Fraction as Q
from itertools import combinations

q = 2**61-1

def mat_mul(A, B, mod=None):
    Bt = list(zip(*B))
    if mod: return [[sum(a*b for a, b in zip(r, c)) % mod for c in Bt] for r in A]
    return [[sum(a*b for a, b in zip(r, c)) for c in Bt] for r in A]

def kron(A, B): return [[a*b for a in ra for b in rb] for ra in A for rb in B]

def rank_mod(M, mod):
    M = [r[:] for r in M]; rk = 0; n = len(M[0]) if M else 0
    for c in range(n):
        p = next((i for i in range(rk, len(M)) if M[i][c] % mod), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]; iv = pow(M[rk][c], mod-2, mod)
        M[rk] = [x*iv % mod for x in M[rk]]
        for i in range(len(M)):
            if i != rk and M[i][c] % mod:
                g = M[i][c]; M[i] = [(x-g*y) % mod for x, y in zip(M[i], M[rk])]
        rk += 1
    return rk

def setup(h):
    trip = list(combinations(range(h), 3))
    G = [[Q(int(i == j))-Q(1, 9) for j in range(h)] for i in range(h)]
    P = []
    for t in trip:
        u = [Q(int(i in t)) for i in range(h)]
        Gu = [sum(G[i][j]*u[j] for j in range(h)) for i in range(h)]
        d = sum(a*b for a, b in zip(u, Gu)); assert d == 2
        P.append([[u[i]*Gu[j]/d for j in range(h)] for i in range(h)])
    I = [[Q(int(i == j)) for j in range(h)] for i in range(h)]
    Qc = [[[I[i][j]-p[i][j] for j in range(h)] for i in range(h)] for p in P]
    return trip, G, I, P, Qc

def part1(h, npairs, seed):
    sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'partial-swap'))
    from frames import Space, tens, perp, proj
    trip, G, I, P, Qc = setup(h); v = len(trip); G2 = kron(G, G); m = h*h
    F = Space(I, h); FF = tens(F, F); zero = Space([], m)
    line = [Space([[Q(int(i in t)) for i in range(h)]], h) for t in trip]; lp = [perp(L, G, h) for L in line]
    rng = random.Random(seed)
    sub = lambda b, a: [[x-y for x, y in zip(r1, r2)] for r1, r2 in zip(proj(b, G2), proj(a, G2))]
    for a in rng.sample(range(v), min(v, 6)):
        assert sub(FF, tens(F, line[a])) == kron(I, Qc[a])
        assert sub(tens(lp[a], F), zero) == kron(Qc[a], I)
    for _ in range(npairs):
        a1, a2 = rng.randrange(v), rng.randrange(v); D0 = tens(lp[a1], F); want = kron(Qc[a1], Qc[a2])
        assert sub(D0+tens(line[a1], line[a2]), tens(F, line[a2])) == want     # X entrance
        assert sub(D0, tens(lp[a1], line[a2])) == want                          # Y entrance
    print('h=%d part1: closed forms exact on %d aux and %d data pairs (X and Y)' % (h, min(v, 6), npairs), flush=True)

def part2(h, seed, R=2):
    trip, G, I, P, Qc = setup(h); v = len(trip); m = h*h; rng = random.Random(seed)
    inv6 = pow(6, q-2, q)
    red = lambda x: (x.numerator % q) * pow(x.denominator % q, q-2, q) % q
    Qm = [[[red(x) for x in r] for r in A] for A in Qc]; Im = [[int(i == j) for j in range(h)] for i in range(h)]
    # S0 = Lw Up unimodular; S0^-1 = Up^-1 Lw^-1 computed mod q (exact integer inverse reduces correctly)
    Lw = [[rng.randint(-R, R) if j < i else int(i == j) for j in range(m)] for i in range(m)]
    Up = [[rng.randint(-R, R) if j > i else int(i == j) for j in range(m)] for i in range(m)]
    S = mat_mul(Lw, Up, q)
    def tri_inv(T, lower):
        n = len(T); X = [[0]*n for _ in range(n)]
        for c in range(n):
            X[c][c] = 1
            rows = range(c+1, n) if lower else range(c-1, -1, -1)
            for i in rows:
                js = range(c, i) if lower else range(i+1, c+1)
                X[i][c] = -sum(T[i][j]*X[j][c] for j in js) % q
        return X
    Si = mat_mul(tri_inv(Up, False), tri_inv(Lw, True), q)
    assert mat_mul(S, Si, q) == [[int(i == j) for j in range(m)] for i in range(m)]
    bad = {}
    def corner(p, k):
        top = Si[:k]                                   # rows L of S^-1
        right = [r[m-k:] for r in S]                   # columns R of S
        return rank_mod(mat_mul(mat_mul(top, p, q), right, q), q) == k
    for a in range(v):
        if not corner(kron(Im, Qm[a]), h): bad['aux1'] = bad.get('aux1', 0)+1
        if not corner(kron(Qm[a], Im), h): bad['aux2'] = bad.get('aux2', 0)+1
    # data: corner = Si[L] (Qa1 (x) Qa2) S[:,R]; factor Qa1(x)Qa2 = (Qa1(x)I)(I(x)Qa2) for speed
    A1 = [mat_mul(Si[:2*h-1], kron(Qm[a], Im), q) for a in range(v)]
    B2 = [mat_mul(kron(Im, Qm[a]), [r[m-2*h+1:] for r in S], q) for a in range(v)]
    nd = 0
    for a1 in range(v):
        for a2 in range(v):
            nd += 1
            if rank_mod(mat_mul(A1[a1], B2[a2], q), q) < 2*h-1: bad['data'] = bad.get('data', 0)+1
    print('h=%d m=%d v=%d part2 (one S0, seed %d): aux checked %d, data pairs checked %d, singular corners %s'
          % (h, m, v, seed, 2*v, nd, bad or 0), flush=True)
    return not bad

if __name__ == '__main__':
    for h in map(int, sys.argv[1:]):
        if h <= 8: part1(h, 6, h)
        part2(h, 100+h)
