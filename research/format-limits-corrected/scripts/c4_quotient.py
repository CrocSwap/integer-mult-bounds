"""Lemma Q: a unit with degenerate labels is dominated by its quotient.

Setting.  A unit has ports with F_2 (complex) or Q (bit) labels spanning a space W of dimension d.  For the complex
side the form is the standard dot product on F_2^n, rad = W cap W^perp has dimension rho, the Gram rank is
r = d - rho, and pi : W -> W/rad is the quotient map.  A 'total' j is read by the targets from a frame f_j, the span
of the labels of its sources.  Reading total j at a cut frame g costs the frame-lemma price
    d(f_j, g) = dim f_j + dim g - 2 dim(f_j cap g)      (upstream/build/sections/03-motifs.tex:154-186),
where all targets stand at one common frame g that lies in every target's sink; because f_j lies in W, f_j cap g lies
in rad, so only cuts g inside rad matter.  Per total, for g inside rad,
    d(f_j, g) >= dim f_j - dim(f_j cap rad) = dim pi(f_j).
Hence for every schedule of cuts (a chain 0 = g_0 < g_1 < ... of subspaces of rad, each total read at one of them)
    cst_E2'  >=  cst_quotient = sum_j dim pi(f_j)  >=  cst_pair = sum_j rank pairing(sources_j, readers_j),
the last being the pairing-rank floor of a total, which only depends on the Gram.  The quotient unit (labels mod rad, same Gram
and decoder) has window r = d - rho <= h - 2 rho for every realisation with window h = d + rho.  Certified exponents X
are non-increasing in the window and in the copy cost, so X_deg(s) <= X(s, r/k, cst_quotient/v) for every s.

This script checks, with exact ranks:
* the one degenerate paired cube (p = 3: 8 ports in F_2^6, 16 helper registers, six totals each of dimension 3; the
  instance is data/toys/sol_p3_cone_R16.json): d 4, rho 2, copy cost 18 when read at 0, 16 for the best schedule of cuts
  over all flags of rad, 12 for the quotient (= the pairing-rank bound); window 6 against 2 for the quotient, which has
  only 2 distinct labels;
* the paired cubes p = 3..12 (ports chi_S: three index pairs, one of two bits each, form 9I - J on the bit side): only the
  complex p = 3 is degenerate, the bit side never;
* E8 (120 root lines in doubled standard coordinates, nine F_2 label coordinates, e8units.standard_e8) decorated by one
  isotropic direction e on the bit side (nine star totals) and by weight-2 isotropic directions on the complex side
  (eight coordinate totals of 78 lines): the best schedule recovers exactly the quotient cost 72 at a larger window
  (10 against 8; 11/13/15 against 9); a decoration aligned with two totals needs 73;
* 737 random instances (337 with extra-coordinate radicals, 400 with intrinsic radicals; Python's seeded Mersenne
  Twister, seeds 1 and 7): no schedule beats the quotient;
* the certified exponents X (hi of skel.X at the best odd s in 3..13) of the quotient against the degenerate realisation,
  with the references of the punctured units (bit 111/63, complex 112/64).
Run: python3 c4_quotient.py
"""
import itertools
import random
import time

import numpy as np

from report import check, finish, DATA, load_json
from e8units import (standard_e8, e8_labels, f2_rank, rank_q, row_basis_idx_q, gram_rank_q, dot2, span_basis,
                     rows_to_int)
from skel import X as skel_X
from fractions import Fraction as Fr

