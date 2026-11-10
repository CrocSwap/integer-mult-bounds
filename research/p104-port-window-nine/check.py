#!/usr/bin/env python3
"""Exact checks for THEOREM.md. Standard library only, writes nothing, reads only data/ in this package.
Run from anywhere:  python3.12 -I -B research/p104-port-window-nine/check.py
One 'PASS [tag] claim' line per claim; any failed claim prints FAIL and the exit status is 1.
The final marker is PASS_P104_PORT_WINDOW_NINE.  Tags: [C] exact computation, [P+C] a proof in THEOREM.md
evaluated on explicit objects, [R] recorded solver rows (read from data/sat_rows.json, not repeated here)."""
import os, sys, json, random, itertools, collections, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
T0 = time.time()
FAILS = []


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


def PASS(tag, msg):
    print('PASS [%s] %s' % (tag, msg), flush=True)


def FAIL(tag, msg):
    FAILS.append(msg)
    print('FAIL [%s] %s' % (tag, msg), flush=True)


def claim(cond, tag, msg):
    (PASS if cond else FAIL)(tag, msg)
    return cond


# ----------------------------------------------------------------------------------------------------------
# F_p linear algebra (matrices are lists of rows of ints)
# ----------------------------------------------------------------------------------------------------------
def rank_p(M, p):
    A = [[x % p for x in r] for r in M]
    A = [r for r in A if r]
    if not A or not A[0]:
        return 0
    rk, n = 0, len(A)
    for c in range(len(A[0])):
        piv = next((i for i in range(rk, n) if A[i][c]), None)
        if piv is None:
            continue
        A[rk], A[piv] = A[piv], A[rk]
        inv = pow(A[rk][c], -1, p)
        A[rk] = [x * inv % p for x in A[rk]]
        for i in range(rk + 1, n):
            f = A[i][c]
            if f:
                A[i] = [(x - f * y) % p for x, y in zip(A[i], A[rk])]
        rk += 1
        if rk == n:
            break
    return rk


def mmT(A, B, p):
    """A B^T mod p; A, B lists of rows of equal length."""
    return [[sum(a * b for a, b in zip(ra, rb)) % p for rb in B] for ra in A]


def mm(A, B, p):
    Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(ra, cb)) % p for cb in Bt] for ra in A]


