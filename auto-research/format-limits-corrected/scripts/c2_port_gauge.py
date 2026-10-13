"""Exact checks of the port-gauge rank calculus: C_q gates, frame detours and route rigidity (over F2^n).

Notation.  Labels are vectors of F2^n with the standard dot product; q is an ODD vector (q.q = 1).  C_a denotes the
single-axis Clifford gate  cgate(n, a)  and Z a product of such gates.  T_F is the canonical Clifford frame operator of
a subspace F, with T_0 = identity and T_FULL = the Fourier transform F on all n axes.  The frame distance is
d(F, G) = dim F + dim G - 2 dim(F cap G).  The Clifford rank of an operator is the rank reported by
clifford_exact.lower_child (the rank of the Fourier part of its normal form).

A. Cost instrument.  For a product Z = C_{q_1}^{s_1} ... C_{q_k}^{s_k} (s_i = +-1) let  B = sum_i q_i q_i^T  over F2.
   Claim: rank_{F2}(B) equals the exact Clifford rank of Z (240 random products, n = 4..7, seeded).
B. Detour theorem, exhaustive over all subspaces G of F2^n (n = 3..6), with q odd, L = FULL, q^perp the hyperplane:
   Y family  0 -> G -> q^perp :  extra cost d(0,G) + d(G,q^perp) - d(0,q^perp)  is 0 iff G <= q^perp, else exactly 2;
   X family  <q> -> G -> L    :  extra cost d(<q>,G) + d(G,L) - d(<q>,L)        is 0 iff q in G,      else exactly 2.
C. Route rigidity (exact, n = 3, 4, exhaustive over all pairs of subspaces).  For frames f_X, f_Y the route
   R = T_{f_Y} T_{f_X}^{-1}  is compared with F (matrix products, R acting after T_{f_X}^{-1}): the right mismatch rank is
   rank(F^{-1} R) (zero iff R = F M with M monomial) and the left mismatch rank is rank(R F^{-1}) (zero iff R = M F),
   M a monomial operator (permutation x diagonal x translation).  Claim: R equals F modulo a monomial on at least one
   side only for pairs with dim f_X + dim f_Y = n and f_X cap f_Y = 0 (a necessary condition: the pairs where it
   holds are a proper subset of these complementary pairs), and the number of such pairs by (dim f_X, dim f_Y) is
   as logged below.  Mismatch ranks are also given for the boundary pairs of a port with label q.
D. Gauge descent.  If q lies in span(axes of Z) with odd support (q = sum of an odd subset of the axes of
   Z = C^{(x)k}) then multiplying by C_q lowers the rank by exactly one,  T_E C_q^{-1} = T_{E cap q^perp};
   if q is outside span(axes) and orthogonal to it the rank rises by exactly one.
"""
import collections
import random
import sys

from report import check, finish, main_file

sys.path.insert(0, str(main_file('research/direct-delivery504-global/vendor/clifford/clifford_exact.py').parent))
import clifford_exact as ce  # noqa: E402  (the repository's exact Clifford compiler, unmodified)
from clifford_exact import rank, parity, cgate, ident, canonical_frame, lower_child, fourier  # noqa: E402

# ----------------------------------------------------------------------------------------------------------------
# Expected values (from the exact run; each is re-derived below and compared).
EXPECTED = {
    # A: number of random products tested and number of mismatches between rank(B) and the exact Clifford rank
    'instrument': dict(products=240, mismatches=0),
    # B: per n: number of subspaces of F2^n, number of odd q tested (the first ones in increasing order; all odd q
    #    for n <= 5, the first 10 for n = 6), and the histogram {(family, G on the geodesic?, extra cost): count}
    'detour': {
        3: dict(subspaces=16, qs=4, geo=20, off=44),
        4: dict(subspaces=67, qs=8, geo=128, off=408),
        5: dict(subspaces=374, qs=16, geo=1072, off=4912),
        6: dict(subspaces=2825, qs=10, geo=3740, off=24510),
    },
    # C: mismatch ranks (right, left) for q = 1 and the number of pairs with route == F on a side, by
    #    (dim f_X, dim f_Y, dim f_X cap f_Y); 'sides' = how many of those pairs are monomial-equal to F on both sides /
    #    only on the left (R = M F) / only on the right (R = F M); 'complementary' = number of all pairs with
    #    dim f_X + dim f_Y = n and f_X cap f_Y = 0 (a superset of the rigid pairs); both are extra details of the run
    'route': {
        3: dict(sides=dict(both=8, left=8, right=8), complementary=58,
                mism={'<q>,q^perp': (0, 0), '<q>,L': (1, 1), '0,L': (0, 0), '0,q^perp': (1, 1), 'L,q^perp': (2, 2)},
                rigid={(0, 3, 0): 1, (1, 2, 0): 11, (2, 1, 0): 11, (3, 0, 0): 1}),
        4: dict(sides=dict(both=16, left=51, right=51), complementary=802,
                mism={'<q>,q^perp': (0, 0), '<q>,L': (1, 1), '0,L': (0, 0), '0,q^perp': (1, 1), 'L,q^perp': (3, 3)},
                rigid={(0, 4, 0): 1, (1, 3, 0): 26, (2, 2, 0): 64, (3, 1, 0): 26, (4, 0, 0): 1}),
    },
    # D: n = 7, Z = C^{(x)k}, q = sum of the first sz axes (sz odd, sz <= k): (k, sz) -> (rank Z, rank C_q Z)
    'descent': {(3, 1): (3, 2), (3, 3): (3, 2), (5, 1): (5, 4), (5, 3): (5, 4), (5, 5): (5, 4),
                (7, 1): (7, 6), (7, 3): (7, 6), (7, 5): (7, 6), (7, 7): (7, 6)},
    # D: Z = C^{(x)3} on axes e0,e1,e2 and q = e5 (outside and orthogonal): rank 3 -> 4
    'outside': (3, 4),
}

