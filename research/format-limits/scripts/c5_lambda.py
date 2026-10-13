"""Lemma lambda: a phase-frame butterfly needs sqrt(-1); a different payload ring cannot remove the butterfly layer.

The complex interface (upstream/build/sections/03-motifs.tex:568-640, 05-layers.tex:1-100) is built from the
butterfly kernel C = aI + bX on one address bit (X the bit swap), H0 = D1 C D2 with D1, D2 diagonal, and the
phase frames q_U = wt(P_U x) mod 4.  The checks below are exact (Fractions, integers mod M, sympy), no floats.

T1  length-8 synthetic (Nussbaumer) transform over R = Q[y]/(y^4+1), root y of order 8
    (upstream/build/sections/06-transforms.tex, synthetic DIF): three levels 'H0 on one address bit, then a
    twiddle y^(-k)'.  The product of the six factors equals B_8 F_8^- exactly.  The three twiddle factors are signed
    permutations (monomial, bit-legal controlled shifts); the three H0 factors are not monomial (row support 2).
T2  Fermat specialisation y -> 2, R -> Z/17: the same program is the bit-reversed length-8 NTT with root 2.
T3  Fourier mass: monomials preserve row support and a 2-point butterfly level at most doubles it; the target has
    row support 8 = 2^3 blocks, so at least 3 butterfly levels are needed, the same as the complex DFT_8.
T4  Kernel lemma over Z/M (M odd): D1 (aI+bX) D2 = u [[1,1],[1,-1]] with D1, D2 invertible diagonal, u a unit,
    aI+bX invertible, is solvable iff -1 is a square mod M, and in every solution
    lambda = (a-b)/(a+b) satisfies lambda^2 = -1 (an order-4 Walsh phase).  Brute force over the listed M.
T5  Directional-kernel lemma: for a 2x2 matrix K, conjugation of K (x) I by the address map x1 += x2 fixes K (x) I
    iff K commutes with X, i.e. K = aI + bX.
T6  The complex identities hold verbatim in Z/17 with i = 4: C^2 = X and H0 = b S C S, lambda = +-i.
T7  A REAL butterfly D1 H D2 never lies in span(I, X) (a complex d1 is needed with e1 = +-i e2).
T8  In the phase calculus a residual vector v of weight 2 mod 4 gives H^m diag(i^(wt(v) [v.x])) H^m / 2^m a
    permutation (a translation, rank 0); weights 3 and 1 do not.
real  T7 and T8 together: real kernels have no subspace-labelled directional version, and only weight-2 mod 4
    directions are free translations.
Run: python3 c5_lambda.py
"""
import itertools
import time
from fractions import Fraction as Fr
from math import gcd

import numpy as np
import sympy as sp

from report import check, finish

# ---------------------------------------------------------------------------------------------------------------
# expected values (from the recorded runs)
EXPECTED = {
    'T1_factors': (3, 3),                 # (monomial twiddle factors, non-monomial H0 factors)
    'T3_support': 8,                      # row support (ring blocks) of the length-8 transform; levels = 3
    'T3_levels': 3,
    # M -> number of solutions (a, b, e1, e2) of the kernel equation; nonzero iff -1 is a square mod M
    'T4': {3: 0, 5: 32, 7: 0, 9: 0, 11: 0, 13: 288, 15: 0, 17: 512, 21: 0, 25: 800, 29: 1568, 33: 0, 37: 2592,
           41: 3200, 45: 0, 65: 9216},
    'T6_lambda': 4,                       # (a-b)/(a+b) in Z/17 with i = 4
    'T8': {(1, 1, 0): True, (1, 1, 1): False, (1, 0, 0): False},
}

R = 4           # y^R = -1 : the ring Q[y]/(y^4+1)
T = 8           # transform length, root w = y of order 2R = 8


# ---------------------------------------------------------------------------------------------------------------
def ymul_matrix(a):
    """R x R matrix of multiplication by y^a on coefficient vectors (a signed permutation)."""
    M = [[0] * R for _ in range(R)]
    for k in range(R):
        e = (k + a) % (2 * R)
        sign = 1
        if e >= R:
            e -= R
            sign = -1
        M[e][k] = sign
    return M


def zeros(n):
    return [[Fr(0)] * n for _ in range(n)]


def matmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    C = [[Fr(0)] * p for _ in range(n)]
    for i in range(n):
        Ai = A[i]
        for k in range(m):
            if Ai[k] != 0:
                Bk, a = B[k], Ai[k]
                for j in range(p):
                    if Bk[j] != 0:
                        C[i][j] += a * Bk[j]
    return C


def put_block(i, j, M, big):
    for r in range(R):
        for c in range(R):
            big[i * R + r][j * R + c] = Fr(M[r][c])


def is_monomial(A):
    return all(sum(1 for x in row if x != 0) == 1 for row in A) and all(sum(1 for x in col if x != 0) == 1 for col in zip(*A))


def max_row_support_blocks(A):
    """row support counted in ring blocks (an R x R block is nonzero iff some entry is)."""
    n = len(A) // R
    return max(sum(1 for j in range(n) if any(A[i * R + r][j * R + c] != 0 for r in range(R) for c in range(R)))
               for i in range(n))