# ---------------------------------------------------------------------------------------------------------------
# expected values (from the recorded runs)
EXPECTED = {
    'toy': dict(d=4, rho=2, r=2, n_totals=6, dim_f=3, cst0=18, cstE2=16, cstQ=12, window_deg=6, window_quot=2,
                n_labels=2, rad=[0b110011, 0b001111, 0b111100]),
    # paired cubes p = 3..12: number of ports and complex (d, rho); the bit side is nondegenerate
    'paired_v': {3: 8, 4: 32, 5: 80, 6: 160, 7: 280, 8: 448, 9: 672, 10: 960, 11: 1320, 12: 1760},
    # E8 rows: (d, rho, r, window of the degenerate realisation, cst0, cstE2, cstQ, cstC)
    'e8_bit_e': (9, 1, 8, 10, 81, 72, 72, 72),
    'e8_cx': {1: (10, 1, 9, 11, 80, 72, 72, 72), 2: (11, 2, 9, 13, 88, 72, 72, 72), 3: (12, 3, 9, 15, 96, 72, 72, 72)},
    'e8_cx_aligned': (11, 2, 9, 13, 86, 73, 72, 72),
    # random instances: 'tests', no violation of cst_E2' >= cst_quotient, and how often a cut schedule beats reading at 0
    # ('gain') / equals the quotient ('equal').  The recorded run (gain 257 of 337, gain 376 and equal 374 of 400)
    # minimised only over the flags built from subsets of the radical basis ('coordinate flags'); the optimum over ALL
    # flags of the radical (this script's best_e2) is slightly better: gain_all 275, 379, equal_all 391.
    'random_extra': dict(tests=337, violations=0, gain=257, gain_all=275),             # extra-coordinate radicals
    'random_intrinsic': dict(tests=400, violations=0, gain=376, equal=374, gain_all=379, equal_all=391),
    # certified X (hi, best s over 3,5,...,13) printed to 5 significant digits; None = deficit D <= 0 at every s
    'X': {'toy_deg': None, 'toy_quot': None,
          'bit_quot': '5.1598e-03', 'bit_e_deg': '4.0462e-03',
          'cx_quot': '4.5356e-03', 'cx_rho1': '3.6522e-03', 'cx_rho2': '3.0570e-03', 'cx_rho3': '2.6286e-03',
          'bit_punct': '6.0005e-03', 'cx_punct': '5.1863e-03',
          'bit_star_floor': '8.0093e-03', 'cx_star_floor': '7.0728e-03'},
}


# ---------------------------------------------------------------------------------------------------------------
# F_2 helpers on integer bit vectors
def f2_rad(basis):
    """basis (echelon, decreasing) of W cap W^perp for W = span(basis): solve A c = 0 with A_ij = b_i . b_j."""
    n = len(basis)
    A = [[dot2(basis[i], basis[j]) for j in range(n)] for i in range(n)]
    rows = [sum(A[i][j] << j for j in range(n)) for i in range(n)]
    red = []
    for r in rows:
        for (p, rr) in red:
            if r >> p & 1:
                r ^= rr
        if r:
            p = r.bit_length() - 1
            red = [(pp, (rr ^ r) if rr >> p & 1 else rr) for pp, rr in red]
            red.append((p, r))
    pivs = {p for p, _ in red}
    ker = []
    for fj in [j for j in range(n) if j not in pivs]:
        c = 1 << fj
        for p, rr in red:
            if rr & c:
                c |= 1 << p
        x = 0
        for i in range(n):
            if c >> i & 1:
                x ^= basis[i]
        assert all(dot2(x, b) == 0 for b in basis)
        ker.append(x)
    return span_basis(ker)


def f2_dim(vecs):
    return len(span_basis(vecs))


def in_span(x, basis):
    for b in basis:
        if x ^ b < x:
            x ^= b
    return x == 0


def quot_dim(f, rad):
    """dim pi(f) = dim (f + rad) - dim rad."""
    return f2_dim(list(f) + list(rad)) - len(rad)


def subspaces_of(rad, all_subspaces):
    """subspaces of rad as echelon-basis tuples.  all_subspaces=False: only spans of subsets of the given basis (the
    coordinate subspaces); True: every subspace (spans of subsets of the nonzero vectors, deduplicated)."""
    rho = len(rad)
    pool = [x for x in _span_elems(rad) if x] if all_subspaces else list(rad)
    subs = {}
    for k in range(rho + 1):
        for comb in itertools.combinations(pool, k):
            sp = tuple(sorted(span_basis(list(comb)), reverse=True))
            subs[sp] = len(sp)
    return list(subs)


