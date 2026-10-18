#!/usr/bin/env python3
"""Bit-side orthogonal-pair decoders: exact verifier (standard library only).

Model (PR620 / PR757 / PR761 label decoders, priced by PR446 Theorem C): the 120 E8 root lines,
B0 = (1 + G) mod 2 with G the norm-2 Gram matrix, and a puncture P.  A label decoder is a list of
terms (p_j, q_j) of nonzero label functionals with sum_j p_j q_j^T = I_9; term j reads targets
R(p_j) \\ P and sources R(q_j) \\ P and costs rank_Q G[R(p_j)\\P, R(q_j)\\P].  For a root line a the
functional lambda_a has R(lambda_a) = {t : B0[t][a] = 1} = (lines orthogonal to a) + {a}.

Sections
  A  geometry: 120 lines, B0 of F2 rank 9, reader code 1 + 255 z^56 + 255 z^64 + z^120, W-invariance
  B  reduction thresholds: 8 hyperplane types x 511 functionals; all 120 root hyperplanes; the
     1080-direction D7 orbit; all 28 standard rank-6 subspaces (theta_6 = 26)
  C  pair-cost dichotomy on punctured root pairs: orthogonal 6, odd 7, equal 7
  D  the nine-pair witness: F2 duality, entrywise decoder identity on 102 live lines, cost 54
  E  explicit decoders for p = 0..25 with cost max(72 - p, 54)
  F  the ratio theorem's integer inequalities (9/17, equality only at p = 18)
  G  the selected bit supplier's own puncture (PR589 word): one dual root, P110 extension cost 62
  H  favorable pricing with the pinned engines: PR589 gate, copy knob, hosting wall, kappa
  I  negative controls

Run from anywhere:  python3 -I -B research/bit-orthogonal-pair-decoders/verify.py [--repo ROOT] [--out NEW.json]
"""
import argparse
import gzip
import hashlib
import importlib.util
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = []
SUMMARY = {}


def check(tag, cond, info=''):
    ok = bool(cond)
    RESULTS.append((tag, ok))
    print(('PASS ' if ok else 'FAIL ') + tag + (': ' + info if info else ''), flush=True)
    return ok


# ---------------------------------------------------------------- A. geometry and code
def e8_lines():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si, sj in itertools.product((2, -2), repeat=2):
            v = [0] * 8
            v[i], v[j] = si, sj
            roots.append(tuple(v))
    roots += [s for s in itertools.product((1, -1), repeat=8) if s.count(-1) % 2 == 0]
    return sorted(r for r in roots if next(x for x in r if x) > 0)


LINES = e8_lines()
N = len(LINES)
FULL = (1 << N) - 1


def ip(x, y):
    return sum(a * b for a, b in zip(x, y))


