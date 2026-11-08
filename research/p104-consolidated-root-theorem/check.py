"""Exact checks for the consolidated root theorem. Python 3.12, standard library only.
    python3.12 -I -B check.py [--quick] [--twisted]
Runs: (0) the base chain-optimality checker and the core checker; (1) rigidity of the shortest root by an
exact tangent-space computation over Q; (2) the D_root formula against the #6833 invoice (50-digit Decimal);
(3) the dense-x/dense-y decision logs for L = 4, 6, 8 (cost and sign-prefilter recomputed, L = 4 enumeration redone,
Singular re-run if it is installed); (4) the lemmas of the all-L single-host theorem; (5) the e=1 floor;
(6) the exact L=2 D-free-basis and D-job tests. --twisted re-runs the two twisted-site Groebner decisions (about 90 s).
Prints PASS_P104_CONSOLIDATED_ROOT_THEOREM on success."""
import sys, os, math, re, json, itertools, subprocess, shutil, collections
from fractions import Fraction as Fr
from decimal import Decimal as Dd, getcontext
HERE = os.path.dirname(os.path.abspath(__file__)); SUPP = os.path.join(HERE, "supp")
QUICK = "--quick" in sys.argv
fails = []
def ck(c, m):
    if not c: fails.append(m); print("FAIL", m)
    return c
f = lambda x: x * math.log(x) if x > 0 else 0.0

# ------------------------------------------------------------------ 0. sub-checkers
print("0. base checker and core checker")
for name, marker in (("base_check.py", "PASS_P104_ROOT_CHAIN_OPTIMALITY"), ("root_check.py", "PASS_ROOT_CORE")):
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, name)] + (["--quick"] if QUICK else []), capture_output=True, text=True)
    ck(marker in r.stdout and r.returncode == 0, name + " failed")
    print("   %-14s %s" % (name, marker if marker in r.stdout else "FAILED"))

# ------------------------------------------------------------------ linear algebra over Q
def I_(n): return [[Fr(int(i == j)) for j in range(n)] for i in range(n)]
def mm(A, B):
    Bt = list(zip(*B)); return [[sum(a * b for a, b in zip(r, c)) for c in Bt] for r in A]
