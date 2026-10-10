#!/usr/bin/env python3
"""Exact evaluation of the design ceiling of PROOF.md (Python stdlib only).

For every p >= 7, PROOF.md shows that every word on #144's paired-cube design pays at least

    C(p) = v [ 3(f(1) + f(2) + f(h-4))      source data registers (the K itinerary, fixed)
             + 3 f(h-1) + 2 f(2)            target data registers and endpoint children
             + 2 U2                         two non-idle units per source
             + tau ]                        registers at each target's hyperplane, or a stop of y_T
         + (v - n_g)(3 f(1) - f(3))         source roles enter from frame 0
         + 3h f(h-2)                        star copies

with h = 2p, m = 3h, f(r) = r ln(m/r), v = 8 C(p,3) and

    U2  = f(3) + 3 f(1) + 3 f(h-2)
    eps = f(1) + f(h-3) - f(h-2),   delta = f(1) + f(h-2) - f(h-1)
    mu  = 4(p-3),   tau = min(6 eps, 3 delta + 3 eps - U2/mu),   n_g = floor(v / |col|).

Then a < D / C(p) with D = 2v - 3h(h-2), and kappa < a / (1 + a).

Arithmetic is exact. Every logarithm is enclosed between two rationals: partial sums of 2 atanh from below, the same
plus a geometric tail from above, both rounded outward to the grid 2^-200. A lower bound is used wherever a term
enters C positively and an upper bound wherever it is subtracted, so every printed ceiling is a true upper bound.
The script also asserts the side conditions of the charging argument at every p, and bounds all p > P_MAX by the tail
of PROOF.md.

Usage:  python3 research/design-ceiling/ceiling.py [--check] [--brute]
  --check  compare the results with expected.json
  --brute  brute-force the counting lemmas at small p (sanity only; the proofs in PROOF.md cover every p >= 7)
"""
import argparse
import json
import sys
import time
from fractions import Fraction as Q
from itertools import combinations, product
from math import comb
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')

HERE = Path(__file__).resolve().parent
GRID = 1 << 200
P_MIN, P_MAX = 7, 99
T0 = time.time()


def log(*a):
    print('[%4.0fs]' % (time.time() - T0), *a, flush=True)


