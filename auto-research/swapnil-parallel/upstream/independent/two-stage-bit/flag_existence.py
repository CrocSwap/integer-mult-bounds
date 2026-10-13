"""Mod-p evaluation at one random point of the flag-basis family, at h = 46, 47 (m = h^2).
A nonzero value mod p at an integer point proves the corresponding polynomial is not identically zero.
Checks: (1) aux/centre corner diagonal factors, every line; corner strictly-upper zero, sampled lines;
(2) inner-lemma corner A[0,h-1] for both data rank-(h-1) classes, every line;
(3) data entrance corner factors det1 (rows of S) and det2 (columns of S^-1), sampled pairs."""
import sys, random
from itertools import combinations
p = (1 << 61)-1
h = int(sys.argv[1]); rng = random.Random(int(sys.argv[2])); m = h*h; CR = 10**6
iv = lambda x: pow(x % p, p-2, p)
nz = lambda: rng.choice([-1, 1])*rng.randint(1, CR)
def inv(A):
    n = len(A); M = [[x % p for x in r]+[int(i == j) for j in range(n)] for i, r in enumerate(A)]
    for c in range(n):
        k = next(i for i in range(c, n) if M[i][c]); M[c], M[k] = M[k], M[c]
        f = iv(M[c][c]); M[c] = [x*f % p for x in M[c]]
        for i in range(n):
            if i != c and M[i][c]: g = M[i][c]; M[i] = [(a-g*b) % p for a, b in zip(M[i], M[c])]
    return [r[n:] for r in M]
def det(A):
    M = [[x % p for x in r] for r in A]; n = len(M); d = 1
    for c in range(n):
        k = next((i for i in range(c, n) if M[i][c]), None)
        if k is None: return 0
        if k != c: M[c], M[k] = M[k], M[c]; d = -d
        d = d*M[c][c] % p; f = iv(M[c][c])
        for i in range(c+1, n):
            if M[i][c]: g = M[i][c]*f % p; M[i] = [(a-g*b) % p for a, b in zip(M[i], M[c])]
    return d % p
mm = lambda A, B: [[sum(a*b for a, b in zip(r, c)) % p for c in zip(*B)] for r in A]
T = lambda A: [list(r) for r in zip(*A)]
mv = lambda A, x: [sum(a*b for a, b in zip(r, x)) % p for r in A]
R = [[[nz() if i <= b and j <= b else 0 for j in range(h)] for i in range(h)] for b in range(h)]; R[h-1][h-1][h-1] = 0
C = []
for b in range(h):
    Cb = [[nz() if i >= b and j >= b else 0 for j in range(h)] for i in range(h)]
    if b < h-1: Cb[b][b] = 0
    for bb in range(b+1, h):
        Cb[b][bb] = 0
        s = sum(R[bb][i][j]*Cb[i][j] for i in range(b, bb+1) for j in range(b, bb+1)) % p
        Cb[b][bb] = -s*iv(R[bb][b][bb]) % p
    C.append(Cb)
for i in range(h):                     # trace conditions (all i, j), mod p
    for j in range(h): assert sum(R[i][x][y]*C[j][x][y] for x in range(h) for y in range(h)) % p == 0
U = [[rng.randint(-CR, CR) for _ in range(h)] for _ in range(h)]; V = [[rng.randint(-CR, CR) for _ in range(h)] for _ in range(h)]
Ui, Vi = inv(U), inv(V)
trip = list(combinations(range(h), 3)); v = len(trip)
inv9, inv2 = iv(9), iv(2)
def tg(t):                             # t = indicator, g = G t / (t^T G t) with G = I - J/9, t^T G t = 2
    tv = [int(i in t) for i in range(h)]; g = [(x - 3*inv9) * inv2 % p for x in tv]; return tv, g