def canon(v):
    """Primitive integer representative with first nonzero coordinate positive."""
    g = 0
    for x in v:
        g = gcd(g, abs(int(x)))
    v = tuple(int(x) // g for x in v)
    return v if next(x for x in v if x) > 0 else tuple(-x for x in v)


INDEX = {canon(v): i for i, v in enumerate(LINES)}
G = [[ip(LINES[i], LINES[j]) // 4 for j in range(N)] for i in range(N)]
ROW = [sum(((1 + G[i][j]) % 2) << j for j in range(N)) for i in range(N)]   # B0 rows = lambda_i codewords


def bit(mask, j):
    return mask >> j & 1


def members(mask):
    return [j for j in range(N) if mask >> j & 1]


def mask_of(idx):
    m = 0
    for j in idx:
        m |= 1 << j
    return m


def f2_basis(vectors):
    basis = []
    for v in vectors:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return basis


def span_codewords(basis):
    words = [0]
    for b in basis:
        words += [w ^ b for w in words]
    return words


def rank_q(vectors):
    """Exact rational rank of integer vectors."""
    rows = [[Q(x) for x in v] for v in vectors]
    rank, ncol = 0, len(rows[0]) if rows else 0
    for c in range(ncol):
        piv = next((i for i in range(rank, len(rows)) if rows[i][c] != 0), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i][c] != 0:
                f = rows[i][c] / rows[rank][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def independent(vectors):
    """Maximal independent subsequence of integer vectors in Q^8 (exact incremental elimination)."""
    echelon, out = [], []
    for v in vectors:
        r = [Q(x) for x in v]
        for p, b in echelon:
            if r[p]:
                f = r[p]
                r = [x - f * y for x, y in zip(r, b)]
        piv = next((i for i, x in enumerate(r) if x), None)
        if piv is not None:
            echelon.append((piv, [x / r[piv] for x in r]))
            out.append(v)
            if len(out) == 8:
                break
    return out


def span_basis(idx):
    return independent([LINES[i] for i in idx])


def pair_cost(R, A):
    """rank_Q G[R, A] = rank of the Gram pairing between span(R) and span(A)."""
    br, ba = span_basis(R), span_basis(A)
    if not br or not ba:
        return 0
    return rank_q([[ip(x, y) for y in ba] for x in br])


def reflection_perm(r):
    perm = []
    for x in LINES:
        y = tuple(4 * a - ip(x, r) * b for a, b in zip(x, r))   # 4 * s_r(x), same line
        perm.append(INDEX[canon(y)])
    return perm


def permute(mask, perm):
    out = 0
    for j in members(mask):
        out |= 1 << perm[j]
    return out


def section_a():
    check('A.lines', N == 120 and all(ip(v, v) == 8 for v in LINES), '120 E8 lines, norm^2 8 in doubled coordinates')
    check('A.gram', all(G[i][i] == 2 for i in range(N)) and
          all(G[i][j] in (-1, 0, 1) for i in range(N) for j in range(N) if i != j), 'Gram entries 2 / 0 / +-1')
    basis = f2_basis(ROW)
    code = [w for w in span_codewords(basis) if w]
    weights = Counter(w.bit_count() for w in code)
    check('A.f2-rank', len(basis) == 9, 'B0 = (1 + G) mod 2 has F2 rank 9')
    check('A.code', weights == Counter({56: 255, 64: 255, 120: 1}), 'reader code 1 + 255 z^56 + 255 z^64 + z^120')
    roots = set(ROW)
    check('A.root-functionals', len(roots) == 120 and all(ROW[a] == mask_of([t for t in range(N) if t == a or G[t][a] == 0])
                                                         for a in range(N)),
          'R(lambda_a) = lines orthogonal to a, plus a; 120 distinct weight-64 codewords')
    codeset = set(code)
    perms = [reflection_perm(r) for r in LINES]
    check('A.W-invariant', all(permute(b, p) in codeset for p in perms for b in basis),
          'all 120 reflections map the code to itself (so W(E8) acts on functionals)')
    return code, perms


# ---------------------------------------------------------------- B. reduction thresholds
SIMPLE = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0), (-2, 2, 0, 0, 0, 0, 0, 0),
          (0, -2, 2, 0, 0, 0, 0, 0), (0, 0, -2, 2, 0, 0, 0, 0), (0, 0, 0, -2, 2, 0, 0, 0),
          (0, 0, 0, 0, -2, 2, 0, 0), (0, 0, 0, 0, 0, -2, 2, 0)]
TYPES = ['D7', 'A7', 'A6+A1', 'A4+A2+A1', 'A4+A3', 'D5+A2', 'E6+A1', 'E7']   # node i of Bourbaki's E8 removed


def nullspace(rows):
    m = [[Q(x) for x in r] for r in rows]
    pivots, rank = [], 0
    for c in range(8):
        p = next((i for i in range(rank, len(m)) if m[i][c] != 0), None)
        if p is None:
            continue
        m[rank], m[p] = m[p], m[rank]
        m[rank] = [x / m[rank][c] for x in m[rank]]
        for i in range(len(m)):
            if i != rank and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[rank])]
        pivots.append(c)
        rank += 1
    out = []
    for f in [c for c in range(8) if c not in pivots]:
        v = [Q(0)] * 8
        v[f] = Q(1)
        for i, c in enumerate(pivots):
            v[c] = -m[i][f]
        den = 1
        for x in v:
            den = den * x.denominator // gcd(den, x.denominator)
        out.append(canon([int(x * den) for x in v]))
    return out


def inside(normals):
    return mask_of([t for t in range(N) if all(ip(LINES[t], n) == 0 for n in normals)])


