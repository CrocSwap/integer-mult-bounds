"""Core exact checker. Standard library only. Run:  python3 -I -B check.py [--quick]
Checks the numeric / algebraic certificates of THEOREM.md sections 2-6:
  1  Dieudonne in the rank-one model (product formula, N=n impossible algebraically, N=n+1 sign-Gram root exact over Q, n=2..20)
  2  mask lemma (exact identity M(D) = -prod A_k Delta_k A_k^-1; coordinate masks in the OUTPUT frame; site-frame gap example)
  3  star optimality, exact-precision (50-digit Decimal) uniform dual, N = 2..1199
  4  staircase / majorisation bound (base package): bound = chain = twin, unbalanced worse, staircase lemma, exhaustive sign model
  5  S identity and block roots: all partitions of 18, break-even D_root
Prints PASS_ROOT_CORE at the end if everything holds."""
import sys, math, random, itertools
from fractions import Fraction as Fr
from decimal import Decimal, getcontext
QUICK = "--quick" in sys.argv
fails = []
def ck(c, m):
    if not c: fails.append(m); print("FAIL", m)
    return c
random.seed(1)
# ---------------------------------------------------------------- linear algebra over Q
def I_(n): return [[Fr(int(i == j)) for j in range(n)] for i in range(n)]
def mm(A, B):
    Bt = list(zip(*B)); return [[sum(a * b for a, b in zip(r, c)) for c in Bt] for r in A]
def inv(A):
    n = len(A); M = [r[:] + I_(n)[i] for i, r in enumerate(A)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c] != 0); M[c], M[p] = M[p], M[c]
        pv = M[c][c]; M[c] = [v / pv for v in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]; M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return [r[n:] for r in M]
def sub(A, B): return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]
def add(A, B): return [[a + b for a, b in zip(r, s)] for r, s in zip(A, B)]
def sc(c, A): return [[c * a for a in r] for r in A]
def T_of(x, y):  # I - 2 x y^T
    n = len(x); return [[Fr(int(i == j)) - 2 * x[i] * y[j] for j in range(n)] for i in range(n)]
def word(Ts, n):  # T_{N-1} ... T_0
    P = I_(n)
    for T in Ts: P = mm(T, P)
    return P
def signroot(n):
    """sign-Gram root: x_i=e_i (i<n), y_i=(sgn(i-j))_j, x_n = S^-1(-1,..,-1), y_n=(1,..,1); y_i x_j = sgn(i-j)."""
    s = lambda i, j: 1 if i > j else -1
    xs = [[Fr(int(j == i)) for j in range(n)] for i in range(n)]
    ys = [[Fr(0 if i == j else s(i, j)) for j in range(n)] for i in range(n)] + [[Fr(1)] * n]
    S = [[Fr(0 if i == j else s(i, j)) for j in range(n)] for i in range(n)]
    xn = [sum(a * b for a, b in zip(r, [Fr(-1)] * n)) for r in inv(S)]
    xs.append(xn); return xs, ys

print("1. Dieudonne in the rank-one model")
# 1a product formula  P = I - 2 X K^-1 Y,  K = I + 2L, L = strict lower triangle of G = Y X  (G_ij = y_i x_j)
for (n, N) in ((2, 3), (3, 4), (4, 5), (3, 5), (5, 8)):
    xs = [[Fr(random.randint(-3, 3)) for _ in range(n)] for _ in range(N)]
    ys = []
    for x in xs:   # random y with y x = 0
        y = [Fr(random.randint(-3, 3)) for _ in range(n)]
        k = next(i for i in range(n) if x[i] != 0) if any(x) else 0
        if any(x): y[k] = -sum(y[i] * x[i] for i in range(n) if i != k) / x[k]
        ys.append(y)
    P = word([T_of(xs[k], ys[k]) for k in range(N)], n)
    G = [[sum(ys[i][a] * xs[j][a] for a in range(n)) for j in range(N)] for i in range(N)]
    K = [[Fr(int(i == j)) + (2 * G[i][j] if i > j else 0) for j in range(N)] for i in range(N)]
    X = [[xs[j][a] for j in range(N)] for a in range(n)]; Y = ys
    Q = sub(I_(n), sc(2, mm(mm(X, inv(K)), Y)))
    ck(P == Q, "product formula n=%d N=%d" % (n, N))