def best_e2(fs, rad, all_subspaces=True):
    """minimum over complete flags 0 < g_1 < ... < g_rho = rad of sum_j min_{g in flag} d(f_j, g), exactly."""
    rho = len(rad)
    subs = subspaces_of(rad, all_subspaces)

    def dcut(f, g):
        cap = f2_dim([x for x in _span_elems(g) if in_span(x, f)])
        return len(f) + len(g) - 2 * cap

    def inside(a, b):
        return f2_dim(list(a) + list(b)) == len(b)
    cache = {}

    def cost(fi, g):
        key = (fi, g)
        if key not in cache:
            cache[key] = dcut(fs[fi], g)
        return cache[key]
    best = None

    def flags(cur, chain):
        nonlocal best
        if len(cur) == rho:
            c = sum(min(cost(i, g) for g in chain) for i in range(len(fs)))
            best = c if best is None else min(best, c)
            return
        for g in subs:
            if len(g) == len(cur) + 1 and inside(cur, g):
                flags(g, chain + [g])
    flags((), [()])
    return best


def _span_elems(g):
    """all vectors of the span of the basis g."""
    out = [0]
    for b in g:
        out += [x ^ b for x in out]
    return out


# ---------------------------------------------------------------------------------------------------------------
def toy_p3():
    t0 = time.time()
    c = load_json(DATA / 'toys' / 'sol_p3_cone_R16.json')
    ports, fr = c['ports'], c['frames']
    tot = [fr[f] for _, _, f in c['ret']]                     # the six total frames f_j (bit vectors in F_2^6)
    W = span_basis(ports)
    d = len(W)
    rad = f2_rad(W)
    rho = len(rad)
    Ex = EXPECTED['toy']
    cst0 = sum(len(span_basis(f)) for f in tot)
    cstE2 = best_e2([tuple(span_basis(f)) for f in tot], rad)
    cstE2_coord = best_e2([tuple(span_basis(f)) for f in tot], rad, all_subspaces=False)
    cstQ = sum(quot_dim(span_basis(f), rad) for f in tot)
    # pairing rank between the span of a total's source labels and the readers' span (all ports)
    cstC = sum(f2_rank(np.array([[dot2(a, b) for b in ports] for a in span_basis(f)])) for f in tot)
    rad_vecs = sorted(x for x in _span_elems(rad) if x)
    check('C4.toy_p3.degeneracy', (d, rho, d - rho) == (Ex['d'], Ex['rho'], Ex['r']) and rad_vecs == sorted(Ex['rad']),
          'port span d = %d, radical rho = %d (nonzero radical vectors %s), Gram rank %d'
          % (d, rho, [format(x, '06b') for x in rad_vecs], d - rho))
    check('C4.toy_p3.costs', (len(tot), cst0, cstE2, cstE2_coord, cstQ, cstC) == (Ex['n_totals'], Ex['cst0'], Ex['cstE2'], Ex['cstE2'],
                                                                                  Ex['cstQ'], Ex['cstQ'])
          and all(len(span_basis(f)) == Ex['dim_f'] for f in tot),
          '%d totals of dim %d: copy cost at 0 = %d, best cut schedule over all flags of rad = %d (coordinate flags: %d), '
          'quotient = %d = pairing-rank bound %d' % (len(tot), Ex['dim_f'], cst0, cstE2, cstE2_coord, cstQ, cstC))
    labels = {reduce_mod(p, rad) for p in ports}
    check('C4.toy_p3.window_labels', (c['h'], d - rho, len(labels)) == (Ex['window_deg'], Ex['window_quot'], Ex['n_labels']),
          'window of the degenerate realisation %d, of the quotient %d; quotient has %d distinct labels (ports mod rad)'
          % (c['h'], d - rho, len(labels)))
    print('  (toy_p3: %.1f s)' % (time.time() - t0), flush=True)
    return dict(d=d, rho=rho, cstE2=cstE2, cstQ=cstQ, window=c['h'], v=c['v'])


def reduce_mod(x, rad):
    for b in rad:
        if x ^ b < x:
            x ^= b
    return x


# ---------------------------------------------------------------------------------------------------------------
def paired_cube(p, tau=3):
    ports = []
    for I in itertools.combinations(range(p), tau):
        for bb in itertools.product((0, 1), repeat=tau):
            x = [0] * (2 * p)
            for i, b in zip(I, bb):
                x[2 * i + b] = 1
            ports.append(x)
    return ports