# ---------------------------------------------------------------------------------------------- enclosed logarithms
def down(x):
    return Q((x.numerator * GRID) // x.denominator, GRID)


def up(x):
    return Q(-((-x.numerator * GRID) // x.denominator), GRID)


def atanh(z, upper, terms=45):
    """Partial sum of atanh z = sum z^(2j+1)/(2j+1) for 0 <= z < 1: a lower bound; with the tail, an upper bound."""
    s = sum((z ** (2 * j + 1) / (2 * j + 1) for j in range(terms)), Q(0))
    return s + z ** (2 * terms + 1) / ((2 * terms + 1) * (1 - z * z)) if upper else s


_LN = {}


def ln(x, upper):
    """A rational bound on ln x for rational x >= 1: ln x = k ln 2 + ln y with 1 <= y < 2, ln y = 2 atanh((y-1)/(y+1))."""
    key = (x, upper)
    if key not in _LN:
        assert x >= 1
        y, k = x, 0
        while y >= 2:
            y /= 2
            k += 1
        value = 2 * k * atanh(Q(1, 3), upper) + 2 * atanh((y - 1) / (y + 1), upper)
        _LN[key] = up(value) if upper else down(value)
    return _LN[key]


# ---------------------------------------------------------------------------------------------- the floor at one p
def floor_at(p):
    h, m = 2 * p, 6 * p
    v = 8 * comb(p, 3)
    D = 2 * v - 3 * h * (h - 2)
    lo = lambda r: r * ln(Q(m, r), False)          # f(r) from below
    hi = lambda r: r * ln(Q(m, r), True)           # f(r) from above
    col = 12 * (p - 3) + 12 * comb(p - 3, 2) + 8 * comb(p - 3, 3)
    mu = 4 * (p - 3)
    eps_lo, eps_hi = lo(1) + lo(h - 3) - hi(h - 2), hi(1) + hi(h - 3) - lo(h - 2)
    delta_lo, delta_hi = lo(1) + lo(h - 2) - hi(h - 1), hi(1) + hi(h - 2) - lo(h - 1)
    U2_lo, U2_hi = lo(3) + 3 * lo(1) + 3 * lo(h - 2), hi(3) + 3 * hi(1) + 3 * hi(h - 2)
    idle = lo(3) + 3 * lo(h - 1)
    rho_hi = U2_hi / mu
    tau = min(6 * eps_lo, 3 * delta_lo + 3 * eps_lo - rho_hi)
    n_g = v // col
    # side conditions of PROOF.md, section 9 (each is also proved or explained there)
    side = dict(
        deficit_positive=D > 0,
        widths_in_range=3 * (h - 1) < m and h - 4 >= 1,
        gauge_at_a_line_is_cheaper=hi(3) <= 3 * lo(1),                   # g3 = min(3 f(1), f(3)) = f(3)
        eps_below_f1=0 < eps_lo and eps_hi <= lo(1),                     # a non-unit T-register can pay 3 eps
        rho_at_most_3eps=rho_hi <= 3 * eps_lo,                           # a target that pays rho twice
        small_unit_net=U2_lo - 3 * eps_hi >= rho_hi,                     # one big unit: U2 + mu rho >= 2 U2
        no_big_unit=col >= 2 * mu,                                       # no big unit: |col| rho >= 2 U2
        tau_positive=tau > 0,
    )
    assert all(side.values()), (p, {k: ok for k, ok in side.items() if not ok})
    stars = 3 * h * lo(h - 2)
    data_only = v * (6 * lo(h - 1) + 2 * lo(2)) + stars
    ladder = [data_only]                                                 # no auxiliary registers
    ladder.append(data_only + v * idle)                                  # + one unit per source (Lemma E)
    ladder.append(data_only + v * 2 * U2_lo)                             # + a second non-idle unit (Lemma D)
    ladder.append(ladder[-1] + v * tau)                                  # + T-registers or a stop of y_T (Lemma T)
    ladder.append(ladder[-1] + (v - n_g) * (3 * lo(1) - hi(3)))          # + source roles enter from 0 (Lemma E)
    ladder.append(ladder[-1] + v * (3 * (lo(1) + lo(2) + lo(h - 4)) - 3 * hi(h - 1)))    # + K itinerary (fixed)
    return dict(p=p, h=h, m=m, v=v, D=D, col=col, mu=mu, n_g=n_g, ladder=ladder, C=ladder[-1],
                per_port=dict(source_data=float(3 * (lo(1) + lo(2) + lo(h - 4))), target_data=float(3 * lo(h - 1) + 2 * lo(2)),
                              units=float(2 * U2_lo), tau=float(tau), source_entry=float((v - n_g) * (3 * lo(1) - hi(3)) / v),
                              stars=float(stars / v), eps=float(eps_lo), delta=float(delta_lo), U2=float(U2_lo),
                              rho=float(rho_hi)))


def ceil_grid(x, digits=7):
    return -((-x.numerator * 10 ** digits) // x.denominator)


# ---------------------------------------------------------------------------------------------- counting lemmas
def brute(p, every_w):
    """|col(S)|, Lemma S (rank h-1) and Lemma M (min over w of N(w) = 4(p-3)) for one source S, by enumeration.
    With every_w, all 2^h - 2 vectors w are tried; otherwise one w from each orbit of the symmetries that fix S and
    col(S): permutations of the free pairs and the swap of the two coordinates of a free pair."""
    P = [frozenset(2 * i + b for i, b in zip(I, bits)) for I in combinations(range(p), 3) for bits in product((0, 1), repeat=3)]
    q = [sum(1 << c for c in S) for S in P]
    cube = [frozenset(c // 2 for c in S) for S in P]
    h, S0 = 2 * p, 0
    col = [t for t in range(len(P)) if cube[t] != cube[S0] and len(P[t] & P[S0]) in (0, 2)]
    assert len(P) == 8 * comb(p, 3)
    assert len(col) == 12 * (p - 3) + 12 * comb(p - 3, 2) + 8 * comb(p - 3, 3)
    assert all((q[t] & q[S0]).bit_count() % 2 == 0 for t in col)
    pivots = {}
    for x in (q[t] for t in col):
        while x:
            top = x.bit_length() - 1
            if top not in pivots:
                pivots[top] = x
                break
            x ^= pivots[top]
    assert len(pivots) == h - 1, 'Lemma S'
    qc = [q[t] for t in col]
    if every_w:
        ws = range(1, 1 << h)
    else:
        own = [c // 2 for c in sorted(P[S0])]
        free = [i for i in range(p) if i not in own]
        ws = []
        for bits in range(64):
            base = sum(1 << (2 * own[k // 2] + k % 2) for k in range(6) if bits >> k & 1)
            for one in range(len(free) + 1):
                for both in range(len(free) + 1 - one):
                    w = base
                    for j, i in enumerate(free):
                        if j < one:
                            w |= 1 << (2 * i)
                        elif j < one + both:
                            w |= 3 << (2 * i)
                    ws.append(w)
    least = min(sum((w & x).bit_count() & 1 for x in qc) for w in ws if w not in (0, q[S0]))
    assert least == 4 * (p - 3), ('Lemma M', p, least)
    return len(col), least


# ---------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--brute', action='store_true')
    a = ap.parse_args()
    if a.brute:
        for p, every in ((7, True), (8, True)) + tuple((p, False) for p in range(7, 17)):
            n, least = brute(p, every)
            log('p = %2d: |col| = %4d, span of col = q_S-perp, min N(w) = %d = 4(p-3) over %s w' % (
                p, n, least, 'every' if every else 'one per orbit of'))
        log('PASS counting lemmas at small p')
        return
    rows = [floor_at(p) for p in range(P_MIN, P_MAX + 1)]
    names = ('data registers and star copies only', '+ one unit per source', '+ a second non-idle unit per source',
             '+ registers at each target hyperplane', '+ source roles enter from frame 0',
             '+ K itinerary of the source registers')
    ladder = []
    for k, name in enumerate(names):
        best = max(rows, key=lambda r: Q(r['D']) / r['ladder'][k])
        ladder.append(dict(floor=name, p=best['p'], ceiling='%d/10^7' % ceil_grid(Q(best['D']) / best['ladder'][k])))
        log('%-40s a < %s   (largest at p = %d)' % (name, ladder[-1]['ceiling'], best['p']))
    best = max(rows, key=lambda r: Q(r['D']) / r['C'])
    a_max = Q(best['D']) / best['C']
    # tail: for every p >= 7, C > 9 v (h-1) ln 3 and D < 2v (PROOF.md, section 10), so a < 2 / ((18p - 9) ln 3)
    tail = 2 / ((18 * (P_MAX + 1) - 9) * ln(Q(3), False))
    assert tail < a_max, 'the tail bound must lie below the maximum over the computed range'
    kappa = a_max / (1 + a_max)
    out = dict(p_range=[P_MIN, P_MAX], p=best['p'], h=best['h'], v=best['v'], D=best['D'],
               ceiling_a='%d/10^7' % ceil_grid(a_max), ceiling_kappa='%d/10^7' % ceil_grid(kappa),
               tail='%d/10^7' % ceil_grid(tail), ladder=ladder,
               table={str(r['p']): '%d/10^7' % ceil_grid(Q(r['D']) / r['C']) for r in rows
                      if r['p'] in (7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 20, 30, 40, 60, 99)})
    log('side conditions hold at every p in %d..%d; tail for p >= %d: a < %s' % (P_MIN, P_MAX, P_MAX + 1, out['tail']))
    log('per port at p = %d: %s' % (best['p'], ', '.join('%s %.2f' % kv for kv in best['per_port'].items())))
    log('CEILING: a < %s and kappa < a/(1+a) < %s, for every word on the design at every p' % (
        out['ceiling_a'], out['ceiling_kappa']))
    if a.check:
        expected = json.loads((HERE / 'expected.json').read_text())
        assert out == expected, 'results differ from expected.json'
        log('PASS results equal expected.json')
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
