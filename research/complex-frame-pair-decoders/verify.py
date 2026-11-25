#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Frame-pair decoders and the exact 8-term copy-cost floor on punctured complex E8 units.

Standard library only. Exact integer, F2 and rational arithmetic throughout.

Model (PR717 B14, D2/D3 scope): the 120 E8 root lines; a puncture P removes lines; an exact
8-term decoder is D = R A, T = R B with A B^T = 2 I, so that D T^T = 2G on the live lines
(G the integer inner products).  Term k costs the F2 rank of the label pairing between its row
support (live lines not orthogonal to a_k) and column support (live lines not orthogonal to b_k).
The label pairing of two lines is (<r_i, r_j> + 1) mod 2, which this script uses directly; it
never constructs PR717's simple-root coordinates.

Sections (each prints PASS/FAIL lines):
  A  model facts: 120 lines, nondegenerate rank-9 pairing, distinct pairing rows
  B  violator census for the eight W(E8) hyperplane-flat types (all 511 hyperplanes and all
     130,305 codimension-2 pairs of F2^9 functionals)
  C  the D7 orbit: 1080 directions, unique 14-line violator sets, pairwise unions >= 21, no
     coincidence with a root functional
  D  frame-pair census: all 1260 frames disjoint from the coordinate frame, all (S, T) splits;
     every solution is built and checked exactly
  E  attaining chain: explicit exact decoders for every puncture size p = 0..24
  F  replay of the three vendored PR717 D3 hits and their root-pair structure
  G  favorable-budget pricing on the selected (U8/T37) profile with the pinned moment and outer
     engines, and the PR589 bit-supplier cap
  H  negative controls
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []
LOG = []


def check(tag, cond, info=''):
    line = ('PASS ' if cond else 'FAIL ') + tag + (' | ' + info if info else '')
    print(line, flush=True)
    LOG.append(line)
    if not cond:
        FAILS.append(tag)


# ---------------------------------------------------------------- A. E8 lines and pairing
def e8_roots():
    """240 roots in doubled coordinates; same enumeration order as PR717's e8model (adapter only)."""
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0] * 8
                v[i], v[j] = 2 * si, 2 * sj
                roots.append(tuple(v))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            roots.append(tuple(s))
    return roots


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def ip(x, y):
    """True inner product of doubled-coordinate vectors."""
    d = dot(x, y)
    assert d % 4 == 0
    return d // 4


def neg(v):
    return tuple(-a for a in v)


ROOTS = e8_roots()
LINES = []
_seen = set()
for r in ROOTS:
    key = r if r > neg(r) else neg(r)
    if key not in _seen:
        _seen.add(key)
        LINES.append(r)
NL = len(LINES)
IP = [[ip(LINES[i], LINES[j]) for j in range(NL)] for i in range(NL)]
# Label pairing as a 120-bit row mask: bit j of NROW[i] is (<r_i,r_j> + 1) mod 2.
NROW = [sum(((IP[i][j] + 1) & 1) << j for j in range(NL)) for i in range(NL)]
ALL = (1 << NL) - 1
FRAME0 = []
for a in range(4):
    for s in (1, -1):
        v = [0] * 8
        v[2 * a], v[2 * a + 1] = 2, 2 * s
        FRAME0.append(LINES.index(tuple(v)))
P112 = [i for i in range(NL) if i not in FRAME0]


def popcount(x):
    return bin(x).count('1')


def f2_rank(rows):
    basis = {}
    rank = 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                rank += 1
                break
    return rank


def mask(idx):
    m = 0
    for i in idx:
        m |= 1 << i
    return m


def pair_rank(rows, cols):
    """F2 rank of the label pairing between the lines in `rows` and the lines in `cols`."""
    cm = mask(cols)
    return f2_rank([NROW[i] & cm for i in rows])


def span_dim(idx):
    return f2_rank([NROW[i] for i in idx])


def section_a():
    check('A.lines', NL == 120 and len(ROOTS) == 240, '120 lines from 240 roots')
    check('A.pairing-values', all(IP[i][i] == 2 for i in range(NL)) and
          {IP[i][j] for i in range(NL) for j in range(NL) if i != j} == {-1, 0, 1},
          'line inner products are 2 on the diagonal and 0/+-1 off it')
    check('A.pairing-rank-9', f2_rank(NROW) == 9, 'the 120x120 label pairing has F2 rank 9 (nondegenerate on the 9-dim label span)')
    check('A.distinct-rows', len(set(NROW)) == 120, 'distinct lines have distinct pairing rows (distinct label functionals)')
    check('A.frame0', len(FRAME0) == 8 and all(IP[a][b] == 0 for a in FRAME0 for b in FRAME0 if a != b),
          'coordinate frame e_{2a} +- e_{2a+1}: eight mutually orthogonal lines; P112 has %d lines' % len(P112))


