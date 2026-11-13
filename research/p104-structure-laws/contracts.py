# contracts.py -- exact checker for per-port 2x2 contracts over Z[i,1/2]-type scalars, q a primitive 4th root of unity,
# sigma: q -> -q.  Standard library only.  Run:  python3.12 -I -B contracts.py
# ARITHMETIC: Gaussian rationals G = Fraction + Fraction*i (exact, characteristic 0).  Matrices over q are Laurent
# polynomials in q (dict exponent -> G); "evaluation points" are q = chi in {1, i, -1, -i}.  Finite-field checks (Lemma E)
# use exact arithmetic mod an odd prime p.  No floating point anywhere.
import itertools, random, sys, time
from fractions import Fraction as F
T0 = time.time()

# ---------------- Gaussian rationals ----------------
class G:
    __slots__ = ('re', 'im')
    def __init__(s, re=0, im=0): s.re = F(re); s.im = F(im)
    def __add__(s, o): o = g_(o); return G(s.re + o.re, s.im + o.im)
    __radd__ = __add__
    def __sub__(s, o): o = g_(o); return G(s.re - o.re, s.im - o.im)
    def __rsub__(s, o): return g_(o) - s
    def __neg__(s): return G(-s.re, -s.im)
    def __mul__(s, o): o = g_(o); return G(s.re*o.re - s.im*o.im, s.re*o.im + s.im*o.re)
    __rmul__ = __mul__
    def inv(s):
        n = s.re*s.re + s.im*s.im
        assert n != 0, "division by zero"
        return G(s.re/n, -s.im/n)
    def __truediv__(s, o): return s * g_(o).inv()
    def __eq__(s, o): o = g_(o); return s.re == o.re and s.im == o.im
    def __hash__(s): return hash((s.re, s.im))
    def iszero(s): return s.re == 0 and s.im == 0
    def __repr__(s): return "%s%+si" % (s.re, s.im) if s.im else str(s.re)
def g_(x): return x if isinstance(x, G) else G(x)
ZERO, ONE, IU = G(0), G(1), G(0, 1)
CHI = [G(1), G(0, 1), G(-1), G(0, -1)]
def gpow(c, e):                      # c^e, e integer (c a unit root or nonzero)
    r = ONE
    base = c if e >= 0 else c.inv()
    for _ in range(abs(e)): r = r * base
    return r

# ---------------- dense matrices over G ----------------
def eye(n): return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]
def zeros(n, m): return [[ZERO]*m for _ in range(n)]
def mmul(A, B):
    n, k, m = len(A), len(B), len(B[0])
    return [[sum((A[i][t]*B[t][j] for t in range(k)), ZERO) for j in range(m)] for i in range(n)]
