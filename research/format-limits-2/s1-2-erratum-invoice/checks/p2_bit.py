"""P2: bit invoice of the #555 R439 word (nine stages, m = 64, L = 9, K = 4, T = 32, live 28416).
c is the root a of  sum_r (r n_r / (m W)) (m/r)^a + 32 m (sum n) / (1e16 W) m^a = 1   (the moment root with its bad term).
CHECKED here: c to 24 digits, the mass identity, and the profile-level cst-unit knobs (a child r -> r-1 on all 288 calls).
The word-level knobs (port with idle repack, helper by pattern) need the per-register climbs and the idle-packing model of
the unpublished card B26/knobs.py (> 120 s) and are RECORDED in the README, not checked."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from invoice import *

E = load('pr555/EXPECTED.json.gz')['nine']
P = {int(r): n for r, n in E['profile'].items()}
m, W = 64, E['bit']['live']
N = 288


def c_of(P, W_=W, prec=60):
    with localcontext() as ctx:
        ctx.prec = prec
        terms = [(D(r * n) / D(m * W_), (D(m) / D(r)).ln()) for r, n in P.items() if n]
        terms.append((D(32 * m * sum(P.values())) / D(10 ** 16 * W_), D(m).ln()))
        a = D(0)
        for _ in range(100):
            f = sum(p * (a * l).exp() for p, l in terms) - 1
            df = sum(p * l * (a * l).exp() for p, l in terms)
            na = a - f / df
            if abs(na - a) < D(10) ** -(prec - 5):
                return na
            a = na
        raise RuntimeError


c0 = c_of(P)
lit = D(E['bit_lower_decimal'])
check('P2.root', abs(c0 / lit - 1) < D('2e-22'), 'c = %s vs shipped %s (rel %.1e, 24-digit grid)' % (str(c0)[:28], lit, float(c0 / lit - 1)))
check('P2.mass', hmass(P) == 1808352 == E['bit']['rank_mass'] and m * W - hmass(P) == 10272 == 256 * 111 - 288 * 63,
      'mass %d = rank_mass; deficit mW - mass = 10272 = 256 v - 288 cst (v = 111, cst = 63)' % hmass(P))
d = lambda Q: float((c_of(Q) / c0 - 1) * 100)
def edit(*ch):
    Q = Counter(P)
    for r, n in ch:
        Q[r] += n * N
    return Q
unit = {r: d(edit((r, -1), (r - 1, 1))) for r in range(2, 8)}
unit[1] = d(edit((1, -1)))
check('P2.cst-unit', abs(unit[7] - 2.8017) < 0.0006 and abs(d(edit((7, -2), (6, 2))) - 5.603) < 0.003,
      '1 cst unit (copy 7->6, all 288 calls): %+.4f%% c; 2nd unit: %+.3f%% cumulative' % (unit[7], d(edit((7, -2), (6, 2)))))
check('P2.unit-any-rank', all(2.80 <= unit[r] <= 2.817 for r in range(1, 8)) and abs(unit[1] - 2.816) < 0.001,
      'a child r->r-1 on any rank costs %s%% c (width irrelevant)' % ' '.join('r%d %.4f' % (r, unit[r]) for r in range(1, 8)))
finish()