# Dual coordinates: phi_i = (pairing with nine basis lines).  An F2-linear isomorphism of the label span,
# so the 511 nonzero functionals lambda . phi_i are exactly the 511 hyperplanes of the label space.
def dual_coordinates():
    basis = []
    for i in range(NL):
        if f2_rank([NROW[b] for b in basis] + [NROW[i]]) == len(basis) + 1:
            basis.append(i)
        if len(basis) == 9:
            break
    phi = [sum(((NROW[i] >> b) & 1) << k for k, b in enumerate(basis)) for i in range(NL)]
    return basis, phi


BASIS9, PHI = dual_coordinates()
LAMBDAS = list(range(1, 512))
VMASK = {lam: mask(i for i in range(NL) if popcount(lam & PHI[i]) & 1) for lam in LAMBDAS}
ROOT_FUNCTIONAL = {}
for _i in range(NL):
    # the functional of line i: lambda with lambda . phi_j = pairing(i, j) for all j
    _cands = [lam for lam in LAMBDAS if VMASK[lam] == NROW[_i]]
    assert len(_cands) == 1
    ROOT_FUNCTIONAL[_i] = _cands[0]


# ---------------------------------------------------------------- B. violator census
def solve_rational(M, rhs):
    """Solve M x = rhs exactly (M square, invertible) with Fractions."""
    n = len(M)
    A = [[Q(x) for x in row] + [Q(b)] for row, b in zip(M, rhs)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c] / A[c][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [A[i][n] / A[i][i] for i in range(n)]


SIMPLE = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0), (-2, 2, 0, 0, 0, 0, 0, 0)] + \
    [tuple(-2 if t == k else 2 if t == k + 1 else 0 for t in range(8)) for k in range(1, 6)]


def fundamental_weights():
    """omega_i with <omega_i, alpha_j> = delta_ij, as integer doubled-coordinate directions."""
    out = []
    for i in range(8):
        # unknown x (true coordinates): sum_t x_t * alpha_j[t]/2 = delta_ij
        M = [[Q(a, 2) for a in alpha] for alpha in SIMPLE]
        x = solve_rational(M, [1 if j == i else 0 for j in range(8)])
        den = 1
        for v in x:
            den = den * v.denominator // math.gcd(den, v.denominator)
        vec = tuple(int(v * den) for v in x)
        out.append(vec)
    return out


def support_mask(a):
    return mask(i for i in range(NL) if dot(a, LINES[i]) != 0)


def census_type(a):
    C = support_mask(a)
    sizes = sorted(popcount(VMASK[lam] & C) for lam in LAMBDAS)
    vm = [VMASK[lam] & C for lam in LAMBDAS]
    pi7 = min(popcount(vm[x] | vm[y]) for x in range(511) for y in range(x + 1, 511))
    span = f2_rank([NROW[i] for i in range(NL) if C >> i & 1])
    return dict(support=popcount(C), flat_lines=NL - popcount(C), span=span, pi8=sizes[0], pi8_second=sizes[1], pi7=pi7)


EXPECTED_TYPES = {  # flat lines -> (subsystem, |C|, pi8, second pi8, pi7)
    63: ('E7', 57, 1, 24, 25), 42: ('D7', 78, 14, 34, 42), 37: ('E6+A1', 83, 27, 28, 51),
    28: ('A7', 92, 28, 35, 56), 23: ('D5+A2', 97, 33, 41, 61), 22: ('A6+A1', 98, 35, 35, 62),
    16: ('A4+A3', 104, 40, 43, 68), 14: ('A4+A2+A1', 106, 43, 43, 70)}