print("   product formula P = I - 2 X K^-1 Y verified exactly on random rank-one words")
# 1b N = n impossible: -I forces X K^-1 Y = I; for N = n, X,Y square invertible => K = Y X = G, but diag K = 1, diag G = 0.
# (algebraic, no numerics) -- sanity: the sign-Gram diag of G is 0 and K diag is 1
# 1c N = n+1: exact sign-Gram roots, n = 2..20 even; odd n must fail (det of a product of transvections is 1)
for n in range(2, 21, 2):
    xs, ys = signroot(n)
    ck(all(sum(a * b for a, b in zip(ys[i], xs[i])) == 0 for i in range(n + 1)), "y_k x_k=0 n=%d" % n)
    ck(all(sum(a * b for a, b in zip(ys[i], xs[j])) == (1 if i > j else -1) for i in range(n + 1) for j in range(n + 1) if i != j), "sign Gram n=%d" % n)
    P = word([T_of(xs[k], ys[k]) for k in range(n + 1)], n)
    ck(P == sc(-1, I_(n)), "product = -I at n=%d" % n)
    if n <= 6:   # Z = I + L - U has rank one (Gram law), G_ij G_ji = -1
        G = [[sum(a * b for a, b in zip(ys[i], xs[j])) for j in range(n + 1)] for i in range(n + 1)]
        ck(all(G[i][j] * G[j][i] == -1 for i in range(n + 1) for j in range(n + 1) if i != j), "G_ij G_ji=-1")
print("   sign-Gram root (N=n+1) multiplies to -I exactly over Q for every even n = 2..20 (incl. n=20 of the P104 root)")

print("2. mask lemma: exact identity and the frame gap")
def rand_proj(n, r):
    while True:
        B = [[Fr(random.randint(-3, 3)) for _ in range(n)] for _ in range(n)]
        try: Bi = inv(B)
        except StopIteration: continue
        E = [[Fr(int(i == j and i < r)) for j in range(n)] for i in range(n)]
        return mm(mm(B, E), Bi)
n = 4; N = n + 1
xs, ys = signroot(n); Ts = [T_of(xs[k], ys[k]) for k in range(N)]
A = []   # A_k = T_{N-1} ... T_{k+1}
for k in range(N):
    P = I_(n)
    for j in range(k + 1, N): P = mm(Ts[j], P)
    A.append(P)
Ai = [inv(a) for a in A]
Ek = [[Fr(random.randint(0, 1)) for _ in range(n)] for _ in range(N)]          # coordinate (output-frame) masks
Pk = [mm(mm(Ai[k], [[Ek[k][i] if i == j else Fr(0) for j in range(n)] for i in range(n)]), A[k]) for k in range(N)]  # site-frame masks
def Mof(Dv):
    P = I_(n)
    for k in range(N):
        Dl = add(I_(n), sc(Dv[k] - 1, Pk[k]))
        P = mm(mm(Dl, Ts[k]), P)
    return P
for trial in range(5):
    Dv = [Fr(random.randint(2, 9), random.randint(1, 5)) for _ in range(N)]
    M = Mof(Dv)
    target = [[(-1) * math.prod(Dv[k] ** int(Ek[k][i]) for k in range(N)) if i == j else Fr(0) for j in range(n)] for i in range(n)]
    ck(M == target, "M(D) = -diag(prod D^eps) with output-frame coordinate masks")
    # general identity M(D) = - prod_{k desc} A_k Delta_k A_k^-1
    Pr = I_(n)
    for k in reversed(range(N)):
        Pr = mm(Pr, mm(mm(A[k], add(I_(n), sc(Dv[k] - 1, Pk[k]))), Ai[k]))
    ck(M == sc(-1, Pr), "M(D) = -prod A_k Delta_k A_k^-1")