# ---- A: the F2 cost instrument ---------------------------------------------------------------------------------


def brank(terms, n):
    """rank over F2 of B = sum_i q_i q_i^T  (row j of B is the xor of the q_i whose bit j is set)."""
    B = [0] * n
    for q, _s in terms:
        for j in range(n):
            if q >> j & 1:
                B[j] ^= q
    return rank(B)


rng = random.Random(14)
bad = 0
tot = 0
for n in (4, 5, 6, 7):
    for _ in range(60):
        k = rng.randrange(1, 8)
        terms = [(rng.randrange(1, 1 << n), rng.choice((-1, 1))) for _ in range(k)]
        op = ident(n)
        for q, s in terms:
            op = op.then(cgate(n, q, s))
        r_ex = lower_child(op)[0]['rank']
        r_b = brank(terms, n)
        tot += 1
        bad += (r_ex != r_b)
check('C2.instrument', (tot, bad) == (EXPECTED['instrument']['products'], EXPECTED['instrument']['mismatches']),
      'rank_F2(sum q q^T) vs exact Clifford child rank: %d random C-products, n=4..7, mismatches = %d' % (tot, bad))


# ---- B: detour theorem -----------------------------------------------------------------------------------------
def subspaces(n):
    """all subspaces of F2^n, as frozensets of vectors (breadth-first closure under adding one vector)."""
    vecs = range(1, 1 << n)
    layer = {frozenset({0})}
    seen = {frozenset({0})}
    while layer:
        nxt = set()
        for S in layer:
            for v in vecs:
                if v not in S:
                    T = frozenset(S | {x ^ v for x in S})
                    if T not in seen:
                        seen.add(T)
                        nxt.add(T)
        layer = nxt
    return list(seen)


def dim(S):
    return len(S).bit_length() - 1


def dd(f, g):
    return dim(f) + dim(g) - 2 * dim(f & g)


for n in (3, 4, 5, 6):
    subs = subspaces(n)
    full = frozenset(range(1 << n))
    qs = [q for q in range(1, 1 << n) if parity(q)]
    qsel = qs if n <= 5 else qs[:10]
    counts = collections.Counter()
    theorem = True
    for q in qsel:
        perp = frozenset(x for x in range(1 << n) if parity(x & q) == 0)
        zero = frozenset({0})
        line = frozenset({0, q})
        for G in subs:
            ex_y = dd(zero, G) + dd(G, perp) - dd(zero, perp)
            ex_x = dd(line, G) + dd(G, full) - dd(line, full)
            geo_y = G <= perp
            geo_x = q in G
            counts[('Y', geo_y, ex_y)] += 1
            counts[('X', geo_x, ex_x)] += 1
            theorem &= (ex_y == (0 if geo_y else 2)) and (ex_x == (0 if geo_x else 2))
    e = EXPECTED['detour'][n]
    want = {('Y', True, 0): e['geo'], ('Y', False, 2): e['off'], ('X', True, 0): e['geo'], ('X', False, 2): e['off']}
    ok = theorem and dict(counts) == want and len(subs) == e['subspaces'] and len(qsel) == e['qs']
    check('C2.detour-n%d' % n, ok,
          '%d subspaces x %d odd q: extra cost of a detour via G is 0 on the geodesic set (%d per family) and exactly 2 '
          'off it (%d per family) for Y: 0->G->q^perp (G <= q^perp) and X: <q>->G->L (q in G)'
          % (len(subs), len(qsel), counts[('Y', True, 0)], counts[('Y', False, 2)]))


