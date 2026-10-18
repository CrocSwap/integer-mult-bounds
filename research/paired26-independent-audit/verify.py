"""Separately authored audit of PR1624's fixed paired26 completion minimum 62.

Written from the prose of PR1624's proof.md (head 712a9b9a) only; PR1624's
verify.py and audit.py were not read. Every finite premise that the written
lower bound uses is recomputed here with exact integer/Fraction arithmetic, and
the attaining decoder plus all 256 optimal classes are expanded entrywise.

A separate binding stage runs merged PR1020's own charge code
(research/root-pair-first-drop-seed48) on its 69 decoder and on the 62 witness.
That stage imports predecessor code on purpose; it is a binding check, not an
independent implementation.

JosieElliston's Claude session 15 (substantial AI assistance). Apache-2.0.
"""
import hashlib
import importlib.util
import itertools
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRED = ROOT / 'research' / 'root-pair-first-drop-seed48'


def need(cond, reason):
    if not cond:
        raise ValueError(reason)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


# ---------------------------------------------------------------- spec data
# Transcribed from PR1624 proof.md (Sections 2, 5, 6, 8, 9).
PUNCTURE = [0, 23, 24, 25, 26, 34, 35, 36, 37, 48, 60, 61, 62, 63, 66, 67,
            72, 73, 76, 77, 78, 79, 82, 83, 88, 89]
J_LABEL = [0, 1, 2, 3, 6, 12, 20, 30, 42]
MINOR_ROWS = [1, 2, 3, 6, 12, 20, 30, 42]
A0 = [Q(x, 2) for x in (1, -1, -1, -1, 1, 1, -1, 1)]
B0 = [Q(x) for x in (0, 0, 0, 0, 0, 0, -2, 2)]
# root index: (label dimension, live support size, annihilator functionals)
TABLE = {
    0: (7, 31, [1, 140, 141]), 23: (8, 43, [121]), 24: (8, 42, [117]),
    25: (8, 43, [118]), 26: (8, 42, [122]), 30: (8, 33, [12]),
    34: (8, 43, [244]), 35: (8, 42, [248]), 36: (8, 43, [251]),
    37: (8, 42, [247]), 48: (8, 43, [286]), 60: (8, 42, [382]),
    61: (8, 43, [370]), 62: (8, 42, [355]), 63: (8, 43, [367]),
    66: (8, 43, [334]), 67: (8, 42, [322]), 72: (8, 42, [336]),
    73: (8, 43, [348]), 76: (8, 42, [499]), 77: (8, 43, [511]),
    78: (8, 42, [494]), 79: (8, 43, [482]), 82: (8, 43, [451]),
    83: (8, 42, [463]), 88: (8, 42, [477]), 89: (8, 43, [465]),
}
B_CANDIDATES = [23, 25, 30, 34, 36, 61, 63, 66, 73, 77, 79, 82, 89]
C_DOTS = [-1, -1, 2, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1]
PAIRS = [(23, 34), (25, 36), (61, 77), (63, 79), (66, 82), (73, 89)]
WITNESS_B_ROOTS = [23, 25, 30, 61, 63, 66, 73]
WITNESS_A_ROWS = [
    ['1/2', 0, 0, 2, 1, 1, 1, 1], ['-1/2', 1, 1, 2, 0, 0, 0, 0],
    ['-1/2', 1, 1, 0, 0, 0, 0, 0], ['-1/2', 0, 0, 0, -1, -1, 1, 1],
    ['1/2', 0, 0, 0, -1, 1, -1, 1], ['1/2', 0, 0, 0, 1, -1, -1, 1],
    ['-1/2', -1, 1, 0, 0, 0, 0, 0], ['1/2', -1, 1, 0, 0, 0, 0, 0]]