ndiag = sum(1 for k in range(N) if any(Pk[k][i][j] != 0 for i in range(n) for j in range(n) if i != j))
ncomm = sum(1 for k in range(N) if mm(Pk[k], Ts[k]) != mm(Ts[k], Pk[k]))
ncomm_pairs = sum(1 for a in range(N) for b in range(a) if mm(Pk[a], Pk[b]) != mm(Pk[b], Pk[a]))
ck(ndiag > 0 and ncomm > 0 and ncomm_pairs > 0, "frame-gap witness found")
print("   M(D) = -prod A_k Delta_k A_k^-1 exact; with output-frame coordinate masks E_k the target is diagonal for ANY site-frame P_k = A_k^-1 E_k A_k")
print("   frame gap witness (n=4): %d/%d site masks not diagonal, %d/%d not commuting with own T_k, %d pairs of site masks non-commuting" % (ndiag, N, ncomm, N, ncomm_pairs))
print("   => 'masks are coordinates' is forced only in the output frame; site-frame coordinate masks need [P_k,U_k]=0 (extra hypothesis H-site)")

print("3. star optimality (uniform dual), 50-digit Decimal, N = 2..1199")
getcontext().prec = 50
D8 = Decimal(8)
def fD(x): return Decimal(x) * Decimal(x).ln() if x > 0 else Decimal(0)
NMAX = 1199
f8 = [Decimal(0)] + [fD(8 * m) for m in range(1, NMAX + 1)]       # f(8m)
f8p = [None] + [fD(8 * m + 1) for m in range(1, NMAX + 1)]       # f(8m+1)
best_all = [None] * (NMAX + 1)      # min over 1<=h<=m of r(h,m), m>=2
best_ex = [None] * (NMAX + 1)       # min over 1<=h<m
for m in range(2, NMAX + 1):
    ba = bx = None
    for h in range(1, m + 1):
        r = (f8p[m] - f8[m - h]) / (h * (m - 1))
        if ba is None or r < ba: ba = r
        if h < m and (bx is None or r < bx): bx = r
    best_all[m], best_ex[m] = ba, bx
worst_margin = None; prefmin = None; arg = None
for N in range(2, NMAX + 1):
    rho = f8p[N] / (N * (N - 1))
    cand = best_ex[N]
    if prefmin is not None and prefmin < cand: cand = prefmin
    mar = cand / rho - 1
    ck(mar > Decimal("1e-6"), "dual strictness fails at N=%d (margin %s)" % (N, mar))
    if worst_margin is None or mar < worst_margin: worst_margin, arg = mar, N
    prefmin = best_all[N] if prefmin is None else min(prefmin, best_all[N])
print("   every non-star field has price per covered ordered pair > rho_N = f(8N+1)/(N(N-1)) for all N=2..1199;")
print("   smallest margin %.4f%% at N=%d (all other N larger margin, 50-digit arithmetic)" % (100 * worst_margin, arg))
for N in (6, 8, 10, 12, 18):
    rho = f8p[N] / (N * (N - 1)); c = min(best_ex[N], min(best_all[m] for m in range(2, N)))
    print("   N=%2d margin %.2f%%" % (N, 100 * (c / rho - 1)))
# explicit field coverage count: a field with h hosts and m sites covers h*(m-1) ordered pairs
cnt = lambda h, m: sum(1 for i in range(h) for j in range(m) if i != j)
ck(all(cnt(h, m) == h * (m - 1) for m in range(1, 9) for h in range(1, m + 1)), "coverage count h(m-1)")