def section_b():
    weights = fundamental_weights()
    check('B.weights', all(sum(Q(dot(w, a), 4) == 0 for a in SIMPLE) == 7 for w in weights),
          'eight fundamental-weight directions, each orthogonal to seven simple roots')
    rows = {}
    for w in weights:
        info = census_type(w)
        rows[info['flat_lines']] = info
    ok = set(rows) == set(EXPECTED_TYPES) and all(
        (rows[f]['support'], rows[f]['pi8'], rows[f]['pi8_second'], rows[f]['pi7']) == EXPECTED_TYPES[f][1:]
        and rows[f]['span'] == 9 for f in rows)
    table = '; '.join('%s flat %d: |C|=%d pi8=%d (next %d) pi7=%d' % (EXPECTED_TYPES[f][0], f, rows[f]['support'],
                      rows[f]['pi8'], rows[f]['pi8_second'], rows[f]['pi7']) for f in sorted(rows, reverse=True))
    check('B.census', ok, table)
    nonroot = min(rows[f]['pi8'] for f in rows if f != 63)
    check('B.thresholds', nonroot == 14 and rows[63]['pi8_second'] == 24 and min(r['pi7'] for r in rows.values()) == 25,
          'only E7 (root) normals drop to an 8-dim span with one puncture (their own line); every other type needs >= 14; '
          'a root normal by another hyperplane needs >= 24; any 7-dim span needs >= 25 punctures')
    # the root type's unique one-line violator set is the line itself, through its own functional
    alpha = next(i for i in range(NL) if LINES[i] == (2, 2, 0, 0, 0, 0, 0, 0))
    C = support_mask(LINES[alpha])
    check('B.root-self-line', VMASK[ROOT_FUNCTIONAL[alpha]] & C == 1 << alpha,
          'for a root normal alpha the 1-line violator set is {alpha}, via the functional of alpha itself')
    allroots = True
    for i in range(NL):
        C = support_mask(LINES[i])
        sizes = sorted((popcount(VMASK[lam] & C), lam) for lam in LAMBDAS)
        allroots &= sizes[0] == (1, ROOT_FUNCTIONAL[i]) and VMASK[ROOT_FUNCTIONAL[i]] & C == 1 << i and sizes[1][0] == 24
    check('B.root-all-120', allroots, 'checked directly for all 120 root normals: unique 1-line set {alpha}; every other hyperplane >= 24')
    return rows, weights


# ---------------------------------------------------------------- C. D7 orbit
def canon(v):
    g = 0
    for a in v:
        g = math.gcd(g, abs(a))
    v = tuple(a // g for a in v)
    first = next(a for a in v if a)
    return v if first > 0 else neg(v)


def orbit(start):
    seen = {canon(start)}
    frontier = [canon(start)]
    while frontier:
        nxt = []
        for v in frontier:
            for r in LINES:
                d = dot(v, r)
                u = tuple(4 * a - d * b for a, b in zip(v, r))  # 4 * reflection, integral
                c = canon(u)
                if c not in seen:
                    seen.add(c)
                    nxt.append(c)
        frontier = nxt
    return sorted(seen)


def section_c(weights):
    d7 = next(w for w in weights if NL - popcount(support_mask(w)) == 42)
    dirs = orbit(d7)
    check('C.orbit', len(dirs) == 1080, 'W(E8) orbit of the D7 normal: %d directions' % len(dirs))
    v14 = {}
    root_funcs = set(ROOT_FUNCTIONAL.values())
    coincide = 0
    inflat_all = True
    rank_ok = True
    for d in dirs:
        C = support_mask(d)
        sizes = sorted((popcount(VMASK[lam] & C), lam) for lam in LAMBDAS)
        assert sizes[0][0] == 14 and sizes[1][0] >= 34
        lam = sizes[0][1]
        v14[d] = VMASK[lam] & C
        coincide += lam in root_funcs
        flat = [i for i in range(NL) if not C >> i & 1]
        inflat_all &= all(popcount(VMASK[lam] >> i & 1) for i in flat)
        # removing any one flat line leaves a rank-7 set: a flat of rank <= 6 misses >= 2 of the 42 lines
        # (not needed by the main argument; recorded as a cross-check of D7 rigidity)
        if d == dirs[0]:
            rank_ok = all(rank_q([LINES[j] for j in flat if j != i]) == 7 for i in flat)
    sets = list(v14.values())
    check('C.unique-14', len(set(sets)) == 1080, 'each D7 direction has a unique 14-line violator set (next >= 34); 1080 distinct sets')
    mn = min(popcount(a | b) for a, b in itertools.combinations(sets, 2))
    check('C.unions', mn == 21, 'any two distinct D7 violator sets have union >= %d > 15' % mn)
    check('C.no-root-coincidence', coincide == 0, 'no D7 minimizing functional equals a root functional')
    check('C.flat-lines-violate', inflat_all and rank_ok, 'all 42 flat lines violate the minimizing functional; flat minus any line has rank 7')
    return len(dirs)


def rank_q(vectors):
    rows = [[Q(x) for x in v] for v in vectors]
    r = 0
    ncol = len(rows[0]) if rows else 0
    for c in range(ncol):
        p = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c] / rows[r][c]
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