def section_b(code, perms):
    table = {}
    for i, name in enumerate(TYPES):
        (w,) = nullspace([SIMPLE[j] for j in range(8) if j != i])
        H = inside([w])
        taus = sorted((c & ~H).bit_count() for c in code)
        table[name] = dict(lines=H.bit_count(), min=taus[0], next=taus[1], minimizers=taus.count(taus[0]))
    expect = {'E7': (63, 1, 24), 'D7': (42, 14, 34), 'E6+A1': (37, 27, 28), 'A7': (28, 28, 35),
              'D5+A2': (23, 33, 41), 'A6+A1': (22, 35, 35), 'A4+A3': (16, 40, 43), 'A4+A2+A1': (14, 43, 43)}
    check('B.types', all((table[k]['lines'], table[k]['min'], table[k]['next']) == v for k, v in expect.items()),
          '; '.join('%s %d lines min %d next %d' % (k, table[k]['lines'], table[k]['min'], table[k]['next'])
                    for k in TYPES))
    others = [table[k]['min'] for k in TYPES if k not in ('E7', 'D7')]
    check('B.only-two-cheap', min(others) >= 27 and table['E7']['next'] >= 24 and table['D7']['next'] >= 34
          and table['E7']['minimizers'] == 1 and table['D7']['minimizers'] == 1,
          'below 24 punctures only root self-lines (1) and D7 normals (14) reduce a reader span')
    # every root hyperplane directly
    ok = True
    for a in range(N):
        H = inside([LINES[a]])
        taus = sorted(((c & ~H).bit_count(), c) for c in code)
        ok &= taus[0] == (1, ROW[a]) and taus[1][0] >= 24
    check('B.roots', ok, 'for all 120 roots a: lambda_a needs 1 puncture (a itself), every other functional >= 24')
    # D7 orbit
    (d7,) = nullspace([SIMPLE[j] for j in range(1, 8)])
    seen, frontier = {d7}, [d7]
    while frontier:
        nxt = []
        for v in frontier:
            for r in LINES:
                u = canon(tuple(4 * a - ip(v, r) * b for a, b in zip(v, r)))
                if u not in seen:
                    seen.add(u)
                    nxt.append(u)
        frontier = nxt
    sets, ok = [], True
    for w in seen:
        H = inside([w])
        taus = sorted(((c & ~H).bit_count(), c) for c in code)
        ok &= taus[0][0] == 14 and taus[1][0] >= 34 and taus[0][1].bit_count() == 56
        sets.append(taus[0][1] & ~H)
    union = min((x | y).bit_count() for x, y in itertools.combinations(sets, 2))
    check('B.D7', len(seen) == 1080 and ok and union >= 21,
          '%d D7 directions: unique weight-56 minimizer with 14 punctures, next >= 34; pairwise unions >= %d'
          % (len(seen), union))
    # codimension two: all 28 standard rank-6 subspaces
    theta6, witness = None, None
    for I in itertools.combinations(range(8), 6):
        U = inside(nullspace([SIMPLE[j] for j in I]))
        for c in code:
            t = (c & ~U).bit_count()
            if theta6 is None or t < theta6:
                theta6, witness = t, (I, c, U)
    check('B.theta6', theta6 == 26, 'bringing any reader set into a rank-6 root subspace needs >= %d punctures' % theta6)
    SUMMARY['thresholds'] = dict(table=table, d7_directions=len(seen), d7_min_union=union, theta6=theta6)
    return witness


# ---------------------------------------------------------------- C/D/E. decoders
def decoder_terms(pairs):
    return [(ROW[a], ROW[b]) for a, b in pairs]


def decoder_identity(terms, live):
    for t in members(live):
        acc = 0
        for c, d in terms:
            if bit(c, t):
                acc ^= d
        if (acc ^ ROW[t]) & live:
            return False
    return True


def costs(terms, live):
    return [pair_cost(members(c & live), members(d & live)) for c, d in terms]


def section_c():
    a = 0
    orth = [b for b in range(N) if b != a and G[a][b] == 0]
    odd = [b for b in range(N) if G[a][b] in (1, -1)]
    co = {pair_cost(members(ROW[a] & ~mask_of([a, b])), members(ROW[b] & ~mask_of([a, b]))) for b in orth}
    cd = {pair_cost(members(ROW[a] & ~mask_of([a, b])), members(ROW[b] & ~mask_of([a, b]))) for b in odd}
    ce = pair_cost(members(ROW[a] & ~mask_of([a])), members(ROW[a] & ~mask_of([a])))
    check('C.dichotomy', len(orth) == 63 and len(odd) == 56 and co == {6} and cd == {7} and ce == 7,
          'term (lambda_a, lambda_b), both punctured: cost 6 for all 63 orthogonal b, 7 for all 56 odd b, 7 for b = a')