print("4. staircase / majorisation bound (base package), L even 4..18")
f = lambda x: x * math.log(x) if x > 0 else 0.0
TOL = 1e-9
cc = lambda m: f(8 * m + 1) - f(8 * m - 8)
def bound(L): return f(8 * L + 1) + sum(cc((k + 1) // 2) for k in range(1, L + 1))
def runs(idle, lo, hi):
    out, r = [], 0
    for k in range(lo, hi + 1):
        if k in idle: r += 1
        else:
            if r: out.append(r)
            r = 0
    if r: out.append(r)
    return out
def fcost(lo, hi, Y):
    idle = set(range(lo, hi + 1)) - set(Y)
    return f(8 * (hi - lo + 1) + 1) - sum(f(8 * r) for r in runs(idle, lo, hi))
def chain_fields(a, b):
    return [(c, a - 1, (c,)) for c in range(a)] + [(a, a + c, (a + c,)) for c in range(b)]
def twin_fields(a, b):
    return [(0, c, (c,)) for c in range(a)] + [(a + c, a + b - 1, (a + c,)) for c in range(b)]
def Dflds(fs, L): return f(8 * L + 1) + sum(fcost(*t) for t in fs)
for L in range(4, 19, 2):
    g = L // 2
    ck(abs(bound(L) - Dflds(chain_fields(g, g), L)) < TOL and abs(bound(L) - Dflds(twin_fields(g, g), L)) < TOL, "bound=chain=twin L=%d" % L)
    for a in range(1, L):
        if a != g: ck(Dflds(chain_fields(a, L - a), L) > bound(L) + 1e-6, "unbalanced chain(%d|%d) L=%d" % (a, L - a, L))
ck(abs(bound(18) - 1418.8458829) < 1e-6, "L=18 value")
print("   bound(18) = %.10f = chain(9|9) = outer-nested twin; all unbalanced chains strictly above, L=4..18" % bound(18))
def hull_sizes(q, L):
    out = []
    for i in range(L):
        best = None
        for p in (0, 1):
            lo = i
            for j in range(i):
                if q[j] != p: lo = j; break
            hi = i
            for j in range(L - 1, i, -1):
                if q[j] == p: hi = j; break
            n_ = hi - lo + 1
            if best is None or n_ < best: best = n_
        out.append(best)
    return out
LMAXS = 14 if QUICK else 16
for L in range(4, LMAXS + 1, 2):
    for qm in range(1 << (L - 1)):
        q = [0] + [(qm >> j) & 1 for j in range(L - 1)]
        ns = sorted(hull_sizes(q, L))
        for k, v in enumerate(ns, 1):
            if v < (k + 1) // 2: ck(False, "staircase L=%d q=%s" % (L, q))
print("   staircase lemma n_(k) >= ceil(k/2) holds for all sign patterns q, L <= %d" % LMAXS)
def rowc(lo, hi, i): return f(8 * (hi - lo + 1) + 1) - f(8 * (i - lo)) - f(8 * (hi - i))
LMAXE = 14 if QUICK else 18
for L in range(4, LMAXE + 1, 2):
    best = 1e18; nmin = 0
    for qm in range(1 << (L - 1)):
        q = [0] + [(qm >> j) & 1 for j in range(L - 1)]
        tot = 0.0
        for i in range(L):
            bc = 1e18
            for p in (0, 1):
                lo = i
                for j in range(i):
                    if q[j] != p: lo = j; break
                hi = i
                for j in range(L - 1, i, -1):
                    if q[j] == p: hi = j; break
                c = rowc(lo, hi, i)
                if c < bc: bc = c
            tot += bc
            if tot > best + TOL: break
        else:
            if tot < best - TOL: best, nmin = tot, 1
            elif abs(tot - best) <= TOL: nmin += 1
    ck(abs(best + f(8 * L + 1) - bound(L)) < 1e-8 and nmin == 2, "exhaustive sign-model minimum L=%d (min %.6f, minimisers %d)" % (L, best, nmin))
print("   exhaustive minimum of the sign-factorisation model over q in {+-}^L (best p per row) equals the bound, exactly 2 minimisers, L <= %d" % LMAXE)

print("5. S identity and block roots")
v, c, L = 104, 56, 18
ck(v - c == 48 and L * (v - c) - 1 * v == 760 == v * (L - 1) - L * c, "S=760")
for e in range(0, 5):
    ck(L * (v - c) - (1 + e) * v == 760 - 104 * e, "S with e extra units")
droot = lambda s: f(8 * s + 1) + sum(cc((k + 1) // 2) for k in range(1, s + 1))
Dtot = 226939 / 104.0                      # quoted: total D of the 18-call native ledger (18 calls), per port
Dn = Dtot - droot(18)
ck(abs(droot(18) * 104 - 147560) < 0.5, "root net 147,560")
S0 = 760 / 104.0; base = S0 / Dtot
def partitions(n, m=None):
    if m is None: m = n
    if n == 0: yield []; return
    for k in range(min(n, m), 0, -1):
        for r in partitions(n - k, k): yield [k] + r
bestD = {}; worst_true = -9
for part in partitions(18):
    b = len(part)
    Dr = sum(droot(s) for s in part) + Dn
    Skept = S0 / Dr / base - 1            # S as if the extra units were free
    Strue = (S0 - (b - 1)) / Dr / base - 1
    if b >= 2:
        ck(Strue < -1e-9, "a block root pays: %s %.4f" % (part, Strue))
        worst_true = max(worst_true, Strue)
    if b not in bestD or Skept > bestD[b][0]: bestD[b] = (Skept, Strue, part)
print("   all %d partitions of 18 into b>=2 blocks have true-S gain < 0; best true-S gain over all partitions = %.2f%%" % (sum(1 for _ in partitions(18)) - 1, 100 * worst_true))
print("   best S-kept (D-gain only) / true-S gain by b (best partition for the S-kept gain):")
for b in range(1, 7):
    sk, st, pt = bestD[b]; print("     b=%d %-22s S kept %+6.1f%%  true S %+6.1f%%" % (b, pt, 100 * sk, 100 * st))
ck(abs(100 * bestD[2][0] - 10.3) < 0.1 and abs(100 * bestD[2][1] + 4.8) < 0.1, "b=2 table +10.3/-4.8")
ck(abs(100 * bestD[3][0] - 17.3) < 0.1 and abs(100 * bestD[3][1] + 14.8) < 0.1, "b=3 table +17.3/-14.8")
ck(abs(100 * bestD[6][0] - 30.5) < 0.1 and abs(100 * bestD[6][1] + 58.8) < 0.1, "b=6 table +30.5/-58.8")
# marginal D gains fall: balanced blocks
gains = [100 * (bestD[b + 1][0] - bestD[b][0]) for b in range(1, 6)]
ck(all(gains[i] > gains[i + 1] for i in range(4)), "marginal D-gain per block falls")
print("   marginal D gain per extra block (percentage points):", ["%.1f" % g for g in gains], "; each block costs exactly 1/(S/104)=%.2f%% of S" % (100 / S0))
# break-even for ONE extra unit: D_root <= ?
be = (Dtot * (S0 - 1) / S0) - Dn
print("   break-even D_root with e=1 extra unit: %.1f per port (chain %.1f; ratio %.3f)" % (be, droot(18), be / droot(18)))
ck(1119 < be < 1121, "break-even ~ 1120")
for e in (1, 2, 3):
    print("     e=%d: D_root must be <= %.1f  (%.1f%% of chain)" % (e, (Dtot * (S0 - e) / S0) - Dn, 100 * ((Dtot * (S0 - e) / S0) - Dn) / droot(18)))
print()
print("FAILURES:", len(fails))
print("PASS_ROOT_CORE" if not fails else "FAIL_ROOT_CORE")