# ---------------------------------------------------------------- decoders
def decoder_cost(rowvecs, colvecs, live):
    """Exactness of D T^T = 2G on `live` and the per-term costs."""
    live = list(live)
    D = [[ip(LINES[i], a) for a in rowvecs] for i in live]
    T = [[ip(LINES[i], b) for b in colvecs] for i in live]
    exact = all(sum(x * y for x, y in zip(D[p], T[q])) == 2 * IP[live[p]][live[q]]
                for p in range(len(live)) for q in range(len(live)))
    costs = []
    for k in range(len(rowvecs)):
        R = [live[p] for p in range(len(live)) if D[p][k]]
        A = [live[p] for p in range(len(live)) if T[p][k]]
        costs.append(pair_rank(R, A))
    return exact, costs


def frames_in(pool):
    pool = list(pool)
    orth = {i: mask(j for j in pool if j != i and IP[i][j] == 0) for i in pool}
    out = []

    def rec(clique, cand):
        if len(clique) == 8:
            out.append(tuple(clique))
            return
        c = cand
        while c:
            j = c.bit_length() - 1
            c &= ~(1 << j)
            rec(clique + [j], cand & orth[j] & ((1 << j) - 1))

    for i in pool:
        rec([i], orth[i] & ((1 << i) - 1))
    return sorted(tuple(sorted(f)) for f in out)


def frame_pair_solutions(F0, F1):
    """All splits: row normals S (from F0) and T (from F1); every column partner is a cross-frame line with
    odd inner product and orthogonal to all other row normals.

    Eight-bit neighborhood masks (woklerx #1099 / frame-pair-enumeration-fast-seed93)
    preserve the exact search domain, acceptance condition, multiplicity and order.
    """
    if len(F0) != 8 or len(F1) != 8 or len(set(F0 + F1)) != 16:
        raise ValueError('two disjoint ordered eight-element frames required')
    neighbors = [sum(bool(IP[g][f]) << j for j, f in enumerate(F0)) for g in F1]
    reverse_neighbors = [sum(bool(IP[f][g]) << j for j, g in enumerate(F1)) for f in F0]
    sols = []
    for selected in range(256):
        left = [j for j in range(8) if selected >> j & 1]
        partners = [[] for _ in range(8)]
        for g, adjacent in enumerate(neighbors):
            hit = adjacent & selected
            if hit and hit & (hit - 1) == 0:
                partners[hit.bit_length() - 1].append(g)
        if any(not partners[f] for f in left):
            continue
        for choice in itertools.product(*(partners[f] for f in left)):
            # Retain the reference injectivity guard even though singleton
            # neighborhoods already partition these first-partner lists.
            if len(set(choice)) != len(left):
                continue
            chosen = sum(1 << g for g in choice)
            right = [g for g in range(8) if not chosen >> g & 1]
            remainder = [f for f in range(8) if not selected >> f & 1]
            second = [[] for _ in range(8)]
            for f in remainder:
                hit = reverse_neighbors[f] & (255 ^ chosen)
                if hit and hit & (hit - 1) == 0:
                    second[hit.bit_length() - 1].append(f)
            if any(not second[g] for g in right):
                continue
            for choice2 in itertools.product(*(second[g] for g in right)):
                if len(set(choice2)) != len(right):
                    continue
                sols.append([(F0[f], F1[g]) for f, g in zip(left, choice)] +
                            [(F1[g], F0[f]) for g, f in zip(right, choice2)])
    return sols


def pair_decoder(pairs, live):
    """Root-pair decoder (a_k = alpha_k, b_k = 2<alpha_k,beta_k> beta_k).  Exactness on every live set is
    equivalent to <a_k, b_l> = 2 delta_kl, i.e. A^T B = 2I, hence A B^T = 2I and D T^T = R (A B^T) R^T = 2G."""
    dual = all((IP[a][b] in (1, -1)) if k == l else IP[a][b] == 0
               for k, (a, _) in enumerate(pairs) for l, (_, b) in enumerate(pairs))
    costs = [pair_rank([i for i in live if IP[a][i]], [i for i in live if IP[b][i]]) for a, b in pairs]
    return dual, costs


def build_pairs(pairs):
    rows, cols = [], []
    for a, b in pairs:
        e = IP[a][b]
        assert e in (1, -1)
        rows.append(LINES[a])
        cols.append(tuple(2 * e * x for x in LINES[b]))
    return rows, cols


def relative_type(F0, F1):
    common = Counter(sum(1 for f in F0 if IP[g][f] and IP[h][f]) for g, h in itertools.combinations(F1, 2))
    return tuple(sorted(common.items()))