def rev3(j):
    return int(format(j, '03b')[::-1], 2)


def build_T1():
    target = zeros(T * R)       # bit-reversed length-8 transform: (F^- z)_j = (1/8) sum_k w^(-jk) z_k at slot rev3(j)
    for j in range(T):
        for k in range(T):
            put_block(rev3(j), k, [[Fr(x, T) for x in row] for row in ymul_matrix(-(j * k) % (2 * R))], target)

    def butterfly_level(bit):
        A = zeros(T * R)
        h = Fr(1, 2)
        for s in range(T):
            if (s >> bit) & 1:
                continue
            p = s | (1 << bit)
            for (o, i, sg) in ((s, s, 1), (s, p, 1), (p, s, 1), (p, p, -1)):
                put_block(o, i, [[h * sg * (1 if r == c else 0) for c in range(R)] for r in range(R)], A)
        return A

    def twiddle_level(bit, t):
        A = zeros(T * R)
        wt_exp = (2 * R) // t               # w_t = y^(2R/t)
        for s in range(T):
            b = (s >> bit) & 1
            k = s & ((1 << bit) - 1)
            put_block(s, s, ymul_matrix((-(wt_exp * k * b)) % (2 * R)), A)
        return A

    factors = []                            # first element is applied first
    for lev, bit in enumerate((2, 1, 0)):
        t = T >> lev
        factors.append(('H0 on bit %d' % bit, butterfly_level(bit)))
        factors.append(('twiddle w_%d^-k on bit %d' % (t, bit), twiddle_level(bit, t)))
    prog = None
    for name, Fm in factors:
        prog = Fm if prog is None else matmul(Fm, prog)
    return target, factors, prog, rev3


def reduce_mod_17(M):
    """evaluate an R-block matrix at y = 2 (ring Q[y]/(y^4+1) -> Z/17)."""
    P = 17
    n = len(M) // R
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            val = sum(M[i * R + r][j * R + 0] * (2 ** r) for r in range(R))
            out[i][j] = (val.numerator * pow(val.denominator, -1, P)) % P
    return out


def kernel_lemma(M):
    """number of solutions (a, b, e1, e2) of D1 (aI+bX) D2 = u H over Z/M and whether lambda^2 = -1 in all."""
    U = np.array([x for x in range(M) if gcd(x, M) == 1])
    isunit = np.zeros(M, dtype=bool)
    isunit[U] = True
    sols = 0
    lam_ok = True
    A = np.arange(M)
    for a in range(M):
        for b in range(M):
            if not isunit[(a * a - b * b) % M]:
                continue
            # row 1: (a e1, b e2) equal and a unit; row 2: (b e1, a e2) sums to 0 and first entry a unit
            r10 = (a * U) % M
            r11 = (b * U) % M
            r20 = (b * U) % M
            r21 = (a * U) % M
            ok = (r10[:, None] == r11[None, :]) & isunit[r10][:, None] \
                & (((r20[:, None] + r21[None, :]) % M) == 0) & isunit[r20][:, None]
            cnt = int(ok.sum())
            if cnt:
                sols += cnt
                s = (a + b) % M
                if isunit[s]:
                    lam = ((a - b) * pow(s, -1, M)) % M
                    if (lam * lam) % M != M - 1:
                        lam_ok = False
                else:
                    lam_ok = False
    return sols, lam_ok


