"""A. Format ceiling, rev. 2: certified skeleton roots X(s, w, x) and the kappa ceiling.

X(s, w, x) is the root q of F_s(q) = D_s for the R-free B_K skeleton (skel.profile, theorem variant: active climbs at
cap a = h - k, copies at cap h, idle slots of rank r at cap max(r, h)); D_s/v = (s-1)k - s x, m = k + s(h-k).
Roots are bracketed with rational-interval arithmetic (cert.root_bracket); the upper end 'hi' is the certified value.

Units (k = 1):
  bit, punctured star unit of #545/#555: v = 111 live lines, decoder constant 63 (x = 63/111), window h = 8;
  complex, punctured unit of #523 and its descendants (#531 ... #569): v = 112, copy cost 64 (x = 64/112), h = 9;
  superseded rev. 1 scope: the full E8 unit v = 120, copy cost 72 (x = 3/5) on both sides.
kappa <= X/(1+X) with X = min(X_bit*, X_cx*) (README section A.4 for the outer form).
"""
from fractions import Fraction as Fr

from report import check, finish, near
from skel import X

S_LIST = (3, 5, 7, 9, 11, 13)
UNITS = {  # name: (h, cst, v)
    'bit-111/63': (8, 63, 111),
    'cx-112/64': (9, 64, 112),
    'bit-120/72': (8, 72, 120),
    'cx-120/72': (9, 72, 120),
}
# certified upper ends (hi) recorded by the original runs; compared to relative 1e-12
EXPECTED = {
    'bit-111/63': {3: 5.947449820544458e-3, 5: 6.00049473312529e-3, 7: 5.2094781808670505e-3,
                   9: 4.607152286783883e-3, 11: 4.1489567374021555e-3, 13: 3.7878851034153518e-3},
    'cx-112/64': {3: 5.047389571662491e-3, 5: 5.186252252886545e-3, 7: 4.512993851037537e-3,
                  9: 3.994628507503969e-3, 11: 3.5988803552243387e-3, 13: 3.2864689075796437e-3},
    'bit-120/72': {3: 3.997571235241277e-3, 5: 5.159798631791548e-3, 7: 4.623205298039335e-3,
                   9: 4.139748562309081e-3, 11: 3.752885369025204e-3, 13: 3.440493799826091e-3},
    'cx-120/72': {3: 3.5307429201300307e-3, 5: 4.535607180902823e-3, 7: 4.059761375276634e-3,
                  9: 3.6334780884322328e-3, 11: 3.2929429181725836e-3, 13: 3.0181922014469375e-3},
}
KAPPA_CEILING = 5.1595e-3          # rev. 2, complex binds
KAPPA_BIT_ONLY = 5.9647e-3          # bit-only corollary c/(1+c)
KAPPA_REV1 = 4.5151e-3              # superseded rev. 1 value (x = 3/5)
FRONTIER = {'bit': 1.733052823330162e-3, 'cx': 0.00159868506668458107128}   # #555 c (s = 9), #568 b (s = 9)
HEADROOM_S9 = {'bit': 2.658, 'cx': 2.499}
COPY_UNIT = {5: 3.9, 9: 2.8, 11: 2.65}   # % gain of bit X per copy-rank unit per stage (63 -> 62)

tab = {}
for name, (h, cst, v) in UNITS.items():
    row = {}
    for s in S_LIST:
        r = X(s, h, 1, Fr(cst, v))
        row[s] = r
    tab[name] = row
    ok = all(abs(float(row[s]['hi']) / EXPECTED[name][s] - 1) < 1e-12 and row[s]['hi'] - row[s]['lo'] < Fr(1, 10**15)
             for s in S_LIST)
    check('A1.roots.' + name, ok, ' '.join('s%d:%.5e' % (s, float(row[s]['hi'])) for s in S_LIST))
    best = max(S_LIST, key=lambda s: row[s]['hi'])
    check('A1.best-s.' + name, best == 5, 'max over s in %s at s = %d' % (list(S_LIST), best))

xb, xc = tab['bit-111/63'][5]['hi'], tab['cx-112/64'][5]['hi']
Xmin = min(xb, xc)
kap = Xmin / (1 + Xmin)
check('A1.kappa-ceiling', xc < xb and near(kap, KAPPA_CEILING, 7),
      'X_bit* %.5e, X_cx* %.5e (complex binds); kappa <= X/(1+X) = %.7e' % (xb, xc, float(kap)))
check('A1.kappa-bit-only', near(xb / (1 + xb), KAPPA_BIT_ONLY, 7), 'c/(1+c) <= %.7e' % float(xb / (1 + xb)))
x1 = min(tab['bit-120/72'][5]['hi'], tab['cx-120/72'][5]['hi'])
check('A1.rev1-superseded', near(x1 / (1 + x1), KAPPA_REV1, 7),
      'the x = 3/5 scope gives %.7e; the punctured units have x = 63/111, 64/112 < 3/5' % float(x1 / (1 + x1)))
for side, name in (('bit', 'bit-111/63'), ('cx', 'cx-112/64')):
    ratio = float(tab[name][9]['hi']) / FRONTIER[side]
    check('A1.headroom-s9.' + side, near(ratio, HEADROOM_S9[side], 3),
          'X(s=9) / frontier value = %.3f' % ratio)
for s, pct in COPY_UNIT.items():
    up = X(s, 8, 1, Fr(62, 111))['hi']
    g = 100 * float(up / tab['bit-111/63'][s]['hi'] - 1)
    check('A1.copy-unit.s%d' % s, abs(g - pct) < 0.05, 'bit X gain for cst 63 -> 62 at s = %d: +%.2f%%' % (s, g))
# Units with smaller copy ratio x are outside the realised-unit scope; their ceilings show what a cheaper decoder would
# move (no word exists on either unit).  Best s = 3 on both.
HYPO = {'bit-102/54': (8, 54, 102, 8.245729422632946e-3), 'cx-104/56': (9, 56, 104, 6.799964322294041e-3)}
for name, (h, cst, v, exp) in HYPO.items():
    rr = {s: X(s, h, 1, Fr(cst, v))['hi'] for s in S_LIST}
    sb = max(rr, key=rr.get)
    check('A1.outside-scope.' + name, sb == 3 and abs(float(rr[3]) / exp - 1) < 1e-12,
          'x = %d/%d: X* = %.5e at s = %d (not a realised unit)' % (cst, v, rr[sb], sb))
finish()