UT, VT, UiT, ViT = T(U), T(V), T(Ui), T(Vi)
bad = 0
for t in trip:
    tv, g = tg(t)
    a, b = mv(VT, tv), mv(Vi, g)       # I(x)P: x_beta = R_beta a, y_beta = C_beta b
    c, d = mv(UT, tv), mv(Ui, g)       # P(x)I: R_beta^T c, C_beta^T d
    for be in range(h):
        f1 = sum(R[be][be][j]*a[j] for j in range(h)) % p; f2 = sum(C[be][be][j]*b[j] for j in range(h)) % p
        f3 = sum(R[be][i][be]*c[i] for i in range(h)) % p; f4 = sum(C[be][i][be]*d[i] for i in range(h)) % p
        bad += not (f1 and f2 and f3 and f4)
    # inner lemma corners: data s1 uses A = U^T Q U^-T (line of the Q factor), exit A' = V^T Q V^-T
    bad += not (c[0]*d[h-1] % p and a[0]*mv(Vi, g)[h-1] % p)
print('h=%d v=%d: lines with a zero diagonal or zero inner corner: %d' % (h, v, bad))
# explicit corners for sampled lines (lower-triangular check), both orientations
for t in rng.sample(trip, 3):
    tv, g = tg(t); a, b, c, d = mv(VT, tv), mv(Vi, g), mv(UT, tv), mv(Ui, g)
    X1 = [mv(R[be], a) for be in range(h)]; Y1 = [mv(C[be], b) for be in range(h)]
    X2 = [mv(T(R[be]), c) for be in range(h)]; Y2 = [mv(T(C[be]), d) for be in range(h)]
    up = sum(1 for i in range(h) for j in range(i+1, h) if sum(x*y for x, y in zip(X1[i], Y1[j])) % p or sum(x*y for x, y in zip(X2[i], Y2[j])) % p)
    print('  line %s: nonzero strictly-upper corner entries (both orientations): %d' % (t, up))
# data entrance factors
vecM = lambda M: [M[x][y] % p for x in range(h) for y in range(h)]
lam = [vecM(mm(mm(U, R[be]), VT)) for be in range(h)]
mu = [vecM(mm(mm(UiT, C[be]), Vi)) for be in range(h)]
dot = lambda x, y: sum(a*b for a, b in zip(x, y)) % p
assert all(dot(l, u) == 0 for l in lam for u in mu)
def proj_out(vs, basis):                # random combos of vs projected to annihilate 'basis' vectors
    Gr = inv([[dot(x, y) for y in basis] for x in basis]); out = []
    for _ in range(h-1):
        f = [rng.randint(-CR, CR) for _ in range(m)]; cf = mv(Gr, [dot(f, y) for y in basis])
        out.append([(fi - sum(cj*y[k] for cj, y in zip(cf, basis))) % p for k, fi in enumerate(f)])
    return out
annmu = proj_out(None, mu)              # functionals with f . mu_l = 0
kerlam = proj_out(None, lam)            # vectors with lam_beta . w = 0
for _ in range(3):
    t1, t2 = rng.choice(trip), rng.choice(trip); tv1, g1 = tg(t1); tv2, g2 = tg(t2)
    i0 = next(i for i in range(h) if tv1[i]); j0 = next(i for i in range(h) if g1[i])
    E = lambda x, y: [x[i]*y[j] % p for i in range(h) for j in range(h)]
    e = lambda k: [int(i == k) for i in range(h)]
    Imb = [E(tv1, e(j)) for j in range(h)]+[E(e(i), tv2) for i in range(h) if i != i0]
    Rsp = [E(g1, e(j)) for j in range(h)]+[E(e(i), g2) for i in range(h) if i != j0]
    d1 = det([[dot(f, x) for x in Imb] for f in lam+annmu])
    d2 = det([[dot(f, x) for x in kerlam+mu] for f in Rsp])
    print('  pair %s %s: det1 %s, det2 %s' % (t1, t2, 'nonzero' if d1 else 'ZERO', 'nonzero' if d2 else 'ZERO'))
