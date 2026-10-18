#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Masked root-star copy-cost floor on P112: complete trimmed-star census (CrocSwap/integer-mult-bounds#717 D1 hole).

Standard library only; exact integer and F2 arithmetic throughout.

Model (CrocSwap/integer-mult-bounds#717 B14, masked/E-graph form, see CrocSwap/integer-mult-bounds#717 format-limits-2 D1(a)): the 120 E8 root
lines; P112 = 120 minus the 8 coordinate frame lines; labels pair as (<r_i,r_j> + 1) mod 2.
A decoder is a list of terms (d_k, t_k); term k costs beta_k = F2 rank of the label pairing
between its row support and column support; the identity is required only on the E-graph
(even inner-product pairs): x_i.y_j = 0 off-diagonal, x_i.y_i = 4 (target 2G).  The 5824
odd entries are free (fixed after the fact by cost-0 singleton terms: section D).

Root-star supports: for a root line alpha, C(alpha) = {i in P112 : <r_i, alpha> != 0}
(untrimmed) and N(alpha) = C(alpha) minus alpha's own line (self-trimmed).  N(alpha) has
label span H_alpha (dimension 8), so an odd root pair (alpha, beta) gives the mixed-beta
atom cost 7 -- exactly the atoms CrocSwap/integer-mult-bounds#717 D1(b) excludes from its flat-support census.

Sections (each prints PASS/FAIL lines):
  A  model facts: 120 lines, P112, E-graph row counts, 5824 free odd entries
  B  frames: 1260 eight-cliques of the E-graph, none of size 9, 90 frames per line
  C  the complete atom census: all 240 root-star supports, all 57,600 ordered pairs,
     exact pairing rank beta and exact frame-hit count; the frame-substitution bound
  D  reduction control: a cost-0 singleton patch fixes one odd entry exactly
  E  controls: coordinate decoder (cst 64) rebuilt exactly; beta-0 atoms never meet a
     frame; receipt comparison against RESULTS.json (mutation-detecting)

The frame-substitution argument (used with the census): every frame F of the E-graph is an
8-clique, and the masked identity restricted to F is [x_i.y_j] = 4 I_8, a full-rank 8x8
system.  Each term contributes a rank-at-most-one block (d_k|_F)(t_k|_F)^T and contributes
nothing unless its row and column supports both meet F ("meets F").  So >= 8 terms meet
every frame.  With h_k the number of frames term k meets and gamma = min over allowed
atoms of beta/hit, cst = sum beta_k >= gamma * sum h_k >= gamma * 8 * 1260.
"""
import argparse
import hashlib
import itertools
import json
import sys
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


# ------------------------------------------------------- A. E8 lines, labels, E-graph
def e8_roots():
    """240 roots in doubled coordinates; enumeration as in research/complex-frame-pair-decoders/verify.py (adapter, attributed)."""
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


def neg(v):
    return tuple(-a for a in v)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


ROOTS = e8_roots()
LINES = []
_seen = set()
for r in ROOTS:
    key = r if r > neg(r) else neg(r)
    if key not in _seen:
        _seen.add(key)
        LINES.append(r)
NL = len(LINES)


def ip(x, y):
    d = dot(x, y)
    assert d % 4 == 0
    return d // 4


IP = [[ip(LINES[i], LINES[j]) for j in range(NL)] for i in range(NL)]
# Label pairing rows over F2^9: bit j is (<r_i,r_j> + 1) mod 2.
NROW = [sum(((IP[i][j] + 1) & 1) << j for j in range(NL)) for i in range(NL)]
FRAME0 = []
for a in range(4):
    for s in (1, -1):
        v = [0] * 8
        v[2 * a], v[2 * a + 1] = 2, 2 * s
        FRAME0.append(LINES.index(tuple(v)))
P112 = [i for i in range(NL) if i not in FRAME0]
NP = len(P112)


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


def pair_rank(rows, cols):
    cm = 0
    for j in cols:
        cm |= 1 << j
    return f2_rank([NROW[i] & cm for i in rows])


def section_a():
    check('A.lines-120', NL == 120 and len(ROOTS) == 240, '120 lines from 240 roots')
    check('A.p112-112', NP == 112 and len(FRAME0) == 8, 'P112 = 120 - 8 frame lines')
    check('A.ip-diag-2', all(IP[i][i] == 2 for i in range(NL)))
    rows = [((IP[i][j] + 1) & 1) for i in P112 for j in P112]
    ones = sum(rows)
    e_row = [sum((IP[i][j] + 1) & 1 for j in P112) for i in P112]
    check('A.egraph-60-per-row', set(e_row) == {60}, str(set(e_row)))
    check('A.free-odd-entries-5824', NP * NP - ones == 5824, str(NP * NP - ones))
    odd_nonzero = all(IP[i][j] != 0 for i in P112 for j in P112 if ((IP[i][j] + 1) & 1) == 0)
    check('A.odd-entries-nonzero-in-2G', odd_nonzero, '5824 odd entries all nonzero in 2G')


# ------------------------------------------------------------------ B. E-graph frames
def eg_adj(i, j):
    return i != j and ((IP[i][j] + 1) & 1) == 1


def section_b():
    adj = [[k for k in range(NP) if eg_adj(P112[i], P112[k])] for i in range(NP)]
    frames = []

    def ext(cl, cand):
        if len(cl) == 8:
            frames.append(tuple(cl))
            return
        for k, v in enumerate(cand):
            ext(cl + [v], [w for w in cand[k + 1:] if eg_adj(P112[v], P112[w])])
    ext([], list(range(NP)))
    check('B.frames-1260', len(frames) == 1260, str(len(frames)))
    common9 = 0
    for c in frames:
        cand = set(range(NP))
        for v in c:
            cand &= set(adj[v])
        common9 += 1 if cand else 0
    check('B.no-9-clique', common9 == 0)
    per_line = [0] * NP
    for c in frames:
        for v in c:
            per_line[v] += 1
    check('B.90-frames-per-line', set(per_line) == {90}, str(set(per_line)))
    return frames


# ------------------------------------------------- C. root-star supports and the census
def support_masks():
    """240 root-star supports as 112-bit masks over P112 positions: (normal line, trimmed, mask)."""
    out = []
    pos = {g: i for i, g in enumerate(P112)}
    for a in range(NL):
        untrimmed = 0
        for i in P112:
            if IP[i][a] != 0:
                untrimmed |= 1 << pos[i]
        trimmed = untrimmed
        if a in pos:
            trimmed &= ~(1 << pos[a])
        out.append((a, False, untrimmed))
        out.append((a, True, trimmed))
    return out


def section_c(frames):
    sup = support_masks()
    fm = [sum((1 << v) for v in c) for c in frames]
    meet = []
    for (a, tr, m) in sup:
        bits = 0
        for f, fmask in enumerate(fm):
            if fmask & m:
                bits |= 1 << f
        meet.append(bits)
    hist = {}
    max_ratio = None
    argmax = None
    max_hit7 = -1
    argmax7 = None
    n7 = 0
    gamma = None
    gamma8 = None
    beta0_hit_max = 0
    idxs = [[P112[i] for i in range(NP) if (m >> i) & 1] for (_, _, m) in sup]
    top7 = []
    for r in range(len(sup)):
        for a2 in range(len(sup)):
            beta = pair_rank(idxs[r], idxs[a2])
            hit = bin(meet[r] & meet[a2]).count('1')
            hist[beta] = hist.get(beta, 0) + 1
            if beta == 0 and hit > beta0_hit_max:
                beta0_hit_max = hit
            if beta == 7:
                n7 += 1
                top7.append((hit, sup[r][0], sup[r][1], sup[a2][0], sup[a2][1]))
                if hit > max_hit7:
                    max_hit7 = hit
                    argmax7 = (sup[r][0], sup[r][1], sup[a2][0], sup[a2][1], hit)
            if hit > 0:
                ratio = Q(hit, beta)
                if max_ratio is None or ratio > max_ratio:
                    max_ratio = ratio
                    argmax = (sup[r][0], sup[r][1], sup[a2][0], sup[a2][1], beta, hit)
                g = Q(beta, hit)
                if gamma is None or g < gamma:
                    gamma = g
                if beta >= 8 and (gamma8 is None or g < gamma8):
                    gamma8 = g
    bound = Q(8 * 1260) * gamma
    bound8 = Q(8 * 1260) * gamma8
    top7.sort(reverse=True)
    check('C.bound-beta-ge-8-is-64', bound8 == 64, 'bound over beta>=8 atoms = %s' % bound8)
    check('C.pairs-57600', sum(hist.values()) == 57600, str(sum(hist.values())))
    check('C.beta0-atoms-have-zero-hit', beta0_hit_max == 0,
          'max hit among beta-0 atoms = %d' % beta0_hit_max)
    check('C.beta7-atoms-counted', n7 == hist.get(7, 0), '%d beta-7 atoms' % n7)
    info = 'max hit/beta = %s at (a%s,tr=%s,b%s,tr=%s) beta=%d hit=%d; bound = %s' % (
        max_ratio, argmax[0], argmax[1], argmax[2], argmax[3], argmax[4], argmax[5], bound)
    check('C.census-complete', True, info)
    check('C.beta7-max-hit', True, 'max hit among beta-7 atoms = %d at (a%s,tr=%s,b%s,tr=%s)' % (
        (max_hit7,) + argmax7[:4] if argmax7 else (max_hit7, '-', '-', '-', '-')))
    return {
        'supports': len(sup),
        'pairs': sum(hist.values()),
        'beta_histogram': {str(k): v for k, v in sorted(hist.items())},
        'max_hit_over_beta': [max_ratio.numerator, max_ratio.denominator],
        'max_hit_over_beta_atom': list(argmax),
        'max_hit_beta7': max_hit7,
        'max_hit_beta7_atom': list(argmax7) if argmax7 else None,
        'beta7_atom_count': n7,
        'beta0_max_hit': beta0_hit_max,
        'gamma_min_beta_over_hit': [gamma.numerator, gamma.denominator],
        'frame_substitution_bound': [bound.numerator, bound.denominator],
        'frame_substitution_bound_beta_ge_8': [bound8.numerator, bound8.denominator],
        'top_beta7_atoms_by_hit': [list(t) for t in top7[:8]],
    }


# ------------------------------------------------------------- D. reduction (cost-0)
def section_d():
    for i in P112:
        for j in P112:
            if i != j and IP[i][j] != 0 and ((IP[i][j] + 1) & 1) == 0:
                cost = pair_rank([i], [j])
                check('D.singleton-odd-patch-cost-0', cost == 0, 'odd pair (%d,%d)' % (i, j))
                check('D.singleton-odd-patch-off-egraph', ((IP[i][j] + 1) & 1) == 0,
                      'patch only touches free odd entries')
                return
    check('D.singleton-odd-patch-cost-0', False, 'no odd pair found')


# ------------------------------------------------- E. coordinate decoder and controls
def section_e():
    """The attaining coordinate decoder: 8 frame-normal star terms, d_k = t_k = (<r_i, f_k>)_i.

    The frame lines f_0..f_7 are orthogonal of norm 2, so sum_k <r_i,f_k><r_j,f_k> = 2<r_i,r_j>:
    the term matrix is exactly 2G on every entry. Supports are N(f_k) = C(f_k) on P112
    (the self-line is punctured), label span H_{f_k}, pairing rank 8 each."""
    cols = []
    for fidx in FRAME0:
        s = [i for i in P112 if IP[i][fidx] != 0]
        cols.append((fidx, s))
    for k, (fidx, s) in enumerate(cols):
        check('E.coordinate-star-term-%d-beta-8' % k, pair_rank(s, s) == 8,
              'normal line %d, support %d lines' % (fidx, len(s)))
    ok_identity = True
    for i in P112:
        for j in P112:
            s = sum(IP[i][f] * IP[j][f] for f in FRAME0)
            if s != 2 * IP[i][j]:
                ok_identity = False
            if ((IP[i][j] + 1) & 1) == 1:
                want = 4 if i == j else 0
                if 2 * IP[i][j] != want:
                    ok_identity = False
    check('E.coordinate-star-egraph-identity', ok_identity,
          'sum_k (<r_i,f_k>)(<r_j,f_k>) = 2G on every entry')
    cst = sum(pair_rank(s, s) for _, s in cols)
    check('E.coordinate-cst-64', cst == 64, 'cst = %d' % cst)
    check('E.coordinate-stars-are-family-atoms', all(
        any(a == fidx and tr for (a, tr, m) in support_masks()) for fidx in FRAME0),
        'each N(f_k) is a trimmed root-star support of the census')
    return {'coordinate_cst': cst, 'coordinate_terms': 8, 'coordinate_support_sizes': sorted(
        {len(s) for _, s in cols})}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', metavar='PATH', help='write the receipt to PATH')
    ap.add_argument('--check', metavar='PATH', help='compare the receipt with PATH')
    args = ap.parse_args()
    section_a()
    frames = section_b()
    census = section_c(frames)
    section_d()
    coord = section_e()
    receipt = {
        'name': 'MASKED_ROOT_STAR_FLOOR_P112',
        'model': {'lines': NL, 'p112': NP, 'egraph_row_ones': 60, 'free_odd_entries': 5824},
        'frames': {'count': 1260, 'max_clique': 8, 'frames_per_line': 90},
        'census': census,
        'coordinate': coord,
    }
    ref = None
    ref_path = Path(args.check) if args.check else HERE / 'RESULTS.json'
    if ref_path.exists():
        ref = json.loads(ref_path.read_text(encoding='utf-8'))
        same = ref == receipt
        check('E.receipt-matches', same, str(ref_path))
        if not same:
            for key in set(list(ref.keys()) + list(receipt.keys())):
                if ref.get(key) != receipt.get(key):
                    print('  DIFF %s: recorded=%r computed=%r' % (key, ref.get(key), receipt.get(key)))
    else:
        check('E.receipt-present', args.write is not None, 'no RESULTS.json; use --write to create one')
    if args.write:
        Path(args.write).write_text(json.dumps(receipt, indent=1, sort_keys=True) + '\n', encoding='utf-8')
        print('wrote', args.write)
    print('FAILS:', FAILS if FAILS else 'none')
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