# ---- C: route rigidity -----------------------------------------------------------------------------------------
def frame_op(n, S):
    b = []
    for v in sorted(S):
        if v and rank(b + [v]) > len(b):
            b.append(v)
    return canonical_frame(n, tuple(b))


for n in (3, 4):
    subs = subspaces(n)
    full = frozenset(range(1 << n))
    zero = frozenset({0})
    F = fourier(n)
    Fi = F.adjoint()
    ops = {S: frame_op(n, S) for S in subs}
    q = next(x for x in range(1, 1 << n) if parity(x))
    perp = frozenset(x for x in range(1 << n) if parity(x & q) == 0)
    line = frozenset({0, q})

    def mism(fx, fy):
        R = ops[fx].adjoint().then(ops[fy])
        return lower_child(R.then(Fi))[0]['rank'], lower_child(Fi.then(R))[0]['rank']

    got_mism = {'<q>,q^perp': mism(line, perp), '<q>,L': mism(line, full), '0,L': mism(zero, full),
                '0,q^perp': mism(zero, perp), 'L,q^perp': mism(full, perp)}
    rigid = collections.Counter()
    rigid_pairs = set()
    sides = collections.Counter()
    for fx in subs:
        for fy in subs:
            a, b = mism(fx, fy)                       # (right, left) mismatch ranks
            if a == 0 or b == 0:
                rigid[(dim(fx), dim(fy), dim(fx & fy))] += 1
                rigid_pairs.add((fx, fy))
                sides['both' if a == 0 and b == 0 else 'right' if a == 0 else 'left'] += 1
    # necessary condition: dims sum to n and the frames meet only in 0
    complementary = {(fx, fy) for fx in subs for fy in subs if dim(fx) + dim(fy) == n and dim(fx & fy) == 0}
    e = EXPECTED['route'][n]
    ok = (got_mism == e['mism'] and dict(rigid) == e['rigid'] and rigid_pairs <= complementary
          and len(complementary) == e['complementary'] and dict(sides) == e['sides'])
    check('C2.route-n%d' % n, ok,
          'q=%d: route == F modulo monomials on a side for %d pairs, all with dim fX + dim fY = %d and fX cap fY = 0 '
          '(of %d such pairs; by (dim fX, dim fY): %s; monomial-equal on both sides / only left / only right: %d/%d/%d); '
          'mismatch ranks (right,left): (<q>,q^perp)=%s (<q>,L)=%s (0,L)=%s (0,q^perp)=%s (L,q^perp)=%s'
          % (q, len(rigid_pairs), n, len(complementary), dict(sorted((k[:2], v) for k, v in rigid.items())),
             sides['both'], sides['left'], sides['right'], got_mism['<q>,q^perp'],
             got_mism['<q>,L'], got_mism['0,L'], got_mism['0,q^perp'], got_mism['L,q^perp']))

# ---- D: gauge descent ------------------------------------------------------------------------------------------
n = 7
descent = {}
for k in (3, 5, 7):
    for sz in (1, 3, 5, 7):
        if sz > k:
            continue
        q = sum(1 << i for i in range(sz))          # odd support: q is a sum of an odd number of the axes of Z
        op = ident(n)
        for a in [1 << i for i in range(k)]:
            op = op.then(cgate(n, a))
        r0 = lower_child(op)[0]['rank']
        r1 = lower_child(op.then(cgate(n, q)))[0]['rank']
        descent[(k, sz)] = (r0, r1)
op = ident(n)
for a in (1, 2, 4):
    op = op.then(cgate(n, a))
outside = (lower_child(op)[0]['rank'], lower_child(op.then(cgate(n, 1 << 5)))[0]['rank'])
n_down = sum(1 for r0, r1 in descent.values() if r1 == r0 - 1)
check('C2.gauge-descent',
      descent == EXPECTED['descent'] and outside == EXPECTED['outside'] and n_down == len(descent) == 9,
      'n=7, Z = C^(x)k (k=3,5,7), q = sum of an odd number of the axes: rank(C_q Z) = rank(Z) - 1 in %d/%d cases; '
      'q = e5 outside and orthogonal to the axes e0,e1,e2: rank %d -> %d (+1)'
      % (n_down, len(descent), outside[0], outside[1]))

finish()
