"""CHECKED (exact; exhaustive where stated): the Sp-invariant two-point point X* = x I + y A of the packing relaxation on W(2k-1,2), k = 2..5.
 (1) the non-collinearity graph A is strongly regular with lambda = mu = 2^(2k-2), degree 2^(2k-1) (all point pairs), so A^2 = (d-mu) I + mu J and
     spec A is contained in {2^(2k-1), +-2^(k-1)};  (2) X* is PSD, its lifted moment matrix is PSD (Schur complement), entries lie in [0, min(x_p,x_q)],
     objective sum_p X_pp = 2^k+1;  (3) every generator inequality sum_{q in L} X_pq <= X_pp holds with equality (all generators for k <= 4, 60 seeded random for k = 5),
     and every point lies on N_L/(2^k+1) generators (all generators, k <= 4)."""
import os, sys, random
from fractions import Fraction as Fr
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from sympl import bf, lagrangians, random_lagrangian

rng = random.Random(5)
for k in (2, 3, 4, 5):
    N = 4 ** k - 1
    nb = [0] * (N + 1)
    for p in range(1, N + 1):
        m = 0
        for q in range(1, N + 1):
            if bf(p, q, k):
                m |= 1 << (q - 1)
        nb[p] = m
    d, lam = 2 ** (2 * k - 1), 2 ** (2 * k - 2)
    deg_ok = all(nb[p].bit_count() == d for p in range(1, N + 1))
    srg = all((nb[p] & nb[q]).bit_count() == lam for p in range(1, N + 1) for q in range(p + 1, N + 1))
    check('T.srg-k%d' % k, deg_ok and srg, "k'=%d: %d points, non-collinearity graph regular of degree %d and every pair (adjacent or not) has exactly %d common neighbours, so A^2 = %d I + %d J and spec A within {%d, +-%d}"
          % (k, N, d, lam, d - lam, lam, d, 2 ** (k - 1)))
    x = Fr(1, 2 ** k - 1)
    y = x / 2 ** (k - 1)
    eig = [x + y * d, x + y * 2 ** (k - 1), x - y * 2 ** (k - 1)]
    schur = eig[0] - x * x * N            # X* - x^2 J on the all-ones direction (other eigenvalues unchanged since J kills them)
    check('T.psd-k%d' % k, min(eig) == 0 and eig[1] == 2 * x and schur == 0 and 0 < y <= x and N * x == 2 ** k + 1,
          "k'=%d: X* = x I + y A, x = 1/(2^k'-1), y = x/2^(k'-1): eigenvalues %s >= 0 (min 0); moment matrix [[1,x1^T],[x1,X*]]: Schur complement X*-x^2 J has eigenvalue %s on the all-ones vector; 0 < y <= x; objective N x = %s = 2^k'+1"
          % (k, [str(e) for e in eig], schur, N * x))
    if k <= 4:
        Ls = lagrangians(k)
        cnt = {}
        for L in Ls:
            for p in L:
                cnt[p] = cnt.get(p, 0) + 1
        thru = set(cnt.values()) == {len(Ls) // (2 ** k + 1)} and len(cnt) == N
        mode = 'all %d generators' % len(Ls)
    else:
        Ls = [random_lagrangian(k, rng) for _ in range(60)]
        thru = True
        mode = '60 seeded random generators'
    ok = True
    for L in Ls:
        lm = 0
        for q in L:
            lm |= 1 << (q - 1)
        for p in range(1, N + 1):
            c = (nb[p] & lm).bit_count()
            ok &= (c == 0) if p in L else (c == 2 ** (k - 1))
            s = (x if p in L else c * y)                    # sum_{q in L} X*_pq (q = p contributes x, collinear q != p contribute 0)
            ok &= s == x
    check('T.clique-k%d' % k, ok and thru, "k'=%d: %s x all %d points p: #{q in L : b(p,q)=1} = 0 (p in L) or 2^(k'-1), so sum_{q in L} X*_pq = x = X*_pp (equality); generators through a point: N_L/(2^k'+1)%s"
          % (k, mode, N, ' (exhaustive)' if k <= 4 else ' (not enumerated at k\'=5; follows from transitivity, proved in README)'))
finish()
