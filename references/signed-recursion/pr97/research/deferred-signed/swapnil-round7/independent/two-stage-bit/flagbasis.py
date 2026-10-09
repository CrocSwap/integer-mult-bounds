"""Children profiles of every two-stage bit edge class in ONE nested controlled basis S = T (I (x) K).
Coordinates (x, y), y fastest; T acts on the slow factor x by G_y on fibre y.
Basis modes:
  struct  : G_y row 0 = row (y+1 mod h) of W^-1, G_y^-1 e_{h-1} = column y of W (W generic unimodular)
            -> stage-1 corner M[y,y'] = g_y . k_y' is the cyclic shift (the best possible: diag is forced 0)
  nested  : generic unimodular G_y, K   (negative control: stage-1 corners not merged)
  tensor  : all G_y equal               (negative control: stage-1 aux corner singular)
  dense   : one generic unimodular S0   (negative control: no stage-2 structure)
Pivots of S_p are computed by the rightmost-pivot lower-lower elimination mod q (and exactly over Q at h=6 for
a sample, with factor.bruhat). A child is a maximal run H_i -> D_j, H_{i+1} -> D_{j+1}, ... (contiguous, same
order). 'other' counts Bruhat moves that are not H<->D transpositions (must be 0)."""
import sys, random
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'partial-swap'))
from fractions import Fraction as Q
from itertools import combinations
q = 2**61-1

def red(x): return x.numerator % q * pow(x.denominator % q, q-2, q) % q
def mm(A, B):
    Bt = list(zip(*B)); return [[sum(a*b for a, b in zip(r, c)) % q for c in Bt] for r in A]
def kron(A, B): return [[a*b % q for a in ra for b in rb] for ra in A for rb in B]
def eye(n): return [[int(i == j) for j in range(n)] for i in range(n)]

def piv_modq(A):
    """Rightmost-pivot lower-lower elimination; returns {row: col} (singular rows have no pivot)."""
    M = [r[:] for r in A]; n = len(M); out = {}
    for i in range(n):
        r = M[i]; c = next((j for j in range(len(r)-1, -1, -1) if r[j]), None)
        if c is None: continue
        out[i] = c; iv = pow(r[c], q-2, q)
        for k in range(i+1, n):
            if M[k][c]:
                f = M[k][c]*iv % q; M[k] = [(x-f*y) % q for x, y in zip(M[k], r)]
    return out

def swapmat(p):
    m = len(p)
    return [[(int(i == j)-p[i][j]) % q for j in range(m)]+p[i][:] for i in range(m)] + \
           [p[i][:]+[(int(i == j)-p[i][j]) % q for j in range(m)] for i in range(m)]

def children(p):
    """Children widths of the partial swap S_p from its Bruhat involution (mod q)."""
    m = len(p); w = piv_modq(swapmat(p)); assert len(w) == 2*m
    other = sum(1 for i, c in w.items() if c != i and (i < m) == (c < m))
    inv_ok = all(w[c] == i for i, c in w.items())
    hd = sorted((i, c) for i, c in w.items() if i < m <= c)
    out = []; prev = None
    for i, c in hd:
        if prev and i == prev[0]+1 and c == prev[1]+1: out[-1] += 1
        else: out.append(1)
        prev = (i, c)
    return tuple(sorted(out, reverse=True)), other, inv_ok

RR = 10**6   # generic coefficients: the lemma is a Zariski-open statement, small ranges hit coincidences
def unimod(n, rng, R=None):
    R = R or RR
    L = [[rng.randint(-R, R) if j < i else int(i == j) for j in range(n)] for i in range(n)]
    U = [[rng.randint(-R, R) if j > i else int(i == j) for j in range(n)] for i in range(n)]
    return [[sum(L[i][k]*U[k][j] for k in range(n)) for j in range(n)] for i in range(n)]

def inv_int(A):
    """Exact inverse of an integer matrix as Fractions."""
    n = len(A); M = [[Q(x) for x in r]+[Q(int(i == j)) for j in range(n)] for i, r in enumerate(A)]
    for c in range(n):
        p = next(i for i in range(c, n) if M[i][c]); M[c], M[p] = M[p], M[c]
        f = M[c][c]; M[c] = [x/f for x in M[c]]
        for i in range(n):
            if i != c and M[i][c]: g = M[i][c]; M[i] = [a-g*b for a, b in zip(M[i], M[c])]
    return [r[n:] for r in M]

