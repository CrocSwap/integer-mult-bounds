"""Exact integer realisations of the Pappus 9_3 and Desargues 10_3 configurations, structured coordinate frames, and the
three-total decoder model of #2111 (written for this package; standard library only, exact integer arithmetic).

Model (#2111 README sec. 1, #446/#595): a decoder configuration is a list of v pairs (p(t), q(t)) in Z^3 x Z^3 with
p(t).q(t) != 0.  R_j = {t : p_j(t) != 0}, A_j = {s : q_j(s) != 0}.  An admissible B over F2 has unit diagonal and B_ts = 1
(t != s) only where p(t).q(s) = 0; only entries inside some block R_j x A_j affect cost(B) = sum_j rank_F2 B[R_j, A_j].
"""
from math import gcd
import itertools


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def prim(v):
    """Primitive integer representative, first nonzero coordinate positive."""
    g = 0
    for x in v:
        g = gcd(g, x)
    assert g != 0, 'zero vector'
    v = tuple(x // g for x in v)
    s = next(x for x in v if x)
    return tuple(-x for x in v) if s < 0 else v


def det3(a, b, c):
    return dot(a, cross(b, c))


def pappus(a=(0, 1, 3), b=(0, 2, 5)):
    """Pappus 9_3: A_i = (a_i, 0, 1) on y = 0, B_j = (b_j, 1, 1) on y = z; C_k = A_iB_j x A_jB_i ({i,j,k} = {0,1,2}).
    Lines: l (y=0), m (y=z), the Pappus line through C_0, C_1, C_2, and the six cross lines A_iB_j (i != j)."""
    A = [prim((x, 0, 1)) for x in a]
    B = [prim((x, 1, 1)) for x in b]
    names = ['A0', 'A1', 'A2', 'B0', 'B1', 'B2', 'C0', 'C1', 'C2']
    cl = {(i, j): prim(cross(A[i], B[j])) for i in range(3) for j in range(3) if i != j}
    C = []
    for k in range(3):
        i, j = [x for x in range(3) if x != k]
        C.append(prim(cross(cl[(i, j)], cl[(j, i)])))
    pts = A + B + C
    lines = [prim(cross(A[0], A[1])), prim(cross(B[0], B[1])), prim(cross(C[0], C[1]))] + [cl[(i, j)] for (i, j) in sorted(cl)]
    lnames = ['l', 'm', 'pap'] + ['A%dB%d' % ij for ij in sorted(cl)]
    inc = set()
    for i in range(3):
        inc |= {('A%d' % i, 'l'), ('B%d' % i, 'm'), ('C%d' % i, 'pap')}
    for (i, j) in sorted(cl):
        k = 3 - i - j
        inc |= {('A%d' % i, 'A%dB%d' % (i, j)), ('B%d' % j, 'A%dB%d' % (i, j)), ('C%d' % k, 'A%dB%d' % (i, j))}
    return dict(name='pappus', points=pts, pnames=names, lines=lines, lnames=lnames, incidences=sorted(inc))


def desargues(O=(0, 0, 1), a=((1, 0, 1), (0, 1, 1), (2, 3, 1)), lam=(2, 3, -1)):
    """Desargues 10_3: centre O, triangles a_i and b_i = a_i + lam_i O (affine chart z = 1 for the a_i), c_ij = a_ia_j x b_ib_j.
    Lines: O a_i b_i (3), a_i a_j c_ij (3), b_i b_j c_ij (3), axis (1)."""
    O = prim(O)
    A = [prim(x) for x in a]
    B = [prim(tuple(A[i][j] + lam[i] * O[j] for j in range(3))) for i in range(3)]
    pairs = [(0, 1), (0, 2), (1, 2)]
    c = {}
    for (i, j) in pairs:
        c[(i, j)] = prim(cross(cross(A[i], A[j]), cross(B[i], B[j])))
    pts = [O] + A + B + [c[p] for p in pairs]
    pnames = ['O', 'a0', 'a1', 'a2', 'b0', 'b1', 'b2', 'c01', 'c02', 'c12']
    lines = [prim(cross(A[i], B[i])) for i in range(3)] + [prim(cross(A[i], A[j])) for (i, j) in pairs] + \
            [prim(cross(B[i], B[j])) for (i, j) in pairs] + [prim(cross(c[(0, 1)], c[(0, 2)]))]
    lnames = ['Oab0', 'Oab1', 'Oab2'] + ['a%d%d' % p for p in pairs] + ['b%d%d' % p for p in pairs] + ['axis']
    inc = set()
    for i in range(3):
        inc |= {('O', 'Oab%d' % i), ('a%d' % i, 'Oab%d' % i), ('b%d' % i, 'Oab%d' % i)}
    for (i, j) in pairs:
        for x in 'ab':
            inc |= {('%s%d' % (x, i), '%s%d%d' % (x, i, j)), ('%s%d' % (x, j), '%s%d%d' % (x, i, j)), ('c%d%d' % (i, j), '%s%d%d' % (x, i, j))}
        inc.add(('c%d%d' % (i, j), 'axis'))
    return dict(name='desargues', points=pts, pnames=pnames, lines=lines, lnames=lnames, incidences=sorted(inc))


def check_config(C, n, k):
    """Exact check: n distinct points, n distinct lines, the incidence relation dot == 0 equals the combinatorial n_3
    incidence list exactly (no extra incidences), and every point / line has exactly k incidences."""
    pts, lines = C['points'], C['lines']
    if len(set(pts)) != n or len(set(lines)) != n:
        return False
    actual = {(C['pnames'][i], C['lnames'][j]) for i in range(n) for j in range(n) if dot(pts[i], lines[j]) == 0}
    want = {tuple(x) for x in C['incidences']}
    if actual != want or len(want) != n * k:
        return False
    return all(sum(1 for (p, _) in want if p == nm) == k for nm in C['pnames']) and \
        all(sum(1 for (_, l) in want if l == nm) == k for nm in C['lnames'])


def adj(M):
    """Adjugate of a 3x3 integer matrix (rows), so adj(M) M = det(M) I."""
    c0, c1, c2 = M
    # columns of adj are the cross products of rows: adj(M)[:, i]
    r = [cross(c1, c2), cross(c2, c0), cross(c0, c1)]
    return [[r[j][i] for j in range(3)] for i in range(3)]


def matvec(M, v):
    return tuple(sum(M[i][j] * v[j] for j in range(3)) for i in range(3))


def transpose(M):
    return [[M[j][i] for j in range(3)] for i in range(3)]


def frames(C):
    """All structured frames: ('P', i, j, k) = three non-collinear configuration points sent to e_1, e_2, e_3;
    ('L', i, j, k) = three non-concurrent configuration lines sent to the coordinate lines."""
    n = len(C['points'])
    out = []
    for tri in itertools.combinations(range(n), 3):
        if det3(*[C['points'][i] for i in tri]) != 0:
            out.append(('P',) + tri)
    for tri in itertools.combinations(range(n), 3):
        if det3(*[C['lines'][i] for i in tri]) != 0:
            out.append(('L',) + tri)
    return out


def transform(C, fr):
    """Exact projective change of coordinates for a frame; returns (points', lines') as primitive integer vectors.
    Points transform by p' = G p, lines by l' = H l with H^T G = det * I, so all incidences are preserved."""
    kind, i, j, k = fr
    if kind == 'P':
        U = [C['points'][x] for x in (i, j, k)]          # rows u_1,u_2,u_3; M = U^T has them as columns
        M = transpose(U)
        G = adj(M)                                      # det(M) M^{-1}: sends u_i to det * e_i
        H = transpose(M)                                # l' = M^T l, l'_m = l . u_m
    else:
        N = [C['lines'][x] for x in (i, j, k)]          # rows l_1,l_2,l_3
        G = N                                           # p'_m = l_m . p
        H = transpose(adj(N))                           # l' = det * N^{-T} l, sends l_m to det * e_m
    P2 = [prim(matvec(G, p)) for p in C['points']]
    L2 = [prim(matvec(H, l)) for l in C['lines']]
    return P2, L2


def setup(P, Q):
    """#2111 kit.setup, re-implemented: blocks R_j, A_j and the in-block incidences 'free'."""
    v = len(P)
    R = [[t for t in range(v) if P[t][j]] for j in range(3)]
    A = [[s for s in range(v) if Q[s][j]] for j in range(3)]
    free = [(t, s) for t in range(v) for s in range(v)
            if t != s and dot(P[t], Q[s]) == 0 and any(P[t][j] and Q[s][j] for j in range(3))]
    return R, A, free


def rank2(rows):
    piv = {}
    r = 0
    for x in rows:
        while x:
            h = x.bit_length() - 1
            if h in piv:
                x ^= piv[h]
            else:
                piv[h] = x
                r += 1
                break
    return r


def cost_of(P, Q, B):
    """Exact cost of an explicit 0/1 matrix B after checking admissibility from the raw integer vectors.
    Returns None if B is not admissible."""
    v = len(P)
    for t in range(v):
        if B[t][t] != 1:
            return None
        for s in range(v):
            if t != s and B[t][s] and dot(P[t], Q[s]) != 0:
                return None
    c = 0
    for j in range(3):
        R = [t for t in range(v) if P[t][j]]
        A = [s for s in range(v) if Q[s][j]]
        c += rank2([sum(B[t][s] << i for i, s in enumerate(A)) for t in R])
    return c


def tomat(g, free, v):
    B = [[int(t == s) for s in range(v)] for t in range(v)]
    for i, (t, s) in enumerate(free):
        if g >> i & 1:
            B[t][s] = 1
    return B


def odd_diagonal(P, Q):
    """a = 0 case of #2162's 2-adic corollary: all primitive integer diagonal products odd => reduction mod 2 is a CR2
    realisation over GF(2)."""
    return all(dot(prim(P[t]), prim(Q[t])) % 2 for t in range(len(P)))