def ident(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def zeros(a, b):
    return [[0] * b for _ in range(a)]


def madd(A, B, p, s=1):
    return [[(x + s * y) % p for x, y in zip(ra, rb)] for ra, rb in zip(A, B)]


def hcat(A, B):
    return [ra + rb for ra, rb in zip(A, B)]


def vcat(A, B):
    return [list(r) for r in A] + [list(r) for r in B]


def inverse(M, p):
    n = len(M)
    A = [[x % p for x in r] + ident(n)[i] for i, r in enumerate(M)]
    for c in range(n):
        piv = next((i for i in range(c, n) if A[i][c]), None)
        if piv is None:
            return None
        A[c], A[piv] = A[piv], A[c]
        inv = pow(A[c][c], -1, p)
        A[c] = [x * inv % p for x in A[c]]
        for i in range(n):
            if i != c and A[i][c]:
                f = A[i][c]
                A[i] = [(x - f * y) % p for x, y in zip(A[i], A[c])]
    return [r[n:] for r in A]


def transpose(M):
    return [list(r) for r in zip(*M)]


def solve_linear(rows, rhs, ncols, p, rng):
    """One uniformly random solution of rows * u = rhs over F_p, or None."""
    A = [[x % p for x in r] + [b % p] for r, b in zip(rows, rhs)]
    piv_cols, rk = [], 0
    for c in range(ncols):
        piv = next((i for i in range(rk, len(A)) if A[i][c]), None)
        if piv is None:
            continue
        A[rk], A[piv] = A[piv], A[rk]
        inv = pow(A[rk][c], -1, p)
        A[rk] = [x * inv % p for x in A[rk]]
        for i in range(len(A)):
            if i != rk and A[i][c]:
                f = A[i][c]
                A[i] = [(x - f * y) % p for x, y in zip(A[i], A[rk])]
        piv_cols.append(c)
        rk += 1
    if any(A[i][ncols] for i in range(rk, len(A))):
        return None
    u = [rng.randrange(p) for _ in range(ncols)]
    for i, c in enumerate(piv_cols):
        u[c] = (A[i][ncols] - sum(A[i][t] * u[t] for t in range(ncols) if t not in piv_cols)) % p
    return u


# ----------------------------------------------------------------------------------------------------------
# Ports, the three systems, orthogonal 8-sets
# ----------------------------------------------------------------------------------------------------------
PORTS = load('ports_p104.json')['ports']
DOT = [bytearray((a & b).bit_count() & 1 for b in range(512)) for a in range(512)]
dot = lambda a, b: DOT[a][b]
wt = lambda a: a.bit_count()
P120 = [x for x in range(512) if wt(x) % 4 == 3]


def orth_8sets(V):
    """All sets of 8 pairwise orthogonal vectors of V (dot = 0); also reports whether a 9-set exists."""
    n = len(V)
    nb = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j and dot(V[i], V[j]) == 0:
                nb[i] |= 1 << j
    out, nine = [], [False]

    def rec(cl, cand, size):
        if size == 8:
            out.append(cl)
            if cand:
                nine[0] = True
            return
        while cand:
            low = cand & -cand
            i = low.bit_length() - 1
            cand ^= low
            rec(cl + [V[i]], cand & nb[i], size + 1)
    rec([], (1 << n) - 1, 0)
    return out, nine[0]


def edge_ports(V, K):
    """Ports outside K with exactly two odd K-neighbours: list of (port, (i, j)) with i<j indices into K."""
    Ks = set(K)
    res = []
    for t in V:
        if t in Ks:
            continue
        A = tuple(i for i, c in enumerate(K) if dot(t, c))
        if len(A) == 2:
            res.append((t, A))
    return res


def gamma_data(V, K):
    Ed = edge_ports(V, K)
    deg = collections.Counter(c for _, A in Ed for c in A)
    return Ed, [deg.get(i, 0) for i in range(len(K))]


# ----------------------------------------------------------------------------------------------------------
# Representation checker.  A rep of the configuration (m points K, simple graph Gamma on K with edge ports)
# has ports 0..m-1 (the points) and m..m+E-1 (edge ports, edges[i] = (c, d)); labels W[P], U[P] are k x r
# matrices over F_p with r = m*k + j; coordinate c*k+t is the t-th coordinate of block c, the last j are x.
# 'orth' is the set of port pairs that must have zero blocks.  analyse() tests the premises of THEOREM.md
# (gauge, supports, diagonal blocks I, zero blocks) and evaluates every inequality of the proofs, whether or
# not the premises hold, so that planted violations show up.
# ----------------------------------------------------------------------------------------------------------
def abstract_orth(m, edges):
    nP = m + len(edges)
    o = set()
    for a in range(m):
        for b in range(a + 1, m):
            o.add((a, b))
    for a in range(m):
        for i, e in enumerate(edges):
            if a not in e:
                o.add((a, m + i))
    for i, e in enumerate(edges):
        for i2 in range(i + 1, len(edges)):
            if set(e) & set(edges[i2]):
                o.add((m + i, m + i2))
    return o


def analyse(rep):
    p, k, m, j, edges = rep['p'], rep['k'], rep['m'], rep['j'], rep['edges']
    W, U, orth = rep['W'], rep['U'], rep['orth']
    r = m * k + j
    nP = m + len(edges)
    prob, viol = [], []
    st = collections.Counter()
    I = ident(k)

    def B(S, T):
        return mmT(W[S], U[T], p)
    # --- premises
    for c in range(m):
        e = [[1 if t == c * k + x else 0 for t in range(r)] for x in range(k)]
        if W[c] != e or U[c] != e:
            prob.append('gauge at point %d' % c)
    for i, (c, d) in enumerate(edges):
        allowed = set(range(c * k, (c + 1) * k)) | set(range(d * k, (d + 1) * k)) | set(range(m * k, r))
        for M in (W[m + i], U[m + i]):
            if any(v % p and t not in allowed for row in M for t, v in enumerate(row)):
                prob.append('support of edge port %d' % i)
    for S in range(nP):
        if B(S, S) != I:
            prob.append('diagonal block of port %d' % S)
    for (S, T) in orth:
        if any(any(row) for row in B(S, T)) or any(any(row) for row in B(T, S)):
            prob.append('mask block (%d,%d)' % (S, T))

    def Wc(P, c): return [row[c * k:(c + 1) * k] for row in W[P]]
    def Uc(P, c): return [row[c * k:(c + 1) * k] for row in U[P]]
    def Wx(P): return [row[m * k:] for row in W[P]]
    def Ux(P): return [row[m * k:] for row in U[P]]
    def Xb(S, T): return mmT(Wx(S), Ux(T), p)
    def alpha(S, T, c): return mmT(Wc(S, c), Uc(T, c), p)

    star, g = {}, {}
    deg = collections.Counter()
    for c in range(m):
        Tl = [m + i for i, e in enumerate(edges) if c in e]
        deg[c] = len(Tl)
        if not Tl:
            continue
        n = len(Tl)
        gam = {P: madd(alpha(P, P, c), Xb(P, P), p) for P in Tl}
        for P in Tl:
            g[(P, c)] = rank_p(gam[P], p)
        D = zeros(n * k, n * k)
        for a, P in enumerate(Tl):
            for x in range(k):
                for y in range(k):
                    D[a * k + x][a * k + y] = gam[P][x][y]
        Xc = [[0] * (n * k) for _ in range(n * k)]
        Mc = [[0] * (n * k) for _ in range(n * k)]
        for a, S in enumerate(Tl):
            for b, T in enumerate(Tl):
                xb, ab = Xb(S, T), alpha(S, T, c)
                for x in range(k):
                    for y in range(k):
                        Xc[a * k + x][b * k + y] = xb[x][y]
                        Mc[a * k + x][b * k + y] = ab[x][y]
        for a, S in enumerate(Tl):
            for b, T in enumerate(Tl):
                if a != b and any(any(row) for row in madd(alpha(S, T, c), Xb(S, T), p)):
                    prob.append('star at %d not block diagonal' % c)
        rD, xc = rank_p(D, p), rank_p(Xc, p)
        y = rank_p(hcat(D, Xc), p) - rD       # = x_c - dim(col D cap col X)
        y2 = rank_p(vcat(D, Xc), p) - rD      # row version
        G = sum(g[(P, c)] for P in Tl)
        star[c] = dict(Tl=Tl, y=y, y2=y2, xc=xc, G=G, gam=gam)
        ok = rank_p(Mc, p) <= k
        st['rankM'] += 1
        if not ok:
            viol.append('rank M_c <= k at %d' % c)
        st['Star'] += 1
        if not G <= k + xc - y - y2:
            viol.append('(Star) at point %d: %d > %d' % (c, G, k + xc - y - y2))
        st['Star-Y'] += 1
        if not G <= k + j - (y + y2):
            viol.append('(Star, Y form) at point %d' % c)
        st['Y<=j'] += 1
        if not (y <= xc <= j and y2 <= xc):
            viol.append('Y_c <= x_c <= j at %d' % c)
        # containment lemma, columns and rows, for every edge port at c
        for P in Tl:
            Q = gam[P]
            XP = Xb(P, P)
            st['containment'] += 1
            if not (rank_p(hcat(Q, XP), p) - g[(P, c)] <= y and rank_p(vcat(Q, XP), p) - g[(P, c)] <= y2):
                viol.append('containment at port %d end %d' % (P, c))
    # --- (E') on every edge port
    for i, (c, d) in enumerate(edges):
        P = m + i
        gc, gd = g[(P, c)], g[(P, d)]
        ycs = [star[c]['y'], star[c]['y2'], star[d]['y'], star[d]['y2']]
        Yc = Fr(star[c]['y'] + star[c]['y2'], 2)
        Yd = Fr(star[d]['y'] + star[d]['y2'], 2)
        st['(E-prime)'] += 1
        s4 = gc + gd + min(ycs) - k
        sY = gc + gd + min(Yc, Yd) - k
        if s4 < 0 or sY < 0:
            viol.append("(E') at edge port %d: slack %s" % (i, min(s4, sY)))
        if s4 == 0:
            st['tight'] += 1
        # identity I = gamma(c) + gamma(d) - X  (needs the diagonal and support premises)
        lhs = madd(madd(star[c]['gam'][P], star[d]['gam'][P], p), Xb(P, P), p, -1)
        if lhs != I:
            prob.append('edge identity at port %d' % i)
        if gc > 0 and Yc > 0:
            st['gY'] += 1
        if gd > 0 and Yd > 0:
            st['gY'] += 1
    # --- (LR) and its sub-lemmas
    for c, s in star.items():
        Tl = s['Tl']
        L = {P: [Wx(P)[a] + Wc(P, c)[a] for a in range(k)] for P in Tl}
        R = {P: [Ux(P)[a] + Uc(P, c)[a] for a in range(k)] for P in Tl}
        Ls = [row for P in Tl for row in L[P]]
        Rs = [row for P in Tl for row in R[P]]
        ell, rho = rank_p(Ls, p), rank_p(Rs, p)
        G = s['G']
        st['LR-sub'] += 1
        if rank_p(mmT(Ls, Rs, p), p) != G:
            prob.append('rank(L R^T) != G at %d' % c)
        if not ell - G <= j + k - rho:
            viol.append('LR step 2 at %d' % c)
        for P in Tl:
            d = [x for x in edges[P - m] if x != c][0]
            lam, rh = rank_p(L[P], p), rank_p(R[P], p)
            gc, gd = g[(P, c)], g[(P, d)]
            st['LR-sub'] += 1
            if not (lam - gc <= ell - G and rh - gc <= rho - G):
                viol.append('LR step 3 at port %d end %d' % (P, c))
            if not (lam >= k - gd and rh >= k - gd):
                viol.append('LR step 5 at port %d end %d' % (P, c))
            st['(LR)'] += 1
            sl = j + 2 * (gc + gd) - G - k
            if sl < 0:
                viol.append('(LR) at port %d end %d: slack %d' % (P, c, sl))
            if sl == 0:
                st['tight'] += 1
    # --- Theorem 3' conclusions (only meaningful when the premises hold)
    nz = [c for c in range(m) if deg[c] > 0]
    E = len(edges)
    if nz:
        lam_sum = sum(max(Fr(deg[c], 2) - 2, 0) for c in nz)
        st['general'] += 1
        if not Fr(j) * (len(nz) + lam_sum) >= k * (E - len(nz)):
            viol.append("general bound j/k >= (E-n')/(n'+sum (Lambda-2)^+) fails")
        if min(deg[c] for c in nz) >= 4:
            st['mindeg4'] += 1
            if not j >= k:
                viol.append("Theorem 3': j >= k fails with min degree >= 4 (j=%d, k=%d)" % (j, k))
    return dict(prob=prob, viol=viol, st=st, j=j, k=k)


def new_rep(p, k, m, j, edges, orth=None):
    return dict(p=p, k=k, m=m, j=j, edges=list(edges), W={}, U={},
                orth=abstract_orth(m, edges) if orth is None else orth)


def point_labels(rep):
    p, k, m, j = rep['p'], rep['k'], rep['m'], rep['j']
    r = m * k + j
    for c in range(m):
        e = [[1 if t == c * k + x else 0 for t in range(r)] for x in range(k)]
        rep['W'][c] = [list(row) for row in e]
        rep['U'][c] = [list(row) for row in e]


def gram_abstract(p, m, edges, k=1):
    """Gram representation of the configuration: W_T = e_c + e_d + v, U_T = e_c + e_d - v (valid over every F_p);
    tensored with I_k."""
    rep = new_rep(p, k, m, k, edges)
    point_labels(rep)
    r = m * k + k
    for i, (c, d) in enumerate(edges):
        W, U = [], []
        for x in range(k):
            w = [0] * r
            w[c * k + x] = w[d * k + x] = 1
            u = list(w)
            w[m * k + x] = 1
            u[m * k + x] = p - 1
            W.append(w)
            U.append(u)
        rep['W'][m + i], rep['U'][m + i] = W, U
    return rep


def cover_rep(p, m, edges, rng):
    """0/1 clique-cover representation: every edge port sits in exactly one clique: the clique of an end point
    (each point hosts at most one edge) or a coordinate x shared with pairwise disjoint edges."""
    host = {}
    xc = []   # list of lists of edge indices (pairwise disjoint)
    order = list(range(len(edges)))
    rng.shuffle(order)
    for i in order:
        c, d = edges[i]
        opts = [e for e in (c, d) if e not in host]
        if opts and rng.random() < 0.6:
            host[rng.choice(opts)] = i
            continue
        for cl in xc:
            if all(not set(edges[i]) & set(edges[i2]) for i2 in cl) and rng.random() < 0.7:
                cl.append(i)
                break
        else:
            xc.append([i])
    placed = {}
    for c, i in host.items():
        placed[i] = ('pt', c)
    for q, cl in enumerate(xc):
        for i in cl:
            placed[i] = ('x', q)
    j = len(xc)
    rep = new_rep(p, 1, m, j, edges)
    point_labels(rep)
    r = m + j
    for i in range(len(edges)):
        kind, q = placed[i]
        row = [0] * r
        row[q if kind == 'pt' else m + q] = 1
        rep['W'][m + i] = [list(row)]
        rep['U'][m + i] = [list(row)]
    return rep


def dsum(r1, r2):
    assert r1['p'] == r2['p'] and r1['m'] == r2['m'] and r1['edges'] == r2['edges']
    p, m = r1['p'], r1['m']
    k1, k2, j1, j2 = r1['k'], r2['k'], r1['j'], r2['j']
    k, j = k1 + k2, j1 + j2
    r = m * k + j
    out = new_rep(p, k, m, j, r1['edges'], r1['orth'])

    def place(row, which):
        new = [0] * r
        kk, jj = (k1, j1) if which == 1 else (k2, j2)
        off, xoff = (0, 0) if which == 1 else (k1, j1)
        for c in range(m):
            for t in range(kk):
                new[c * k + off + t] = row[c * kk + t]
        for t in range(jj):
            new[m * k + xoff + t] = row[m * kk + t]
        return new
    for key in ('W', 'U'):
        for P in r1[key]:
            out[key][P] = [place(row, 1) for row in r1[key][P]] + [place(row, 2) for row in r2[key][P]]
    return out


def scale_ports(rep, rng, which=None):
    """(W_T, U_T) -> (M W_T, M^{-T} U_T) with M random invertible, for every edge port (a symmetry of all premises)."""
    p, k, m = rep['p'], rep['k'], rep['m']
    out = dict(rep, W=dict(rep['W']), U=dict(rep['U']))
    for i in range(len(rep['edges'])):
        P = m + i
        while True:
            M = [[rng.randrange(p) for _ in range(k)] for _ in range(k)]
            Mi = inverse(M, p)
            if Mi is not None:
                break
        out['W'][P] = mm(M, rep['W'][P], p)
        out['U'][P] = mm(transpose(Mi), rep['U'][P], p)
    return out


def swapped(rep):
    return dict(rep, W=rep['U'], U=rep['W'])


def random_solved_rep(p, m, edges, k, j, rng, dens=0.7):
    """Random W on the allowed supports, then each U_S solved from the linear conditions B_TS = 0 (T orthogonal
    to S) and B_SS = I.  Returns a rep or None if some system is unsolvable."""
    rep = new_rep(p, k, m, j, edges)
    point_labels(rep)
    r = m * k + j
    nP = m + len(edges)
    supp = {}
    for i, (c, d) in enumerate(edges):
        P = m + i
        supp[P] = list(range(c * k, (c + 1) * k)) + list(range(d * k, (d + 1) * k)) + list(range(m * k, r))
        W = [[0] * r for _ in range(k)]
        for a in range(k):
            for t in supp[P]:
                if rng.random() < dens:
                    W[a][t] = rng.randrange(1, p)
        if rank_p(W, p) < k:
            return None
        rep['W'][P] = W
    for P in range(m, nP):
        U = [[0] * r for _ in range(k)]
        S = supp[P]
        for i in range(k):
            rows, rhs = [], []
            for T in range(nP):
                if T == P or (min(T, P), max(T, P)) in rep['orth']:
                    for a in range(k):
                        rows.append([rep['W'][T][a][t] for t in S])
                        rhs.append(1 if (T == P and a == i) else 0)
            sol = solve_linear(rows, rhs, len(S), p, rng)
            if sol is None:
                return None
            for t, v in zip(S, sol):
                U[i][t] = v
        rep['U'][P] = U
    return rep


def rep_from_ports(vecs_K, Ed, k, rng=None, scale=False):
    """Gram representation of a real configuration in characteristic 2: the orthonormal basis K + v
    (v = all-ones + sum K) turns dot into the standard form, so labels are coordinate vectors.  Tensored with I_k
    and, if scale, random invertible scalings of the edge ports (K ports stay in the gauge)."""
    m = len(vecs_K)
    v = 0x1FF
    for c in vecs_K:
        v ^= c
    assert dot(v, v) == 1 and all(dot(v, c) == 0 for c in vecs_K)
    edges = [A for _, A in Ed]
    vecs = list(vecs_K) + [t for t, _ in Ed]
    orth = {(a, b) for a in range(len(vecs)) for b in range(a + 1, len(vecs)) if dot(vecs[a], vecs[b]) == 0}
    rep = new_rep(2, k, m, k, edges, orth)
    point_labels(rep)
    r = m * k + k
    for idx, (t, A) in enumerate(Ed):
        co = [dot(t, c) for c in vecs_K] + [dot(t, v)]
        rows = []
        for x in range(k):
            w = [0] * r
            for c in range(m):
                w[c * k + x] = co[c]
            w[m * k + x] = co[m]
            rows.append(w)
        rep['W'][m + idx] = rows
        rep['U'][m + idx] = [list(w) for w in rows]
    return scale_ports(rep, rng) if scale else rep


def summarize(results):
    tot = collections.Counter()
    for res in results:
        tot.update(res['st'])
    return tot


# ----------------------------------------------------------------------------------------------------------
# Section 1: port systems, K-types, hypotheses of Theorem 3'
# ----------------------------------------------------------------------------------------------------------
def section_ports():
    claim(len(PORTS) == 104 and len(set(PORTS)) == 104 and all(wt(x) % 4 == 3 for x in PORTS), 'C',
          'P104: 104 distinct vectors of F_2^9, every weight 3 mod 4 (so dot(p,p)=1)')
    claim(sorted(collections.Counter(wt(x) for x in PORTS).items()) == [(3, 70), (7, 34)] and set(PORTS) <= set(P120)
          and len(P120) == 120, 'C', 'P104 has 70 ports of weight 3 and 34 of weight 7 and sits inside P120 (120 vectors)')
    deleted = sorted(set(P120) - set(PORTS))
    fr = [c for c in itertools.combinations(deleted, 8) if all(dot(a, b) == 1 for a, b in itertools.combinations(c, 2))]
    claim(len(deleted) == 16 and len(fr) == 2 and set(fr[0]) | set(fr[1]) == set(deleted), 'C',
          'the 16 vectors of P120 outside P104 are exactly two odd 8-cliques (P112 = P104 plus one of them)')
    systems = {'P104': list(PORTS), 'P112a': list(PORTS) + list(fr[0]), 'P112b': list(PORTS) + list(fr[1]), 'P120': list(P120)}
    want = {'P104': 1728, 'P112a': 4032, 'P112b': 4032, 'P120': 8640}
    sets8 = {}
    for name, V in systems.items():
        S, nine = orth_8sets(V)
        sets8[name] = (V, S)
        claim(len(S) == want[name] and not nine, 'C', '%s: %d orthogonal 8-sets, and no 9 pairwise orthogonal ports' % (name, len(S)))
    types = {}
    t_h = time.time()
    for name, (V, S) in sets8.items():
        cnt = collections.Counter()
        h1 = h2 = True
        lam_ok = True
        nonisolated8 = True
        for K in S:
            Ed, degs = gamma_data(V, K)
            cnt[(len(Ed), tuple(sorted(degs)))] += 1
            pairs = [A for _, A in Ed]
            h1 &= len(set(pairs)) == len(pairs)
            for (s, A), (t, B) in itertools.combinations(Ed, 2):
                if len(set(A) & set(B)) == 1 and dot(s, t) != 0:
                    h2 = False
            lam_ok &= all(Fr(d, 2) >= 2 for d in degs)         # lambda_T = 1/2 gives Lambda_c = d_c / 2
            nonisolated8 &= all(d > 0 for d in degs)
        types[name] = cnt
        claim(h1 and h2, 'P+C', '%s: on every orthogonal 8-set, edge ports have distinct pairs (H1) and edge ports sharing exactly one '
              'vertex are orthogonal (H2)' % name)
        mind = min(min(t[1]) for t in cnt)
        claim(mind >= 4 and nonisolated8 and lam_ok, 'P+C',
              "%s: every orthogonal 8-set has n'=8 and minimum degree %d >= 4, so lambda=1/2 gives every charge Lambda_c = d_c/2 >= 2" % (name, mind))
    p104 = types['P104']
    exp = {(22, (5, 5, 5, 5, 6, 6, 6, 6)): 960, (22, (5, 5, 5, 5, 5, 6, 6, 7)): 384, (21, (5, 5, 5, 5, 5, 5, 6, 6)): 384}
    claim(dict(p104) == exp, 'C', 'P104 K-types (E; sorted degrees): (22;5,5,5,5,6,6,6,6) x 960, (22;5,5,5,5,5,6,6,7) x 384, '
          '(21;5,5,5,5,5,5,6,6) x 384; minimum degree 5 on all 1728')
    p112 = {(25, (6, 6, 6, 6, 6, 6, 7, 7)): 3584, (24, (6,) * 8): 448}
    claim(dict(types['P112a']) == p112 and dict(types['P112b']) == p112, 'C',
          'P112 K-types: (25;6^6,7,7) x 3584 and (24;6^8) x 448, for either choice of clique')
    claim(dict(types['P120']) == {(28, (7,) * 8): 8640}, 'C', 'P120 K-type: (28;7^8) on all 8640 orthogonal 8-sets')
    return systems, sets8


# ----------------------------------------------------------------------------------------------------------
# Section 2: inequalities on explicit representations
# ----------------------------------------------------------------------------------------------------------
def report(tag, label, results, need_gY=False, need_tight=False):
    tot = summarize(results)
    bad = [v for res in results for v in res['viol']]
    pr = [v for res in results for v in res['prob']]
    ok = not bad and not pr
    extra = ''
    if need_gY:
        ok &= tot['gY'] > 0
        extra += '; %d edge ends with g>0 and Y>0' % tot['gY']
    if need_tight:
        ok &= tot['tight'] > 0
    claim(ok, tag, "%s: %d reps, premises hold, (E') x%d, (LR) x%d, (Star) x%d, containment x%d, no violation; %d tight cases%s"
          % (label, len(results), tot["(E-prime)"], tot['(LR)'], tot['Star'], tot['containment'], tot['tight'], extra))
    if bad or pr:
        print('   first problems:', (pr + bad)[:4], flush=True)


def section_reps(systems, sets8):
    rng = random.Random(20251110)
    # (a) Gram of P104 and of P120, k = 1, over F_2: one K of each type, plus a spread of K's
    for name in ('P104', 'P120'):
        V, S = sets8[name]
        seen, picks = set(), []
        for K in S:
            Ed, degs = gamma_data(V, K)
            key = (len(Ed), tuple(sorted(degs)))
            if key not in seen:
                seen.add(key)
                picks.append(K)
        picks += S[::max(1, len(S) // 25)]
        res = [analyse(rep_from_ports(K, gamma_data(V, K)[0], 1)) for K in picks]
        res_j = {(r['j'], r['k']) for r in res}
        claim(res_j == {(1, 1)}, 'C', '%s Gram representation at k=1 (inner dimension 9 = 8k + j): j = k = 1 on %d choices of K' % (name, len(res)))
        report('P+C', '%s Gram, k=1, F_2' % name, res, need_tight=True)
    # (b) Gram tensor I_3 with random port scalings
    for name in ('P104', 'P120'):
        V, S = sets8[name]
        picks = S[::max(1, len(S) // 8)][:8]
        res = [analyse(rep_from_ports(K, gamma_data(V, K)[0], 3, rng, scale=True)) for K in picks]
        claim({(r['j'], r['k']) for r in res} == {(3, 3)}, 'C', '%s Gram tensor I_3 with random port scalings: j = k = 3' % name)
        report('P+C', '%s Gram tensor I_3, random scalings, F_2' % name, res, need_tight=True)
    # (c) the 14-port witness, k = 2, rank 17 (j = 1 < k): minimum degree < 4, so no contradiction
    w = load('witness14.json')
    Kw = [PORTS[i] for i in w['K']]
    others = [PORTS[i] for i in w['others']]
    Ed = edge_ports(Kw + others, Kw)
    claim(len(Ed) == 6 and sorted(t for t, _ in Ed) == sorted(others), 'C', 'witness: the six extra ports are exactly the edge ports of K0')
    edges = {t: A for t, A in Ed}
    order = [t for t in others]
    kk, jj, m = w['k'], 1, 8
    for p in (2, 3):
        rep = new_rep(p, kk, m, jj, [edges[t] for t in order],
                      {(a, b) for a in range(14) for b in range(a + 1, 14)
                       if dot((Kw + order)[a], (Kw + order)[b]) == 0})
        r = m * kk + jj
        for a, idx in enumerate(w['K'] + w['others']):
            rows = []
            for cc in w['coords'][str(idx)]:
                row = [0] * r
                row[cc] = 1
                rows.append(row)
            if a < m:
                rep['W'][a], rep['U'][a] = rows, [list(x) for x in rows]
            else:
                rep['W'][a], rep['U'][a] = rows, [list(x) for x in rows]
        # coordinates in the file: block of i-th K element is 2i, 2i+1; extra coordinate 16 (matches the gauge)
        res = analyse(rep)
        n_orth = 2 * len(rep['orth'])
        Bfull = [[0] * 28 for _ in range(28)]
        for a in range(14):
            for b in range(14):
                blk = mmT(rep['W'][a], rep['U'][b], p)
                for x in range(2):
                    for y in range(2):
                        Bfull[2 * a + x][2 * b + y] = blk[x][y]
        rk = rank_p(Bfull, p)
        claim(rk == 17 and not res['prob'] and n_orth == 150, 'C', 'witness over F_%d: 14-port 2-block pattern, B 28x28 of rank %d < 18 = 9k, premises hold (gauge, supports, diagonal blocks I_2, zero blocks on all %d ordered orthogonal pairs)' % (p, rk, n_orth))
        report('P+C', "witness (k=2, j=1), F_%d" % p, [res], need_tight=True)
        if p == 2:
            scaled = [analyse(scale_ports(rep, rng)) for _ in range(5)]
            report('P+C', 'witness with random port scalings, F_2', scaled)
    # (d) random small-graph representations over F_2 and F_3
    graphs = {'triangle': (3, [(0, 1), (0, 2), (1, 2)]), 'star3': (4, [(0, 1), (0, 2), (0, 3)]),
              'path4': (4, [(0, 1), (1, 2), (2, 3)]), 'C4': (4, [(0, 1), (1, 2), (2, 3), (0, 3)]),
              'K4-e': (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)]),
              'K4': (4, list(itertools.combinations(range(4), 2))), 'K5': (5, list(itertools.combinations(range(5), 2)))}
    results, kinds = [], collections.Counter()
    for p in (2, 3):
        for gname, (m, edges) in graphs.items():
            reps = []
            for _ in range(2):
                reps.append(('cover', cover_rep(p, m, edges, rng)))
            reps.append(('gram', gram_abstract(p, m, edges)))
            reps.append(('gram x I_2', gram_abstract(p, m, edges, 2)))
            for _ in range(3):
                reps.append(('gram + cover', dsum(gram_abstract(p, m, edges), cover_rep(p, m, edges, rng))))
            reps.append(('gram + cover + cover', dsum(dsum(gram_abstract(p, m, edges), cover_rep(p, m, edges, rng)), cover_rep(p, m, edges, rng))))
            if gname != 'K5':
                for (k, j) in ((1, 2), (1, 3), (1, 4), (2, 2), (2, 3)):
                    for _ in range(8):
                        rr = random_solved_rep(p, m, edges, k, j, rng)
                        if rr is not None:
                            reps.append(('random solved', rr))
            for kind, rep in list(reps):
                reps.append((kind + ', scaled', scale_ports(rep, rng)))
            reps += [(kind + ', W<->U', swapped(rep)) for kind, rep in reps[:8]]
            for kind, rep in reps:
                results.append(analyse(rep))
                kinds[kind] += 1
    nrand = sum(v for k_, v in kinds.items() if k_.startswith('random solved'))
    claim(nrand >= 20, 'C', 'random linear-solved representations found on the small graphs (F_2, F_3): %d (plus %d structured ones)' % (nrand, len(results) - nrand))
    report('P+C', 'small-graph representations over F_2 and F_3 (7 graphs, 0/1 covers, Gram, direct sums, scalings, random solved)',
           results, need_gY=True, need_tight=True)
    k5 = [r for r in results if r['st']['mindeg4']]
    claim(len(k5) >= 20 and all(r['j'] >= r['k'] for r in k5), 'P+C', "Theorem 3': j >= k on all %d representations whose graph has minimum degree >= 4 (K5)" % len(k5))
    # (e) planted violations: the checker must be able to fail
    planted_a = new_rep(3, 1, 5, 0, list(itertools.combinations(range(5), 2)))
    point_labels(planted_a)
    for i, (c, d) in enumerate(planted_a['edges']):
        row = [0] * 5
        row[c] = row[d] = 1
        planted_a['W'][5 + i] = [row]
        planted_a['U'][5 + i] = [[2 * x % 3 for x in row]]          # B_TT = 2*2 = 1 mod 3, but the star zeros are gone
    res_a = analyse(planted_a)
    claim(res_a['prob'] and any('(LR)' in v for v in res_a['viol']) and any('Theorem 3' in v for v in res_a['viol']), 'C',
          'planted violation A (K5 over F_3, edge ports e_c+e_d with j=0, star zeros dropped): premises flagged, (LR) violated (%d times), j >= k fails'
          % sum('(LR)' in v for v in res_a['viol']))
    b = cover_rep(2, 5, list(itertools.combinations(range(5), 2)), random.Random(5))
    planted_b = dict(b, W=dict(b['W']), U=dict(b['U']))
    target = 5 + b['edges'].index((0, 1))
    row = [0] * (5 + b['j'])
    row[2] = 1
    planted_b['W'][target] = [list(row)]
    planted_b['U'][target] = [list(row)]
    res_b = analyse(planted_b)
    claim(res_b['prob'] and any(v.startswith("(E')") or v.startswith('(LR)') or v.startswith('(Star') or 'containment' in v for v in res_b['viol']), 'C',
          'planted violation B (K5 cover representation with port T_01 moved onto the coordinate of point 2, mask broken): premises flagged, inequality violated (%s)'
          % '; '.join(sorted({v.split(' at')[0].split(':')[0] for v in res_b['viol']})[:3]))
    # a control: a valid rep with the same graph passes
    ctl = analyse(dsum(gram_abstract(2, 5, list(itertools.combinations(range(5), 2))), cover_rep(2, 5, list(itertools.combinations(range(5), 2)), random.Random(5))))
    claim(not ctl['prob'] and not ctl['viol'], 'C', 'control: a valid K5 representation (Gram + cover, k=2) raises neither flags nor violations')


# ----------------------------------------------------------------------------------------------------------
# Section 3: corollaries on the abstract graphs G_Gamma
# ----------------------------------------------------------------------------------------------------------
def g_graph(m, edges):
    """G_Gamma: points, pairs (edge ports); point ~ edge iff incident; edges ~ iff disjoint; points pairwise non-adjacent."""
    nP = m + len(edges)
    orth = abstract_orth(m, edges)
    adj = {a: set() for a in range(nP)}
    for a in range(nP):
        for b in range(nP):
            if a != b and (min(a, b), max(a, b)) not in orth:
                adj[a].add(b)
    return adj


def f2_rank_I_plus_A(adj):
    n = len(adj)
    rows = [[1 if (a == b or b in adj[a]) else 0 for b in range(n)] for a in range(n)]
    return rank_p(rows, 2)


def girth(adj):
    best = 99
    for s in adj:
        d, par, q = {s: 0}, {s: None}, [s]
        for x in q:
            for y in adj[x]:
                if y not in d:
                    d[y], par[y] = d[x] + 1, x
                    q.append(y)
                elif par[x] != y:
                    best = min(best, d[x] + d[y] + 1)
    return best


def section_corollaries():
    for n in (5, 6, 7):
        edges = list(itertools.combinations(range(n), 2))
        res = []
        for p in (2, 3, 5):
            res.append(analyse(gram_abstract(p, n, edges)))
        claim(all(not r['prob'] and not r['viol'] and r['j'] == 1 and r['k'] == 1 for r in res), 'P+C',
              "G_{K_%d}: the Gram representation (vectors e_c, e_c+e_d+v, <v,v>=-1) is valid over F_2, F_3, F_5 with rank %d = n+1; "
              "Theorem 3' (n'=%d, E=%d, min degree %d >= 4) gives rank >= n+1 per block, so H_f(G_{K_%d}) = %d"
              % (n, n + 1, n, len(edges), n - 1, n, n + 1))
    # Petersen = G_{K4}
    m, edges = 4, list(itertools.combinations(range(4), 2))
    adj = g_graph(m, edges)
    cubic = all(len(a) == 3 for a in adj.values())
    claim(len(adj) == 10 and cubic and girth(adj) == 5, 'C', 'G_{K4} has 10 vertices, is cubic and has girth 5')
    # explicit isomorphism with Kneser K(5,2): point a -> {a,5}, pair {b,c} -> {1,2,3,4} minus {b,c}
    img = {}
    for a in range(4):
        img[a] = frozenset((a + 1, 5))
    for i, (b, c) in enumerate(edges):
        img[4 + i] = frozenset({1, 2, 3, 4} - {b + 1, c + 1})
    kn = {a: {b for b in img if a != b and not (img[a] & img[b])} for a in img}
    claim(len(set(img.values())) == 10 and kn == adj, 'C', 'the map point a -> {a,5}, pair {b,c} -> {1,2,3,4} minus {b,c} is an isomorphism G_{K4} -> Kneser K(5,2) = Petersen graph')
    claim(f2_rank_I_plus_A(adj) == 5, 'C', 'the F_2 rank of I + A(Petersen) is 5, so H(Petersen; F_2) <= 5, consistent with the proved k=1 floor 5')
    # Theorem 3' general form for K4: Lambda = 3/2 < 2, E = 6, n' = 4
    E, n = 6, 4
    bound = Fr(E - n, n + sum(max(Fr(3, 2) - 2, 0) for _ in range(n)))
    claim(bound == Fr(1, 2), 'P+C', "Petersen: Theorem 3' general form gives j/k >= (E-n')/(n'+sum (Lambda-2)^+) = 2/4, so rank >= 4.5 k and H_f(Petersen; F) >= 9/2 over every field")
    res = []
    rng = random.Random(7)
    for p in (2, 3):
        for _ in range(6):
            res.append(analyse(dsum(gram_abstract(p, m, edges), cover_rep(p, m, edges, rng))))
        res.append(analyse(gram_abstract(p, m, edges)))
    report('P+C', 'Petersen (K4) representations, F_2 and F_3', res)
    claim(all(Fr(r['j'], r['k']) >= Fr(1, 2) for r in res), 'P+C', 'every checked Petersen representation has j/k >= 1/2 (best seen: Gram, j/k = 1, ratio (4+1)/1 = 5)')


# ----------------------------------------------------------------------------------------------------------
# Section 4: restriction of scalars (field-only dependence), F_4 over F_2
# ----------------------------------------------------------------------------------------------------------
def f4_mul(a, b):
    r = 0
    for i in range(2):
        if (b >> i) & 1:
            r ^= a << i
    if r & 4:
        r ^= 0b111
    return r


def f4_inv(a):
    return next(b for b in range(1, 4) if f4_mul(a, b) == 1)


def f4_rank(M):
    A = [list(r) for r in M]
    rk, n = 0, len(A)
    for c in range(len(A[0])):
        piv = next((i for i in range(rk, n) if A[i][c]), None)
        if piv is None:
            continue
        A[rk], A[piv] = A[piv], A[rk]
        inv = f4_inv(A[rk][c])
        A[rk] = [f4_mul(inv, x) for x in A[rk]]
        for i in range(n):
            if i != rk and A[i][c]:
                f = A[i][c]
                A[i] = [x ^ f4_mul(f, y) for x, y in zip(A[i], A[rk])]
        rk += 1
    return rk


def rho_entry(a):
    # multiplication by a in the F_2-basis {1, w}: columns a*1 and a*w; elements are 2-bit ints (bit 1 = w)
    c1, c2 = a, f4_mul(a, 2)
    return [[c1 & 1, c2 & 1], [(c1 >> 1) & 1, (c2 >> 1) & 1]]


def rho(M):
    out = []
    for row in M:
        blocks = [rho_entry(a) for a in row]
        for t in range(2):
            out.append([blocks[b][t][s] for b in range(len(row)) for s in range(2)])
    return out


def f4_mm(A, B):
    return [[__import__('functools').reduce(lambda x, y: x ^ y, (f4_mul(A[i][t], B[t][j]) for t in range(len(B))), 0)
             for j in range(len(B[0]))] for i in range(len(A))]


def section_scalars():
    rng = random.Random(4)
    ok_hom = ok_rank = True
    for _ in range(60):
        n = rng.choice((2, 3, 4))
        A = [[rng.randrange(4) for _ in range(n)] for _ in range(n)]
        Bm = [[rng.randrange(4) for _ in range(n)] for _ in range(n)]
        ok_hom &= rho(f4_mm(A, Bm)) == mm(rho(A), rho(Bm), 2)
        ok_rank &= rank_p(rho(A), 2) == 2 * f4_rank(A)
    claim(ok_hom and ok_rank and rho([[1]]) == ident(2) and rho([[0]]) == zeros(2, 2), 'P+C',
          'restriction of scalars F_4 -> F_2: rho(AB) = rho(A) rho(B), rho(1) = I_2, rho(0) = 0, rank_F2 rho(A) = 2 rank_F4 A (60 random matrices)')


# ----------------------------------------------------------------------------------------------------------
# Section 5: recorded solver rows (read from data/sat_rows.json; nothing is solved here)
# ----------------------------------------------------------------------------------------------------------
def section_rows():
    rows = load('sat_rows.json')
    inst = rows['instances']
    info = {}
    for name, d in inst.items():
        K = [PORTS[i] for i in d['K']]
        E = [PORTS[i] for i in d['edge_ports']]
        Ed = [(t, tuple(i for i, c in enumerate(K) if dot(t, c))) for t in E]
        deg = collections.Counter(c for _, A in Ed for c in A)
        okcfg = (all(dot(a, b) == 0 for a, b in itertools.combinations(K, 2)) and all(len(A) == 2 for _, A in Ed)
                 and len({A for _, A in Ed}) == len(Ed)
                 and all(dot(s, t) == 0 for (s, A), (t, B) in itertools.combinations(Ed, 2) if len(set(A) & set(B)) == 1))
        nz = [c for c in range(len(K)) if deg[c] > 0]
        npr, Ecount = len(nz), len(E)
        lam = sum(max(Fr(deg[c], 2) - 2, 0) for c in nz)
        thr = Fr(Ecount - npr) / (npr + lam)             # Theorem 3' general form: j/k >= thr
        info[name] = dict(n=len(K), thr=thr)
        claim(okcfg and (len(K), npr, Ecount, min(deg[c] for c in nz)) == tuple(d['shape']), 'C',
              "recorded instance %s: %d orthogonal points (%d non-isolated), %d edge ports with distinct pairs, minimum degree %d, "
              "edge ports at one vertex orthogonal; Theorem 3' gives j/k >= %s" % (name, len(K), npr, Ecount, d['shape'][3], thr))
    decided = [r for r in rows['rows'] if r['result'] in ('SAT', 'UNSAT')]
    for r in rows['rows']:
        i = info[r['instance']]
        r['_j'] = r['rank'] - i['n'] * r['k']
        r['_pred'] = Fr(r['_j']) < i['thr'] * r['k']        # theorem says infeasible
    sat = [r for r in decided if r['result'] == 'SAT']
    claim(len(sat) >= 6 and not any(r['_pred'] for r in sat), 'R',
          "recorded rows: none of the %d SAT rows lies below the Theorem 3' threshold" % len(sat))
    pred = [r for r in decided if r['_pred']]
    claim(len(pred) >= 3 and all(r['result'] == 'UNSAT' for r in pred), 'R',
          "recorded rows: every decided row that Theorem 3' predicts infeasible came back UNSAT (%d rows: %s)" % (len(pred), ', '.join(r['id'] for r in pred)))
    claim(all(r['result'] == 'SAT' for r in decided if r.get('role') == 'control'), 'R',
          'recorded rows: every same-size control (decided) came back SAT (%d controls)' % sum(1 for r in decided if r.get('role') == 'control'))
    probe = [r for r in decided if r.get('role') == 'probe']
    claim(len(probe) == 2 and all(r['result'] == 'UNSAT' and not r['_pred'] for r in probe), 'R',
          "recorded sharpness probe (Petersen, k=2, rank 9, j/k = 1/2 = the threshold): allowed by Theorem 3', answered UNSAT with and without symmetry breaking")
    und = [r for r in rows['rows'] if r['result'] not in ('SAT', 'UNSAT')]
    claim(len(und) >= 3 and all(r.get('used') is False for r in und), 'R',
          'recorded undecided runs (k=6 rank 53 and its rank-54 control, k=4 rank 17 without symmetry breaking) are flagged not used (%d runs)' % len(und))


def main():
    systems, sets8 = section_ports()
    section_reps(systems, sets8)
    section_corollaries()
    section_scalars()
    section_rows()
    if FAILS:
        print('FAILED %d claim(s) in %.1f s' % (len(FAILS), time.time() - T0))
        sys.exit(1)
    print('PASS_P104_PORT_WINDOW_NINE (%.1f s)' % (time.time() - T0))


if __name__ == '__main__':
    main()