WITNESS_B_ROWS = [
    [0, 0, 0, 0, '1/2', '1/2', '1/2', '1/2'], [0, 0, 0, 1, '-1/2', '-1/2', '-1/2', '-1/2'],
    [0, 1, 1, -1, '1/2', '1/2', '1/2', '1/2'], [0, 0, 0, 0, '-1/2', '-1/2', '1/2', '1/2'],
    [0, 0, 0, 0, '-1/2', '1/2', '-1/2', '1/2'], [0, 0, 0, 0, '1/2', '-1/2', '-1/2', '1/2'],
    [-2, -1, 0, 0, '1/2', '1/2', '-1/2', '1/2'], [2, 0, 1, 0, '-1/2', '-1/2', '1/2', '-1/2']]
WITNESS_TABLE = [(43, 31, 8, 7, 6)] + [(73, 43, 9, 8, 8)] * 2 + [(45, 33, 9, 8, 8)] + [(73, 43, 9, 8, 8)] * 4


# ---------------------------------------------------------------- geometry
def doubled_roots():
    out = set()
    for i, j in itertools.combinations(range(8), 2):
        for s, t in itertools.product((-2, 2), repeat=2):
            v = [0] * 8
            v[i], v[j] = s, t
            out.add(tuple(v))
    for v in itertools.product((-1, 1), repeat=8):
        if sum(x < 0 for x in v) % 2 == 0:
            out.add(v)
    reps = {max(v, tuple(-x for x in v)) for v in out}
    return sorted(reps)


def f2_rank(rows):
    """Rank of F2 row vectors given as ints (lowest-set-bit pivoting)."""
    basis = []
    for r in rows:
        for b in basis:
            r = min(r, r ^ b)
        if r:
            basis.append(r)
            basis.sort(reverse=True)
    return len(basis)


def f2_inverse(rows, n):
    """Inverse of an n x n F2 matrix given as row bit-ints (bit j = column j)."""
    aug = [(rows[i] | (1 << (n + i))) for i in range(n)]
    for c in range(n):
        p = next((i for i in range(c, n) if aug[i] >> c & 1), None)
        need(p is not None, 'H singular over F2')
        aug[c], aug[p] = aug[p], aug[c]
        for i in range(n):
            if i != c and aug[i] >> c & 1:
                aug[i] ^= aug[c]
    return [r >> n for r in aug]


