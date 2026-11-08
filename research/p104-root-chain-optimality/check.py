"""Exact checks for the chain-root optimality bound. Standard library only; run with python3.12 -I -B check.py.
Prints PASS_P104_ROOT_CHAIN_OPTIMALITY on success.  Option --quick stops the exhaustive sign enumeration at L=14."""
import sys, math, os
f = lambda x: x * math.log(x) if x > 0 else 0.0
TOL = 1e-9
QUICK = "--quick" in sys.argv
LS = list(range(4, 19, 2))
fails = []
def ck(cond, msg):
    if not cond:
        fails.append(msg); print("FAIL", msg)
    return cond

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
    """non-A field with mask [lo,hi], sites Y with a y-component; idle = mask minus Y"""
    idle = set(range(lo, hi + 1)) - set(Y)
    return f(8 * (hi - lo + 1) + 1) - sum(f(8 * r) for r in runs(idle, lo, hi))
def chain_fields(a, b):
    """chain(a|b): left sites 0..a-1 with fields [c,a-1], right sites a..a+b-1 with fields [a,a+c]; hosts at inner ends"""
    fs = [(c, a - 1, (c,)) for c in range(a)]
    fs += [(a, a + c, (a + c,)) for c in range(b)]
    return fs
def twin_fields(a, b):
    fs = [(0, c, (c,)) for c in range(a)] + [(a + c, a + b - 1, (a + c,)) for c in range(b)]
    return fs
cc = lambda m: f(8 * m + 1) - f(8 * m - 8)          # cost of a field of size m with host at an end
def bound(L):
    g = L // 2
    return f(8 * L + 1) + 2 * sum(cc(m) for m in range(1, g + 1))
def D_fields(fs, L): return f(8 * L + 1) + sum(fcost(lo, hi, Y) for lo, hi, Y in fs)