def basis(h, mode, rng):
    """Return S, S^-1 as exact Fraction matrices (m x m)."""
    m = h*h
    if mode == 'flag':
        return flag_basis(h, rng)
    if mode == 'dense':
        S = unimod(m, rng, 2); Si = inv_int(S); return [[Q(x) for x in r] for r in S], Si
    K = unimod(h, rng)
    if mode == 'struct':
        Wm = unimod(h, rng); Wi = inv_int(Wm); Gs = []
        for y in range(h):
            w = [Q(Wm[r][y]) for r in range(h)]                  # k_y = w_y : G_y w_y = e_{h-1}
            rows = [Wi[(y+1) % h]]                               # g_y = dual of w_{y+1}; g_y . w_y = 0
            j0 = next(j for j in range(h) if w[j]); u = [Q(int(j == j0))/w[j0] for j in range(h)]
            for _ in range(h-2):
                r = [Q(rng.randint(-RR, RR)) for _ in range(h)]; d = sum(a*b for a, b in zip(r, w))
                rows.append([a-d*b for a, b in zip(r, u)])
            r = [Q(rng.randint(-RR, RR)) for _ in range(h)]; d = sum(a*b for a, b in zip(r, w))
            rows.append([a-d*b+c for a, b, c in zip(r, u, u)])
            Gs.append(rows)
    elif mode == 'tensor':
        G0 = [[Q(x) for x in r] for r in unimod(h, rng)]; Gs = [G0]*h
    else:
        Gs = [[[Q(x) for x in r] for r in unimod(h, rng)] for _ in range(h)]
    Gi = [inv_int(G) if all(x.denominator == 1 for r in G for x in r) else None for G in Gs]
    Gi = [g if g is not None else inv_frac(G) for g, G in zip(Gi, Gs)]
    Ki = inv_int(K)
    S = [[Q(0)]*m for _ in range(m)]; Si = [[Q(0)]*m for _ in range(m)]
    # S = T (I (x) K):  S[(x,y),(x',y')] = G_y[x,x'] K[y,y'];  S^-1 = (I (x) K^-1) T^-1
    for x in range(h):
        for y in range(h):
            for x2 in range(h):
                g = Gs[y][x][x2]; gi = None
                for y2 in range(h):
                    S[x*h+y][x2*h+y2] = g*K[y][y2]
                    Si[x*h+y][x2*h+y2] = Ki[y][y2]*Gi[y2][x][x2]
    return S, Si

def flag_basis(h, rng):
    """First h rows of S <-> matrices U R_b V^T (R_b supported on [0..b]^2), last h columns of S^-1 <->
    U^-T C_b V^-1 (C_b supported on [b..h-1]^2). For b < b': R_b^T C_b' = 0 and R_b C_b'^T = 0 identically, so
    both stage corners are lower triangular. Trace conditions tr(R_i^T C_j) = 0 (all i, j) make S S^-1 = I."""
    m = h*h; rnd = lambda: Q(rng.randint(1, RR))
    R = []
    for b in range(h):
        Rb = [[rnd() if i <= b and j <= b else Q(0) for j in range(h)] for i in range(h)]
        if b == h-1: Rb[b][b] = Q(0)                       # i = j trace condition R_b[b][b] C_b[b][b] = 0:
        R.append(Rb)                                       # zero R at b = h-1, zero C below (else R_0 = 0)
    C = []
    for b in range(h):
        Cb = [[rnd() if i >= b and j >= b else Q(0) for j in range(h)] for i in range(h)]
        if b < h-1: Cb[b][b] = Q(0)
        for bb in range(b+1, h):                           # tr(R_bb^T C_b) = 0, slack entry (b, bb)
            Cb[b][bb] = Q(0)
            s = sum(R[bb][i][j]*Cb[i][j] for i in range(b, bb+1) for j in range(b, bb+1))
            Cb[b][bb] = -s/R[bb][b][bb]
        C.append(Cb)
    U = [[Q(x) for x in r] for r in unimod(h, rng)]; V = [[Q(x) for x in r] for r in unimod(h, rng)]
    Ui, Vi = inv_frac(U), inv_frac(V)
    mulq = lambda A, B: [[sum(a*b for a, b in zip(r, c)) for c in zip(*B)] for r in A]
    Tr = lambda A: [list(x) for x in zip(*A)]
    lam = [sum(mulq(mulq(U, Rb), Tr(V)), []) for Rb in R]          # row-major vec, index x*h+y
    mu = [sum(mulq(mulq(Tr(Ui), Cb), Vi), []) for Cb in C]
    assert all(sum(a*b for a, b in zip(l, u)) == 0 for l in lam for u in mu)
    # X = [Z | W | mu] with lam Z = I_h, W a complement of span(mu) in ker(lam); S = X^-1
    ker = nullspace(lam, m); cur = [u[:] for u in mu]; W = []
    def rc():                                               # random kernel vector
        cf = [rng.randint(-3, 3) for _ in ker]
        return [sum(c*x for c, x in zip(cf, col)) for col in zip(*ker)]
    while len(W) < m-2*h:                                   # generic complement (not the sparse nullspace basis)
        k = [Q(x) for x in rc()]
        if rank_frac(cur+[k]) > len(cur): cur.append(k); W.append(k)
    Lt = Tr(lam); Gm = mulq(lam, Lt); Z = Tr(mulq(Lt, inv_frac(Gm)))
    Z = [[a+b for a, b in zip(z, rc())] for z in Z]           # generic preimages of e_1..e_h
    X = Tr(Z+W+mu); S = inv_frac(X)
    assert S[:h] == lam
    return S, X

