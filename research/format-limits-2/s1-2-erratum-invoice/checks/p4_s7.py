"""P4: stage count s = 9 -> 7 (P = 4 -> 3 bank pairs) on the #626 invoice.  Geometry by P: m = 1 + 8(2P+1), W = 2 P T v,
deficit D = T[2Pv - (2P+1) cst], calls = T(2P+1), idle cover I = calls * 8 (s-3) v, v = 112, cst = 64, T = 8.  The per-call
local profile (ck 3858 / jp8 3902 + 1856) is the P = 4 one: the P = 3 local program was NOT built, so s = 7 is a model.
A cut of k w9 helpers per call (all calls) returns the average w9 climb profile of the provider; the freed width is
hosted idle mass.  Scope: the #626 local words only."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from invoice import *

w = Word626()
V, CST, T = 112, 64, 8
def geom(P):
    return dict(m=1 + 8 * (2 * P + 1), W=2 * P * T * V, D=T * (2 * P * V - (2 * P + 1) * CST), calls=T * (2 * P + 1))
Pk = {p: Counter(x for r in w.d[p]['regs'] for x in r) for p in CALLS}
sumw = {p: sum(a * n for a, n in Pk[p].items()) - 1856 for p in CALLS}
w9 = {}
for p in CALLS:
    regs = w.helpers(p, 9); c = Counter(x for r in regs for x in r)
    w9[p] = {a: D(n) / len(regs) for a, n in c.items()}
g9 = geom(4)
check('P4.gate-geometry', (g9['m'], g9['W'], g9['D'], g9['calls']) == (73, 7168, 2560, 72), 'P=4 reproduces m=73, W=7168, D=2560, 72 calls')
def build(s, k):
    P = (s - 1) // 2; g = geom(P); ck = g['calls'] // 9; cnt = {'ck': ck, 'jp8': g['calls'] - ck}
    H = Counter(); hz = D(0)
    for p, c in cnt.items():
        for a, n in Pk[p].items(): H[a] += n * c
        for a, n in w9[p].items(): H[a] -= n * D(str(k)) * c
        hz += c * (sumw[p] - 9 * D(str(k)))
    I = g['calls'] * (s - 3) * 8 * V; left = I - hz; cw = (s - 3) * 8
    H[cw] += left / cw
    return g, H, left, hz, I, sum(a * n for a, n in H.items()) - (g['m'] * g['W'] - g['D'])
for s in (9, 7):
    g, H, left, hz, I, res = build(s, 0)
    check('P4.mass-identity-s%d' % s, abs(res) < D('1e-9'), 's=%d: mass = mW - D (residual %s), idle I=%d, hosted Hz=%d, leftover %s' % (s, res, I, hz, left))
g7, H7, l7, hz7, I7, _ = build(7, 0)
check('P4.overflow-s7', I7 == 200704 and hz7 == 218248 and l7 == -17544,
      's=7 (56 calls, 8 ck + 48 jp8): I=%d, Hz=%d, hosting overflow %d = %.1f%% of the idle cover I' % (I7, hz7, -l7, float(-l7 / I7) * 100))
for p in CALLS:
    print('INFO k needed (%s alone) = %.1f' % (p, float((sumw[p] - 3584) / 9)))
kneed = (sumw['jp8'] * 48 + sumw['ck'] * 8 - 3584 * 56) / D(9) / 56
check('P4.k-fit', 34 < kneed < 36, 'fit at s=7 needs k = %.1f w9 helpers cut per call (R 492 -> %.0f)' % (kneed, 492 - kneed))
ref = root(build(9, 0)[1], 73, 7168)
rows = []
for k in (35, 40, 60):
    g9_, H9, l9, *_ = build(9, k); g7_, H7_, l7_, *_ = build(7, k)
    b9 = root(H9, g9_['m'], g9_['W']); b7 = root(H7_, g7_['m'], g7_['W'])
    rows.append((k, float((b9 / ref - 1) * 100), float(b7 * 1000), float((b7 / b9 - 1) * 100), float(l7_)))
    check('P4.worse-k%d' % k, l7_ >= 0 and b7 > b9 and 0.1 < rows[-1][3] < 0.3,
          'k=%d: b9 %+.2f%% vs k=0 (same cut at s=9); b7 = %.4e; b7/b9 at the same R = %+.2f%% (the cut buys s=7 admission only)' % (k, rows[-1][1], b7, rows[-1][3]))
deep = []
for k in (234, 300, 480):
    row = []
    for s in (9, 7, 5):
        g, H, l, *_ = build(s, k)
        row.append(float(root(H, g['m'], g['W']) * 1000) if l >= 0 else None)
    deep.append(row)
    check('P4.deep-k%d' % k, row[0] > row[1] > row[2] if None not in row else False, 'b x1e3 at s=9/7/5: %s (s=9 largest at every k)' % ['%.3f' % x for x in row])
finish()