def q_rref(rows, ncols):
    """Exact rational RREF. Returns (rank, pivot columns, reduced rows)."""
    m = [[Q(x) for x in r] for r in rows]
    piv, r = [], 0
    for c in range(ncols):
        p = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        s = m[r][c]
        m[r] = [x / s for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [x - f * y for x, y in zip(m[i], m[r])]
        piv.append(c)
        r += 1
        if r == len(m):
            break
    return r, piv, m[:r]


def q_nullspace(rows, ncols):
    rank, piv, red = q_rref(rows, ncols)
    free = [c for c in range(ncols) if c not in piv]
    basis = []
    for f in free:
        v = [Q(0)] * ncols
        v[f] = Q(1)
        for i, pc in enumerate(piv):
            v[pc] = -red[i][f]
        basis.append(v)
    return rank, basis


def modp_rank(rows, ncols, p=(1 << 61) - 1):
    m = [[x % p for x in r] for r in rows]
    r = 0
    for c in range(ncols):
        k = next((i for i in range(r, len(m)) if m[i][c]), None)
        if k is None:
            continue
        m[r], m[k] = m[k], m[r]
        inv = pow(m[r][c], p - 2, p)
        m[r] = [x * inv % p for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c]:
                f = m[i][c]
                m[i] = [(x - f * y) % p for x, y in zip(m[i], m[r])]
        r += 1
    return r


def det_int(mat):
    """Exact determinant by Fraction elimination (different routine from q_rref)."""
    m = [[Q(x) for x in r] for r in mat]
    n, d = len(m), Q(1)
    for c in range(n):
        p = next((i for i in range(c, n) if m[i][c] != 0), None)
        if p is None:
            return Q(0)
        if p != c:
            m[c], m[p] = m[p], m[c]
            d = -d
        d *= m[c][c]
        for i in range(c + 1, n):
            f = m[i][c] / m[c][c]
            if f:
                m[i] = [x - f * y for x, y in zip(m[i], m[c])]
    return d


def same_line(z, v):
    """True when nonzero vectors z and v are proportional."""
    k = next(i for i, x in enumerate(v) if x != 0)
    if z[k] == 0:
        return False
    s = Q(z[k]) / Q(v[k])
    return all(Q(z[i]) == s * v[i] for i in range(8))


class Model:
    def __init__(self, puncture=PUNCTURE, unit_label=True):
        self.v = doubled_roots()
        need(len(self.v) == 120 and all(dot(x, x) == 8 for x in self.v), 'E8 line model')
        off = 1 if unit_label else 0
        self.N = [[(off + dot(x, y) // 4) % 2 for y in self.v] for x in self.v]
        self.rowbits = [sum(b << j for j, b in enumerate(row)) for row in self.N]
        self.P = list(puncture)
        self.L = [i for i in range(120) if i not in set(self.P)]
        # greedy label basis: first nine independent pairing rows
        J = []
        for i in range(120):
            if f2_rank([self.rowbits[k] for k in J + [i]]) > len(J):
                J.append(i)
        self.J = J
        self.ell = [sum(self.N[i][J[c]] << c for c in range(len(J))) for i in range(120)]

    def S(self, z):
        """Actual live support of the normal z (z is a true-scale vector)."""
        return [i for i in self.L if dot(self.v[i], z) != 0]

    def d(self, z):
        return f2_rank([self.ell[i] for i in self.S(z)])

    def q(self, x, y):
        sy = self.S(y)
        mask = sum(1 << j for j in sy)
        return f2_rank([self.rowbits[i] & mask for i in self.S(x)])

    def lam(self, lam, i):
        return bin(lam & self.ell[i]).count('1') % 2


def inverse8(M):
    rank, piv, _ = q_rref(M, 8)
    need(rank == 8, 'singular basis')
    aug = [[Q(x) for x in M[i]] + [Q(int(i == j)) for j in range(8)] for i in range(8)]
    _, _, red = q_rref(aug, 16)
    return [r[8:] for r in red]


def dual_from_B(Bcols):
    """Columns b_k -> A with A B^T = 2I, returned as column lists."""
    Bm = [[Bcols[k][r] for k in range(8)] for r in range(8)]  # rows
    inv = inverse8(Bm)  # B^{-1}
    # A = 2 B^{-T}: A[r][k] = 2 * inv[k][r]
    return [[2 * inv[k][r] for r in range(8)] for k in range(8)]


def check_decoder(model, Acols, Bcols, label):
    """Normal identities, all ordered live entries, supports and charges."""
    for j in range(8):
        for k in range(8):
            need(dot(Acols[j], Bcols[k]) == 2 * (j == k), label + ': A^T B = 2I')
    Arows = [[Acols[k][r] for k in range(8)] for r in range(8)]
    Brows = [[Bcols[k][r] for k in range(8)] for r in range(8)]
    for r in range(8):
        for s in range(8):
            need(dot(Arows[r], Brows[s]) == 2 * (r == s), label + ': A B^T = 2I')
    L, v = model.L, model.v
    D = [[dot(v[i], Acols[k]) / 2 for k in range(8)] for i in L]
    T = [[dot(v[i], Bcols[k]) / 2 for k in range(8)] for i in L]
    zero_rhs = 0
    for a, i in enumerate(L):
        for b, j in enumerate(L):
            rhs = Q(dot(v[i], v[j]), 2)  # 2 r_i . r_j with r = v/2
            zero_rhs += rhs == 0
            need(dot(D[a], T[b]) == rhs, label + ': all-entry identity')
    terms = []
    for k in range(8):
        sa = [L[a] for a in range(len(L)) if D[a][k] != 0]
        sb = [L[b] for b in range(len(L)) if T[b][k] != 0]
        need(sa == model.S(Acols[k]) and sb == model.S(Bcols[k]), label + ': support')
        mask = sum(1 << j for j in sb)
        cost = f2_rank([model.rowbits[i] & mask for i in sa])
        dense = q_dense_f2_rank([[model.N[i][j] for j in sb] for i in sa])
        need(cost == dense, label + ': two F2 ranks agree')
        terms.append((len(sa), len(sb), f2_rank([model.ell[i] for i in sa]),
                      f2_rank([model.ell[i] for i in sb]), cost))
    return terms, zero_rhs


def q_dense_f2_rank(mat):
    m = [list(r) for r in mat]
    if not m:
        return 0
    r = 0
    for c in range(len(m[0])):
        p = next((i for i in range(r, len(m)) if m[i][c]), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        for i in range(len(m)):
            if i != r and m[i][c]:
                m[i] = [(x ^ y) for x, y in zip(m[i], m[r])]
        r += 1
    return r


# ---------------------------------------------------------------- stages
def stage_geometry(M, out):
    need(M.L == sorted(set(range(120)) - set(PUNCTURE)) and len(M.L) == 94, 'live set')
    need(f2_rank(M.rowbits) == 9, 'ambient pairing rank 9')
    need(M.J == J_LABEL, 'greedy label basis')
    H = [sum(M.N[J_LABEL[r]][J_LABEL[c]] << c for c in range(9)) for r in range(9)]
    Hi = f2_inverse(H, 9)
    for i in range(120):
        # u = ell_i H^{-1} (row vector)
        u = 0
        for r in range(9):
            if M.ell[i] >> r & 1:
                u ^= Hi[r]
        for j in range(120):
            need(bin(u & M.ell[j]).count('1') % 2 == M.N[i][j], 'N = ell H^-1 ell^T')
    need(f2_rank([M.rowbits[i] & sum(1 << j for j in M.L) for i in M.L]) == 9, 'live pairing rank 9')
    need(det_int([M.v[i] for i in MINOR_ROWS]) == -256, 'live doubled-root minor -256')
    need(M.q(A0, B0) == 6 and M.d(A0) == 8 and M.d(B0) == 7, 'designated pair (8,7) cost 6')
    need(dot(A0, B0) == 2, 'a . b = 2')
    out['geometry'] = {'live': 94, 'pairing_rank': 9, 'J_label': M.J, 'minor': -256,
                       'checked_bilinear_entries': 14400, 'designated_pair': [8, 7, 6]}


def stage_kernels(M, out):
    """Sections 4-5: all 511 annihilator kernels, exact rank and kernel lines."""
    ranks = {}
    lines = {}
    for lam in range(1, 512):
        Z = [M.v[i] for i in M.L if M.lam(lam, i)]
        rank, ker = q_nullspace(Z, 8)
        need(modp_rank(Z, 8) == rank, 'mod-p rank agrees')
        need(rank >= 7, 'no kernel of dimension >= 2 (lambda=%d)' % lam)
        ranks[rank] = ranks.get(rank, 0) + 1
        if rank == 7:
            z = ker[0]
            need(all(dot(row, z) == 0 for row in Z), 'kernel vector annihilates every row')
            hit = [j for j in range(120) if same_line(z, M.v[j])]
            need(len(hit) == 1, 'rank-7 kernel is a root line')
            lines.setdefault(hit[0], []).append(lam)
    need(ranks == {8: 482, 7: 29}, 'rank census 482/29')
    need(sorted(lines) == sorted(set(PUNCTURE) | {30}), 'reduced lines = P u {30}')
    inventory = {}
    for j, lams in sorted(lines.items()):
        z = [Q(x, 2) for x in M.v[j]]
        dim, size = M.d(z), len(M.S(z))
        # annihilator of W(z) by direct enumeration, cross-checking the kernel route
        W = [M.ell[i] for i in M.S(z)]
        ann = [lam for lam in range(1, 512) if all(bin(lam & w).count('1') % 2 == 0 for w in W)]
        need(ann == sorted(lams), 'annihilator by enumeration = kernel route')
        inventory[j] = (dim, size, ann)
    compare_table(inventory, TABLE)
    M.inventory = inventory
    # every other nonzero normal has d = 9: by (4.1) and the census above.
    out['kernels'] = {'functionals': 511, 'rank8': 482, 'rank7': 29, 'lines': len(lines),
                      'dim7_lines': [j for j in lines if inventory[j][0] == 7]}
    return sorted(lines)


def compare_table(inventory, table):
    """Compare the recomputed reduced-line inventory with the Section 5 table."""
    need(sorted(inventory) == sorted(table), 'table lines')
    for j in sorted(table):
        need(inventory[j] == table[j], 'table row for root %d' % j)


def check_claim(terms, claimed):
    need([t[4] for t in terms] == list(claimed), 'claimed charges')
    return sum(claimed)


def stage_compat(M, lines, out):
    """Section 6: perp intersections, dot products and charges."""
    a_perp = [j for j in lines if dot(M.v[j], A0) == 0]
    b_perp = [j for j in lines if dot(M.v[j], B0) == 0]
    need(b_perp == [30], 'reduced A directions in b-perp = {r30}')
    need(a_perp == B_CANDIDATES, 'reduced B directions in a-perp = the 13')
    need(0 not in a_perp and 0 not in b_perp, 'r0 excluded from both sides')
    c = [Q(x, 2) for x in M.v[30]]
    need(c == [0, Q(1), Q(-1), 0, 0, 0, 0, 0], 'c = r30')
    cd = [dot(c, [Q(x, 2) for x in M.v[j]]) for j in B_CANDIDATES]
    need(cd == C_DOTS and 0 not in cd, 'c . r_j over the 13, none zero')
    qs = [M.q(c, [Q(x, 2) for x in M.v[j]]) for j in B_CANDIDATES]
    need(qs == [7 if j == 30 else 8 for j in B_CANDIDATES], 'q(c, r_j)')
    need(all(TABLE[j][0] == 8 for j in B_CANDIDATES), 'all 13 have d = 8')
    out['compatibility'] = {'b_perp': b_perp, 'a_perp': a_perp, 'c_dots': cd, 'q_c': qs}


def root(M, j):
    return [Q(x, 2) for x in M.v[j]]


def stage_witness(M, out):
    """Section 8: rebuild A = 2 B^-T from the B choice and compare with the display."""
    Bcols = [B0] + [root(M, j) for j in WITNESS_B_ROOTS]
    Acols = dual_from_B(Bcols)
    Ad = [[Q(x) for x in r] for r in WITNESS_A_ROWS]
    Bd = [[Q(x) for x in r] for r in WITNESS_B_ROWS]
    need([[Acols[k][r] for k in range(8)] for r in range(8)] == Ad, 'displayed A = 2 B^-T')
    need([[Bcols[k][r] for k in range(8)] for r in range(8)] == Bd, 'displayed B = chosen roots')
    need(Acols[0] == A0 and Bcols[0] == B0, 'first pair exact')
    terms, zero = check_decoder(M, Acols, Bcols, 'witness62')
    need(check_claim(terms, [6] + [8] * 7) == 62, 'cost 62')
    need(terms == WITNESS_TABLE, 'Section 8 term table')
    M.witness_terms = terms
    need(zero == 4572, 'zero right-hand sides 4572')
    out['witness62'] = {'term_costs': [t[4] for t in terms], 'total': 62, 'entries': 8836,
                        'zero_rhs_entries': zero}
    return Acols, Bcols


def stage_classes(M, out):
    """Section 9: all 256 independent 7-sets, each expanded entrywise."""
    c = root(M, 30)
    for x, y in PAIRS:
        need([p + q for p, q in zip(root(M, x), c)] == root(M, y), 'x_j + c = partner')
    cols = [[2 * x for x in B0], M.v[30], M.v[23], M.v[25], M.v[61], M.v[63], M.v[66], M.v[73]]
    need(det_int([[cols[k][r] for k in range(8)] for r in range(8)]) == 1024, 'det 1024')
    indep = []
    for S in itertools.combinations(B_CANDIDATES, 7):
        rank, _, _ = q_rref([M.v[j] for j in S], 8)
        if rank == 7:
            indep.append(S)
    need(len(indep) == 256, '256 independent seven-sets')
    structural = set()
    for take_c in (True, False):
        if take_c:
            for pick in itertools.product(*PAIRS):
                structural.add(tuple(sorted((30,) + pick)))
        else:
            for dbl in range(6):
                for pick in itertools.product(*[p for i, p in enumerate(PAIRS) if i != dbl]):
                    structural.add(tuple(sorted(PAIRS[dbl] + pick)))
    need(structural == set(indep), 'structural 2^6 + 6*2^5 formula')
    costs = {}
    for S in indep:
        Bcols = [B0] + [root(M, j) for j in S]
        Acols = dual_from_B(Bcols)
        need(Acols[0] == A0, 'first A column exactly a')
        need(not any(same_line(Acols[k], c) for k in range(1, 8)), 'no residual A on c')
        terms, _ = check_decoder(M, Acols, Bcols, 'class %s' % (S,))
        tot = sum(t[4] for t in terms)
        costs[tot] = costs.get(tot, 0) + 1
    need(costs == {62: 256}, 'all 256 classes cost 62')
    out['classes'] = {'independent_sets': 256, 'expanded_entrywise': 256, 'cost_62': 256}


def stage_branch67(M, out):
    """Own Case II witness: first pair (a,b), second pair (c,c), six generic pairs."""
    c = root(M, 30)
    need(dot(c, c) == 2 and dot(c, A0) == 0 and dot(c, B0) == 0, 'c fits the second pair')
    # residual space U = {a, c}^perp for B columns: pick small integer vectors,
    # project to the required perps by solving with the fixed duals.
    best = None
    for seed in range(1, 40):
        cand = []
        x = seed
        for k in range(6):
            vec = []
            for r in range(8):
                x = (x * 1103515245 + 12345) % (1 << 31)
                vec.append(Q(x % 7 - 3))
            # make b_k perpendicular to a and c (A columns a, c are fixed)
            vec = [vec[r] - dot(vec, A0) / dot(B0, A0) * B0[r] for r in range(8)]
            vec = [vec[r] - dot(vec, c) / dot(c, c) * c[r] for r in range(8)]
            cand.append(vec)
        Bcols = [B0, c] + cand
        rank, _, _ = q_rref([[Bcols[k][r] for r in range(8)] for k in range(8)], 8)
        if rank < 8:
            continue
        Acols = dual_from_B(Bcols)
        if Acols[0] != A0 or not same_line(Acols[1], c):
            continue
        terms, _ = check_decoder(M, Acols, Bcols, 'branch67')
        best = [t[4] for t in terms]
        break
    need(best == [6, 7, 9, 9, 9, 9, 9, 9], 'own branch-67 witness attains 67')
    out['branch67_own_witness'] = {'term_costs': best, 'total': sum(best)}


def gdot(x, y):
    """Ordinary (non-conjugating) dot product of Gaussian-rational vectors given as (re, im)."""
    (xr, xi), (yr, yi) = x, y
    return (dot(xr, yr) - dot(xi, yi), dot(xr, yi) + dot(xi, yr))


def gsupport(M, z):
    zr, zi = z
    return [i for i in M.L if dot(M.v[i], zr) != 0 or dot(M.v[i], zi) != 0]


def section10_example(M, Acols, Bcols):
    """Proof section 10: isotropic complex shear of the 62 witness and its real look-alike."""
    zero = [Q(0)] * 8
    Ac = [(col, zero) for col in Acols]
    Bc = [(col, zero) for col in Bcols]
    Ac[1] = (Acols[1], Acols[2])                       # A1 + i A2
    Bc[2] = (Bcols[2], [-x for x in Bcols[1]])         # B2 - i B1
    need(Ac[0] == (A0, zero) and Bc[0] == (B0, zero), 'section 10: designated pair unchanged')
    need(gdot(Ac[1], Ac[1]) == (0, 0), 'section 10: A column is isotropic')
    for j in range(8):
        for k in range(8):
            need(gdot(Ac[j], Bc[k]) == (2 * (j == k), 0), 'section 10: A^T B = 2I over Q(i)')
    # square matrices: A^T B = 2I implies A B^T = 2I, so D T^T = 2 R R^T on every entry.
    costs = []
    for k in range(8):
        sa, sb = gsupport(M, Ac[k]), gsupport(M, Bc[k])
        mask = sum(1 << j for j in sb)
        costs.append(f2_rank([M.rowbits[i] & mask for i in sa]))
    need(costs == [6, 8, 9, 8, 8, 8, 8, 8], 'section 10: complex example charges (6,8,9,8,...) = 63')
    # conjugate transpose gives 4 - 4i at live position (root 1, root 1)
    Dc = [(dot(M.v[1], z[0]) / 2, dot(M.v[1], z[1]) / 2) for z in Ac]
    Tc = [(dot(M.v[1], z[0]) / 2, dot(M.v[1], z[1]) / 2) for z in Bc]
    herm = (sum(d[0] * t[0] + d[1] * t[1] for d, t in zip(Dc, Tc)),
            sum(d[1] * t[0] - d[0] * t[1] for d, t in zip(Dc, Tc)))
    need(herm == (4, -4), 'section 10: conjugate transpose gives 4 - 4i at (1, 1)')
    # real look-alike: same separate supports, broken duality
    Ar = list(Acols)
    Br = list(Bcols)
    Ar[1] = [x + 2 * y for x, y in zip(Acols[1], Acols[2])]
    Br[2] = [x - 3 * y for x, y in zip(Bcols[2], Bcols[1])]
    for k in range(8):
        need(M.S(Ar[k]) == gsupport(M, Ac[k]) and M.S(Br[k]) == gsupport(M, Bc[k]),
             'section 10: real look-alike has the same separate supports')
    return costs, Ar, Br


def stage_binding(M, Acols, Bcols, out):
    """Run merged PR1020's own charge code on its 69 decoder and on the 62 witness."""
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for f in pins['files']:
        if f['usage'] != 'input':
            continue
        raw = (ROOT / f['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == f['sha256'], 'source pin: ' + f['path'])
    spec = importlib.util.spec_from_file_location('pr1020_verify', PRED / 'verify.py')
    pv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pv)
    roots, pairing, labels, viol, supports = pv.model.setup()
    need([tuple(r) for r in roots] == M.v, 'PR1020 root indexing = spec indexing')
    need(all(pairing[i] == M.rowbits[i] for i in range(120)), 'PR1020 pairing = spec N')
    puncture = sum(1 << i for i in PUNCTURE)
    cert = json.loads((PRED / 'CERTIFICATE.json').read_text(encoding='utf-8'))
    need(cert['witness_puncture'] == PUNCTURE, 'PR1020 puncture = spec P')
    A69, B69 = pv.decoder(roots, 48, 0)
    r69 = pv.decoder_check(roots, pairing, puncture, A69, B69)
    need(r69['term_costs'] == [6] + [9] * 7 and r69['copy_cost'] == 69, 'PR1020 own 69')
    need([[Q(x) for x in r] for r in cert['exact_eight_term_completion']['A']] == A69, '69 A = certificate')
    need([A69[r][0] for r in range(8)] == A0 and [B69[r][0] for r in range(8)] == B0,
         'PR1020 first pair = spec (a, b)')
    A = [[Acols[k][r] for k in range(8)] for r in range(8)]
    B = [[Bcols[k][r] for k in range(8)] for r in range(8)]
    r62 = pv.decoder_check(roots, pairing, puncture, A, B)
    need(r62['term_costs'] == [6] + [8] * 7 and r62['copy_cost'] == 62, 'PR1020 code prices 62')
    # our own checker on PR1020's decoder
    t69, _ = check_decoder(M, [[A69[r][k] for r in range(8)] for k in range(8)],
                           [[B69[r][k] for r in range(8)] for k in range(8)], 'pr1020-69')
    need([t[4] for t in t69] == [6] + [9] * 7, 'own checker prices PR1020 at 69')
    out['binding'] = {'pr1020_code_on_69': r69['term_costs'], 'pr1020_code_on_62': r62['term_costs'],
                      'own_checker_on_69': [t[4] for t in t69]}


# ---------------------------------------------------------------- controls
def controls(M, Acols, Bcols):
    done = []

    def reject(label, fn, reason):
        try:
            fn()
        except ValueError as e:
            need(reason in str(e), 'control %s failed for the wrong reason: %s' % (label, e))
            done.append(label)
            return
        raise ValueError('control accepted: ' + label)

    halfB = [list(col) for col in Bcols]
    halfB[3] = [x / 2 for x in halfB[3]]
    reject('wrong dual scale', lambda: check_decoder(M, Acols, halfB, 'c1'), 'A^T B = 2I')
    _, Ar, Br = section10_example(M, Acols, Bcols)  # supports checked equal inside
    reject('separate-support real look-alike (proof sec. 10)',
           lambda: check_decoder(M, Ar, Br, 'c2'), 'A^T B = 2I')
    reject('omit unit label', lambda: need(Model(unit_label=False).J == J_LABEL, 'label basis'),
           'label basis')
    reject('25-line puncture (restore line 0)', lambda: need(
        Model(puncture=PUNCTURE[1:]).q(A0, B0) == 6, 'restored'), 'restored')
    bad_table = dict(TABLE)
    bad_table[30] = (8, 33, [13])
    reject('wrong annihilator in the table', lambda: compare_table(M.inventory, bad_table),
           'table row for root 30')
    reject('61-unit undercharge claim', lambda: check_claim(M.witness_terms, [6] + [8] * 6 + [7]),
           'claimed charges')
    reject('dependent seven-set', lambda: dual_from_B(
        [B0] + [root(M, j) for j in [23, 34, 25, 36, 30, 61, 63]]), 'singular basis')
    return done


def run():
    out = {}
    M = Model()
    stage_geometry(M, out)
    lines = stage_kernels(M, out)
    stage_compat(M, lines, out)
    Acols, Bcols = stage_witness(M, out)
    stage_classes(M, out)
    stage_branch67(M, out)
    costs10, _, _ = section10_example(M, Acols, Bcols)
    out['section10_complex_example'] = {'term_costs': costs10, 'total': sum(costs10),
                                        'real_lookalike_same_supports': True}
    stage_binding(M, Acols, Bcols, out)
    out['controls'] = controls(M, Acols, Bcols)
    return out


def main():
    out = run()
    print(json.dumps(out, sort_keys=True, default=str))
    print('PASS_PAIRED26_INDEPENDENT_AUDIT premises=sections2,4,5,6,8,9 classes=256 '
          'branch67=own pr1020_binding=69,62 controls=%d' % len(out['controls']))


if __name__ == '__main__':
    main()