def nullspace(A, n):
    M = [r[:] for r in A]; piv = []; r0 = 0
    for c in range(n):
        p = next((i for i in range(r0, len(M)) if M[i][c]), None)
        if p is None: continue
        M[r0], M[p] = M[p], M[r0]; f = M[r0][c]; M[r0] = [x/f for x in M[r0]]
        for i in range(len(M)):
            if i != r0 and M[i][c]: g = M[i][c]; M[i] = [x-g*y for x, y in zip(M[i], M[r0])]
        piv.append(c); r0 += 1
    out = []
    for fc in [c for c in range(n) if c not in piv]:
        v = [Q(0)]*n; v[fc] = Q(1)
        for i, c in enumerate(piv): v[c] = -M[i][fc]
        out.append(v)
    return out

def rank_frac(A):
    M = [r[:] for r in A]; rk = 0
    for c in range(len(M[0])):
        p = next((i for i in range(rk, len(M)) if M[i][c]), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]
        for i in range(rk+1, len(M)):
            if M[i][c]: f = M[i][c]/M[rk][c]; M[i] = [a-f*b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk

def inv_frac(A):
    n = len(A); M = [r[:]+[Q(int(i == j)) for j in range(n)] for i, r in enumerate(A)]
    for c in range(n):
        p = next(i for i in range(c, n) if M[i][c]); M[c], M[p] = M[p], M[c]
        f = M[c][c]; M[c] = [x/f for x in M[c]]
        for i in range(n):
            if i != c and M[i][c]: g = M[i][c]; M[i] = [a-g*b for a, b in zip(M[i], M[c])]
    return [r[n:] for r in M]

def setup(h):
    trip = list(combinations(range(h), 3))
    G = [[Q(int(i == j))-Q(1, 9) for j in range(h)] for i in range(h)]
    def projU(vecs):            # G-orthogonal projector onto span(vecs) (column convention)
        if not vecs: return [[Q(0)]*h for _ in range(h)]
        B = []
        for v in vecs:                                      # keep an independent subset
            if rank_frac(B+[list(v)]) > len(B): B.append(list(v))
        Bc = list(map(list, zip(*B)))
        GB = [[sum(G[i][k]*Bc[k][j] for k in range(h)) for j in range(len(B))] for i in range(h)]
        Gr = [[sum(B[a][k]*GB[k][b] for k in range(h)) for b in range(len(B))] for a in range(len(B))]
        Gri = inv_frac(Gr)
        BtG = [[sum(B[a][k]*G[k][j] for k in range(h)) for j in range(h)] for a in range(len(B))]
        X = [[sum(Bc[i][a]*Gri[a][b] for a in range(len(B))) for b in range(len(B))] for i in range(h)]
        return [[sum(X[i][b]*BtG[b][j] for b in range(len(B))) for j in range(h)] for i in range(h)]
    tv = [[Q(int(i in t)) for i in range(h)] for t in trip]
    P = [projU([t]) for t in tv]
    I = [[Q(int(i == j)) for j in range(h)] for i in range(h)]
    Qc = [[[I[i][j]-p[i][j] for j in range(h)] for i in range(h)] for p in P]
    return trip, tv, G, P, Qc, I, projU

def run(h, mode, seed, npairs, nside, exact_sample=0):
    rng = random.Random(seed); m = h*h
    trip, tv, G, P, Qc, I, projU = setup(h); v = len(trip)
    S, Si = basis(h, mode, rng)
    Sm = [[red(x) for x in r] for r in S]; Sim = [[red(x) for x in r] for r in Si]
    assert mm(Sm, Sim) == eye(m)
    Rm = lambda A: [[red(x) for x in r] for r in A]
    Pm = [Rm(p) for p in P]; Qm = [Rm(p) for p in Qc]; Im = eye(h)
    def conj(A): return mm(mm(Sm, A), Sim)
    res = {}
    def rec(name, A, rank):
        ch = children(conj(A)); res.setdefault(name, {}); key = (rank,)+ch
        res[name][key] = res[name].get(key, 0)+1
    for a in range(v):
        rec('s1 aux exit  I(x)Q_b', kron(Im, Qm[a]), m-h)
        rec('s1 centre    I(x)P_b', kron(Im, Pm[a]), h)
        rec('s2 aux entr  Q_a(x)I', kron(Qm[a], Im), m-h)
        rec('s2 centre    P_a(x)I', kron(Pm[a], Im), h)
    for _ in range(npairs):
        a1, a2 = rng.randrange(v), rng.randrange(v)
        rec('data s1      Q_a1(x)P_a2', kron(Qm[a1], Pm[a2]), h-1)
        rec('data s2 entr Q_a1(x)Q_a2', kron(Qm[a1], Qm[a2]), m-2*h+1)
        rec('data s2 exit P_a1(x)Q_a2', kron(Pm[a1], Qm[a2]), h-1)
    for _ in range(nside):     # side edges: pi = P_V - P_U for nested source spans / target complements
        T_ = trip[rng.randrange(v)]; i = rng.choice(T_)
        src = [s for s, t in enumerate(trip) if i in t and set(t) & set(T_) == {i}]
        Ss = rng.sample(src, rng.randint(1, len(src)))
        U = [tv[s] for s in Ss]; PU = projU(U)
        PT = P[trip.index(T_)]; PYt = [[I[r][c]-PT[r][c] for c in range(h)] for r in range(h)]
        dU = sum(1 for _ in range(1))  # placeholder
        b = rng.randrange(v)
        for nm, pi in (('U->F', [[I[r][c]-PU[r][c] for c in range(h)] for r in range(h)]),
                       ('U->Yt', [[PYt[r][c]-PU[r][c] for c in range(h)] for r in range(h)]),
                       ('0->U', PU)):
            pim = Rm(pi); rk = len(piv_modq(pim))
            rec('s1 side %-5s pi(x)P_b' % nm, kron(pim, Pm[b]), rk)
            rec('s2 side %-5s P_a(x)pi' % nm, kron(Pm[b], pim), rk)
    if exact_sample:            # exact Q check of the S_p Bruhat involution on a sample of edges
        from factor import bruhat, swapmat as swq, mul
        ok = 0; tot = 0
        for a in rng.sample(range(v), exact_sample):
            for A in (kronQ(I, Qc[a]), kronQ(I, P[a]), kronQ(Qc[a], I), kronQ(P[a], I)):
                pp = mul(mul(S, A), Si); piv, *_ = bruhat(swq(pp), track=False)
                wq = piv_modq(swapmat(Rm(pp))); tot += 1; ok += all(piv[i] == wq[i] for i in range(2*m))
        res['_exact Q == mod q Bruhat'] = {(ok, tot): 1}
    return res

def kronQ(A, B): return [[a*b for a in ra for b in rb] for ra in A for rb in B]

if __name__ == '__main__':
    h, mode, seed, npairs, nside = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    ex = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    RR = int(sys.argv[7]) if len(sys.argv) > 7 else 10**6
    res = run(h, mode, seed, npairs, nside, ex)
    print('h=%d m=%d mode=%s seed=%d   key = (rank, child widths..., other-moves, involution-ok): count' % (h, h*h, mode, seed))
    for k in sorted(res):
        print('  %-28s' % k, dict(sorted(res[k].items())), flush=True)