def section_d():
    F1s = frames_in(P112)
    check('D.frames', len(F1s) == 1260, '%d frames inside P112 (disjoint from the coordinate frame)' % len(F1s))
    hist = Counter()
    types = Counter()
    built = 0
    allgood = True
    example = None
    for F1 in F1s:
        sols = frame_pair_solutions(FRAME0, list(F1))
        hist[len(sols)] += 1
        types[(len(sols) > 0, relative_type(FRAME0, F1))] += 1
        live = [i for i in range(NL) if i not in FRAME0 and i not in F1]
        for pairs in sols:
            exact, costs = pair_decoder(pairs, live)
            built += 1
            allgood &= exact and costs == [7] * 8
            if example is None:
                example = dict(F1=list(F1), pairs=pairs)
    check('D.census', hist == Counter({8: 896, 0: 364}), 'solutions per frame: %s' % dict(sorted(hist.items())))
    tdesc = {str(k): v for k, v in sorted(types.items(), key=lambda kv: -kv[1])}
    check('D.types', len(types) == 3 and all(ok == (dict(t).get(4, 0) == 0) for ok, t in types),
          'relative position (common F0-neighbours of F1 pairs) -> admissible: %s' % tdesc)
    check('D.exact-56', allgood and built == 7168, '%d frame-pair decoders built; every one satisfies A^T B = 2I and has eight cost-7 terms on its P104 (cst 56)' % built)
    F1 = example['F1']
    live = [i for i in range(NL) if i not in FRAME0 and i not in F1]
    rows, cols = build_pairs(example['pairs'])
    exact, costs = decoder_cost(rows, cols, live)
    check('D.full-exactness-crosscheck', exact and costs == [7] * 8, 'one decoder rechecked entrywise: D T^T = 2G on all 104 x 104 live pairs')
    return F1s, example, hist, types


def section_e(F1s, example):
    F1 = example['F1']
    pairs = example['pairs']
    # ordering of F1 lines: each F1 line is the self-line of exactly one term
    f1order = [b if b in F1 else a for a, b in pairs]
    chain = {}
    extra = [i for i in range(NL) if i not in FRAME0 and i not in F1]
    coord_rows = [LINES[f] for f in FRAME0]
    for p in range(0, 25):
        if p <= 8:
            P = FRAME0[:p]
            rows, cols = coord_rows, coord_rows
            kind = 'coordinate frame, %d of its lines punctured' % p
        else:
            j = min(p - 8, 8)
            P = FRAME0 + f1order[:j] + extra[:max(0, p - 16)]
            rows, cols = build_pairs(pairs)
            kind = 'frame pair, %d partner lines + %d extra lines punctured' % (j, max(0, p - 16))
        live = [i for i in range(NL) if i not in P]
        exact, costs = decoder_cost(rows, cols, live)
        bound = max(72 - p, 56)
        chain[p] = dict(live=len(live), exact=exact, cost=sum(costs), lower_bound=bound, kind=kind,
                        ratio=str(Q(sum(costs), len(live))), punctured=sorted(P), live_rank=rank_q([LINES[i] for i in live]))
    ok = all(c['exact'] and c['cost'] == c['lower_bound'] and c['live_rank'] == 8 and len(c['punctured']) == p
             for p, c in chain.items())
    check('E.chain', ok, 'p=0..24: exact decoders with cst = max(72-p, 56) at every p (attaining the theorem)')
    best = min(chain, key=lambda p: Q(chain[p]['cost'], chain[p]['live']))
    check('E.best-ratio', best == 16 and Q(chain[16]['cost'], chain[16]['live']) == Q(7, 13) and
          Q(chain[8]['cost'], chain[8]['live']) == Q(4, 7),
          'minimum copy ratio along the chain is 56/104 = 7/13 at p = 16 (P112: 64/112 = 4/7)')
    return chain


# ---------------------------------------------------------------- F. PR717 hit replay
def load_hit(path):
    D, T = [], []
    for line in path.read_text().splitlines():
        s = line.strip()
        if s.startswith('d:'):
            D.append([int(x) for x in s[2:].split()])
        if s.startswith('t:'):
            T.append([int(x) for x in s[2:].split()])
    return [list(c) for c in zip(*D)], [list(c) for c in zip(*T)]  # live x n


def recover(live, col):
    """Exact vector a with <r_i, a> = col[p] for every live line; returns doubled coordinates or None."""
    idx = []
    for p, i in enumerate(live):
        if rank_q([LINES[live[q]] for q in idx] + [LINES[i]]) == len(idx) + 1:
            idx.append(p)
        if len(idx) == 8:
            break
    M = [[Q(x, 4) for x in LINES[live[p]]] for p in idx]
    a = solve_rational(M, [col[p] for p in idx])
    ok = all(sum(Q(x, 4) * y for x, y in zip(LINES[i], a)) == col[p] for p, i in enumerate(live))
    return a if ok else None


