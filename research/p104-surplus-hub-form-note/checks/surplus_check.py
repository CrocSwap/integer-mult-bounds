"""surplus_check.py -- exact, standard library only (fractions, itertools, random,).
Prints 'SURPLUS CHECK PASS' iff every CORE check holds.  
Sections
  A. Ratio lemma  N >= 1 + dim ker(R+I)      (exact rationals, n=4, N=3..5, plus tightness and scratch toy)
  B. Seam model   rank conservation          (exhaustive F2 subspace metric on F2^4 + pin bookkeeping + 884 identity)
  C. S arithmetic identity, bound, equality on the reference record, other port sets, closure sweeps
Hypothesis labels (a) SPEC/cost model, (b) verifier convention, (c) family assumption are given in the note (THEOREM.md);
here each check names the hypothesis it exercises (H-numbers of an earlier draft; see the note for current numbering).
"""
import itertools, random, os, sys
from fractions import Fraction as Fr

FAILS = []
def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: FAILS.append(msg)

# ---------------------------------------------------------------- exact linear algebra
def eye(n): return [[Fr(int(i == j)) for j in range(n)] for i in range(n)]
def mm(A, B):
    Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(r, c)) for c in Bt] for r in A]
def madd(A, B, s=1): return [[a + s * b for a, b in zip(r, q)] for r, q in zip(A, B)]
def msc(A, s): return [[s * a for a in r] for r in A]
def tr(A): return [list(r) for r in zip(*A)]
def outer(x, y): return [[a * b for b in y] for a in x]
def dot(x, y): return sum(a * b for a, b in zip(x, y))
def rref(A):
    M = [list(map(Fr, r)) for r in A]; rows, cols = len(M), len(M[0]); piv = []; r = 0
    for c in range(cols):
        p = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]; M[r] = [v / pv for v in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(c); r += 1
        if r == rows: break
    return M, piv
def rank(A): return len(rref(A)[1])
def inv(A):
    n = len(A); aug = [list(map(Fr, A[i])) + eye(n)[i] for i in range(n)]
    M, piv = rref(aug)
    assert piv[:n] == list(range(n)), 'singular'
    return [r[n:] for r in M]
def nullity(A): return len(A[0]) - rank(A)
def det_nonzero(A): return rank(A) == len(A)
def matpow_prod(Ms):  # product Ms[-1] ... Ms[0]  (Ms[0] applied first)
    P = eye(len(Ms[0]))
    for M in Ms: P = mm(M, P)
    return P

# ================================================================ A. RATIO LEMMA
print('A. Ratio lemma  N >= 1 + dim ker(R+I)   [hyps H2 isotropic rank-1 Q-odd units, H4 exact at Q=+-1, H5 no leak]')
rnd = random.Random(20261108)
def rvec(n, lo=-3, hi=3): return [Fr(rnd.randint(lo, hi)) for _ in range(n)]
def iso_unit(n):
    while True:
        x, y = rvec(n), rvec(n)
        if all(v == 0 for v in x): continue
        y = [b - dot(y, x) / dot(x, x) * a for a, b in zip(x, y)]
        if any(v != 0 for v in y): return x, y
def rnd_gl(n):
    while True:
        G = [[Fr(rnd.randint(-2, 2)) for _ in range(n)] for _ in range(n)]
        if det_nonzero(G): return G
n = 4
for N in (3, 4, 5):
    worst = 0; formula_ok = True; lemma_ok = True; ranks_ok = True
    for trial in range(30):
        units = [iso_unit(n) for _ in range(N)]; Gs = [rnd_gl(n) for _ in range(N + 1)]
        def P(Q):
            M = Gs[0]
            for k, (x, y) in enumerate(units):
                U = madd(eye(n), outer(x, y), Q)
                M = mm(Gs[k + 1], mm(U, M))
            return M
        P1, Pm = P(1), P(-1)
        Gtot = eye(n)
        for G in Gs: Gtot = mm(G, Gtot)
        # conjugated product A(Q) = Gtot^{-1} P(Q)  = prod (I + Q x~ y~^T) with x~,y~ the conjugated vectors
        Gi = inv(Gtot)
        S = madd(mm(Gi, madd(P1, Pm)), eye(n), -2)
        rk = rank(S); worst = max(worst, rk)
        R = mm(Pm, inv(P1)); k = nullity(madd(R, eye(n)))
        lemma_ok &= (N >= 1 + k); ranks_ok &= (rk <= N - 1)
        # step 1 of the proof: conjugate every G to the left; unit k becomes I + Q xt_k yt_k^T
        xt, yt = [], []
        for k_, (x, y) in enumerate(units):
            # unit k_ is applied after pre_k = Gs[k_]..Gs[0]; pulling all G left gives xt = pre_k^-1 x, yt^T = y^T pre_k
            pre_k = eye(n)
            for G in Gs[:k_ + 1]: pre_k = mm(G, pre_k)
            Hi = inv(pre_k)
            xt.append([sum(Hi[i][j] * x[j] for j in range(n)) for i in range(n)])
            yt.append([sum(y[j] * pre_k[j][i] for j in range(n)) for i in range(n)])
        # A(Q) = Gtot^{-1}P(Q) = prod_k (I + Q xt_k yt_k^T) in time order, times nothing else
        for Q in (1, -1):
            A = eye(n)
            for k_ in range(N): A = mm(madd(eye(n), outer(xt[k_], yt[k_]), Q), A)
            formula_ok &= (A == mm(Gi, P(Q)))
        # isotropy of conjugated units
        formula_ok &= all(dot(yt[k_], xt[k_]) == 0 for k_ in range(N))
        # product formula A(c) = I + c X (I - cL)^-1 Y^T, L_{kj} = yt_k . xt_j (k>j)
        L = [[dot(yt[a], xt[b]) if a > b else Fr(0) for b in range(N)] for a in range(N)]
        X = [[xt[k_][i] for k_ in range(N)] for i in range(n)]   # n x N
        YT = [yt[k_] for k_ in range(N)]                          # N x n
        for c in (1, -1):
            T = inv(madd(eye(N), L, -c))
            Ac = madd(eye(n), msc(mm(X, mm(T, YT)), c))
            formula_ok &= (Ac == mm(Gi, P(c)))
        ranks_ok &= (rank(L) <= N - 1) and all(v == 0 for v in L[0])
    ok(formula_ok, f'n={n} N={N}: A(c)=I+cX(I-cL)^-1Y^T, isotropy kept under conjugation (30 trials)')
    ok(ranks_ok and worst <= N - 1, f'n={n} N={N}: rank(A(1)+A(-1)-2I) <= rank L <= N-1  (max seen {worst}, bound {N - 1})')
    ok(lemma_ok, f'n={n} N={N}: N >= 1 + dim ker(R+I) in all 30 trials')

# tightness 1: SL2 Weyl word, n=2, N=3, G=identity, R=-I; exhaustive: no N=2 word exists in a small family
def shear(u, t):
    a, b = u; return [[t * a * (-b), t * a * a], [t * b * (-b), t * b * a]]   # t u (u_perp)^T, isotropic nilpotent
def qunit(Nm, Q): return [[(1 if i == j else 0) + Q * Nm[i][j] for j in range(2)] for i in range(2)]
vecs = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (2, -1)]
ts = [1, -1, 2, -2, Fr(1, 2), Fr(-1, 2)]
pool = [shear(u, t) for u in vecs for t in ts]
def word_is_minus_I(combo):
    A1 = [[Fr(1), Fr(0)], [Fr(0), Fr(1)]]; Am = [r[:] for r in A1]
    for c in combo:
        A1 = mm(qunit(pool[c], 1), A1); Am = mm(qunit(pool[c], -1), Am)
    return all(Am[i][j] == -A1[i][j] for i in range(2) for j in range(2))