def load_pairs(path):
    raw = json.loads(path.read_text(encoding='utf-8'))['pairs']
    return [(INDEX[canon(a)], INDEX[canon(b)]) for a, b in raw]


def section_d(pairs):
    A = [a for a, _ in pairs]
    B = [b for _, b in pairs]
    dual = all((1 + G[A[j]][B[k]]) % 2 == (1 if j == k else 0) for j in range(9) for k in range(9))
    check('D.duality', dual and len(set(A + B)) == 18,
          'B0[a_j][b_k] = delta_jk: a_j orthogonal to b_j, odd to every other b_k; 18 distinct lines')
    live = FULL & ~mask_of(A + B)
    terms = decoder_terms(pairs)
    check('D.decoder-identity', decoder_identity(terms, live),
          'sum_j B0[t][a_j] B0[b_j][s] = B0[t][s] for all %d x %d live pairs' % (live.bit_count(), live.bit_count()))
    spans = all(rank_q([LINES[t] for t in members(c & live)]) == 7 and rank_q([LINES[s] for s in members(d & live)]) == 7
                for c, d in terms)
    cs = costs(terms, live)
    check('D.cost', spans and cs == [6] * 9 and live.bit_count() == 102,
          'nine terms, reader and source spans 7, costs %s: cst %d on v = %d (x = 9/17)' % (cs, sum(cs), live.bit_count()))
    SUMMARY['witness'] = dict(v=live.bit_count(), cst=sum(cs), costs=cs)
    return live


def chain_puncture(pairs, p):
    A = [a for a, _ in pairs]
    B = [b for _, b in pairs]
    if p <= 9:
        return A[:p]
    if p <= 18:
        return A + B[:p - 9]
    extra = [t for t in range(N) if t not in A + B][:p - 18]
    return A + B + extra


def section_e(pairs):
    terms = decoder_terms(pairs)
    rows, ok = [], True
    for p in range(26):
        live = FULL & ~mask_of(chain_puncture(pairs, p))
        cs = costs(terms, live)
        good = decoder_identity(terms, live) and sum(cs) == max(72 - p, 54)
        ok &= good
        rows.append([p, live.bit_count(), sum(cs)])
    check('E.chain', ok, 'explicit decoders with cst = max(72 - p, 54) for p = 0..25 (one nine-pair system)')
    SUMMARY['chain'] = rows


# ---------------------------------------------------------------- F. ratio theorem arithmetic
def section_f():
    floor9 = {p: max(72 - p, 54) for p in range(26)}
    ok9 = all(floor9[p] * 17 >= 9 * (120 - p) for p in range(26))
    eq = [p for p in range(26) if floor9[p] * 17 == 9 * (120 - p)]
    many = all(60 * 17 > 9 * (120 - p) for p in range(7, 26)) and all((78 - 2 * p) * 17 > 9 * (120 - p) for p in range(7))
    d7 = all(75 - p > 72 - p and 75 - p >= 55 for p in range(14, 21))
    check('F.ratio', ok9 and eq == [18] and many and d7,
          'cst/v >= 9/17 for p <= 25 with n = 9 (equality only p = 18) and n >= 10 (strict); D7 case strict')
    check('F.compare', Q(54, 102) < Q(56, 104) < Q(64, 112) and Q(54, 102) < Q(63, 111) and Q(62, 110) < Q(63, 111),
          'bit 9/17 < complex 7/13 (PR968) < 4/7; bit 9/17 and 62/110 below the shipped 63/111')