def as_line(a):
    """Index of the root line parallel to a, or None."""
    for i, r in enumerate(LINES):
        ratio = None
        good = True
        for x, y in zip(r, a):
            if x == 0:
                good &= y == 0
            else:
                q = Q(y) / x
                good &= ratio is None or q == ratio
                ratio = q
        if good and ratio:
            return i
    return None


def section_f():
    p112 = P112
    results = {}
    vend = json.loads((HERE / 'SOURCES.json').read_text())['vendored']
    check('F.vendored-pins', all(sha(HERE / rel) == meta['sha256'] for rel, meta in vend.items()) and len(vend) == 3,
          'three PR717 decoder files match their SHA-256 pins (PR717 head %s)' % next(iter(vend.values()))['head'][:7])
    clique717 = [9, 15, 24, 46, 52, 66, 94, 104]  # PR717 d3_punctures.py, P112 indexing
    cases = [('P104_HIT_flip_3a.txt', [p112[q] for q in clique717]), ('P111_HIT_g0.txt', [p112[0]]),
             ('P111_HIT_g111.txt', [p112[111]])]
    for name, extra in cases:
        punct = FRAME0 + extra
        live = [i for i in range(NL) if i not in punct]
        D, T = load_hit(HERE / 'inputs/pr717' / name)
        recorded = [int(l.split()[3]) for l in (HERE / 'inputs/pr717' / name).read_text().splitlines() if l.startswith('term ')]
        exact = all(sum(x * y for x, y in zip(D[p], T[q])) == 2 * IP[live[p]][live[q]]
                    for p in range(len(live)) for q in range(len(live)))
        terms = []
        for k in range(len(D[0])):
            a = recover(live, [row[k] for row in D])
            b = recover(live, [row[k] for row in T])
            R = [live[p] for p in range(len(live)) if D[p][k]]
            A = [live[p] for p in range(len(live)) if T[p][k]]
            la, lb = as_line(a), as_line(b)
            terms.append(dict(cost=pair_rank(R, A), row_root=la, col_root=lb,
                              odd=(la is not None and lb is not None and IP[la][lb] % 2 != 0),
                              both_punctured=(la in punct and lb in punct)))
        results[name] = dict(exact=exact, costs=[t['cost'] for t in terms], recorded_by_pr717=recorded, terms=terms)
        check('F.%s.costs-match-pr717' % name, recorded == [t['cost'] for t in terms],
              'per-term pairing ranks from (<r_i,r_j>+1) mod 2 equal the costs PR717 recorded with its own label model')
        seven = [t for t in terms if t['cost'] == 7]
        check('F.%s' % name, exact and all(t['row_root'] is not None and t['col_root'] is not None and t['odd'] and
                                           t['both_punctured'] for t in seven) and
              all(not (t['odd'] and t['both_punctured']) for t in terms if t['cost'] != 7),
              'exact; costs %s; every cost-7 term is an odd root pair with both lines punctured, and no other term is'
              % sorted(Counter(t['cost'] for t in terms).items()))
    # PR717's P104 clique is an admissible second frame
    F1 = sorted(p112[q] for q in clique717)
    sols = frame_pair_solutions(FRAME0, F1)
    check('F.P104-clique-is-frame-pair', all(IP[a][b] == 0 for a in F1 for b in F1 if a != b) and len(sols) == 8,
          "PR717's random clique is a frame of the admissible relative type with 8 frame-pair decoders")
    return results