print("1. bound versus chain (explicit fields and idle runs), D_root per port")
for L in LS:
    g = L // 2
    bd = bound(L); dch = D_fields(chain_fields(g, g), L); dtw = D_fields(twin_fields(g, g), L)
    ck(abs(bd - dch) < TOL and abs(bd - dtw) < TOL, "bound != chain at L=%d" % L)
    # same via sorted staircase c(ceil(k/2))
    st = f(8 * L + 1) + sum(cc((k + 1) // 2) for k in range(1, L + 1))
    ck(abs(st - bd) < TOL, "staircase sum mismatch L=%d" % L)
    print("   L=%2d bound=%.10f chain=%.10f twin=%.10f" % (L, bd, dch, dtw))
ck(abs(bound(18) - 1418.8458829) < 1e-6, "L=18 value")

print("2. unbalanced chains strictly worse")
for L in LS:
    g = L // 2
    for a in range(1, L):
        if a == g: continue
        d = D_fields(chain_fields(a, L - a), L)
        ck(d > bound(L) + 1e-6, "chain(%d|%d) not worse at L=%d" % (a, L - a, L))
    print("   L=%2d: all %d unbalanced chains strictly above the bound" % (L, L - 2))

def hull_sizes(q, L):
    """For each row i, the smallest field size over the two row signs p (Lemma E hull)."""
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
            n = hi - lo + 1
            if best is None or n < best: best = n
        out.append(best)
    return out

print("3. size staircase #{rows with size <= t} <= min(2t, L), all sign patterns q (q_0 fixed by global flip)")
for L in LS:
    if L > 16: break
    worst = 0
    for qm in range(1 << (L - 1)):
        q = [0] + [(qm >> j) & 1 for j in range(L - 1)]
        ns = sorted(hull_sizes(q, L))
        for k, n in enumerate(ns, 1):           # k-th smallest size must be >= ceil(k/2)
            if n < (k + 1) // 2: ck(False, "staircase violated L=%d q=%s" % (L, q))
    print("   L=%2d: all %d patterns satisfy n_(k) >= ceil(k/2)" % (L, 1 << (L - 1)))

print("4. exhaustive optimum of the sign model: min over q in {+-}^L, best p per row (singleton hosts)")
def fam_cost_row(lo, hi, i): return f(8 * (hi - lo + 1) + 1) - f(8 * (i - lo)) - f(8 * (hi - i))
for L in LS:
    if QUICK and L > 14: break
    best = 1e18; arg = []
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
                c = fam_cost_row(lo, hi, i)
                if c < bc: bc = c
            tot += bc
            if tot > best + TOL: break
        else:
            if tot < best - TOL: best = tot; arg = [q]
            elif abs(tot - best) <= TOL: arg.append(q)
    g = L // 2
    chain_nonA = sum(fcost(lo, hi, Y) for lo, hi, Y in chain_fields(g, g))
    ck(abs(best - chain_nonA) < 1e-8, "enumeration minimum != chain at L=%d" % L)
    ck(abs(best + f(8 * L + 1) - bound(L)) < 1e-8, "enumeration minimum != bound at L=%d" % L)
    ck(len(arg) == 2, "expected exactly 2 minimising q (up to global flip) at L=%d, got %d" % (L, len(arg)))
    print("   L=%2d min=%.10f chain=%.10f minimisers(q0=+)=%d" % (L, best, chain_nonA, len(arg)))
    if L == 18: ck(abs(best - 697.2194902789) < 1e-9, "L=18 697.2194902789")

print("5. dropping R2: uncovered-pivot families found by the exact decision (data from supp/)")
# (mask lo, hi, Y) lists realizable over C with n = L fields-1; L=4 and L=6, cost below chain
FAM = {
 4: [([(0, 1, (0,)), (1, 2, (2,)), (1, 3, (3,))], 3.43957),
     ([(0, 1, (0,)), (1, 2, (2,)), (0, 3, (3,))], 0.43858),
     ([(1, 2, (1,)), (2, 3, (3,)), (0, 2, (0,))], 3.43957),
     ([(1, 2, (1,)), (2, 3, (3,)), (0, 3, (0,))], 0.43858)],
 6: [([(1, 2, (1,)), (2, 3, (3,)), (0, 2, (0,)), (2, 4, (4,)), (2, 5, (5,))], 0.43858),
     ([(2, 3, (2,)), (3, 4, (4,)), (1, 3, (1,)), (3, 5, (5,)), (0, 3, (0,))], 0.43858)]}
for L, lst in FAM.items():
    g = L // 2
    chain_nonA = sum(fcost(lo, hi, Y) for lo, hi, Y in chain_fields(g, g))
    for fs, sv in lst:
        cov = set(s for _, _, Y in fs for s in Y)
        unc = [s for s in range(L) if s not in cov]
        saving = chain_nonA - sum(fcost(lo, hi, Y) for lo, hi, Y in fs)
        ck(len(fs) == L - 1 and len(unc) == 1, "family shape L=%d" % L)
        ck(abs(saving - sv) < 6e-6, "saving L=%d %s: %.5f vs %.5f" % (L, fs, saving, sv))
        print("   L=%d fields=%d uncovered site=%s saving vs chain = %.5f" % (L, len(fs), unc, saving))
# the logs in supp/ must contain these families as REAL
here = os.path.dirname(os.path.abspath(__file__))
for L, name in ((4, "r2test_dec4.out"), (6, "r2test_dec6.out")):
    txt = open(os.path.join(here, "supp", name)).read()
    real = [ln for ln in txt.splitlines() if " REAL " in ln]
    for fs, sv in FAM[L]:
        ck(any(str(fs).replace("[", "[", 1) in ln or str(fs) in ln for ln in real), "family absent from log %s: %s" % (name, fs))
    n0 = [ln for ln in real if ln.startswith("-0.0 ") or ln.startswith("0.0 ")]
    print("   %s: %d realizable lines, %d at exactly the chain cost (chain and twin)" % (name, len(real), len(n0)))

print("FAILURES:", len(fails))
if fails: sys.exit(1)
print("PASS_P104_ROOT_CHAIN_OPTIMALITY")