def main():
    t_all = time.time()
    # ---- T1, T2, T3
    t0 = time.time()
    target, factors, prog, _ = build_T1()
    n_mono = sum(1 for _, F in factors if is_monomial(F))
    n_non = len(factors) - n_mono
    pattern = [(name, is_monomial(F), max_row_support_blocks(F)) for name, F in factors]
    ok_pat = all(m == name.startswith('twiddle') and s == (1 if m else 2) for name, m, s in pattern)
    check('C5.T1', prog == target and (n_mono, n_non) == EXPECTED['T1_factors'] and ok_pat,
          'product of 6 factors == B_8 F_8^- exactly; monomial twiddles %d, non-monomial H0 factors %d (row supports %s)'
          % (n_mono, n_non, [s for _, _, s in pattern]))
    P = 17
    ntt = [[0] * T for _ in range(T)]
    inv8 = pow(8, -1, P)
    for j in range(T):
        for k in range(T):
            ntt[rev3(j)][k] = (pow(2, (-(j * k)) % 16, P) * inv8) % P
    check('C5.T2', reduce_mod_17(prog) == ntt, 'program at y = 2 == bit-reversed length-8 NTT over Z/17 with root 2')
    sup_target = max_row_support_blocks(target)
    sup_ntt = max(sum(1 for x in row if x) for row in ntt)
    dft = np.exp(-2j * np.pi * np.outer(range(T), range(T)) / T) / T     # complex DFT_8: every entry has modulus 1/8
    sup_dft = int(max((np.abs(row) > 1e-12).sum() for row in dft))
    levels = (sup_target - 1).bit_length()
    check('C5.T3', sup_target == sup_ntt == sup_dft == EXPECTED['T3_support'] and levels == EXPECTED['T3_levels'],
          'row support of F_8 over R: %d blocks, of the Z/17 NTT: %d, of the complex DFT_8: %d -> >= %d butterfly levels'
          % (sup_target, sup_ntt, sup_dft, levels))
    print('  (T1-T3: %.1f s)' % (time.time() - t0), flush=True)

    # ---- T4
    t0 = time.time()
    got, allok = {}, True
    for M in EXPECTED['T4']:
        sols, lam_ok = kernel_lemma(M)
        sq = any((x * x) % M == M - 1 for x in range(M))
        got[M] = sols
        good = ((sols > 0) == sq) and (sols == 0 or lam_ok)
        allok &= good
        print('   M=%3d: -1 square=%-5s solutions=%6d lambda^2=-1 in all=%s' % (M, sq, sols, lam_ok if sols else '-'), flush=True)
    check('C5.T4', got == EXPECTED['T4'] and allok,
          'solutions exist iff -1 is a square mod M and lambda^2 = -1 in every solution, M in %s' % sorted(got))
    print('  (T4: %.1f s)' % (time.time() - t0), flush=True)

    # ---- T5
    a_, b_, c_, d_ = sp.symbols('a b c d')
    K = sp.Matrix([[a_, b_], [c_, d_]])
    KI = sp.kronecker_product(K, sp.eye(2))
    Pn = sp.zeros(4, 4)
    for x1 in (0, 1):
        for x2 in (0, 1):
            Pn[2 * (x1 ^ x2) + x2, 2 * x1 + x2] = 1
    cond = sp.simplify(Pn * KI * Pn.inv() - KI)
    sol = sp.solve(list(cond), [c_, d_], dict=True)
    check('C5.T5', sol == [{c_: b_, d_: a_}], 'conjugation by x1 += x2 fixes K (x) I  <=>  %s, i.e. K = aI + bX' % sol)

    # ---- T6: Z/17 with i = 4
    M, i = 17, 4
    assert (i * i) % M == M - 1
    h = pow(2, -1, M)
    a = ((1 + i) * h) % M
    b = ((1 - i) * h) % M

    def mm(A, B):
        return [[sum(A[r][k] * B[k][c] for k in range(2)) % M for c in range(2)] for r in range(2)]
    C = [[a, b], [b, a]]
    X = [[0, 1], [1, 0]]
    S = [[1, 0], [0, i]]
    H0 = [[h, h], [h, (-h) % M]]
    bSCS = [[(b * x) % M for x in row] for row in mm(mm(S, C), S)]
    lam = ((a - b) * pow((a + b) % M, -1, M)) % M
    check('C5.T6', mm(C, C) == X and bSCS == H0 and lam == EXPECTED['T6_lambda'] and lam in {i, M - i},
          'Z/17, i=4: C^2 == X, H0 == b S C S, lambda = (a-b)/(a+b) = %d (i or -i: %s)' % (lam, sorted({i, M - i})))

    # ---- T7, T8 (real kernels; weight of the residual vector)
    d1, d2, e1, e2 = sp.symbols('d1 d2 e1 e2', real=True, nonzero=True)
    H = sp.Matrix([[1, 1], [1, -1]])
    Kr = sp.diag(d1, d2) * H * sp.diag(e1, e2)
    real_sol = sp.solve([sp.Eq(Kr[0, 0], Kr[1, 1]), sp.Eq(Kr[0, 1], Kr[1, 0])], [d1, e1], dict=True)
    z1 = sp.symbols('z1')
    Kc = sp.diag(z1, 1) * H * sp.diag(e1, e2)
    cplx_sol = sp.solve([Kc[0, 0] - Kc[1, 1], Kc[0, 1] - Kc[1, 0]], [z1, e1], dict=True)
    ok7 = (real_sol == [] and cplx_sol == [])
    check('C5.T7', ok7, 'real solutions of D1 H D2 in span(I,X): %s; with complex d1 (needs e1 = +-i e2): %s' % (real_sol, cplx_sol))
    m = 3
    Hm = sp.Matrix([[1]])
    for _ in range(m):
        Hm = sp.kronecker_product(Hm, H)
    xs = list(itertools.product((0, 1), repeat=m))
    t8 = {}
    for v in EXPECTED['T8']:
        w = sum(v)
        ph = sp.diag(*[sp.I ** ((w % 4) * (sum(p * q for p, q in zip(v, x)) % 2)) for x in xs])
        Op = (Hm * ph * Hm) / 2 ** m
        t8[v] = all(sum(1 for t in Op.row(r) if t != 0) == 1 for r in range(2 ** m))
    check('C5.T8', t8 == EXPECTED['T8'],
          'H^m diag(i^(wt*[v.x])) H^m / 2^m is a permutation: ' + ', '.join('v=%s wt=%d: %s' % (v, sum(v), t8[v]) for v in t8))
    check('C5.real', ok7 and t8 == EXPECTED['T8'],
          'no real subspace-labelled butterfly (T7); only weight 2 mod 4 residuals are free translations (T8)')
    print('total %.1f s' % (time.time() - t_all))
    finish()


if __name__ == '__main__':
    main()