# ---------------------------------------------------------------- G. pricing
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def section_g(repo):
    pins = json.loads((HERE / 'SOURCES.json').read_text())['pricing_inputs']
    for rel, h in pins.items():
        check('G.pin.' + rel.split('/')[-1], sha(repo / rel) == h, rel)
    eng = repo / 'research/complex-k492-owner-repair/vendor/multicold/engines'
    M = load_module(eng / 'moment.py', 'pinned_moment')
    B2 = load_module(eng / 'base_two_moment.py', 'pinned_base_two_moment')
    A = load_module(eng / 'outer.py', 'pinned_outer')
    P = load_module(repo / 'research/complex-t21-owners/vendor/pr870/independent/price_profile_t16.py', 'pinned_t16')
    bit = json.loads((repo / 'research/complex-t21-owners/vendor/pr870/inputs/PR589-EXPECTED.json').read_text())
    c = Q(bit['nine']['bit_lower'])
    src = json.loads((HERE / 'SOURCES.json').read_text())['selected_record']
    sel = json.loads((repo / 'certificates/selected-result.json').read_text())
    check('G.selected-record', sel['certificate'] == src['certificate'] and sel['certificate_sha256'] == src['certificate_sha256']
          and sha(repo / sel['certificate']) == src['certificate_sha256'] and sel['kappa'] == src['kappa'],
          'pricing uses the selected record %s (%s)' % (sel['certificate'], sel['decimal']))
    asm = json.loads((repo / sel['certificate']).read_text())
    H0 = Counter({int(r): n for r, n in asm['complex_profile'].items()})
    m, cell = 73, (9 - 1) * 112 - 9 * 64
    mass = sum(r * n for r, n in H0.items())
    T = next(t for t in range(1, 1000) if m * 896 * t - mass == cell * t)
    W0, D0, calls = 896 * T, cell * T, 9 * T
    check('G.identity', m * W0 - mass == D0 and max(H0) == 48,
          'selected profile: %d replicas, 73*%d - mass = %d = %d*((9-1)*112 - 9*64)' % (T, W0, D0, T))

    def scenario(ports, units):
        """PR717 P1 knobs transported to the selected U8 profile: a cst unit lowers one centre cut climb 8 -> 7 in every call;
        a port removes one modal source (1,1,1,5) and target (1,1,4,1,1) climb per call and nine idle
        rank-48 children per replica."""
        H = Counter(H0)
        H[8] -= units * calls
        H[7] += units * calls
        for _ in range(ports):
            for x in (1, 1, 1, 5, 1, 1, 4, 1, 1):
                H[x] -= calls
            H[48] -= 9 * T
        H = Counter({r: n for r, n in H.items() if n})
        W = W0 - T * 8 * ports
        D = T * ((9 - 1) * (112 - ports) - 9 * (64 - units))
        assert all(n > 0 for n in H.values()) and m * W - sum(r * n for r, n in H.items()) == D
        return H, W, D

    out = {}
    for name, (ports, units) in [('selected', (0, 0)), ('P111_knobs', (1, 1)), ('P104_knobs', (8, 8))]:
        H, W, D = scenario(ports, units)
        native = Q(M.certify(H, m, W, False)['lower'])
        conservative = Q(M.certify(H, m, W, True)['lower'])
        checks = P.moment_checks(M, B2, H, m, W, native, D, False)
        o = P.outer47(c, native, A)
        out[name] = dict(W=W, deficit=D, complex_b=str(native), complex_b_decimal=P.decimal(native),
                         conservative_b_decimal=P.decimal(conservative),
                         b_change_percent=P.decimal((native / Q(asm['complex_lower']) - 1) * 100),
                         kappa=o['kappa'], kappa_decimal=o['kappa_decimal'], binding=o['binding'],
                         outer_controls_rejected=o['controls_rejected'], two_engines=len(checks) == 2)
    cap = P.outer47(c, 2 * c, A)
    out['bit_cap'] = dict(kappa=cap['kappa'], kappa_decimal=cap['kappa_decimal'], binding=cap['binding'],
                          gain_over_selected_percent=P.decimal((Q(cap['kappa']) / Q(sel['kappa']) - 1) * 100))
    check('G.gate', out['selected']['complex_b'] == str(Q(asm['complex_lower'])) and
          Q(out['selected']['kappa']) == Q(sel['kappa']),
          'pinned engines on the selected profile reproduce b and kappa = %s exactly' % sel['decimal'])
    check('G.P111', out['P111_knobs']['binding'] == 'complex',
          'P111 knobs: b %+.4f%%, kappa %s (complex-bound)' % (float(Q(out['P111_knobs']['b_change_percent'])),
                                                              out['P111_knobs']['kappa_decimal']))
    check('G.P104', out['P104_knobs']['binding'] == 'bit' and out['P104_knobs']['kappa'] == out['bit_cap']['kappa'],
          'P104 knobs: b %+.4f%% > bit c, kappa capped at %s' % (float(Q(out['P104_knobs']['b_change_percent'])),
                                                                 out['P104_knobs']['kappa_decimal']))
    check('G.bit-cap', out['bit_cap']['binding'] == 'bit',
          'any complex-only change is capped by PR589 at kappa %s (%+.4f%%)' % (
              out['bit_cap']['kappa_decimal'], float(Q(out['bit_cap']['gain_over_selected_percent']))))
    headroom = Q(out['P104_knobs']['complex_b']) / c - 1
    out['P104_headroom_above_bit_percent'] = P.decimal(headroom * 100)
    return out