# ---------------------------------------------------------------- G. the selected supplier's puncture
def section_g(repo, sources):
    rel = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
    data = (repo / rel).read_bytes()
    exp = json.loads((repo / 'research/complex-t21-owners/vendor/pr870/inputs/PR589-EXPECTED.json').read_text())['word']
    raw = gzip.decompress(data)
    check('G.word-pin', hashlib.sha256(data).hexdigest() == sources['pricing_inputs'][rel] == exp['file_sha256']
          and hashlib.sha256(raw).hexdigest() == exp['content_sha256'],
          'selected PR589 word: file and decompressed-content SHA-256 match PR589-EXPECTED')
    word = json.loads(raw)
    sgn = lambda v: tuple(v) if next(x for x in v if x) > 0 else tuple(-x for x in v)   # no rescaling here
    live = [tuple(v) for v in word['lines']]
    supports = sorted({tuple(i for i, x in enumerate(v) if x) for v in live if sum(1 for x in v if x) == 4})
    full = {tuple(2 if k == i else 0 for k in range(8)) for i in range(8)}
    for s in supports:
        for signs in itertools.product((1, -1), repeat=3):
            v = [0] * 8
            v[s[0]] = 1
            for k, j in enumerate(s[1:]):
                v[j] = signs[k]
            full.add(tuple(v))
    full = sorted(full)
    liveset = {sgn(v) for v in live}
    P = [v for v in full if v not in liveset]
    hip = lambda x, y: ip(x, y) // 2
    b0 = lambda x, y: (1 + hip(x, y)) % 2
    check('G.word', len(full) == 120 and len(supports) == 14 and liveset <= set(full) and len(P) == 9 == len(word['punctured'])
          and word['v'] == 111 and word['R'] == exp['R'] == 439,
          'word lines (Hamming coordinates, form <x,y>/2) close to 120 lines; 9 punctured; v = 111, R = 439')
    orth = sum(1 for x in P for y in P if x != y and hip(x, y) == 0)
    duals = [[b for b in full if all(b0(P[j], b) == (1 if j == k else 0) for j in range(9))] for k in range(9)]
    roots = [k for k in range(9) if duals[k]]
    check('G.dual-roots', orth == 44 and len(roots) == 1 and all(len(d) <= 1 for d in duals),
          '44 ordered orthogonal pairs among the punctured lines; exactly one of the nine F2 duals is a root line')
    # decoder on the word's own lines: readers lambda_{a_j}, sources the dual basis of B0[P,P]
    idx = {v: i for i, v in enumerate(full)}
    rowsH = [sum(b0(x, y) << j for j, y in enumerate(full)) for x in full]
    Pi = [idx[v] for v in P]
    M = [[b0(P[j], P[k]) for k in range(9)] for j in range(9)]
    inv = f2_inverse(M)
    readers = [rowsH[i] for i in Pi]
    sources = []
    for j in range(9):
        acc = 0
        for k in range(9):
            if inv[j][k]:
                acc ^= rowsH[Pi[k]]
        sources.append(acc)
    out = {}
    for name, extra in (('P111', []), ('P110', [idx[duals[roots[0]][0]]])):
        livemask = ((1 << 120) - 1) & ~sum(1 << i for i in Pi + extra)
        ident = all(not ((xor_rows([sources[j] for j in range(9) if readers[j] >> t & 1]) ^ rowsH[t]) & livemask)
                    for t in range(120) if livemask >> t & 1)
        cs = [pair_cost_vec(full, readers[j] & livemask, sources[j] & livemask) for j in range(9)]
        out[name] = (ident, cs, livemask.bit_count())
    check('G.P111', out['P111'][0] and sorted(out['P111'][1]) == [7] * 9,
          'shipped P111 label decoder: identity on 111 live lines, nine cost-7 terms, cst 63 (the PR757/PR761 value)')
    check('G.P110', out['P110'][0] and sorted(out['P110'][1]) == [6] + [7] * 8 and out['P110'][2] == 110,
          'puncturing the one dual root line gives P110: identity holds, costs 6 + 8 x 7 = 62 on v = 110')
    check('G.wall', 4 * 110 >= 439 > 4 * 109 and 4 * 102 < 439,
          'necessary nine-stage capacity R <= 4v: 439 <= 440 at v = 110; 439 > 408 at v = 102 (no owner map built)')
    # Scope control: another reader basis on this same puncture can have two cost-6 terms.
    alt_readers, alt_coeffs = [rowsH[Pi[0]], rowsH[Pi[3]]], [1, 1 << 3]
    for f in range(1, 512):
        c = xor_rows([rowsH[Pi[k]] for k in range(9) if f >> k & 1])
        if bit(c, Pi[1]) or bit(c, Pi[4]):
            continue
        if len(f2_basis(alt_readers + [c])) > len(alt_readers):
            alt_readers.append(c)
            alt_coeffs.append(f)
        if len(alt_readers) == 9:
            break
    inv_alt = f2_inverse([[bit(c, p) for p in Pi] for c in alt_readers])
    alt_sources = [xor_rows([rowsH[Pi[k]] for k in range(9) if inv_alt[k][j]]) for j in range(9)]
    alt_costs, alt_ok = {}, True
    for name, extra in (('P111', []), ('P110', [idx[duals[roots[0]][0]]])):
        livemask = FULL & ~mask_of(Pi + extra)
        alt_ok &= all(not ((xor_rows([s for r, s in zip(alt_readers, alt_sources) if bit(r, t)]) ^ rowsH[t]) & livemask)
                      for t in members(livemask))
        alt_costs[name] = [pair_cost_vec(full, r & livemask, s & livemask) for r, s in zip(alt_readers, alt_sources)]
    check('G.reader-basis-scope', alt_ok and alt_sources[:2] == [rowsH[Pi[1]], rowsH[Pi[4]]]
          and alt_costs['P111'] == [6, 6] + [8] * 7 and sum(alt_costs['P110']) == 67,
          'changing the readers permits two cost-6 terms on the same P111, but costs 68 overall (P110: 67), not an improvement')
    SUMMARY['shipped'] = dict(punctured=[list(v) for v in P], ordered_orthogonal_pairs=orth,
                              dual_root={'a': list(P[roots[0]]), 'b': list(duals[roots[0]][0])},
                              P111_costs=out['P111'][1], P110_costs=out['P110'][1],
                              changed_reader_control=dict(reader_coefficients=alt_coeffs,
                                  source_coefficients=[sum(inv_alt[k][j] << k for k in range(9)) for j in range(9)],
                                  costs=alt_costs))