def paired_cubes():
    t0 = time.time()
    degenerate_cx, degenerate_bit, vs, bit_dims = [], [], {}, {}
    for p in range(3, 13):
        P = paired_cube(p)
        vs[p] = len(P)
        ints = [rows_to_int(r) for r in P]
        B = span_basis(ints)
        rho = len(f2_rad(B))
        # bit side: Q labels with form 9 I - J; window = rank_Q of the Gram L Q L^T/9, d = rank_Q L
        h = 2 * p
        Q = [[(9 if i == j else 0) - 1 for j in range(h)] for i in range(h)]
        dq = len(row_basis_idx_q(P))
        rq = gram_rank_q(P, Q, range(len(P)))
        if rho:
            degenerate_cx.append((p, len(B), rho))
        if dq != rq:
            degenerate_bit.append((p, dq, rq))
        bit_dims[p] = (dq, rq)
    check('C4.paired.complex', vs == EXPECTED['paired_v'] and degenerate_cx == [(3, 4, 2)],
          'ports %s; complex labels degenerate only for (p, d, rho) = %s' % (list(vs.values()), degenerate_cx))
    check('C4.paired.bit', not degenerate_bit and all(bit_dims[p] == ((4, 4) if p == 3 else (2 * p, 2 * p)) for p in bit_dims),
          'bit labels (form 9I - J): rank of the labels = rank of the Gram for every p = 3..12 (p: rank) %s; degenerate: %s'
          % ({p: bit_dims[p][0] for p in bit_dims}, degenerate_bit))
    print('  (paired cubes: %.1f s)' % (time.time() - t0), flush=True)


# ---------------------------------------------------------------------------------------------------------------
def e8_rows(rng):
    """the E8 decorations.  The random draws are made in a fixed order (bit decorations, then complex ones) so that the
    generator state after this function is deterministic; it is passed on to the random tests."""
    L, G = standard_e8()
    v = 120
    U9 = e8_labels(G)
    bit_tots = [np.nonzero(U9[:, j])[0] for j in range(9)]          # 9 totals S_j = ports with label bit j set
    cx_tots = [(np.nonzero(L[:, a])[0], np.nonzero(L[:, a])[0]) for a in range(8)]     # coordinate a: readers = sources
    rows = {}

    def bit_decorated(cvec, key):
        P = np.hstack([L, np.array(cvec, dtype=np.int64).reshape(-1, 1), np.zeros((v, 1), dtype=np.int64)])
        e = np.zeros(10, dtype=np.int64)
        e[8] = 1
        d, r = rank_q(P.tolist()), 8
        rho = d - r
        c0 = cE2 = cQ = cC = 0
        for Sj in bit_tots:
            F = P[Sj]
            df = rank_q(F.tolist())
            e_in = rank_q(np.vstack([F, e]).tolist()) == df
            c0 += df
            cE2 += min(df, df + 1 - 2 * int(e_in)) if rho == 1 else df       # cuts: 0 or the line <e>
            cQ += rank_q(L[Sj].tolist())
            cC += rank_q(G[np.ix_(Sj, Sj)].tolist())
        rows[key] = (d, rho, r, d + rho, c0, cE2, cQ, cC)

    bit_decorated([0] * v, 'bit_control')
    bit_decorated([1] * v, 'bit_e_all')
    bit_decorated([rng.randint(0, 1) for _ in range(v)], 'bit_e_random')
    bit_decorated([rng.randint(-3, 3) for _ in range(v)], 'bit_e_lifts')

    u = [rows_to_int(U9[t]) for t in range(v)]
    assert all(dot2(u[s], u[t]) == ((1 + G[s, t]) % 2) for s in range(v) for t in range(v))

    def cx_decorated(cmat, rho_max, key):
        E = [(1 << (9 + 2 * i)) | (1 << (10 + 2 * i)) for i in range(rho_max)]       # weight-2 isotropic directions
        q = []
        for t in range(v):
            x = u[t]
            for i in range(rho_max):
                if cmat[t] >> i & 1:
                    x ^= E[i]
            q.append(x)
        assert all(dot2(q[s], q[t]) == dot2(u[s], u[t]) for s in range(v) for t in range(v))    # Gram unchanged
        B = span_basis(q)
        rad = f2_rad(B)
        d, rho = len(B), len(rad)
        r = d - rho
        c0 = cQ = cC = 0
        fs = []
        for R, A in cx_tots:
            f = span_basis([q[t] for t in A])
            fs.append(tuple(f))
            c0 += len(f)
            cQ += quot_dim(f, rad)
            cC += f2_rank(np.array([[dot2(q[a], q[b]) for b in R] for a in A]))
        cE2 = best_e2(fs, rad) if rho >= 1 else c0
        cE2c = best_e2(fs, rad, all_subspaces=False) if rho >= 1 else c0
        rows[key] = (d, rho, r, d + rho, c0, cE2, cQ, cC)
        rows[key + '_coordflags'] = cE2c

    cx_decorated([0] * v, 0, 'cx_control')
    cx_decorated([1] * v, 1, 'cx_e_all')
    for rho_max in (1, 2, 3):
        cx_decorated([rng.randrange(1 << rho_max) for _ in range(v)], rho_max, 'cx_rho%d' % rho_max)
    cx_decorated([(1 if t in set(cx_tots[0][1].tolist()) else 0) | (2 if t in set(cx_tots[1][1].tolist()) else 0) for t in range(v)],
                 2, 'cx_aligned')
    return rows