# ---------------------------------------------------------------- H. negative controls
def section_h(example, F1s, hist):
    F1 = example['F1']
    pairs = example['pairs']
    live104 = [i for i in range(NL) if i not in FRAME0 and i not in F1]
    rows, cols = build_pairs(pairs)
    # H1: perturb one column vector -> exactness lost
    bad = list(cols)
    bad[0] = tuple(x + y for x, y in zip(bad[0], LINES[FRAME0[0]]))
    exact, _ = decoder_cost(rows, bad, live104)
    check('H.mutated-decoder', not exact, 'adding a frame root to one column vector breaks D T^T = 2G')
    # H2: restore one partner line -> that term costs 8 (cst 57 = 72 - 15)
    restored = next(b if b in F1 else a for a, b in pairs)
    live = live104 + [restored]
    exact, costs = decoder_cost(rows, cols, live)
    check('H.self-line-live', exact and sum(costs) == 57 and sorted(costs) == [7] * 7 + [8],
          'restoring one self-line raises exactly one term to 8: cst 57 at p = 15')
    # H3: even pairing on the same puncture: the coordinate decoder on P104 stays at 64
    exact, costs = decoder_cost([LINES[f] for f in FRAME0], [LINES[f] for f in FRAME0], live104)
    check('H.even-pairs', exact and sum(costs) == 64, 'coordinate (even, alpha = beta) decoder on the same P104 costs 64')
    # H4: an inadmissible frame admits no frame-pair decoder (and the census is not vacuous)
    bad_frames = [F for F in F1s if not frame_pair_solutions(FRAME0, list(F))]
    check('H.inadmissible', len(bad_frames) == 364 and hist[0] == 364, '364 frames of the two other relative types have no solution')
    # H5: a swapped partner assignment is not dual
    swapped = list(pairs)
    (a0, b0), (a1, b1) = swapped[0], swapped[1]
    swapped[0], swapped[1] = (a0, b1), (a1, b0)
    try:
        r2, c2 = build_pairs(swapped)
        exact, _ = decoder_cost(r2, c2, live104)
    except AssertionError:
        exact = False
    check('H.swapped-partners', not exact, 'swapping two column partners breaks duality or the odd pairing')
    # H6: a 25-line puncture can push a support to a 7-dim span (the threshold is sharp)
    alpha = FRAME0[0]
    C = support_mask(LINES[alpha])
    best = min(((VMASK[x] | VMASK[y]) & C, x, y) for x in LAMBDAS for y in LAMBDAS if x < y
               and popcount((VMASK[x] | VMASK[y]) & C) == 25)
    killed = [i for i in range(NL) if best[0] >> i & 1]
    rest = [i for i in range(NL) if C >> i & 1 and i not in killed]
    check('H.pi7-sharp', len(killed) == 25 and span_dim(rest) == 7,
          'puncturing a 25-line codim-2 violator set leaves a root support with a 7-dim label span')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--repo', type=Path, default=HERE.parent.parent, help='repository root (for pricing inputs)')
    parser.add_argument('--out', type=Path, help='optional JSON certificate output (must not exist)')
    args = parser.parse_args()
    if not __debug__:
        sys.exit('assertions must be enabled')
    if args.out and args.out.exists():
        sys.exit('output exists: %s' % args.out)
    section_a()
    rows, weights = section_b()
    orbit_size = section_c(weights)
    F1s, example, hist, types = section_d()
    chain = section_e(F1s, example)
    hits = section_f()
    prices = section_g(args.repo.resolve())
    section_h(example, F1s, hist)
    status = 'PASS_COMPLEX_FRAME_PAIR_DECODERS' if not FAILS else 'FAIL'
    cert = dict(status=status, failures=FAILS,
                census={'%s(%d)' % (EXPECTED_TYPES[f][0], f): v for f, v in sorted(rows.items(), reverse=True)},
                d7_orbit=orbit_size, frame_pairs=dict(frames=len(F1s), admissible=hist[8], inadmissible=hist[0],
                                                       solutions_per_admissible_frame=8),
                chain={str(p): v for p, v in chain.items()}, pr717_hits=hits, pricing=prices, log=LOG,
                scope='Exact 8-term decoders (D = R A, T = R A^-T) in the PR717 B14 label-pairing model, punctures of at '
                      'most 24 of the 120 E8 lines. No word is built; pricing uses PR717 P1 knobs on the selected U8 '
                      'profile and is a favorable budget, not a kappa claim.')
    if args.out:
        args.out.write_text(json.dumps(cert, indent=1, default=str) + '\n')
    print('%s: types 8; D7 orbit %d; frames %d (admissible %d); chain p=0..24; P104 7/13; bit cap kappa %s; controls 6'
          % (status, orbit_size, len(F1s), hist[8], prices['bit_cap']['kappa_decimal']))
    sys.exit(1 if FAILS else 0)


if __name__ == '__main__':
    main()