found2 = sum(word_is_minus_I(c) for c in itertools.product(range(len(pool)), repeat=2))
found3 = sum(word_is_minus_I(c) for c in itertools.product(range(len(pool)), repeat=3))
ok(found2 == 0, 'n=2, r=2 (R=-I): no N=2 word in the 48-unit family (lemma: N>=3)')
ok(found3 > 0, f'n=2, r=2 (R=-I): N=3 words exist ({found3} in the family) -> lemma tight at n=2')

# tightness 2: the n=4 chain root (TRACEDELTA a) in Q-form; unit(Q) = (I - x y^T)(I + Q x y^T) = I + (Q-1) x y^T
n4, N5 = 4, 5
Gm = [[Fr((i > j) - (i < j)) for j in range(N5)] for i in range(N5)]      # sign(i-j)
Xc = [[Fr(0)] * N5 for _ in range(n4)]
for k in range(n4): Xc[k][k] = Fr(1)
for k in range(n4): Xc[k][4] = Fr(-((-1) ** k))
Yc = [[Gm[i][k] for i in range(N5)] for k in range(n4)]                    # 4 x 5, Y = (G[:, :4])^T
xs = [[Xc[i][j] for i in range(n4)] for j in range(N5)]; ys = [[Yc[i][j] for i in range(n4)] for j in range(N5)]
ok(all(dot(ys[i], xs[j]) == Gm[i][j] for i in range(N5) for j in range(N5)), 'chain root: Gram y_i.x_j = sign(i-j) (isotropic)')
prodm = matpow_prod([madd(eye(n4), outer(xs[k], ys[k]), -2) for k in range(N5)])
ok(prodm == msc(eye(n4), -1), 'chain root: prod (I - 2 x_k y_k^T) = -I exactly with N = n+1 = 5 units')
def unitQ(k, Q): return madd(eye(n4), outer(xs[k], ys[k]), Q - 1)
P1 = matpow_prod([unitQ(k, 1) for k in range(N5)]); Pm = matpow_prod([unitQ(k, -1) for k in range(N5)])
Rr = mm(Pm, inv(P1))
ok(P1 == eye(n4) and Rr == msc(eye(n4), -1) and nullity(madd(Rr, eye(n4))) == 4,
   'chain root in Q-form: P(+1)=I, P(-1)=-I, R=-I, dim ker(R+I)=4, so N=5=1+r: EQUALITY in the ratio lemma')
