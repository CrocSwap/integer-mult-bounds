#!/usr/bin/env python3
"""Exact verification of the boundary matrix-product exponent used by the retuned ledger.

The capped-fusion outer (PR1673, Vlado Vojdanovski) charges its batched boundary algebra W^(omega-1) with omega a proven exponent of
W-square matrix products (the note used Strassen, omega<45/16, c=(3-omega)/2=3/32). Here omega is bounded by the explicit exact
rank-40 scheme <3,3,6;40> over Q (Smirnov's rank, rational dyadic variant of Dumas-Pernet-Sedoglavic, vendor/fmm336):
  1. the three vendored files are hash-pinned and the full tensor identity sum_t L[t,a] R[t,b] P[c,t] = <3,3,6> is checked in exact rationals;
  2. its two cyclic rotations <3,6,3;40>, <6,3,3;40> (u'=v, v'=w, w'=u) are checked as full tensor identities as well;
  3. the Kronecker product of the three decompositions is a decomposition of <54,54,54> of rank 40^3=64000 (Kronecker lemma: dimensions 3*3*6=54,
     3*6*3=54, 6*3*3=54 in every mode, ranks multiply);
  4. the exact integer inequality 64000^D < 54^N with omega_up = N/D = 27743/10000 proves omega <= 2.7743 (recursion on W-square matrices, padded to a power of 54).
Writes TENSOR.json. Prints PASS_EXACT_TENSOR_336_40."""
from fractions import Fraction as F
from pathlib import Path
import hashlib, json
HERE = Path(__file__).resolve().parent
V = HERE.parent / 'vendor/fmm336'
OMEGA_N, OMEGA_D = 27743, 10000
RANK, BASE = 40 ** 3, 54


def load(path):
    lines = [l.split() for l in path.read_text().splitlines() if l.strip() and not l.startswith('#')]
    r, c = int(lines[0][0]), int(lines[0][1])
    mat = {}
    for t in lines[1:]:
        i, j = int(t[0]), int(t[1])
        if i == 0:
            break
        assert 1 <= i <= r and 1 <= j <= c and (i - 1, j - 1) not in mat
        mat[(i - 1, j - 1)] = F(t[2])
    return r, c, mat


def identity_holds(U, Vv, W, m, k, n):
    """U[t]: {a_(i,j)}, Vv[t]: {b_(j,l)}, W[t]: {c_(l,i)}; sum_t U V W == sum a_ij b_jl c_li."""
    T = {}
    for u, v, w in zip(U, Vv, W):
        for a, x in u.items():
            for b, y in v.items():
                for c, z in w.items():
                    T[(a, b, c)] = T.get((a, b, c), 0) + x * y * z
    T = {key: val for key, val in T.items() if val != 0}
    want = {(i * k + j, j * n + l, l * m + i): F(1) for i in range(m) for j in range(k) for l in range(n)}
    return T == want


def main():
    src = json.loads((V / 'SOURCE.json').read_text())
    for name, digest in src['sha256'].items():
        assert hashlib.sha256((V / name).read_bytes()).hexdigest() == digest, name
    rl, cl, L = load(V / '3x3x6_40_DPS-accurate_L.sms')
    rr, cr, R = load(V / '3x3x6_40_DPS-accurate_R.sms')
    rp, cp, P = load(V / '3x3x6_40_DPS-accurate_P.sms')
    m, k, n, r = 3, 3, 6, 40
    assert (rl, cl, rr, cr, rp, cp) == (r, m * k, r, k * n, m * n, r)
    U = [dict() for _ in range(r)]; Vv = [dict() for _ in range(r)]; W = [dict() for _ in range(r)]
    for (t, a), x in L.items(): U[t][a] = x
    for (t, b), x in R.items(): Vv[t][b] = x
    for (c, t), x in P.items():
        i, l = divmod(c, n)               # output entry (i,l) of the m x n product
        W[t][l * m + i] = x               # coefficient of c_(l,i) in the trilinear form
    assert all(U) and all(Vv) and all(W)
    ok = [identity_holds(U, Vv, W, 3, 3, 6), identity_holds(Vv, W, U, 3, 6, 3), identity_holds(W, U, Vv, 6, 3, 3)]
    assert all(ok), ok
    # tamper controls: one coefficient moved, or one rotation fed the unrotated triple, must fail the identity
    key = next(iter(W[0])); W[0][key] += F(1, 4)
    assert not identity_holds(U, Vv, W, 3, 3, 6); W[0][key] -= F(1, 4)
    assert not identity_holds(U, Vv, W, 3, 6, 3) and not identity_holds(Vv, W, U, 3, 3, 6)
    assert identity_holds(U, Vv, W, 3, 3, 6)
    # dimensions of the Kronecker product <3,3,6> x <3,6,3> x <6,3,3>
    assert (3 * 3 * 6, 3 * 6 * 3, 6 * 3 * 3) == (BASE,) * 3 and (3 * 6 * 3, 6 * 3 * 3, 3 * 3 * 6) == (BASE,) * 3
    assert (3 * 3 * 6) * (3 * 6 * 3) * (6 * 3 * 3) == BASE ** 3 and 40 ** 3 == RANK
    assert RANK ** OMEGA_D < BASE ** OMEGA_N                      # omega <= N/D, exact integers
    # tightness record: the next smaller decimal fails or is too close to certify, so 2.7743 is not claimed below log_54(64000)
    assert RANK ** OMEGA_D > BASE ** (OMEGA_N - 3)
    out = {'status': 'PASS_EXACT_TENSOR_336_40', 'identities_verified': ['<3,3,6;40>', '<3,6,3;40>', '<6,3,3;40>'],
           'nonzeros': {'L': len(L), 'R': len(R), 'P': len(P)}, 'kronecker': {'base': BASE, 'rank': RANK},
           'omega_up': '%d/%d' % (OMEGA_N, OMEGA_D), 'boundary_constant_c': str(F(3) / 2 - F(OMEGA_N, OMEGA_D) / 2),
           'source': src['url'], 'sha256': src['sha256']}
    (HERE / 'TENSOR.json').write_text(json.dumps(out, indent=1) + '\n')
    print(out['status'], out['omega_up'])
    return F(OMEGA_N, OMEGA_D)


if __name__ == '__main__':
    main()