def rank(M):
    M = [r[:] for r in M]; rk = 0
    for c in range(len(M[0]) if M else 0):
        p = next((r for r in range(rk, len(M)) if M[r][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]; pv = M[rk][c]
        for r in range(rk + 1, len(M)):
            if M[r][c] != 0:
                k = M[r][c] / pv; M[r] = [a - k * b for a, b in zip(M[r], M[rk])]
        rk += 1
    return rk
def sign_root(n):
    s = lambda i, j: 1 if i > j else -1
    S = [[Fr(0 if i == j else s(i, j)) for j in range(n)] for i in range(n)]
    A = [r[:] + I_(n)[i] for i, r in enumerate(S)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0); A[c], A[p] = A[p], A[c]
        pv = A[c][c]; A[c] = [v / pv for v in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                k = A[r][c]; A[r] = [a - k * b for a, b in zip(A[r], A[c])]
    Si = [r[n:] for r in A]
    xs = [[Fr(int(j == i)) for j in range(n)] for i in range(n)] + [[-sum(r) for r in Si]]
    ys = [[Fr(0 if i == j else s(i, j)) for j in range(n)] for i in range(n)] + [[Fr(1)] * n]
    return xs, ys
def T_of(x, y):
    n = len(x); return [[Fr(int(i == j)) - 2 * x[i] * y[j] for j in range(n)] for i in range(n)]

# ------------------------------------------------------------------ 1. rigidity: tangent space over Q
print("1. rigidity of the shortest root (tangent space, exact over Q; the global proof is in THEOREM.md)")
for n in (2, 4, 6):
    N = n + 1; xs, ys = sign_root(n); Ts = [T_of(xs[k], ys[k]) for k in range(N)]
    U = []; P = I_(n)
    for k in range(N): P = mm(Ts[k], P); U.append(P)
    ck(P == [[-v for v in r] for r in I_(n)], "product -I n=%d" % n)
    Am = [None] * N; Q = I_(n)
    for k in reversed(range(N)): Am[k] = Q; Q = mm(Q, Ts[k])
    Um = lambda k: I_(n) if k < 0 else U[k]
    G = [[sum(a * b for a, b in zip(ys[i], xs[j])) for j in range(N)] for i in range(N)]
    Z = [[Fr(1) if i == j else (G[i][j] if i > j else -G[i][j]) for j in range(N)] for i in range(N)]
    ck(rank(Z) == 1 and all(G[i][j] * G[j][i] == -1 for i in range(N) for j in range(N) if i != j), "Z rank 1 n=%d" % n)
    nv = 2 * n * N; J = [[Fr(0)] * nv for _ in range(N + n * n)]
    for k in range(N):
        for a in range(n):
            J[k][k * 2 * n + a] = ys[k][a]; J[k][k * 2 * n + n + a] = xs[k][a]
            for off, dT in ((a, [[-2 * (1 if i == a else 0) * ys[k][j] for j in range(n)] for i in range(n)]),
                            (n + a, [[-2 * xs[k][i] * (1 if j == a else 0) for j in range(n)] for i in range(n)])):
                D = mm(mm(Am[k], dT), Um(k - 1))
                for i in range(n):
                    for j in range(n): J[N + i * n + j][k * 2 * n + off] = D[i][j]
    rk = rank(J); cols = []
    for i in range(n):
        for j in range(n):
            v = []
            for k in range(N):
                v += [xs[k][i] if b == i and False else Fr(0) for b in range(0)]
                # dx_k = E x_k , dy_k = -y_k E with E = e_i e_j^T
                v += [(xs[k][j] if a == i else Fr(0)) for a in range(n)] + [-(ys[k][i] if b == j else Fr(0)) for b in range(n)]
            cols.append(v)
    for m in range(N):
        v = []
        for k in range(N):
            c = 1 if k == m else 0; v += [c * a for a in xs[k]] + [-c * b for b in ys[k]]
        cols.append(v)
    orb = rank(cols)
    inker = all(sum(J[r][c] * col[c] for c in range(nv)) == 0 for col in cols for r in range(len(J)))
    print("   n=%d N=%d: rank J=%d, tangent dim=%d, orbit dim=%d (n^2+n=%d), orbit tangent inside kernel: %s" % (n, N, rk, nv - rk, orb, n * n + n, inker))
    ck(nv - rk == orb == n * n + n and inker, "tangent = orbit n=%d" % n)

# ------------------------------------------------------------------ 2. cost formula against the #6833 invoice
print("2. D_root formula derived from the #6833 invoice (50-digit Decimal)")
getcontext().prec = 50
inv = json.load(open(os.path.join(SUPP, "invoice_6833.json")))
V = 104
def fD(r):
    r = Dd(r); return r * r.ln() if r > 1 else Dd(0)
def histD(T, P): return sum(Dd(n) * fD(r) for r, n in T.items()) - sum(Dd(n) * fD(r) for r, n in P.items())
T = collections.Counter({int(k): v for k, v in inv["targets"].items()}); Pd = collections.Counter({int(k): v for k, v in inv["paid"].items()})
HELP = {1: 14, 2: 8, 3: 4, 4: 109, 5: 17, 6: 3, 7: 10, 8: 40, 9: 359}            # per-call native targets, 18 calls
LOCAL_PAID = {1: 2234, 2: 454, 3: 489, 4: 110, 5: 152, 6: 7, 7: 9, 8: 1}          # per-call native paid
Troot = T - collections.Counter({r: 18 * n for r, n in HELP.items()}); Proot = Pd - collections.Counter({r: 18 * n for r, n in LOCAL_PAID.items()})
Tl, Pl = collections.Counter(), collections.Counter()
for e in inv["caller_events"]:
    if e[0] == "QUERY": Pl[1] += V
    elif e[0] == "IDLE_ONE": Pl[8 * len(e[2])] += V
for t in inv["caller_diagonal"]: Tl[int(t[0] % 2) + 8 * sum(t[2:])] += V
ck(Troot == Tl and Proot == Pl, "root part of the invoice equals the literal root events")
print("   root part of the published invoice == root events of the literal caller word:", Troot == Tl and Proot == Pl)
chain_closed = lambda g: fD(16 * g + 1) + 2 * sum(fD(8 * m + 1) - fD(8 * m - 8) for m in range(1, g + 1))
Droot = histD(Troot, Proot) / V
ck(abs(Droot - chain_closed(9)) < Dd("1e-40"), "D_root literal == chain closed form")
print("   D_root per port = %.10f ; closed form chain(9|9) = %.10f ; |diff| < 1e-40" % (Droot, chain_closed(9)))
masks = sorted(sum(t[2:]) for t in inv["caller_diagonal"][1:19])
ck(masks == sorted([m for m in range(1, 10)] * 2), "field masks of the literal word are 1..9 twice")
idles = sorted(len(e[2]) for e in inv["caller_events"] if e[0] == "IDLE_ONE")
ck(idles == sorted(list(range(1, 9)) * 2), "idle runs 1..8 twice")
Dform = fD(8 * 18 + 1) + sum(fD(8 * m + 1) for m in masks) - sum(fD(8 * r) for r in idles)
ck(abs(Dform - Droot) < Dd("1e-40"), "formula from masks/idles")
S = sum(r * n for r, n in T.items()) - sum(r * n for r, n in Pd.items()); ck(S == 760, "whole-invoice S = 760")
Dtot = histD(T, Pd)
def kappa_of():
    tot = collections.Counter(T); tot.subtract(Pd)
    F = lambda k: sum(Dd(n) * Dd(r) ** (1 - k) for r, n in tot.items())
    lo, hi = Dd(0), Dd("0.02")
    for _ in range(160):
        mid = (lo + hi) / 2; lo, hi = (mid, hi) if F(mid) > 0 else (lo, mid)
    return lo
kap = kappa_of(); ck(abs(kap - Dd("0.0033718")) < Dd("1e-8"), "kappa of the invoice")
phi = lambda x, k: (Dd(x) - Dd(x) ** (1 - k)) / k
Dk = sum(Dd(n) * phi(r, kap) for r, n in T.items()) - sum(Dd(n) * phi(r, kap) for r, n in Pd.items())
ck(abs(Dd(S) / Dk - kap) < Dd("1e-35"), "exact moment identity S/D_kappa = kappa")
Dkroot = (sum(Dd(n) * phi(r, kap) for r, n in Troot.items()) - sum(Dd(n) * phi(r, kap) for r, n in Proot.items())) / V
print("   root share of linearised D: %.2f%% ; exact-moment D_root at kappa = %.4f (ratio %.5f): a rescaling of about -0.78%%" % (100 * Droot * V / Dtot, Dkroot, Dkroot / Droot))
ck(abs(Dkroot / Droot - 1 + Dd("0.0078")) < Dd("0.0002"), "rescaling -0.78%")
kf = float(kap); ph = lambda x: (x - x ** (1 - kf)) / kf
cphi = lambda m: ph(8 * m + 1) - ph(8 * m - 8)
for L in range(4, 13 if not QUICK else 11, 2):
    best = 1e18
    for qm in range(1 << (L - 1)):
        q = [0] + [(qm >> j) & 1 for j in range(L - 1)]; tot = 0.0
        for i in range(L):
            bc = 1e18
            for p in (0, 1):
                lo = next((j for j in range(i) if q[j] != p), i); hi = next((j for j in range(L - 1, i, -1) if q[j] == p), i)
                bc = min(bc, ph(8 * (hi - lo + 1) + 1) - ph(8 * (i - lo)) - ph(8 * (hi - i)))
            tot += bc
        best = min(best, tot)
    ck(abs(best - 2 * sum(cphi(m) for m in range(1, L // 2 + 1))) < 1e-7, "sign model with phi_kappa L=%d" % L)
print("   with the exact kernel phi_kappa in place of x ln x, the exhaustive sign model still equals the chain (L = 4..%d)" % (12 if not QUICK else 10))
for a in range(0, 19):
    if a != 9:
        ck(sum(ph(8 * m + 1) - ph(8 * m - 8) for m in range(1, a + 1)) + sum(ph(8 * m + 1) - ph(8 * m - 8) for m in range(1, 19 - a)) > 2 * sum(cphi(m) for m in range(1, 10)), "chain(a|b) phi")

# ------------------------------------------------------------------ 3. dense logs
print("3. dense x and dense y: decision logs for L = 4, 6, 8")
def fcost(lo, hi, Y):
    m = hi - lo + 1; c = f(8 * m + 1); r = 0
    for k in range(lo, hi + 1):
        if k in Y: c -= f(8 * r); r = 0
        else: r += 1
    return c - f(8 * r)
def chain_fs(L):
    g = L // 2; return [(c, g - 1, (c,)) for c in range(g)] + [(g, g + c, (g + c,)) for c in range(g)]
def twin_fs(L):
    g = L // 2; return [(0, c, (c,)) for c in range(g)] + [(g + c, L - 1, (g + c,)) for c in range(g)]
def sign_ok(fs, L):
    """necessary sign condition: entries with no live full-class field are sign-consistent (signed union-find), uncovered-row rule"""
    cov = [0] * L
    for lo, hi, Y in fs:
        M = ((1 << (hi - lo + 1)) - 1) << lo
        for r in Y: cov[r] |= M
    par = list(range(2 * L)); ps = [0] * (2 * L)
    def find(x):
        q = 0
        while par[x] != x: q ^= ps[x]; x = par[x]
        return x, q
    for i in range(L):
        for j in range(L):
            if i == j or (cov[i] >> j) & 1: continue
            w = 0 if i > j else 1
            ra, pa = find(i); rb, pb = find(L + j)
            if ra == rb:
                if (pa ^ pb) != w: return False
            else: par[ra] = rb; ps[ra] = pa ^ pb ^ w
    for i in range(L):
        if not cov[i] and any(k != i and not (cov[k] >> i) & 1 for k in range(L)): return False
    return True
def parse_e(L):
    out = []
    for l in open(os.path.join(SUPP, "dense_enum_L%d.txt" % L)):
        if "d=" in l and l[0].isdigit():
            fs = tuple((int(a), int(b), tuple(int(ch) for ch in c)) for a, b, c in re.findall(r"\[(\d+),(\d+)\|(\d+)\]", l))
            out.append((float(re.search(r"d=([+-][\d.]+)", l).group(1)), fs))
    return out
def parse_d(L):
    out = []
    for l in open(os.path.join(SUPP, "dense_dec_L%d.txt" % L)):
        m = re.match(r"(\S+) (REAL|dead) pivots \[(.*?)\]", l)
        if m:
            fs = tuple((a, b, tuple(Y)) for a, b, Y in ast_eval(l[l.index("[(") :]))
            out.append((float(m.group(1)), m.group(2), m.group(3), fs))
    return out
import ast
def ast_eval(s):
    return ast.literal_eval(s.strip().rsplit("]", 1)[0] + "]") if False else ast.literal_eval(s.strip())
exp = {4: (10, 6, 4), 6: (34, 4, 2), 8: (60, 2, 0)}      # sign-consistent, realizable, realizable below chain
for L in (4, 6, 8):
    CH = sum(fcost(*t) if False else fcost(t[0], t[1], set(t[2])) for t in chain_fs(L))
    hdr = open(os.path.join(SUPP, "dense_enum_L%d.txt" % L)).readline()
    ck(abs(float(re.search(r"chain=([\d.]+)", hdr).group(1)) - CH) < 1e-6, "chain cost L=%d" % L)
    E = parse_e(L); Dl = parse_d(L)
    ck(len(E) == exp[L][0] == len(Dl), "sign-consistent count L=%d" % L)
    nreal = nbelow = 0
    for (d, fs), (d2, st, piv, fs2) in zip(E, Dl):
        c = sum(fcost(lo, hi, set(Y)) for lo, hi, Y in fs)
        ck(abs(c - CH - d) < 1e-5 and c <= CH + 1e-7 and len(fs) >= L - 1, "cost of a listed family L=%d" % L)
        ck(sign_ok(fs, L), "listed family passes the sign prefilter L=%d" % L)
        ck(abs(d - d2) < 1e-5 and tuple(sorted(fs)) == tuple(sorted(fs2)), "enumeration/decision logs agree L=%d" % L)
        if st == "REAL":
            nreal += 1
            if d < -1e-6: nbelow += 1
            ck(d > -1e-6 or piv.strip() != "" , "a realizable family below the chain has an uncovered pivot row")
    ck(nreal == exp[L][1] and nbelow == exp[L][2], "realizable counts L=%d" % L)
    ck(sorted(map(tuple, (sorted(x) for x in [chain_fs(L), twin_fs(L)]))) == sorted(tuple(sorted(fs)) for (d, st, piv, fs) in Dl if st == "REAL" and abs(d) < 1e-6), "the realizable at chain cost are chain and twin L=%d" % L)
    print("   L=%d: %d sign-consistent families within chain budget; %d realizable (%d below chain, all with an uncovered pivot row); chain and twin are the only realizable at chain cost" % (L, exp[L][0], nreal, nbelow))
for L in (6, 8):
    sv = 2 * (f(9) - f(1)) - (f(8 * (L // 2 + 1) + 1) - f(8 * (L // 2 + 1) - 8))
    print("   pivot-family saving 2c(1) - c(L/2+1) at L=%d: %+.5f" % (L, sv))
    ck((L == 6 and abs(sv - 0.43858) < 1e-4) or (L == 8 and sv < 0), "pivot saving")
ck(all(2 * (f(9)) - (f(8 * (g + 1) + 1) - f(8 * g)) < 0 for g in range(4, 12)), "pivot saving negative for L >= 8")
# re-enumerate L = 4 exactly (all multisets of >= 3 types within the budget) and compare with the stored list
def types(L):
    T_ = []
    for lo in range(L):
        for hi in range(lo, L):
            idx = list(range(lo, hi + 1))
            for mk in range(1, 1 << len(idx)):
                Y = tuple(idx[b] for b in range(len(idx)) if mk >> b & 1); T_.append((fcost(lo, hi, set(Y)), lo, hi, Y))
    T_.sort(); return T_
def enum(L, mx):
    CH = sum(fcost(a, b, set(Y)) for a, b, Y in chain_fs(L)); Ty = types(L); cmin = Ty[0][0]; out = []
    def rec(start, cur, c):
        if len(cur) >= L - 1 and sign_ok(cur, L): out.append((c - CH, tuple(cur)))
        if len(cur) >= mx: return
        for k in range(start, len(Ty)):
            tc = Ty[k]
            if c + tc[0] > CH + 1e-7: break
            if c + tc[0] + max(0, L - 2 - len(cur)) * cmin > CH + 1e-7: continue
            cur.append(tc[1:]); rec(k, cur, c + tc[0]); cur.pop()
    rec(0, [], 0.0); return out
for L, mx in ((4, 8),) + (((6, 10),) if not QUICK else ()):
    Er = enum(L, mx); Es = parse_e(L)
    ck(sorted(tuple(sorted(fs)) for d, fs in Er) == sorted(tuple(sorted(fs)) for d, fs in Es), "re-enumeration L=%d" % L)
    print("   L=%d: Python re-enumeration of all families (>= L-1 fields, up to %d, cost <= chain) gives exactly the stored %d sign-consistent families" % (L, mx, len(Es)))
# Singular re-run, if installed
def singular_script(fs, L):
    vs = []; eqs = []; a = ["a%d" % i for i in range(L)]; al = ["r%d" % j for j in range(L)]; vs += a + al; nd = []; B = {}; X = {}
    for c, (lo, hi, Y) in enumerate(fs):
        for i in Y: B[c, i] = "b%d_%d" % (c, i); vs.append(B[c, i])
        for j in range(lo, hi + 1): X[c, j] = "x%d_%d" % (c, j); vs.append(X[c, j])
        zb = ["zb%d_%d" % (c, i) for i in Y]; zx = ["zx%d_%d" % (c, j) for j in range(lo, hi + 1)]; vs += zb + zx
        nd.append("+".join("%s*%s" % (z, B[c, i]) for z, i in zip(zb, Y)) + "-1")
        nd.append("+".join("%s*%s" % (z, X[c, j]) for z, j in zip(zx, range(lo, hi + 1))) + "-1")
    for i in range(L):
        for j in range(L):
            t = ["%s*%s" % (a[i], al[j])]
            for c, (lo, hi, Y) in enumerate(fs):
                if i in Y and lo <= j <= hi: t.append("%s*%s" % (B[c, i], X[c, j]))
            eqs.append("%d-(%s)" % (0 if i == j else (1 if i > j else -1), "+".join(t)))
    return "ring r=0,(%s),dp;\nideal I=%s;\nideal G=std(I);\nprint(G[1]==1);quit;\n" % (",".join(vs), ",\n".join(eqs + nd))
if shutil.which("Singular"):
    agree = tot = 0
    for L in (4, 6, 8):
        for (d, st, piv, fs) in parse_d(L):
            r = subprocess.run(["Singular", "-q"], input=singular_script(fs, L), capture_output=True, text=True, timeout=600)
            res = {"1": "dead", "0": "REAL"}.get(r.stdout.split()[-1] if r.stdout.split() else "", "ERR")
            tot += 1; agree += (res == st)
    ck(agree == tot, "Singular re-run disagrees with the stored logs")
    print("   Singular is installed: re-ran all %d stored decisions, %d agree (1 in the Groebner basis = unrealizable over C)" % (tot, agree))
else:
    print("   Singular not installed: the stored decisions were not re-run (the logs are checked for cost, prefilter and consistency only)")

# ------------------------------------------------------------------ 4. lemmas of the all-L single-host theorem
print("4. single-host theorem: field-cost lemmas")
c_ = lambda m: f(8 * m + 1) - f(8 * m - 8)
Fm = lambda m, h: f(8 * m + 1) - f(8 * (m - h))
ck(all(Fm(m, h) >= c_(m) + (h - 1) * f(8) - 1e-9 for m in range(1, 200) for h in range(1, m + 1)), "lemma 1 (extra host costs f(8))")
ck(all(c_(a) + c_(b) >= c_(a + b - 1) - 1e-9 for a in range(1, 400) for b in range(1, 400)), "lemma 2 (c subadditive across a shared host)")
ck(all(Fm(m, h) / h >= f(9) - 1e-9 for m in range(1, 400) for h in range(1, m + 1)), "per-incidence cost >= f(9)")
bad = 0
for m in range(1, 13):
    for mk in range(1, 1 << m):
        r = 0; t = f(8 * m + 1); h = bin(mk).count("1")
        for k in range(m):
            if mk >> k & 1: t -= f(8 * r); r = 0
            else: r += 1
        t -= f(8 * r); bad += t < c_(m) + (h - 1) * f(8) - 1e-9
ck(bad == 0, "exact idle-run cost lemma, all (m<=12, Y)")
print("   cost_c >= c(m) + (h-1) f(8) for all (m,h), m < 200 and all host sets m <= 12; c(a)+c(b) >= c(a+b-1) for a,b < 400; per-incidence cost >= f(9)=%.4f" % f(9))

# ------------------------------------------------------------------ 5. e = 1 floor
print("5. roots with one extra unit (e = 1)")
def relax_min(L, R):
    full = (1 << L) - 1
    bits = lambda a, b: (((1 << (b + 1)) - 1) ^ ((1 << a) - 1)) if a <= b else 0
    rowc = lambda lo, hi, i: f(8 * (hi - lo + 1) + 1) - f(8 * (i - lo)) - f(8 * (hi - i))
    opts = []
    for i in range(L):
        o = [(rowc(lo, hi, i), lo, hi, full ^ bits(lo, hi)) for lo in range(i + 1) for hi in range(i, L)]; o.sort(); opts.append(o)
    def ok_pair(i, a, j, b):
        J = a & b & ~(1 << i) & ~(1 << j)
        B0 = J & bits(0, i - 1) if i > 0 else 0; B1 = J & bits(i + 1, j - 1) if j - i > 1 else 0; B2 = J & bits(j + 1, L - 1) if j < L - 1 else 0
        return not (B1 and (B0 or B2))
    def ok_triple(i, a, j, b, k, c):
        J = a & b & c & ~((1 << i) | (1 << j) | (1 << k))
        B0 = J & bits(0, i - 1) if i > 0 else 0; B1 = J & bits(i + 1, j - 1) if j - i > 1 else 0
        B2 = J & bits(j + 1, k - 1) if k - j > 1 else 0; B3 = J & bits(k + 1, L - 1) if k < L - 1 else 0
        return not (B1 and B2 and (B0 or B3))
    minrest = [sum(opts[i][0][0] for i in range(k, L)) for k in range(L + 1)]; best = [1e18]; ch = []
    def dfs(k, cost):
        if cost + minrest[k] >= best[0] - 1e-9: return
        if k == L: best[0] = cost; return
        for (c, lo, hi, off) in opts[k]:
            if cost + c + minrest[k + 1] >= best[0] - 1e-9: break
            good = all(ok_pair(i, ch[i][3], k, off) for i in range(k)) if R == 1 else all(ok_triple(i, ch[i][3], j, ch[j][3], k, off) for i in range(k) for j in range(i + 1, k))
            if good: ch.append((c, lo, hi, off)); dfs(k + 1, cost + c); ch.pop()
    dfs(0, 0.0); return best[0] + f(8 * L + 1)
bound = lambda L: f(8 * L + 1) + sum(c_((k + 1) // 2) for k in range(1, L + 1))
for L in (4, 6, 8):
    ck(abs(relax_min(L, 1) - bound(L)) < 1e-6, "rank-1 relaxation reproduces the chain bound L=%d" % L)
print("   rank-1 pair relaxation reproduces the chain bound at L=4,6,8 (%.3f, %.3f, %.3f)" % tuple(bound(L) for L in (4, 6, 8)))
for L, v in ((4, 194.485), (6, 332.857), (8, 476.552)) + (((10, 633.388),) if not QUICK else ()):
    r2 = relax_min(L, 2); ck(abs(r2 - v) < 5e-3, "rank-2 relaxation L=%d" % L)
    print("   rank-2 triple relaxation L=%d: %.3f (%.3f of chain)" % (L, r2, r2 / bound(L)))
def count_max(L, t):
    full = (1 << L) - 1; bits = lambda a, b: (((1 << (b + 1)) - 1) ^ ((1 << a) - 1)) if a <= b else 0
    opts = [[full ^ bits(lo, hi) for lo in range(max(0, i - t + 1), i + 1) for hi in range(i, min(L - 1, lo + t - 1) + 1)] for i in range(L)]
    def ok(i, a, j, b, k, c):
        J = a & b & c & ~((1 << i) | (1 << j) | (1 << k))
        B0 = J & bits(0, i - 1) if i > 0 else 0; B1 = J & bits(i + 1, j - 1) if j - i > 1 else 0
        B2 = J & bits(j + 1, k - 1) if k - j > 1 else 0; B3 = J & bits(k + 1, L - 1) if k < L - 1 else 0
        return not (B1 and B2 and (B0 or B3))
    best = [0]; chs = []
    def dfs(k, cnt):
        if cnt + (L - k) <= best[0]: return
        if k == L: best[0] = cnt; return
        for off in opts[k]:
            if all(ok(chs[x][0], chs[x][1], chs[y][0], chs[y][1], k, off) for x in range(len(chs)) for y in range(x + 1, len(chs))):
                chs.append((k, off)); dfs(k + 1, cnt + 1); chs.pop()
        dfs(k + 1, cnt)
    dfs(0, 0); return best[0]
for t in (1, 2, 3):
    vals = [count_max(L, t) for L in range(4, 13 if not QUICK else 11, 2)]
    ck(all(v <= 5 * t for v in vals), "count lemma t=%d" % t)
    print("   t=%d: max number of sites with mask size <= t, L = 4.. : %s (bound 5t = %d)" % (t, vals, 5 * t))
v, c, L = 104, 56, 18; Dt = 226939 / 104.0; S0 = 760 / 104.0; Dn = Dt - bound(18)
be = Dt * (S0 - 1) / S0 - Dn
fl5 = f(8 * L + 1) + sum(c_((k + 4) // 5) for k in range(1, L + 1)); fl13 = f(8 * L + 1) + sum(c_((k + 12) // 13) for k in range(1, L + 1))
print("   e=1 break-even D_root <= %.1f ; floor with k-th smallest mask >= ceil(k/5): %.2f ; even ceil(k/13) gives %.1f" % (be, fl5, fl13))
ck(1119 < be < 1121 and abs(fl5 - 1276.03) < 0.01 and fl13 > be and abs(fl13 - 1136.3) < 0.1, "e=1 floor above break-even")

# ------------------------------------------------------------------ 6. exact L = 2 tests: D-free bases, D-jobs
print("6. exact L = 2 example: D-free bases and one D-job")
n = 4
def vec(a, u, p=0, q=0):
    x = [0] * n; y = [0] * n; x[0] = a; y[0] = u; x[1] = a + 1; y[1] = 1 - u; x[2] = 1 - a; y[2] = u - 1; x[3] = q; y[3] = p; return x, y
thin = [vec(0, 1, 0, 1), vec(-1, 2, 1, 0), vec(-1, 3, 1, -1)]
UN = {"L": ([1, 1, 0, 0], [1, -1, 0, 0]), "R": ([-1, 0, 1, 0], [1, 0, 1, 0]), "t0": thin[0], "t1": thin[1], "t2": thin[2]}
Tm = {k: T_of([Fr(a) for a in x], [Fr(b) for b in y]) for k, (x, y) in UN.items()}
for k, (x, y) in UN.items(): ck(sum(a * b for a, b in zip(x, y)) == 0, "unit " + k)
PL = [1, 1, 0, 0]; PR = [1, 0, 1, 0]
def fac(k, Da, Db):
    T_ = Tm[k]
    if k not in ("L", "R"): return T_
    P_ = PL if k == "L" else PR; D_ = Da if k == "L" else Db
    return mm([[Fr(int(i == j)) + (D_ - 1) * P_[i] * int(i == j) for j in range(n)] for i in range(n)], T_)
def Mof(word, Da, Db, job=None, pos=None):
    seq = [fac(k, Da, Db) for k in word]
    if job is not None: seq.insert(pos, job(Da, Db))
    P = I_(n)
    for S_ in seq: P = mm(S_, P)
    return P
GRID = [(Fr(a), Fr(b)) for a in (2, 3, 5, 7) for b in (2, 3, 5, 11)]      # multilinear/degree<=2 polynomials vanish iff they vanish here
def isdiag(M): return all(M[i][j] == 0 for i in range(n) for j in range(n) if i != j)
neg = [[Fr(-int(i == j)) for j in range(n)] for i in range(n)]
good = []
for order in itertools.permutations(UN):
    P = I_(n)
    for k in order: P = mm(Tm[k], P)
    if P == neg and all(isdiag(Mof(order, a, b)) for a, b in GRID): good.append(order)
ck(len(good) == 1, "exactly one ordering gives a diagonal M(D)")
o = good[0]
ck(all(Mof(o, a, b) == [[-(a * b if i == 0 else a if i == 1 else b if i == 2 else 1) * int(i == j) for j in range(n)] for i in range(n)] for a, b in GRID), "M(D) = -diag(DaDb, Da, Db, 1)")
print("   order %s gives M(D) = -diag(Da Db, Da, Db, 1) (all-field carries Da Db); D_root = f(17)+2f(9) = %.4f" % (o, f(17) + 2 * f(9)))
# D-dependent gauge: same product, factors leave the verifier's form
def Eij(i, j, v): return [[v if (a, b) == (i, j) else Fr(0) for b in range(n)] for a in range(n)]
def gmat(Da, Db): return [[Fr(int(i == j)) + Eij(3, 0, Da * Db - 1)[i][j] for j in range(n)] for i in range(n)]
def ginv(Da, Db): return [[Fr(int(i == j)) - Eij(3, 0, Da * Db - 1)[i][j] for j in range(n)] for i in range(n)]
Da, Db = Fr(3), Fr(5); Phis = []
for k, name in enumerate(o):
    g0 = I_(n) if k == 0 else gmat(Da, Db); g1 = I_(n) if k == len(o) - 1 else gmat(Da, Db)
    g0i = I_(n) if k == 0 else ginv(Da, Db)
    Phis.append(mm(mm(g1, fac(name, Da, Db)), g0i))
Mg = I_(n)
for Ph in Phis: Mg = mm(Ph, Mg)
ck(Mg == Mof(o, Da, Db), "gauged product equals M(D)")
nonlegal = 0
for k, name in enumerate(o):
    P1 = Phis[k]
    # evaluate the same gauged factor at D=(1,1): the legal form needs Phi(D) Phi(1)^-1 coordinate-diagonal
    g0 = I_(n) if k == 0 else gmat(Fr(1), Fr(1)); g1 = I_(n) if k == len(o) - 1 else gmat(Fr(1), Fr(1))
    T1 = mm(mm(g1, fac(name, Fr(1), Fr(1))), g0)          # g(1,1) = identity
    # inverse of T1 by exact solve
    A_ = [r[:] + I_(n)[i] for i, r in enumerate(T1)]
    for c in range(n):
        p = next(r for r in range(c, n) if A_[r][c] != 0); A_[c], A_[p] = A_[p], A_[c]; pv = A_[c][c]; A_[c] = [v_ / pv for v_ in A_[c]]
        for r in range(n):
            if r != c and A_[r][c] != 0: kf_ = A_[r][c]; A_[r] = [a - kf_ * b for a, b in zip(A_[r], A_[c])]
    nonlegal += not isdiag(mm(P1, [r[n:] for r in A_]))
ck(nonlegal == 4, "gauge: 4 of 5 factors leave the verifier form")
print("   a D-dependent gauge leaves the product unchanged but %d of 5 factors are not constants times coordinate-diagonal D-monomials" % nonlegal)
# one D-job
cs = [Fr(1), Fr(-1), Fr(2), Fr(-2), Fr(1, 2), Fr(-1, 2)]; ms = [lambda a, b: a, lambda a, b: b, lambda a, b: a * b]
chain = ["L", "t0", "t1", "t2", "R"]; hitsA = hitsB = 0
g0 = (Fr(3), Fr(5))
for d in range(n):
    for s in range(n):
        if d == s: continue
        for cc_ in cs:
            for mf in ms:
                job = lambda a, b, d=d, s=s, cc_=cc_, mf=mf: [[Fr(int(i == j)) + (cc_ * mf(a, b) if (i, j) == (d, s) else 0) for j in range(n)] for i in range(n)]
                for pos in range(6):
                    if isdiag(Mof(chain, *g0, job, pos)) and all(isdiag(Mof(chain, a, b, job, pos)) for a, b in GRID): hitsA += 1
                for drop in ("t0", "t1", "t2"):
                    w = [k for k in chain if k != drop]
                    for pos in range(5):
                        if isdiag(Mof(w, *g0, job, pos)) and all(isdiag(Mof(w, a, b, job, pos)) for a, b in GRID): hitsB += 1
ck(hitsA == 0 and hitsB == 0, "one D-job at L=2")
print("   one job I + c m(D) E_ds (all 12 (d,s), c in {+-1,+-2,+-1/2}, m in {Da,Db,DaDb}): chain+job at any of 6 slots -> %d diagonal words of 1296; one thin dropped -> %d of 3240" % (hitsA, hitsB))
f8, f16 = f(8), f(16); print("   job prices if added anyway: f(8)=%.3f, f(16)=%.3f per port, uncredited" % (f8, f16))

# ------------------------------------------------------------------ 7. optional twisted-site decisions
if "--twisted" in sys.argv:
    print("7. twisted-site decisions (Singular over Q, n = 4, k = 2, |S| = 2)")
    for S_, Sp in (("01", "23"), ("01", "12")):
        r = subprocess.run([sys.executable, "-I", "-B", os.path.join(SUPP, "twisted_site_singular.py"), S_, Sp, "2", "600"], capture_output=True, text=True)
        ok_ = "G[1]= 1" in r.stdout; ck(ok_, "twisted site S=%s S'=%s" % (S_, Sp)); print("   S=%s S'=%s: %s" % (S_, Sp, "1 in the ideal (no solution over C)" if ok_ else r.stdout))
else:
    print("7. twisted-site decisions: not run (add --twisted; about 90 s; script in supp/twisted_site_singular.py)")

print()
print("FAILURES:", len(fails))
print("PASS_P104_CONSOLIDATED_ROOT_THEOREM" if not fails else "FAIL_P104_CONSOLIDATED_ROOT_THEOREM")
sys.exit(1 if fails else 0)