def check_e8(rows):
    Ex = EXPECTED
    names = ('d', 'rho', 'r', 'window', 'cst0', 'cstE2', 'cstQ', 'cstPair')

    def fmt(t):
        return ', '.join('%s %d' % (n, x) for n, x in zip(names, t))
    check('C4.e8_bit_e.controls', rows['bit_control'] == (8, 0, 8, 8, 72, 72, 72, 72),
          'undecorated bit E8: ' + fmt(rows['bit_control']))
    ok = all(rows[k] == Ex['e8_bit_e'] for k in ('bit_e_all', 'bit_e_random', 'bit_e_lifts'))
    check('C4.e8_bit_e', ok, 'E8 bit + isotropic e (every port / random ports / lifts n_T e): ' + fmt(rows['bit_e_all'])
          + '; window 10 vs quotient 8')
    check('C4.e8_cx.controls', rows['cx_control'] == (9, 0, 9, 9, 72, 72, 72, 72) and rows['cx_e_all'][1] == 0,
          'undecorated complex E8: ' + fmt(rows['cx_control']))
    for k in (1, 2, 3):
        t = rows['cx_rho%d' % k]
        check('C4.e8_cx.rho%d' % k, t == Ex['e8_cx'][k], 'E8 complex + weight-2 isotropic decoration rho=%d: %s '
              '(coordinate-flag optimum %d)' % (k, fmt(t), rows['cx_rho%d_coordflags' % k]))
    t = rows['cx_aligned']
    check('C4.e8_cx.aligned', t == Ex['e8_cx_aligned'],
          'aligned decoration (e1 on total-0 sources, e2 on total-1 sources): %s (coordinate-flag optimum %d)'
          % (fmt(t), rows['cx_aligned_coordflags']))
    return rows


# ---------------------------------------------------------------------------------------------------------------
def random_extra(rng):
    """random instances with extra-coordinate radicals: odd-weight vectors in F_2^n decorated by weight-2 isotropic
    directions in extra coordinates."""
    tests = viol = viol_c = gain = gain_c = 0
    for trial in range(400):
        n = rng.randint(6, 9)
        rho_t = rng.randint(1, 3)
        E = [(1 << (n + 2 * i)) | (1 << (n + 1 + 2 * i)) for i in range(rho_t)]
        nports = rng.randint(6, 14)
        ports = []
        while len(ports) < nports:
            x = rng.randrange(1, 1 << n)
            if bin(x).count('1') % 2 == 1:
                for i in range(rho_t):
                    if rng.random() < 0.5:
                        x ^= E[i]
                ports.append(x)
        B = span_basis(ports)
        rad = f2_rad(B)
        if not rad:
            continue
        ntot = rng.randint(2, 6)
        fs = [tuple(span_basis(rng.sample(ports, rng.randint(2, len(ports))))) for _ in range(ntot)]
        cE2 = best_e2(fs, rad)
        cE2c = best_e2(fs, rad, all_subspaces=False)
        cQ = sum(quot_dim(f, rad) for f in fs)
        c0 = sum(len(f) for f in fs)
        tests += 1
        viol += cE2 < cQ
        viol_c += cE2c < cQ
        gain += cE2 < c0
        gain_c += cE2c < c0
    return dict(tests=tests, violations=viol, violations_coord=viol_c, gain=gain_c, gain_all=gain)


