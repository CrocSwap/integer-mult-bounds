"""CHECKED (exact): the descent construction of Section 5 (saturation passes from W(2k-1,2) to W(2k-3,2)) on E7 -> D6 -> D4 and E8 -> E7, and the inequalities
used in the quantitative version on E8."""
import os, sys
from fractions import Fraction as Fr
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from exact import rank_q
from units import UNITS, gram
from lines import abar_rows, alt_labels, window
from sympl import bf, lagrangians


def system(L):
    G = gram(L)
    rows = abar_rows(G)
    labels, k = alt_labels(rows)
    return G, rows, labels, k


def classes(L, labels, k):
    Ls = lagrangians(k)
    m = {}
    for l in labels:
        m[l] = m.get(l, 0) + 1
    return m, [sum(m.get(p, 0) for p in Lg) for Lg in Ls], Ls


def descend(name, L, p_index):
    G, rows, labels, k = system(L)
    T = rank_q([list(r) for r in L])
    m, sizes, _ = classes(L, labels, k)
    p = labels[p_index]
    mp = m[p]
    D = [L[t] for t in range(len(L)) if labels[t] != p and bf(labels[t], p, k) == 0]
    inp = [L[t] for t in range(len(L)) if labels[t] == p]
    orth = all(sum(a * b for a, b in zip(x, y)) == 0 for x in D for y in inp)
    T2 = rank_q([list(r) for r in D])
    G2, rows2, labels2, k2 = system(D)
    m2, sizes2, _ = classes(D, labels2, k2)
    # derived multiplicities: twin classes of the derived system must be the unions {q, q+p}
    pair = {}
    for t in range(len(L)):
        q = labels[t]
        if q != p and bf(q, p, k) == 0:
            key = min(q, q ^ p)
            pair[key] = pair.get(key, 0) + 1
    mult_ok = sorted(pair.values()) == sorted(m2.values()) and len(pair) == len(m2)
    sat = Fr(len(D), T2 * (2 ** k2 + 1))
    return dict(k=k, T=T, mp=mp, v2=len(D), T2=T2, k2=k2, orth=orth, mult_ok=mult_ok, sat2=sat, full=all(s == T2 for s in sizes2), sizes=sizes, lab=labels, D=D)


L7, _ = UNITS['E7']
L6, _ = UNITS['D6']
r1 = descend('E7', L7, 0)
check('S.E7-D6', r1['orth'] and r1['T2'] == r1['T'] - r1['mp'] == 6 and r1['v2'] == 30 and r1['k2'] == 2 and r1['mult_ok'] and r1['full'] and r1['sat2'] == 1,
      'E7 (k\'=3, T=7, saturated) at a label p with m_p=1: the %d lines with labels in p^perp \\ {p} are orthogonal to the class of p, span T-m_p=%d, form a system with k\'=%d, twin classes = {q,q+p} (multiplicity 2), every Lagrangian class is a full basis (saturated; this is the D6 system)' % (r1['v2'], r1['T2'], r1['k2']))
r2 = descend('D6', r1['D'], 0)
check('S.D6-D4', r2['orth'] and r2['T2'] == 4 and r2['v2'] == 12 and r2['k2'] == 1 and r2['mult_ok'] and r2['full'] and r2['sat2'] == 1 and r2['mp'] == 2,
      'D6 (k\'=2, T=6, m_p=2) descends to %d lines in T=%d, k\'=%d, multiplicity 4, saturated (the D4 system)' % (r2['v2'], r2['T2'], r2['k2']))
L8, _ = UNITS['E8']
r3 = descend('E8', L8, 0)
check('S.E8-E7', r3['orth'] and r3['T2'] == 7 and r3['v2'] == 63 and r3['k2'] == 3 and r3['full'] and r3['sat2'] == 1,
      'E8 (k\'=4, saturation 15/17) descends to %d lines in T=%d, k\'=%d, saturated (E7); the level-below saturation is 1, so the inequality of Section 5.3 is slack for E8' % (r3['v2'], r3['T2'], r3['k2']))
# quantitative ingredients on E8: A_p = average class size over generators through p; A_p <= sT + (1-s)m_p with s = 1; sum_p m_p A_p >= v sigma T
G, rows, labels, k = system(L8)
m, sizes, Ls = classes(L8, labels, k)
T = 8
v = len(L8)
sigma = Fr(v, T * (2 ** k + 1))
ok1 = True
tot = Fr(0)
for p, mp in m.items():
    cs = [sizes[i] for i, Lg in enumerate(Ls) if p in Lg]
    Ap = Fr(sum(cs), len(cs))
    ok1 &= Ap <= T
    tot += mp * Ap
check('S.quant-E8', ok1 and tot >= v * sigma * T and sigma == Fr(15, 17),
      'E8: A_p <= T for every occupied label, sum_p m_p A_p = %s >= v sigma T = %s (Cauchy-Schwarz step); sigma = 15/17' % (tot, v * sigma * T))
finish()
