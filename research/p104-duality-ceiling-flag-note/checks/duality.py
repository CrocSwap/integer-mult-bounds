"""Theorem G: isotropic transvections in dimension n with product -I  <->  reflections in dimension rho = N - n with product -I.
Exact rational arithmetic, standard library only."""
import itertools, random, sys
from fractions import Fraction as Q
fails = []
def ck(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg, flush=True)
    if not cond: fails.append(msg)
def eye(n): return [[Q(int(i == j)) for j in range(n)] for i in range(n)]
def mm(A, B):
    Bt = list(zip(*B)); return [[sum(a * b for a, b in zip(r, c)) for c in Bt] for r in A]
def rref(M):
    M = [r[:] for r in M]; piv = []; r = 0
    for c in range(len(M[0])):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]; M[r] = [x / pv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(c); r += 1
    return M[:r], piv
def rank(M): return len(rref(M)[0])
def factor(G):
    """rank factorisation G = C R with C (N x r) and R (r x N)"""
    R, piv = rref(G)
    C = [[row[c] for c in piv] for row in G]
    assert mm(C, R) == G
    return C, R
def refl(q, p):   # I - 2 q p^T  (column q, row p), p.q = 1
    n = len(q); return [[Q(int(i == j)) - 2 * q[i] * p[j] for j in range(n)] for i in range(n)]
def transv(x, y):  # I - 2 x y^T
    n = len(x); return [[Q(int(i == j)) - 2 * x[i] * y[j] for j in range(n)] for i in range(n)]
def prod_left(mats, n):
    """T_N ... T_1 for mats = [T_1, ..., T_N]"""
    P = eye(n)
    for T in mats: P = mm(T, P)
    return P
def negI(n): return [[Q(-int(i == j)) for j in range(n)] for i in range(n)]
def dotv(a, b): return sum(x * y for x, y in zip(a, b))

def reflections_to_transvections(qs, ps):
    N = len(qs); rho = len(qs[0])
    Z = [[dotv(ps[i], qs[j]) for j in range(N)] for i in range(N)]
    G = [[(Z[i][j] if i > j else (-Z[i][j] if i < j else Q(0))) for j in range(N)] for i in range(N)]
    Y, X = factor(G)                     # G = Y X, rows y_k of Y, columns x_l of X
    n = len(X)
    xs = [[X[a][k] for a in range(n)] for k in range(N)]; ys = [Y[k] for k in range(N)]
    iso = all(dotv(ys[k], xs[k]) == 0 for k in range(N))
    word = prod_left([transv(xs[k], ys[k]) for k in range(N)], n)
    return n, iso, word == negI(n), (xs, ys), G

def transvections_to_reflections(xs, ys):
    N = len(xs); n = len(xs[0])
    G = [[dotv(ys[k], xs[l]) for l in range(N)] for k in range(N)]
    Z = [[(Q(1) if i == j else (G[i][j] if i > j else -G[i][j])) for j in range(N)] for i in range(N)]
    P, Qt = factor(Z)                    # Z = P Qt, rows p_i of P, columns q_j of Qt
    rho = len(Qt)
    ps = [P[i] for i in range(N)]; qs = [[Qt[a][j] for a in range(rho)] for j in range(N)]
    unit = all(dotv(ps[i], qs[i]) == 1 for i in range(N))
    word = prod_left([refl(qs[i], ps[i]) for i in range(N)], rho)
    return rho, unit, word == negI(rho)

def check_reflection_word(name, qs, ps, expect_n=None):
    N = len(qs); rho = len(qs[0])
    prodR = prod_left([refl(qs[i], ps[i]) for i in range(N)], rho)
    pre = prodR == negI(rho) and all(dotv(ps[i], qs[i]) == 1 for i in range(N))
    n, iso, ok, (xs, ys), G = reflections_to_transvections(qs, ps)
    ck(pre and iso and ok and n == N - rho, f'{name}: N={N}, rho={rho}: reflections with product -I give isotropic transvections in dimension n={n}=N-rho with product -I')
    rho2, unit, ok2 = transvections_to_reflections(xs, ys)
    ck(unit and ok2 and rho2 == rho, f'{name}: and back: the transvection word returns reflections in dimension {rho2} with product -I')

# ---- Coxeter words (w0 = -I): reduced word by greedy length increase, reflections are the inversion roots
def coxeter(name, simple, positive_funcional):
    d = len(simple)
    def s(a):
        aa = dotv(a, a); return [[Q(int(i == j)) - 2 * a[i] * a[j] / aa for j in range(d)] for i in range(d)]
    S = [s(a) for a in simple]
    w = eye(d); betas = []
    while True:
        for i, a in enumerate(simple):
            wa = [sum(w[r][c] * a[c] for c in range(d)) for r in range(d)]
            if positive_funcional(wa) > 0:
                betas.append(wa); w = mm(w, S[i]); break
        else:
            break
    assert w == negI(d), 'w0 is not -I'
    qs = betas; ps = [[x / dotv(b, b) for x in b] for b in betas]
    # product of s_beta_N ... s_beta_1 = w0 = -I with betas in this order
    check_reflection_word(name, qs, ps)
    return len(betas)
def F(vals):
    return lambda v: sum(Q(a) * x for a, x in zip(vals, v))
# D4, B3, F4 in coordinates (rational)
D4 = [[1, -1, 0, 0], [0, 1, -1, 0], [0, 0, 1, -1], [0, 0, 1, 1]]
coxeter('Coxeter D4 w0', [[Q(x) for x in r] for r in D4], F([1000, 100, 10, 1]))
B3 = [[1, -1, 0], [0, 1, -1], [0, 0, 1]]
coxeter('Coxeter B3 w0', [[Q(x) for x in r] for r in B3], F([100, 10, 1]))
F4 = [[0, 1, -1, 0], [0, 0, 1, -1], [0, 0, 0, 1], [Q(1, 2), Q(-1, 2), Q(-1, 2), Q(-1, 2)]]
nF4 = coxeter('Coxeter F4 w0', [[Q(x) for x in r] for r in F4], F([1000, 100, 10, 1]))
ck(nF4 == 24, 'F4 reduced word of w0 has 24 reflections')
# dihedral words for k = 4 (B2), 6 (G2): Cartan realisation in the simple-root basis
def dihedral_cartan(name, c12, c21, N):
    # s1: e1 -> -e1, e2 -> e2 - c21*e1 (row convention on coordinates); build reflections as matrices acting on coordinate vectors
    A = [[Q(-1), Q(-c12)], [Q(0), Q(1)]]       # s1 acts on coords: a1 -> -a1, a2 -> a2 + (-c12... ) use Cartan pairing
    Bm = [[Q(1), Q(0)], [Q(-c21), Q(-1)]]
    return A, Bm
def refl_from_matrix(M):
    d = len(M); R = [[M[i][j] - Q(int(i == j)) for j in range(d)] for i in range(d)]   # M - I = -2 q p^T (rank one)
    r = next(i for i in range(d) if any(R[i][j] != 0 for j in range(d)))
    j0 = next(j for j in range(d) if R[r][j] != 0)
    q = [R[i][j0] for i in range(d)]                    # a column of M - I
    # M - I = q * u^T with u a row; -2 p = u  => p = -u/2 ; check p.q = 1
    u = [R[r][j] / q[r] for j in range(d)]
    p = [-x / 2 for x in u]
    assert refl(q, p) == M, 'not a reflection'
    assert dotv(p, q) == 1
    return q, p
for name, c12, c21, k in (('dihedral I2(4)=B2', 1, 2, 4), ('dihedral I2(6)=G2', 1, 3, 6)):
    A, Bm = dihedral_cartan(name, c12, c21, k)
    # the inversion reflections of the reduced word s1 s2 s1 ... (conjugates of the simple reflections)
    S = [A, Bm]; w = eye(2)
    for t in range(k):
        i = t % 2
        # beta_t = w * alpha_i where alpha_i is the i-th coordinate vector
        alpha = [Q(int(r == i)) for r in range(2)]
        beta = [sum(w[r][c] * alpha[c] for c in range(2)) for r in range(2)]
        w = mm(w, S[i])
    ck(w == negI(2), f'{name}: reduced word s1 s2 ... of length {k} equals -I')
    # reflection s_beta = w_{t-1} s_i w_{t-1}^{-1}
    refl_list = []
    w = eye(2)
    for t in range(k):
        i = t % 2
        # conjugate: M_beta = w S_i w^{-1}
        winv = [[w[1][1], -w[0][1]], [-w[1][0], w[0][0]]]
        det = w[0][0] * w[1][1] - w[0][1] * w[1][0]
        winv = [[x / det for x in r] for r in winv]
        refl_list.append(mm(mm(w, S[i]), winv)); w = mm(w, S[i])
    pairs = [refl_from_matrix(M) for M in refl_list]
    check_reflection_word(name, [q for q, p in pairs], [p for q, p in pairs])
# ---- random words in rho = 2: choose N - 2 random reflections, then close with two reflections r_N r_{N-1} = M
rng = random.Random(2)
def random_word(N):
    while True:
        pairs = []
        for _ in range(N - 2):
            q = [Q(rng.randint(-4, 4)) for _ in range(2)]
            p0 = [Q(rng.randint(-4, 4)) for _ in range(2)]
            d = dotv(p0, q)
            if d == 0: break
            p = [x / d for x in p0]; pairs.append((q, p))
        else:
            P = eye(2)
            for q, p in pairs: P = mm(refl(q, p), P)
            M = [[-x for x in r] for r in P]            # need r_N r_{N-1} = -P^{-1}
            det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
            if det == 0: continue
            Mi = [[M[1][1] / det, -M[0][1] / det], [-M[1][0] / det, M[0][0] / det]]   # (-P)^-1
            # want r_N r_{N-1} * P = -I, i.e. r_N r_{N-1} = -P^{-1} = Mi
            # r_N = Mi r_{N-1}: reflection needs trace(Mi r) = 0 for det(Mi) = 1 (the product of N-2 reflections has det (+1)^(N-2) with N even)
            q5 = [Q(rng.randint(-4, 4)) for _ in range(2)]
            tr = Mi[0][0] + Mi[1][1]
            Mq = [Mi[0][0] * q5[0] + Mi[0][1] * q5[1], Mi[1][0] * q5[0] + Mi[1][1] * q5[1]]
            # solve p.q5 = 1 and p.Mq = tr/2
            a, b = q5; c_, d_ = Mq
            D_ = a * d_ - b * c_
            if D_ == 0: continue
            p5 = [(Q(1) * d_ - b * (tr / 2)) / D_, (a * (tr / 2) - c_ * Q(1)) / D_]
            r5 = refl(q5, p5)
            r6 = mm(Mi, r5)
            # r6 must be a reflection I - 2 q6 p6^T
            try:
                q6, p6 = refl_from_matrix(r6)
            except (AssertionError, StopIteration):
                continue
            pairs += [(q5, p5), (q6, p6)]
            P = eye(2)
            for q, p in pairs: P = mm(refl(q, p), P)
            if P != negI(2): continue
            return [q for q, p in pairs], [p for q, p in pairs]
for N in (6, 8, 10, 12):
    qs, ps = random_word(N)
    check_reflection_word(f'random rho=2 word', qs, ps)
# control: perturbing one reflection destroys the product -I and the transvection side
qs, ps = random_word(8)
qs2 = [q[:] for q in qs]; qs2[3] = [qs2[3][0] + 1, qs2[3][1]]
ps2 = [p[:] for p in ps]; d = dotv(ps2[3], qs2[3])
if d != 0:
    ps2[3] = [x / d for x in ps2[3]]
    prodR = prod_left([refl(qs2[i], ps2[i]) for i in range(8)], 2)
    n2, iso2, ok2, _, _ = reflections_to_transvections(qs2, ps2)
    ck(prodR != negI(2) and not ok2, 'control: perturbing one reflection destroys the product -I on both sides')
print('PASS_DUALITY' if not fails else 'FAILED_DUALITY')
sys.exit(1 if fails else 0)