def random_intrinsic():
    """W a random subspace of F_2^n (n 6..10) with a nonzero radical; ports = odd-norm vectors of W."""
    rng = random.Random(7)
    tests = viol = viol_c = gain = gain_c = eq = eq_c = 0
    while tests < 400:
        n = rng.randint(6, 10)
        k = rng.randint(3, n - 1)
        gens = [rng.randrange(1, 1 << n) for _ in range(k)]
        B = span_basis(gens)
        rad = f2_rad(B)
        if not rad or len(rad) > 3:
            continue
        span = [0]
        for b in B:
            span += [x ^ b for x in span]
        odd = [x for x in span if dot2(x, x) == 1]
        if len(odd) < 6:
            continue
        ports = rng.sample(odd, min(len(odd), rng.randint(6, 16)))
        Bp = span_basis(ports)
        radp = f2_rad(Bp)
        if not radp or len(radp) > 3:
            continue
        fs = [tuple(span_basis(rng.sample(ports, rng.randint(2, len(ports))))) for _ in range(rng.randint(2, 6))]
        cE2 = best_e2(fs, radp)
        cE2c = best_e2(fs, radp, all_subspaces=False)
        cQ = sum(quot_dim(f, radp) for f in fs)
        c0 = sum(len(f) for f in fs)
        tests += 1
        viol += cE2 < cQ
        viol_c += cE2c < cQ
        gain += cE2 < c0
        gain_c += cE2c < c0
        eq += cE2 == cQ
        eq_c += cE2c == cQ
    return dict(tests=tests, violations=viol, violations_coord=viol_c, gain=gain_c, gain_all=gain, equal=eq_c, equal_all=eq)


# ---------------------------------------------------------------------------------------------------------------
def certified_X(h, k, cst, v):
    """(best hi over s = 3,5,..,13, s) of the certified skeleton exponent, or (None, None) if D <= 0 at every s."""
    x = Fr(cst, v)
    best = (None, None)
    for s in (3, 5, 7, 9, 11, 13):
        r = skel_X(s, h, k, x)
        if r is not None:
            hi = float(r['hi'])
            if best[0] is None or hi > best[0]:
                best = (hi, s)
    return best