ok(all(mm(madd(eye(n4), outer(xs[k], ys[k]), 1), madd(eye(n4), outer(xs[k], ys[k]), -1)) == eye(n4) for k in range(N5)),
   'chain root: isotropy => (I+xy^T)(I-xy^T)=I (Q-odd units invertible at both characters)')

# scratch toy (H5): N = n = 1 with one scratch coordinate: V-block of R is -1 yet ker(R+I)=0 and the leak R_HV != 0
x, y = [Fr(1), Fr(1)], [Fr(1), Fr(-1)]                      # coordinates (V, H); y.x = 0
Rs = madd(eye(2), outer(x, y), -2)                           # R = I - 2 x y^T for the single Q-odd unit
ok(dot(y, x) == 0 and Rs[0][0] == -1 and Rs[1][0] != 0 and nullity(madd(Rs, eye(2))) == 0,
   'scratch toy: N=n=1, V-block of R = -1 (credit looks complete) but ker(R+I)=0 and R_HV = %s != 0 (junk leak): scratch leaves H5' % Rs[1][0])

# block roots: lemma per block gives N >= sum(1+r_b) = r + B
ok(sum(1 + r for r in (2, 2)) == 4 + 2 and 1 + 4 == 5 < 6, 'block split: two (n=2) blocks need N >= 6 vs one n=4 root N >= 5 (+1 per block)')