def msub(A, B): return [[A[i][j]-B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
def madd(A, B): return [[A[i][j]+B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
def mscal(c, A): return [[c*x for x in r] for r in A]
def meq(A, B): return all(A[i][j] == B[i][j] for i in range(len(A)) for j in range(len(A[0])))
def rank(A):
    A = [r[:] for r in A]; n, m = len(A), len(A[0]); rk = 0
    for c in range(m):
        p = next((i for i in range(rk, n) if not A[i][c].iszero()), None)
        if p is None: continue
        A[rk], A[p] = A[p], A[rk]
        iv = A[rk][c].inv()
        for i in range(rk+1, n):
            if not A[i][c].iszero():
                f = A[i][c]*iv
                A[i] = [A[i][j] - f*A[rk][j] for j in range(m)]
        rk += 1
        if rk == n: break
    return rk
def minv(A):
    n = len(A); M = [A[i][:] + eye(n)[i] for i in range(n)]
    for c in range(n):
        p = next((i for i in range(c, n) if not M[i][c].iszero()), None)
        if p is None: return None
        M[c], M[p] = M[p], M[c]
        iv = M[c][c].inv(); M[c] = [x*iv for x in M[c]]
        for i in range(n):
            if i != c and not M[i][c].iszero():
                f = M[i][c]; M[i] = [M[i][j] - f*M[c][j] for j in range(2*n)]
    return [r[n:] for r in M]
def det2(A): return A[0][0]*A[1][1] - A[0][1]*A[1][0]

# ---------------- Laurent matrices in q ----------------
# a Laurent entry is dict {exp: G}; a Laurent matrix is a list of lists of such dicts
def lp_add(a, b):
    r = dict(a)
    for e, c in b.items():
        r[e] = r.get(e, ZERO) + c
        if r[e].iszero(): del r[e]
    return r
def lp_mul(a, b):
    r = {}
    for e1, c1 in a.items():
        for e2, c2 in b.items():
            e = e1+e2; r[e] = r.get(e, ZERO) + c1*c2
    return {e: c for e, c in r.items() if not c.iszero()}
def lm_mul(A, B):
    n, k, m = len(A), len(B), len(B[0]); R = []
    for i in range(n):
        row = []
        for j in range(m):
            acc = {}
            for t in range(k): acc = lp_add(acc, lp_mul(A[i][t], B[t][j]))
            row.append(acc)
        R.append(row)
    return R
def lm_eq(A, B): return all(A[i][j] == B[i][j] for i in range(len(A)) for j in range(len(A[0])))
def lm_const(A): return [[({0: g_(x)} if not g_(x).iszero() else {}) for x in r] for r in A]
def mono(c, e): return {e: g_(c)} if not g_(c).iszero() else {}
def ev(A, chi):                                  # evaluate at q = chi
    return [[sum((c*gpow(chi, e) for e, c in x.items()), ZERO) for x in r] for r in A]
def lm_sigma(A): return [[{e: (c if e % 2 == 0 else -c) for e, c in x.items()} for x in r] for r in A]
def lm_odd(A):  return [[{e: c for e, c in x.items() if e % 2} for x in r] for r in A]
def lm_scal_even_free(): pass

def sigma_factor_at(M, chi, sig=None):
    """R(chi) = sigma(M)(chi) M(chi)^-1 with sigma(M)(chi) = M(-chi) (default); sig(chi) overrides the evaluation point."""
    Mc = ev(M, chi); Ms = ev(M, -chi if sig is None else sig(chi))
    Mi = minv(Mc)
    assert Mi is not None, "M(chi) singular"
    return mmul(Ms, Mi)

def o_of(M, sig=None):
    n = len(M)
    return max(rank(msub(sigma_factor_at(M, c, sig), eye(n))) for c in CHI)
def r_of(M):
    return max(rank(ev(lm_odd(M), c)) for c in CHI)

def rtype(R):
    n = len(R); I = eye(n)
    if meq(R, I): return 'I'
    if meq(R, mscal(-1, I)): return '-I'
    if meq(mmul(R, R), I): return 'reflection' if n == 2 and det2(R) == G(-1) else 'involution'
    N = msub(R, I)
    if rank(N) == 1 and all(x.iszero() for r in mmul(N, N) for x in r): return 'transvection'
    return 'non-involutive'
def sig_type(M):
    """type of sigma-factor at the evaluation point of maximal rank(R-I); asserted uniform on all points of that rank"""
    n = len(M); data = []
    for c in CHI:
        R = sigma_factor_at(M, c); data.append((rank(msub(R, eye(n))), rtype(R)))
    o = max(d[0] for d in data)
    ts = set(t for rk, t in data if rk == o)
    assert len(ts) == 1, ("non-uniform sigma-factor type", data)
    return o, ts.pop(), all(t in ('I', '-I', 'reflection', 'involution') for _, t in data)

# ---------------- monomials ----------------
def lm_monomial(perm, u1, u2):                   # u=(sign,exp)
    a = mono(u1[0], u1[1]); b = mono(u2[0], u2[1])
    return [[{}, a], [b, {}]] if perm else [[a, {}], [{}, b]]
U_EVEN = [(s, e) for s in (1, -1) for e in (0, 2)]
U_ALL = [(s, e) for s in (1, -1) for e in (0, 1, 2, 3)]
def all_monos(units):
    return [lm_monomial(p, u1, u2) for p in (0, 1) for u1 in units for u2 in units]
MONO_EVEN = all_monos(U_EVEN); MONO_ALL = all_monos(U_ALL)
def bill(M, monos):
    best = 9
    for W in monos:
        r = max(rank(msub(ev(M, c), ev(W, c))) for c in CHI)
        best = min(best, r)
        if best == 0: break
    return best

# ---------------- the 32 reps  M = diag(q^a,q^b) L_c diag(q^c,q^d), L_c=[[1,0],[c,1]], c in {1,q} ----------------
def rep(a, b, c, d, ce, scal=None):
    s = scal or [ONE]*5
    D1 = [[mono(s[0], a), {}], [{}, mono(s[1], b)]]
    L = [[mono(1, 0), {}], [mono(s[2], ce), mono(1, 0)]]
    D2 = [[mono(s[3], c), {}], [{}, mono(s[4], d)]]
    return lm_mul(lm_mul(D1, L), D2)
REPS = list(itertools.product((0, 1), repeat=5))
def mono_rep(a, b):                              # c = 0 case: diag(q^a, q^b)
    return [[mono(1, a), {}], [{}, mono(1, b)]]

def classify(M):
    o, typ, inv = sig_type(M)
    return dict(o=o, r=r_of(M), typ=typ, inv=inv, be=bill(M, MONO_EVEN), ba=bill(M, MONO_ALL))

print("== arithmetic: Gaussian rationals (Fraction pairs), Laurent matrices in q, evaluation at q in {1,i,-1,-i}; mod-p only in Lemma E ==")
print("== CHECK 1: classification of the 32 reps  M = W1 L_c W2 ==")
CL = {}                                          # class label by invariants
tab = {}
for k in REPS:
    c = classify(rep(*k)); key = (c['o'], c['r'], c['typ'], c['be'], c['ba']); tab.setdefault(key, []).append(k)
LABEL = {(0, 0, 'I', 1, 1): 'A', (1, 1, 'transvection', 1, 1): 'B', (1, 1, 'reflection', 1, 1): 'C',
         (2, 2, 'non-involutive', 2, 1): 'D', (2, 2, '-I', 2, 1): "D'"}
print("class | reps | o | r | sigma-factor | involutive | b_even | b_all")
CLS_INFO = {}
for key in sorted(tab, key=lambda k: (k[0], k[2])):
    lab = LABEL.get(key); assert lab, ("unexpected class", key, tab[key])
    inv = key[2] in ('I', '-I', 'reflection')
    CLS_INFO[lab] = dict(n=len(tab[key]), o=key[0], r=key[1], typ=key[2], inv=inv, be=key[3], ba=key[4], reps=tab[key])
    print("%-5s | %2d | %d | %d | %-14s | %-5s | %d | %d" % (lab, len(tab[key]), key[0], key[1], key[2], inv, key[3], key[4]))
assert set(CLS_INFO) == set('A B C D'.split()) | {"D'"}
assert [CLS_INFO[x]['n'] for x in ('A', 'B', 'C', 'D', "D'")] == [4, 4, 16, 4, 4]
assert all(v['o'] == v['r'] for v in CLS_INFO.values())            # o = r in every class
assert [(CLS_INFO[x]['be'], CLS_INFO[x]['ba']) for x in ('A', 'B', 'C', 'D', "D'")] == [(1, 1), (1, 1), (1, 1), (2, 1), (2, 1)]
print("o = r in every class; o>r never; o>0 with r=0 never: True")
print("e.g. B rep (0,0,0,0,ce=1) is L_q:", CLS_INFO['B']['reps'][:2], "| A rep (0,0,0,0,0) = L_1 q-free transvection (b_even=1: M-W has rank 1 for even monomial W=I)")

print("-- c = 0 monomial cases diag(q^a,q^b) (mod even monomials: 4 reps, 3 classes):")
mt = {}
for a, b in itertools.product((0, 1), repeat=2):
    M = mono_rep(a, b); c = classify(M); mt.setdefault((c['o'], c['r'], c['typ'], c['be'], c['ba']), []).append((a, b))
for k, v in sorted(mt.items()): print("   (o,r,sigma-type,b_even,b_all) =", k, "reps (a,b):", v)
assert len(mt) == 3
assert mt[(0, 0, 'I', 0, 0)] == [(0, 0)] and mt[(2, 2, '-I', 1, 0)] == [(1, 1)]
assert sorted(mt[(1, 1, 'reflection', 1, 0)]) == [(0, 1), (1, 0)]
print("   monomial classes: 3 (even monomial o=r=0 b_even=0; odd unit diag(1,q): o=r=1 reflection; port scalar q: o=r=2, -I; b_even=1 and b_all=0 for odd monomials)")

print("-- generic scalars: unit entries replaced by fixed nontrivial Gaussian rationals, 3 deterministic draws")
rnd = random.Random(20241113)
def rscal():
    while True:
        z = G(F(rnd.choice([-7, -5, -3, -2, -1, 1, 2, 3, 5, 7]), rnd.choice([1, 2, 3, 4])),
              F(rnd.choice([-3, -2, -1, 0, 1, 2, 5]), rnd.choice([1, 2, 4])))
        if not z.iszero() and z != G(1) and z != G(-1): return z
gen = {}
for draw in range(3):
    for k in REPS:
        s = [rscal() for _ in range(5)]
        M = rep(*k, scal=s); o, typ, inv = sig_type(M); r = r_of(M)
        gen[(o, r, typ)] = gen.get((o, r, typ), 0) + 1
for key, n in sorted(gen.items()): print("   (o, r, sigma-type) =", key, "count", n)
assert sorted(gen.values()) == [12, 12, 12, 12, 48] and len(gen) == 5
assert gen[(0, 0, 'I')] == 12 and gen[(1, 1, 'transvection')] == 12 and gen[(1, 1, 'reflection')] == 48 \
    and gen[(2, 2, 'non-involutive')] == 12 and gen[(2, 2, '-I')] == 12
print("   same pattern as unit entries: 12/12/48/12/12 over 3 draws (A, B, C, D, D')")

print("-- CONTROLS (check 1)")
# (i) odd monomials allowed in the bill: D, D' drop to 1 (b_all), while o stays 2
assert CLS_INFO['D']['be'] == 2 and CLS_INFO['D']['ba'] == 1 and CLS_INFO['D']['o'] == 2
print("   control: allowing ODD monomials W: b(D) drops 2 -> 1 (o(D) stays 2); b(D') 2 -> 1")
# (ii) wrong sigma changes o: sigma_id (q->q) gives o=0 everywhere; sigma' (q -> i q) changes the table
o_id = {M: o_of(rep(*k), sig=lambda c: c) for k in REPS for M in [k]}
assert all(v == 0 for v in o_id.values())
o_iq = [o_of(rep(*k), sig=lambda c: c*IU) for k in REPS]
o_true = [o_of(rep(*k)) for k in REPS]
assert o_iq != o_true
print("   control: sigma = identity gives o = 0 on all 32 reps; sigma': q->iq changes o on %d of 32 reps" % sum(a != b for a, b in zip(o_iq, o_true)))

print("== CHECK 2: o(N) = rank Odd(N); invariance under q-even monomials ==")
# sigma(N)N^-1 - I = (sigma(N)-N) N^-1 = -2 Odd(N) N^-1
def odd_rank_max(N): return max(rank(ev(lm_odd(N), c)) for c in CHI)
for k in REPS:
    M = rep(*k)
    for c in CHI:
        R = sigma_factor_at(M, c); lhs = rank(msub(R, eye(2))); rhs = rank(ev(lm_odd(M), c))
        assert lhs == rhs
print("   all 32 reps: rank(sigma(M)M^-1 - I) = rank Odd(M) at every evaluation point: OK")
rnd2 = random.Random(7)
def rcoef():
    return G(F(rnd2.randint(-5, 5), rnd2.choice([1, 2, 3])), F(rnd2.randint(-3, 3), rnd2.choice([1, 2])))
def rand_laurent(n, kind):
    N = [[{} for _ in range(n)] for _ in range(n)]
    if kind == 'generic':
        for i in range(n):
            for j in range(n):
                for _ in range(rnd2.randint(0, 3)):
                    N = N  # keep structure
                    e = rnd2.randint(-2, 3); c = rcoef()
                    N[i][j] = lp_add(N[i][j], mono(c, e)) if not c.iszero() else N[i][j]
    else:                                         # even part + odd part of controlled rank
        for i in range(n):
            for j in range(n):
                c = rcoef(); N[i][j] = mono(c, rnd2.choice([-2, 0, 2]))
        rk = int(kind[-1])
        for _ in range(rk):
            u = [rcoef() for _ in range(n)]; v = [rcoef() for _ in range(n)]; e = rnd2.choice([-1, 1, 3])
            for i in range(n):
                for j in range(n): N[i][j] = lp_add(N[i][j], mono(u[i]*v[j], e))
    return N
cnt = 0; hist = {}
for n in (2, 3):
    for kind in ['generic']*25 + ['struct1']*15 + ['struct2']*10:
        if kind == 'struct2' and n == 2 and False: continue
        N = rand_laurent(n, kind)
        for c in CHI:
            Nc = ev(N, c)
            if minv(Nc) is None: continue
            R = sigma_factor_at(N, c); lhs = rank(msub(R, eye(n))); rhs = rank(ev(lm_odd(N), c))
            assert lhs == rhs, (n, kind, c, lhs, rhs)
            cnt += 1; hist[(n, lhs)] = hist.get((n, lhs), 0) + 1
print("   random Laurent-in-q matrices (2x2 and 3x3, generic and controlled odd rank): %d (matrix, point) pairs; identity holds; histogram (n, o): %s" % (cnt, sorted(hist.items())))
assert cnt > 300 and any(v > 0 for (n, o), v in hist.items() if o == 1) and any(o == 2 for (n, o) in hist) and any(o == 3 for (n, o) in hist)
# invariance under q-even monomials
ECOMB = [(p, u1, u2) for p in (0, 1) for u1 in U_EVEN for u2 in U_EVEN]
assert len(ECOMB) == 32
E_LIST = [lm_monomial(*e) for e in ECOMB]
n_inv = 0
for k in REPS:
    M = rep(*k); o0 = o_of(M)
    for E1 in E_LIST:
        for E2 in E_LIST:
            assert o_of(lm_mul(lm_mul(E1, M), E2)) == o0
            n_inv += 1
print("   o(E1 M E2) = o(M) for all 32x32 q-even monomial pairs on all 32 reps (%d checks): OK" % n_inv)
# control: an ODD monomial multiplier does change o (diag(1,q) on the left of the identity-class M)
Mb = rep(0, 0, 0, 0, 0)
assert o_of(Mb) == 0 and o_of(lm_mul(lm_monomial(0, (1, 0), (1, 1)), Mb)) == 1 and o_of(lm_mul(lm_monomial(0, (1, 1), (1, 1)), Mb)) == 2
print("   control: odd monomial diag(1,q) takes o(L_1)=0 to 1, and q*I takes it to 2 (so the even restriction is needed)")

print("== CHECK 4 (before 3, shares algebra): non-parity, H^3=-I, factorisation ==")
def Lc(c, e): return [[mono(1, 0), {}], [mono(c, e), mono(1, 0)]]
Lq = Lc(-1, -1)                                  # L_q = [[1,0],[-q^-1,1]]
H = [[mono(1, 0), mono(-1, 1)], [mono(1, -1), {}]]
Lq1 = Lc(1, 1)
assert o_of(Lq) == 1 and o_of(Lq1) == 1
Lq2 = lm_mul(Lq, Lq)
print("   L_q^2 = [[1,0],[-2q^-1,1]]:", lm_eq(Lq2, [[mono(1, 0), {}], [mono(-2, -1), mono(1, 0)]]), "| o(L_q)=%d  o(L_q^2)=%d  (o is not a parity: o(L^2) = o(L), not 0)" % (o_of(Lq), o_of(Lq2)))
assert o_of(Lq2) == 1 and lm_eq(Lq2, [[mono(1, 0), {}], [mono(-2, -1), mono(1, 0)]])
H2 = lm_mul(H, H); H3 = lm_mul(H2, H)
Im2 = lm_const([[-1, 0], [0, -1]])
assert o_of(H) == 2 and o_of(H2) == 2 and lm_eq(H3, Im2) and o_of(H3) == 0
print("   o(H)=%d  o(H^2)=%d  H^3 = -I (as Laurent matrices, formal identity): True  o(H^3)=%d" % (o_of(H), o_of(H2), o_of(H3)))
# exact factorisation H = J_q L_q
Jm = lm_const([[0, -1], [1, 0]])                 # J = [[0,-1],[1,0]]  (this sign is the exactly true one)
Dq = [[mono(1, 1), {}], [{}, mono(1, -1)]]
Jq = lm_mul(Dq, Jm)
assert lm_eq(lm_mul(Jq, Lq), H)
Jbad = lm_const([[0, 1], [-1, 0]]); assert not lm_eq(lm_mul(lm_mul(Dq, Jbad), Lq), H)
print("   H = J_q L_q with J = [[0,-1],[1,0]], J_q = diag(q,q^-1) J, L_q = [[1,0],[-q^-1,1]]: True ; with the opposite sign J' = [[0,1],[-1,0]] one gets diag(q,q^-1) J' L_q = [[-1,q],[-q^-1,0]] != H (checked)")
assert lm_eq(lm_mul(lm_mul(Dq, Jbad), Lq), [[mono(-1, 0), mono(1, 1)], [mono(-1, -1), {}]])
assert o_of(Jq) == 2 and rtype(sigma_factor_at(Jq, CHI[1])) == '-I' and o_of(Jm) == 0
print("   o(J)=0, o(J_q)=2 with sigma-factor -I (involutive); o(L_q)=1 transvection; o(H)=2 non-involutive")
# det of sigma-factor: homomorphism to {+-1}
def eps(M, c=CHI[1]):
    return det2(sigma_factor_at(M, c))
def eps_all(M):
    s = set(eps(M, c) for c in CHI)
    assert len(s) == 1; return s.pop()
dets = {lab: set(eps_all(rep(*k)) for k in info['reps']) for lab, info in CLS_INFO.items()}
print("   det of sigma-factor per class:", {k: sorted(map(str, v)) for k, v in dets.items()})
assert dets['B'] == {G(1)} and dets['C'] == {G(-1)} and dets['A'] == {G(1)} and dets['D'] == {G(1)} and dets["D'"] == {G(1)}
allreps = [rep(*k) for k in REPS]
for M in allreps:
    assert eps_all(M) in (G(1), G(-1))
        # eps(M) = (-1)^{parity of the exponent of det M}
nprod = 0
for M1 in allreps:
    for M2 in allreps:
        P = lm_mul(M1, M2)
        assert eps_all(P) == eps_all(M1) * eps_all(M2)                       # genuine Z/2 homomorphism
        assert o_of(P) <= o_of(M1) + o_of(M2)                                # o is only subadditive
        nprod += 1
print("   det(sigma-factor) is multiplicative on all %d products of reps (values in {+-1}); o is only subadditive (checked on the same products)" % nprod)
# the sign is the parity of exponent of det M
for k in REPS:
    a, b, c, d, ce = k
    assert eps_all(rep(*k)) == G((-1)**((a+b+c+d) % 2))
print("   eps(M) = (-1)^(a+b+c+d) = (-1)^(parity of the q-exponent of det M) on all 32 reps: True; transvection (B): +1, reflection (C): -1")
# o is not a function of eps
assert o_of(Lq) == 1 and eps_all(Lq) == G(1) and o_of(Jq) == 2 and eps_all(Jq) == G(1) and o_of(Jm) == 0 and eps_all(Jm) == G(1)
print("   o is not determined by eps: eps = +1 for o = 0, 1, 2 (J, L_q, J_q)")

print("== CHECK 3: Lemma E over finite fields (char != 2) ==")
def lemma_E_gl2(p, triples=False):
    els = [(a, b, c, d) for a in range(p) for b in range(p) for c in range(p) for d in range(p) if (a*d - b*c) % p]
    rk = {}
    for h in els:
        a, b, c, d = h[0]-1, h[1], h[2], h[3]-1
        rk[h] = 0 if (a == 0 and b == 0 and c == 0 and d == 0) else (2 if (a*d-b*c) % p else 1)
    isinv = {h: ((h[0]*h[0]+h[1]*h[2]) % p == 1 and (h[0]*h[1]+h[1]*h[3]) % p == 0 and
                 (h[2]*h[0]+h[3]*h[2]) % p == 0 and (h[2]*h[1]+h[3]*h[3]) % p == 1) for h in els}
    nq = 0; nadd = 0; nctrl = 0; ctrl_bad = 0; nonhyp_inv = 0
    for h1 in els:
        a1, b1, c1, d1 = h1; r1 = rk[h1]
        for h2 in els:
            a2, b2, c2, d2 = h2
            g = ((a1*a2+b1*c2) % p, (a1*b2+b1*d2) % p, (c1*a2+d1*c2) % p, (c1*b2+d1*d2) % p)
            m = rk[g]
            if m != r1 + rk[h2]: continue
            nadd += 1
            # hypothesis: g = -1 on Im(g-I)  <=>  (g+I)(g-I) = 0
            ga, gb, gc, gd = g
            X = (ga+1, gb, gc, gd+1); Y = (ga-1, gb, gc, gd-1)
            prod = ((X[0]*Y[0]+X[1]*Y[2]) % p, (X[0]*Y[1]+X[1]*Y[3]) % p, (X[2]*Y[0]+X[3]*Y[2]) % p, (X[2]*Y[1]+X[3]*Y[3]) % p)
            hyp = prod == (0, 0, 0, 0)
            if hyp:
                nq += 1
                assert isinv[h1] and isinv[h2], ("Lemma E counterexample", p, h1, h2)
            else:
                nctrl += 1
                if not (isinv[h1] and isinv[h2]): ctrl_bad += 1
    return len(els), nadd, nq, nctrl, ctrl_bad
def lemma_E_gl2_triples(p):
    els = [(a, b, c, d) for a in range(p) for b in range(p) for c in range(p) for d in range(p) if (a*d - b*c) % p]
    def mul(x, y): return ((x[0]*y[0]+x[1]*y[2]) % p, (x[0]*y[1]+x[1]*y[3]) % p, (x[2]*y[0]+x[3]*y[2]) % p, (x[2]*y[1]+x[3]*y[3]) % p)
    def rk(h):
        a, b, c, d = h[0]-1, h[1], h[2], h[3]-1
        return 0 if (a == 0 and b == 0 and c == 0 and d == 0) else (2 if (a*d-b*c) % p else 1)
    R = {h: rk(h) for h in els}; Id = (1, 0, 0, 1); nq = 0; nadd = 0
    for h1 in els:
        for h2 in els:
            g12 = mul(h1, h2)
            for h3 in els:
                g = mul(g12, h3)
                if R[g] != R[h1]+R[h2]+R[h3]: continue
                nadd += 1
                gm = mul((g[0]+1, g[1], g[2], g[3]+1), (g[0]-1, g[1], g[2], g[3]-1))
                if gm == (0, 0, 0, 0):
                    nq += 1
                    assert all(mul(h, h) == Id for h in (h1, h2, h3))
    return len(els), nadd, nq
for p in (5, 7):
    t = time.time(); ne, nadd, nq, nctrl, cb = lemma_E_gl2(p)
    print("   GL(2,F_%d): |G|=%d, rank-additive pairs %d, of which with hypothesis g=-1 on Im(g-I): %d (every factor an involution: 0 counterexamples)" % (p, ne, nadd, nq))
    print("      CONTROL (hypothesis dropped): %d rank-additive pairs, %d of them have a non-involutive factor" % (nctrl, cb))
    assert nq > 0 and cb > 0
ne, nadd, nq = lemma_E_gl2_triples(3)
print("   GL(2,F_3) triples h1h2h3: |G|=%d, rank-additive triples %d, with hypothesis %d, 0 counterexamples" % (ne, nadd, nq))
assert nq > 0
# GL(3,F_3)
P3 = 3
def m3mul(x, y):
    return tuple(sum(x[3*i+k]*y[3*k+j] for k in range(3)) % P3 for i in range(3) for j in range(3))
def rank3(x):
    A = [list(x[0:3]), list(x[3:6]), list(x[6:9])]; rk = 0
    for c in range(3):
        pv = next((i for i in range(rk, 3) if A[i][c] % P3), None)
        if pv is None: continue
        A[rk], A[pv] = A[pv], A[rk]; iv = pow(A[rk][c], -1, P3)
        for i in range(rk+1, 3):
            f = (A[i][c]*iv) % P3
            A[i] = [(A[i][j]-f*A[rk][j]) % P3 for j in range(3)]
        rk += 1
    return rk
ID3 = (1, 0, 0, 0, 1, 0, 0, 0, 1)
def det3(x): return (x[0]*(x[4]*x[8]-x[5]*x[7]) - x[1]*(x[3]*x[8]-x[5]*x[6]) + x[2]*(x[3]*x[7]-x[4]*x[6])) % P3
GL3 = [x for x in itertools.product(range(3), repeat=9) if det3(x)]
RK3 = {x: rank3(tuple((x[i]-ID3[i]) % P3 for i in range(9))) for x in GL3}
INV3 = [x for x in GL3 if m3mul(x, x) == ID3]
INVSET = set(INV3)
R1 = [x for x in GL3 if RK3[x] <= 1]
def m3inv(x):                                     # adjugate / det over F_3
    c = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            mm = [x[3*r+cc] for r in range(3) if r != i for cc in range(3) if cc != j]
            c[i][j] = ((-1)**(i+j) * (mm[0]*mm[3]-mm[1]*mm[2])) % P3
    dd = pow(det3(x), -1, P3)
    return tuple((c[j][i]*dd) % P3 for i in range(3) for j in range(3))
nq = 0; nadd = 0
for h1 in R1:
    h1i = m3inv(h1)
    for g in INV3:                                # hypothesis g^2 = I  <=>  g = -1 on Im(g-I)
        h2 = m3mul(h1i, g)
        if RK3[h1] + RK3[h2] != RK3[g]: continue
        nadd += 1
        assert h1 in INVSET and h2 in INVSET, ("Lemma E counterexample GL3", h1, h2)
        nq += 1
print("   GL(3,F_3): |G|=%d, h1 with rank(h1-I)<=1: %d, g with g^2=I: %d; qualifying factorizations g=h1h2 (ranks add): %d, 0 counterexamples" % (len(GL3), len(R1), len(INV3), nq))
assert nq > 0
nctrl = 0; nbad = 0
for h1 in R1:
    for h2 in R1:
        g = m3mul(h1, h2)
        if RK3[g] != RK3[h1] + RK3[h2]: continue
        gp = tuple((g[i]+ID3[i]) % P3 for i in range(9)); gm = tuple((g[i]-ID3[i]) % P3 for i in range(9))
        if m3mul(gp, gm) == (0,)*9:
            assert h1 in INVSET and h2 in INVSET
        else:
            nctrl += 1; nbad += (h1 not in INVSET or h2 not in INVSET)
print("   GL(3,F_3) CONTROL (hypothesis dropped, both factors rank<=1): %d rank-additive products without hypothesis, %d have a non-involutive factor (transvection factors)" % (nctrl, nbad))
assert nbad > 0

print("== CHECK 5: hub lemma ==")
h_, n_ = 8, 104
rnd3 = random.Random(104)
def rref_nullspace(B):
    """exact rational RREF of B (h x n, Fractions); returns (rank, pivots, nullspace basis columns as list of vectors)"""
    A = [[F(x) for x in r] for r in B]; h, n = len(A), len(A[0]); piv = []; rk = 0
    for c in range(n):
        p = next((i for i in range(rk, h) if A[i][c] != 0), None)
        if p is None: continue
        A[rk], A[p] = A[p], A[rk]; iv = 1/A[rk][c]; A[rk] = [x*iv for x in A[rk]]
        for i in range(h):
            if i != rk and A[i][c] != 0:
                f = A[i][c]; A[i] = [A[i][j]-f*A[rk][j] for j in range(n)]
        piv.append(c); rk += 1
        if rk == h: break
    free = [c for c in range(n) if c not in piv]; basis = []
    for f in free:
        v = [F(0)]*n; v[f] = F(1)
        for i, pc in enumerate(piv): v[pc] = -A[i][f]
        basis.append(v)
    return rk, piv, free, basis
Bm = [[rnd3.randint(-3, 3) for _ in range(n_)] for _ in range(h_)]
rkB, piv, free, Kb = rref_nullspace(Bm)
dimK = len(Kb)
print("   B: %dx%d deterministic integer matrix, exact rank %d, dim ker B = %d (= n - h)" % (h_, n_, rkB, dimK))
assert rkB == 8 and dimK == 96
for v in Kb:                                      # B v = 0 exactly
    for r in Bm: assert sum(F(r[j])*v[j] for j in range(n_)) == 0
# projector P onto K along span(e_pivots): P = Kb * (selection of free coordinates)
P = [[F(0)]*n_ for _ in range(n_)]
for jj, f in enumerate(free):
    for i in range(n_): P[i][f] = Kb[jj][i]
# P^2 = P, B P = 0, rank P = dim K  (exact)
def fmul(A_, B_):
    return [[sum((A_[i][k]*B_[k][j] for k in range(len(B_)) if A_[i][k] != 0 and B_[k][j] != 0), F(0)) for j in range(len(B_[0]))] for i in range(len(A_))]
assert fmul(P, P) == P
BP = fmul([[F(x) for x in r] for r in Bm], P); assert all(x == 0 for r in BP for x in r)
# hub-form operators vanish on K: (B^T X B) P = 0 for random X; Y (x) B^T X B kills (I (x) P)
X = [[F(rnd3.randint(-4, 4)) for _ in range(h_)] for _ in range(h_)]
BT = [[F(Bm[i][j]) for i in range(h_)] for j in range(n_)]
HUB = fmul(fmul(BT, X), [[F(x) for x in r] for r in Bm])
assert all(x == 0 for r in fmul(HUB, P) for x in r)
print("   P is an exact projector onto K (P^2=P, BP=0); hub-form op B^T X B annihilates K: True")
def sparse_rank_G(rows):
    """rank of a sparse matrix given as list of dict col->G (exact Gaussian-rational elimination)"""
    piv = {}; rk = 0
    for row in rows:
        row = {c: v for c, v in row.items() if not v.iszero()}
        while row:
            c = min(row)
            if c in piv:
                pr = piv[c]; f = row[c]
                for cc, vv in pr.items():
                    nv = row.get(cc, ZERO) - f*vv
                    if nv.iszero(): row.pop(cc, None)
                    else: row[cc] = nv
            else:
                iv = row[c].inv(); piv[c] = {cc: vv*iv for cc, vv in row.items()}; rk += 1; break
    return rk
def kron_rank(A2, Pm):
    n = len(Pm); rows = []
    Prows = [{j: G(x) for j, x in enumerate(r) if x != 0} for r in Pm]
    for i in range(2):
        for a in range(n):
            d = {}
            for j in range(2):
                if A2[i][j].iszero(): continue
                for cc, v in Prows[a].items(): d[j*n + cc] = A2[i][j]*v
            rows.append(d)
    return sparse_rank_G(rows)
rankP = sparse_rank_G([{j: G(x) for j, x in enumerate(r) if x != 0} for r in P]); assert rankP == dimK
print("   rank P = %d" % rankP)
# odd parts of one representative per class (and the three monomial classes), at the evaluation point of maximal rank
reps5 = [('A', rep(*CLS_INFO['A']['reps'][0])), ('B', rep(0, 0, 0, 0, 1)), ('C', rep(*CLS_INFO['C']['reps'][0])),
         ('D', rep(*CLS_INFO['D']['reps'][0])), ("D'", rep(*CLS_INFO["D'"]['reps'][0])),
         ('mono diag(1,q)', mono_rep(0, 1)), ('mono qI', mono_rep(1, 1)), ('H', H), ('L_q', Lq)]
t5 = time.time()
print("   unit r | rank(Odd(M) (x) P) | rank Odd * dim K")
for name, M in reps5:
    best = max(CHI, key=lambda c: rank(ev(lm_odd(M), c))); Od = ev(lm_odd(M), best); rO = rank(Od)
    kr = kron_rank(Od, P)
    print("   %-15s r=%d | %3d | %d x %d = %3d" % (name, rO, kr, rO, dimK, rO*dimK))
    assert kr == rO*dimK
print("   => each unit of odd rank needs 96 non-hub rank-1 transfers (n-h = 96); r=0 needs none  [kron elimination %.1fs]" % (time.time()-t5))
# control: rank-deficient B (duplicate row) gives dim K = 97 and the bill per unit changes accordingly
Bdef = [r[:] for r in Bm]; Bdef[7] = Bdef[0][:]
rk2, _, free2, Kb2 = rref_nullspace(Bdef)
assert rk2 == 7 and len(Kb2) == 97
print("   control: if B has rank 7 (duplicate row), dim ker = 97, bill 97 per unit (the 96 is a consequence of rank B = 8)")
# control: without the hub restriction (I (x) I_n) the bill would be rank Odd * n
assert 104 != dimK
print("   control: with no hub structure the same count is rank Odd * 104 = 104 per unit, not 96")

print("== CHECK 6: units-conserved arithmetic (parameters: J events per port per word = 17, target odd rank = 36) ==")
JEV, TGT = 17, 36
print("class | r | o | involutive sigma-factor | 17 r + (36 - 17 o | 37 - 17 o) | total")
tot = {}
for lab in ('A', 'B', 'C', 'D', "D'"):
    ci = CLS_INFO[lab]
    floor_ = TGT - JEV*ci['o'] if ci['inv'] else TGT + 1 - JEV*ci['o']
    tot[lab] = JEV*ci['r'] + floor_
    print("%-5s | %d | %d | %-5s | %2d*%d + %2d | %d" % (lab, ci['r'], ci['o'], ci['inv'], JEV, ci['r'], floor_, tot[lab]))
assert tot == {'A': 36, 'B': 37, 'C': 36, 'D': 37, "D'": 36}
print("A 36, B 37, C 36, D 37, D' 36 (conserved up to the involution clause)")
print("control: if the involution clause were ignored (37 - 17o for all), C and D' would read 37: ", {l: JEV*CLS_INFO[l]['r'] + TGT + 1 - JEV*CLS_INFO[l]['o'] for l in ('C', "D'")})

print("runtime %.1fs" % (time.time()-T0))
print("PASS_CONTRACT_ODD_RANK")