def check_X(toy, rows):
    t0 = time.time()
    cases = {          # key: (h, cst, v)
        'toy_deg': (toy['window'], toy['cstE2'], toy['v']),
        'toy_quot': (toy['d'] - toy['rho'], toy['cstQ'], toy['v']),
        'bit_quot': (rows['bit_e_all'][2], rows['bit_e_all'][6], 120),
        'bit_e_deg': (rows['bit_e_all'][3], rows['bit_e_all'][5], 120),
        'cx_quot': (rows['cx_rho1'][2], rows['cx_rho1'][6], 120),
        'cx_rho1': (rows['cx_rho1'][3], rows['cx_rho1'][5], 120),
        'cx_rho2': (rows['cx_rho2'][3], rows['cx_rho2'][5], 120),
        'cx_rho3': (rows['cx_rho3'][3], rows['cx_rho3'][5], 120),
        'bit_punct': (8, 63, 111),          # punctured references: 111 ports, copy cost 63
        'cx_punct': (9, 64, 112),           # 112 ports, copy cost 64 (the binding reference)
        'bit_star_floor': (8, 64, 120),     # 64/120: unattained star-scope bounds for repeated labels
        'cx_star_floor': (9, 64, 120),
    }
    got = {}
    for key, (h, cst, v) in cases.items():
        hi, s = certified_X(h, 1, cst, v)
        got[key] = None if hi is None else '%.4e' % hi
        print('   %-15s h=%2d cst/v=%d/%d  X* = %s (s=%s)' % (key, h, cst, v, got[key] or 'D<=0 at every s', s), flush=True)
    Ex = EXPECTED['X']
    check('C4.X.toy', got['toy_deg'] == Ex['toy_deg'] and got['toy_quot'] == Ex['toy_quot'],
          'toy_p3: deficit D <= 0 at every s for the degenerate (h=6, 16/8) and the quotient (h=2, 12/8) unit')
    check('C4.X.bit', (got['bit_quot'], got['bit_e_deg']) == (Ex['bit_quot'], Ex['bit_e_deg']),
          'bit E8: quotient (h=8, 72/120) X* = %s versus +e realisation (h=10, 72/120) X* = %s' % (got['bit_quot'], got['bit_e_deg']))
    check('C4.X.cx', tuple(got[k] for k in ('cx_quot', 'cx_rho1', 'cx_rho2', 'cx_rho3'))
          == tuple(Ex[k] for k in ('cx_quot', 'cx_rho1', 'cx_rho2', 'cx_rho3')),
          'complex E8: quotient (h=9) X* = %s versus rho=1/2/3 realisations (h=11/13/15) %s / %s / %s'
          % (got['cx_quot'], got['cx_rho1'], got['cx_rho2'], got['cx_rho3']))
    check('C4.X.references', (got['bit_punct'], got['cx_punct']) == (Ex['bit_punct'], Ex['cx_punct']),
          'punctured references: bit 111/63 (h=8) X* = %s, complex 112/64 (h=9) X* = %s (binding)' % (got['bit_punct'], got['cx_punct']))
    check('C4.X.star_floor', (got['bit_star_floor'], got['cx_star_floor']) == (Ex['bit_star_floor'], Ex['cx_star_floor']),
          'star-scope floor cst/v = 64/120 (unattained bound for repeated labels): bit %s, complex %s'
          % (got['bit_star_floor'], got['cx_star_floor']))
    print('  (certified X: %.1f s)' % (time.time() - t0), flush=True)


def main():
    t_start = time.time()
    toy = toy_p3()
    paired_cubes()
    t0 = time.time()
    rng = random.Random(1)
    rows = e8_rows(rng)
    check_e8(rows)
    print('  (E8 decorations: %.1f s)' % (time.time() - t0), flush=True)
    t0 = time.time()
    re = random_extra(rng)
    Ex = EXPECTED['random_extra']
    check('C4.random_extra', (re['tests'], re['violations'], re['violations_coord'], re['gain'], re['gain_all'])
          == (Ex['tests'], 0, 0, Ex['gain'], Ex['gain_all']),
          '%d instances with extra-coordinate radicals: violations of cst_E2\' >= cst_quotient: %d (coordinate flags: %d); '
          'a cut schedule beats reading at 0 in %d (coordinate flags: %d)'
          % (re['tests'], re['violations'], re['violations_coord'], re['gain_all'], re['gain']))
    ri = random_intrinsic()
    Ex = EXPECTED['random_intrinsic']
    check('C4.random_intrinsic', (ri['tests'], ri['violations'], ri['violations_coord'], ri['gain'], ri['gain_all'], ri['equal'], ri['equal_all'])
          == (Ex['tests'], 0, 0, Ex['gain'], Ex['gain_all'], Ex['equal'], Ex['equal_all']),
          '%d instances with intrinsic radicals: violations %d (coordinate flags: %d); schedule beats reading at 0 in %d '
          '(coordinate flags: %d), equals the quotient in %d (coordinate flags: %d)'
          % (ri['tests'], ri['violations'], ri['violations_coord'], ri['gain_all'], ri['gain'], ri['equal_all'], ri['equal']))
    print('  (random tests: %.1f s)' % (time.time() - t0), flush=True)
    check_X(toy, rows)
    print('total %.1f s' % (time.time() - t_start))
    finish()


if __name__ == '__main__':
    main()
