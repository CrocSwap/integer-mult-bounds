"""CHECKED (exact): the non-unimodular units D5 and E6 (deficient directions, coupling data, N-space).
 (a) deficient row/column directions: for every proper W_z (a hyperplane of the root span) the unique direction d in the span orthogonal to it;
     27 per side for E6, 5 per side for D5.  The pair ranks r(x,y) of two deficient directions are recomputed directly from supports and agree
     with the type table of Theorem 4; incidence (x.y = 0 or not) is tabulated: E6: all 27 x 27 pairs non-orthogonal, 432 pairs of rank 5, 297 of
     rank 6; D5: 20 orthogonal pairs of rank 3, 5 non-orthogonal pairs (a perfect matching) of rank 4.
 (b) N-space: the space of bilinear forms N on the root span with r_t N r_s = 0 on every ordered orthogonal pair (t != s) is 1-dimensional for
     D5 and E6 (so N is proportional to the Gram form whenever B is the dense pairing and the decoder is exact)."""
import os
import sys
from fractions import Fraction as Fr
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from exact import rref, rank_q, nullspace, dot
from units import UNITS, gram, bmasks, block_rank
import floor as FL


def direction(S, basis):
    """Unit-free direction d in span(basis) with d . s = 0 for all rows s of S (S has rank T-1)."""
    M = [[dot(s, b) for b in basis] for s in S]
    ns = nullspace(M, len(basis))
    assert len(ns) == 1
    n = ns[0]
    d = [sum(n[i] * basis[i][c] for i in range(len(basis))) for c in range(len(basis[0]))]
    # normalise: first nonzero coordinate = 1
    f = next(x for x in d if x != 0)
    return tuple(x / f for x in d)


def run(name, want_ranks, want_ndir):
    L, T = UNITS[name]
    a = FL.analyse(L, set(), T)
    G = gram(L)
    Br = bmasks(G)
    span = rref([[Fr(x) for x in r] for r in L])
    assert len(span) == T
    basis = list(span)
    dX = [direction(S, basis) for S in a['tx'] if S]
    dY = [direction(S, basis) for S in a['ty'] if S]
    check('C1.%s-dirs' % name, len(dX) == len(dY) == want_ndir and len(set(dX)) == want_ndir and len(set(dY)) == want_ndir,
          '%s: %d deficient directions per side (distinct)' % (name, len(dX)))
    per_x = sorted(set(sum(1 for y in dY if dot(x, y) != 0) for x in dX))
    check('C1.%s-matching' % name, per_x == ([27] if name == 'E6' else [1]),
          '%s: number of non-orthogonal deficient columns per deficient row direction: %s' % (name, per_x))
    # type indices: index 0 is the empty type; the others follow the order of a['tx'][1:], so dX[i-1] <-> type i
    cnt = {}
    agree = True
    for i, x in enumerate(dX):
        Rx = [t for t in range(len(L)) if dot([Fr(c) for c in L[t]], x) != 0]
        for j, y in enumerate(dY):
            Ay = [t for t in range(len(L)) if dot([Fr(c) for c in L[t]], y) != 0]
            r = block_rank(Br, Rx, Ay)
            agree &= r == a['table'][(i + 1, j + 1)]
            key = ('orth' if dot(x, y) == 0 else 'non', r)
            cnt[key] = cnt.get(key, 0) + 1
    check('C1.%s-pairs' % name, agree and cnt == want_ranks,
          '%s: pair ranks from supports = type table: %s; (incidence, rank) counts %s' % (name, agree, dict(sorted(cnt.items()))))
    # row of the type table: generic x (type 0) against generic and deficient y
    g00 = a['table'][(0, 0)]
    g0j = {a['table'][(0, j)] for j in range(1, len(a['ty']))}
    gi0 = {a['table'][(i, 0)] for i in range(1, len(a['tx']))}
    check('C1.%s-generic' % name, (g00, g0j, gi0) == ((7, {6}, {6}) if name == 'E6' else (5, {4}, {4})),
          '%s: generic/generic rank %d, deficient/generic %s, generic/deficient %s' % (name, g00, sorted(gi0), sorted(g0j)))
    # N-space
    coords = [[dot([Fr(c) for c in b], [Fr(c) for c in r]) for b in basis] for r in L]
    rows = []
    for t in range(len(L)):
        for s in range(len(L)):
            if t != s and G[t][s] == 0:
                rows.append([coords[t][p] * coords[s][q] for p in range(T) for q in range(T)])
    dim = T * T - rank_q(rows)
    check('C1.%s-Nspace' % name, dim == 1, '%s: dim{N : r_t N r_s = 0 on %d ordered orthogonal pairs} = %d' % (name, len(rows), dim))


run('E6', {('non', 5): 432, ('non', 6): 297}, 27)
run('D5', {('orth', 3): 20, ('non', 4): 5}, 5)
finish()