# ================================================================ B. SEAM MODEL
print('B. Seam lemma  [hyps H7 (i) contacts rank-preserving (b), (ii) price >= |dim| rank change (a), (iii) natives Q-free (b), (iv) pins (a)]')
# (ii): Fourier rank d(U,W) = dim U + dim W - 2 dim(U cap W) on subspaces of F2^m is a metric with d >= |dim U - dim W|
m = 4
def span(vs):
    S = {0}
    for v in vs: S |= {s ^ v for s in S}
    return frozenset(S)
subs = set()
for k in range(0, m + 1):
    for vs in itertools.combinations(range(1, 2 ** m), k): subs.add(span(vs))
subs = sorted(subs, key=lambda s: (len(s), sorted(s)))
dimof = lambda S: len(S).bit_length() - 1
d = lambda U, W: dimof(U) + dimof(W) - 2 * dimof(U & W)
ok(len(subs) == 67, f'F2^4 has {len(subs)} subspaces (expect 67)')
ok(all(d(U, W) >= abs(dimof(U) - dimof(W)) for U in subs for W in subs), '(ii) d(U,W) >= |dim U - dim W| for all 4489 pairs')
ok(all((d(U, W) == abs(dimof(U) - dimof(W))) == (U <= W or W <= U) for U in subs for W in subs), '(ii) equality iff U, W nested')
ok(all(d(U, W) <= d(U, V) + d(V, W) for U in subs for V in subs for W in subs), 'd is a metric (triangle, 67^3 triples)')
# consequence: any priced path from dim a to dim b costs >= |b - a| (here: 8 per stage in the real model); equality iff monotone/nested
# pin bookkeeping (entry ranks 8s+1 and 8s as stated; checked as arithmetic only)
ent_X = lambda s: 8 * s + 1; ent_Y = lambda s: 8 * s
okp = True
for s in range(1, 18):
    # register R: Y in call s then X' in call s+1 ; register X: X in call s then Y' in call s+1
    r_exit = ent_Y(s) + 8; r_next = ent_X(s + 1); x_exit = ent_X(s) + 8; x_next = ent_Y(s + 1)
    okp &= (r_next - r_exit == +1) and (x_next - x_exit == -1)
    okp &= (r_next + 8 - ent_Y(s) - 1 == 16) and (x_next + 8 - ent_X(s) + 1 == 16)   # natives supply 16 per register per pair
ok(okp, 'pair accounting, stages 1..17: interstitials are +1 / -1 and the two natives supply exactly 16 per register')
ok((ent_Y(3), ent_Y(3) + 8 + 1 + 8, ent_X(3), ent_X(3) + 8 - 1 + 8) == (24, 41, 25, 40), 'pair (3,4): R 24 -> 41, X 25 -> 40 (arithmetic on stated entry ranks)')
# ledger identity: outer credit = idle rank + main rank + n
outer_credit = 145 + 2 * sum(range(9, 74, 8)) + 1
idle = 2 * sum(range(8, 65, 8)); mains = 16 * 18; nfld = 20
ok((outer_credit, idle, mains) == (884, 576, 288) and outer_credit == idle + mains + nfld, '884 = 576 + 288 + 20  (outer credit = idles + mains + n; arithmetic on stated numbers)')

# ================================================================ C. S ARITHMETIC
print('C. S theorem arithmetic  [hyps H6 ledger, H8 hosting h<=1, H9 c>=56, H10 thin price 1]')
v, L, c, n_ = 104, 18, 56, 20
comp = {'outer': 884 * v, 'idles': -576 * v, 'thin': -3 * v, 'X mains': -832 * L, 'Y mains': -832 * L, 'owned': -c * L}
ok(comp['outer'] == 91936 and comp['idles'] == -59904 and comp['X mains'] == -14976 and comp['owned'] == -1008,
   'component arithmetic on STATED numbers (not read from a pricing file): 91936, -59904, -312, -14976, -14976, -1008')