def xor_rows(rows):
    acc = 0
    for r in rows:
        acc ^= r
    return acc


def pair_cost_vec(full, rmask, amask):
    def basis(mask):
        return independent([full[i] for i in range(120) if mask >> i & 1])
    br, ba = basis(rmask), basis(amask)
    return rank_q([[ip(x, y) for y in ba] for x in br]) if br and ba else 0


def f2_inverse(M):
    n = len(M)
    a = [row[:] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        p = next(i for i in range(c, n) if a[i][c])
        a[c], a[p] = a[p], a[c]
        for i in range(n):
            if i != c and a[i][c]:
                a[i] = [x ^ y for x, y in zip(a[i], a[c])]
    return [row[n:] for row in a]


# ---------------------------------------------------------------- H. pricing
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def section_h(repo, sources):
    pins_ok = True
    for rel, h in sources['pricing_inputs'].items():
        pins_ok &= check('H.pin.' + rel.split('/')[-1], sha(repo / rel) == h, rel)
    if not pins_ok:
        return  # Never import or execute an engine after its frozen source check fails.
    sel = json.loads((repo / 'certificates/selected-result.json').read_text())
    src = sources['selected_record']
    check('H.selected-record', sel['certificate'] == src['certificate'] and sel['certificate_sha256'] == src['certificate_sha256']
          and sel['kappa'] == src['kappa'], 'pricing reads the selected record %s (kappa %s)' % (sel['certificate'], sel['decimal']))
    eng = repo / 'research/complex-k492-owner-repair/vendor/multicold/engines'
    M = load_module(eng / 'moment.py', 'pinned_moment')
    B2 = load_module(eng / 'base_two_moment.py', 'pinned_base_two_moment')
    A = load_module(eng / 'outer.py', 'pinned_outer')
    P = load_module(repo / 'research/complex-t21-owners/vendor/pr870/independent/price_profile_t16.py', 'pinned_t16')
    bit = json.loads((repo / 'research/complex-t21-owners/vendor/pr870/inputs/PR589-EXPECTED.json').read_text())['nine']
    H0 = Counter({int(r): n for r, n in bit['profile'].items()})
    m, W, calls = 64, bit['bit']['live'], 288
    mass = sum(r * n for r, n in H0.items())
    c0 = Q(M.certify(H0, m, W, True)['lower'])
    check('H.bit-gate', c0 == Q(bit['bit_lower']) and mass == bit['bit']['rank_mass'] and m * W - mass == 10272 == 32 * (8 * 111 - 9 * 63),
          'pinned moment engine (inherited bad envelope) reproduces PR589 c = %s; 64*%d - mass = 10272 = 32*(8*111 - 9*63)'
          % (bit['bit_lower_decimal'], W))
    knobs = {}
    for units in (1, 9):
        H = Counter(H0)
        H[7] -= units * calls
        H[6] += units * calls
        D = m * W - sum(r * n for r, n in H.items())
        c = Q(M.certify(H, m, W, True)['lower'])
        rows = P.moment_checks(M, B2, H, m, W, c, D, True)
        knobs[units] = dict(c=str(c), c_decimal=P.decimal(c), change_percent=P.decimal((c / c0 - 1) * 100),
                            deficit=D, two_engines=len(rows) == 2)
    check('H.copy-knob', knobs[1]['deficit'] == 10272 + 288 and knobs[9]['deficit'] == 32 * (8 * 111 - 9 * 54)
          and knobs[1]['two_engines'] and knobs[9]['two_engines'],
          'copy children 7 -> 6 on all 288 calls (profile level, ports fixed): 1 unit %+.4f%% c, 9 units %+.4f%% c'
          % (float(Q(knobs[1]['change_percent'])), float(Q(knobs[9]['change_percent']))))
    # kappa: bit-only changes, the PR589 cap, and the complex P104 budget of PR968 without that cap
    asm = json.loads((repo / sel['certificate']).read_text())
    b0 = Q(asm['complex_lower'])
    k_bit_only = P.outer47(Q(knobs[9]['c']), b0, A)
    check('H.bit-only', k_bit_only['binding'] == 'complex' and Q(k_bit_only['kappa']) == Q(sel['kappa']),
          'any bit-only gain leaves kappa complex-bound at the selected %s' % sel['decimal'])
    CH = Counter({int(r): n for r, n in asm['complex_profile'].items()})
    mc, cell = 73, (9 - 1) * 112 - 9 * 64
    cmass = sum(r * n for r, n in CH.items())
    T = next(t for t in range(1, 1000) if mc * 896 * t - cmass == cell * t)
    H = Counter(CH)                       # PR968 / PR717 P1 knobs at 8 ports and 8 copy units (P104)
    H[8] -= 8 * 9 * T
    H[7] += 8 * 9 * T
    for _ in range(8):
        for x in (1, 1, 1, 5, 1, 1, 4, 1, 1):
            H[x] -= 9 * T
        H[48] -= 9 * T
    H = Counter({r: n for r, n in H.items() if n})
    Wc = 896 * T - T * 8 * 8
    Dc = T * ((9 - 1) * (112 - 8) - 9 * (64 - 8))
    gate = mc * Wc - sum(r * n for r, n in H.items()) == Dc and all(n > 0 for n in H.values())
    b104 = Q(M.certify(H, mc, Wc, False)['lower'])
    rows = P.moment_checks(M, B2, H, mc, Wc, b104, Dc, False)
    cap = P.outer47(c0, 2 * c0, A)
    capped = P.outer47(c0, b104, A)
    uncapped = P.outer47(2 * b104, b104, A)
    check('H.P104-cap', gate and len(rows) == 2 and T == 37 and capped['binding'] == 'bit' and capped['kappa'] == cap['kappa']
          and cap['kappa_decimal'] == '0.001730427469823602',
          'PR968 P104 complex knobs (b %+.4f%%) are capped by PR589 at kappa %s'
          % (float((b104 / b0 - 1) * 100), cap['kappa_decimal']))
    gain = Q(uncapped['kappa']) / Q(sel['kappa']) - 1
    need = b104 * (1 - Q(1, 10**24))
    check('H.P104-uncapped', uncapped['binding'] == 'complex' and Q(uncapped['kappa']) > Q(cap['kappa'])
          and P.outer47(need, b104, A)['kappa'] == uncapped['kappa'],
          'with bit c >= (1 - 10^-24) b_P104 (%+.4f%% over PR589 c) the same budget gives kappa %s (%+.4f%% over selected)'
          % (float((need / c0 - 1) * 100), uncapped['kappa_decimal'], float(gain * 100)))
    SUMMARY['pricing'] = dict(pr589_c=str(c0), copy_knob=knobs, bit_cap_kappa=cap['kappa_decimal'],
                              p104_complex_b=str(b104), p104_b_change_percent=P.decimal((b104 / b0 - 1) * 100),
                              p104_uncapped_kappa=uncapped['kappa_decimal'], p104_uncapped_gain_percent=P.decimal(gain * 100),
                              p104_required_bit_c_above_bit_percent=P.decimal((b104 / c0 - 1) * 100),
                              hosting_wall=dict(R=439, slots_v110=440, slots_v102=408))


# ---------------------------------------------------------------- I. negative controls
def section_i(pairs, live, theta_witness):
    terms = decoder_terms(pairs)
    swapped = list(pairs)
    swapped[0], swapped[1] = (pairs[0][0], pairs[1][1]), (pairs[1][0], pairs[0][1])
    A = [a for a, _ in swapped]
    B = [b for _, b in swapped]
    dual = all((1 + G[A[j]][B[k]]) % 2 == (1 if j == k else 0) for j in range(9) for k in range(9))
    c1 = not dual and not decoder_identity(decoder_terms(swapped), live)
    restored = live | (1 << pairs[0][1])
    c2 = sum(costs(terms, restored)) == 55 and decoder_identity(terms, restored)
    a0 = pairs[0][0]
    bad_b = next(b for b in range(N) if G[a0][b] in (1, -1) and b not in [x for p in pairs for x in p])
    alt = [(a0, bad_b)] + list(pairs[1:])
    c3 = (1 + G[a0][bad_b]) % 2 == 0 and not decoder_identity(decoder_terms(alt), FULL & ~mask_of([x for p in alt for x in p]))
    I, c, U = theta_witness
    c4 = rank_q([LINES[t] for t in members(c & U)]) <= 6 and (c & ~U).bit_count() == 26
    d7 = nullspace([SIMPLE[j] for j in range(1, 8)])[0]
    H = inside([d7])
    code = [w for w in span_codewords(f2_basis(ROW)) if w]
    cmin = min(code, key=lambda w: (w & ~H).bit_count())
    c5 = rank_q([LINES[t] for t in members(cmin & H)]) == 7 and cmin not in ROW
    flip = list(ROW)
    flip[3] ^= 1 << 7
    flip[7] ^= 1 << 3
    c6 = len(f2_basis(flip)) != 9 or Counter(w.bit_count() for w in span_codewords(f2_basis(flip)) if w) != \
        Counter({56: 255, 64: 255, 120: 1})
    check('I.controls', c1 and c2 and c3 and c4 and c5 and c6,
          'swapped partners break duality and identity; restoring b_1 gives 55; an odd partner breaks identity; '
          'a 26-line puncture reaches a rank-6 reader span (theta_6 sharp); a D7 14-set reduces a non-root functional; '
          'a corrupted B0 pair changes the code')
    return 6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(HERE.parents[1]))
    ap.add_argument('--out')
    args = ap.parse_args()
    if sys.flags.optimize:
        check('H.assertions', False, 'the pinned moment and outer engines reject inputs with assert; run without -O')
        sys.exit(1)
    repo = Path(args.repo).resolve()
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    code, perms = section_a()
    theta_witness = section_b(code, perms)
    section_c()
    pairs = load_pairs(HERE / 'WITNESS.json')
    live = section_d(pairs)
    section_e(pairs)
    section_f()
    section_g(repo, sources)
    section_h(repo, sources)
    controls = section_i(pairs, live, theta_witness)
    failed = [t for t, ok in RESULTS if not ok]
    SUMMARY['checks'] = dict(passed=len(RESULTS) - len(failed), failed=failed)
    if args.out:
        out = Path(args.out)
        if out.exists():
            print('refusing to overwrite ' + str(out))
            sys.exit(2)
        out.write_text(json.dumps(SUMMARY, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    if failed:
        print('FAILED %d of %d checks: %s' % (len(failed), len(RESULTS), ' '.join(failed)))
        sys.exit(1)
    pr = SUMMARY['pricing']
    print('PASS_BIT_ORTHOGONAL_PAIR_DECODERS: code 1+255z^56+255z^64+z^120; thresholds 1/14/theta6=26; witness P102 '
          'cst 54 (9/17); chain p=0..25; shipped P111 -> P110 cst 62 (1 dual root, wall 440>=439); copy knob 9 units %s%% c; '
          'P104 uncapped kappa %s; controls %d; no new kappa'
          % (pr['copy_knob'][9]['change_percent'][:8], pr['p104_uncapped_kappa'], controls))


if __name__ == '__main__':
    main()