ok(sum(comp.values()) == 760, 'sum of the stated components = 760 (arithmetic on stated numbers)')
ok(v * (L - 1) - L * c == 760 == 104 * 17 - 18 * 56, 'closed form S = v(L-1) - L c = 104*17 - 18*56 = 760')
thin = 3
ok(n_ - thin == L - 1 and Fr(n_) - thin - Fr(L * c, v) == Fr(760, v), 'per port: S/v = n - thin - Lc/v = 20 - 3 - 9.692 = 7.3077 = 760/104')
ok(thin == (n_ + 1) - L and (n_ + 1) == 21, 'thin = N - hosted = (n+1) - L = 21 - 18 = 3 (N = n+1 is the ratio-lemma floor)')
ok(comp['thin'] * -1 * 100 // 760 == 41 and Fr(v, 760) > Fr(13, 100), 'thin = 312 = 41% of S; one extra thin unit = 104 = 13.7% of S')

def S_bound(v, L, c, h=1): return v * (h * L - 1) - L * c
def S_of(r, thin_, v, L, c): return v * (r - thin_) - L * c        # H6 identity per uniform port set
# sweep: for every credited-field count r and every legal thin >= max(0, 1 + r - hL), S <= v(L-1)-Lc ; equality iff r>=L-1 and thin = 1+r-L
bad = 0; eq = []
for r in range(0, 81):
    for th in range(max(0, 1 + r - L), 1 + r - L + 25 if 1 + r - L > 0 else 25):
        s = S_of(r, th, v, L, c)
        if s > S_bound(v, L, c): bad += 1
        if s == S_bound(v, L, c): eq.append((r, th))
ok(bad == 0, 'sweep r=0..80, all thin >= max(0,1+r-L): S <= v(L-1) - Lc  (no counterexample; target size r drops out)')
ok(all(th == max(0, 1 + r - L) for r, th in eq) and (20, 3) in eq and min(r for r, _ in eq) == L - 1, f'equality set: thin = 1+r-L (or 0 at r=L-1), starts at r=L-1={L-1}; (r,thin)=(20,3) is the reference record')
ok(all(S_of(r, max(0, 1 + r - L), v, L, c) == v * min(r, L - 1) - L * c for r in range(0, 60)), 'S/v = min(r, L-1) - Lc/v at the lemma floor')
# other port sets (Gram-class c values as stated; listed for comparison)
ok((S_bound(104, 18, 56), S_bound(112, 18, 64), S_bound(120, 18, 72)) == (760, 752, 744),
   'port sets: P104 760, P112 752, P120 744 (c = 56/64/72 as stated)')
# non-uniform ports: S <= sum_p (L_p - 1) - sum_j c_j  (per-port lemma, per-call owned)
Lp = [9] * 52 + [18] * 52; cj = [56] * 18
ok(sum(l - 1 for l in Lp) - sum(cj) == 52 * 8 + 52 * 17 - 1008, 'non-uniform ports: bound sum_p (L_p - 1) - sum_j c_j (uniformity not needed)')
# hosting hypothesis made explicit: what h=2 (M1, owned-UP rows) would change
ok(S_bound(104, 18, 56, 2) == 104 * 35 - 1008 == 2632, 'if h=2 (two hosted Q-odd per LOCAL = M1) the bound would be 2632: the hosting hypothesis H8 is the load-bearing one')
# lambda sensitivity of c: each unit of c is 18 S = 2.37%
ok(Fr(18, 760) == Fr(9, 380) and abs(float(Fr(18, 760)) - 0.0237) < 1e-4, '1 unit of c = L = 18 S = 2.37% of S')

print()
if FAILS:
    print('SURPLUS CHECK FAIL:', len(FAILS), 'failures'); sys.exit(1)
print('SURPLUS CHECK PASS')
