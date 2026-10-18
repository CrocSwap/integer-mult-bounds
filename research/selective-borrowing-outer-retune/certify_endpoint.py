#!/usr/bin/env python3
"""Certify the complex supplier endpoint of PR2260's recounted global profile to 10^-DIG.

C = DIG-digit decimal with  conservative_moment(C) < 1  and  conservative_moment(C + 10^-DIG) > 1,
and also native_moment(C) < 1.  The moment is PR2260's (and PR1673's) sum_r r H_r/(m W) (m/r)^b; the conservative
form adds PR2260's retained bad-residue surcharge 32 m sum(H)/(10^16 W) m^b (vendor/pr2260-.../arithmetic/vendor/moment.py).
Enclosures: exact rationals with directed rounding on a 2^-GB grid (the routines of outer/check_ledger.py, PR1786/PR1673 lineage).
usage: certify_endpoint.py [--write]   (default: check the committed ENDPOINT.json)
"""
from fractions import Fraction as Q
from decimal import Decimal, localcontext
from pathlib import Path
import json, sys
sys.set_int_max_str_digits(0)
if not __debug__: raise RuntimeError('Assertions must be enabled')
HERE = Path(__file__).resolve().parent
SPEC = json.loads((HERE / 'SPEC.json').read_text())
DIG = SPEC['outer_refinement']['endpoint_digits']
profile = {int(r): n for r, n in SPEC['expected']['global_profile'].items()}
m = SPEC['geometry']['dimension']; W = SPEC['expected']['live']
assert (m, W) == (73, 7168) and sum(r * n for r, n in profile.items()) == 520704 and m * W - 520704 == 2560
assert m * m > 2 * max(profile) ** 2
BAD = Q(32 * m * sum(profile.values()), 10 ** 16 * W)   # weight of the conservative rank-1 surcharge term

GB = int((DIG + 130) * 3.3220) + 16
ONE = 1 << GB
def _cd(a, b): return -((-a) // b)
def down(x): return Q((x * ONE).__floor__(), ONE)
def up(x): return Q(_cd(x.numerator * ONE, x.denominator), ONE)
LN = GB // 3 + 12; EN = GB // 6 + 12
def unit_log(y):
    z = (y - 1) / (y + 1); p, q = z.numerator, z.denominator; p2, q2 = p * p, q * q
    pl = ONE * p // q; ph = _cd(ONE * p, q); sl = sh = 0
    for j in range(LN):
        sl += pl // (2 * j + 1); sh += _cd(ph, 2 * j + 1); pl = pl * p2 // q2; ph = _cd(ph * p2, q2)
    tail = _cd(2 * ph * q2, (2 * LN + 1) * (q2 - p2))
    return Q(2 * sl, ONE), Q(2 * sh + tail, ONE)
ln2 = unit_log(Q(2))
def log(x):
    k = 0
    while x >= 2: x /= 2; k += 1
    lo, hi = unit_log(x)
    return down(lo + k * ln2[0]), up(hi + k * ln2[1])
def exp(x):
    assert 0 <= x < Q(1, 100)
    xl = x.numerator * ONE // x.denominator; xu = _cd(x.numerator * ONE, x.denominator)
    tl = th = sl = sh = ONE
    for j in range(1, EN):
        tl = ((tl * xl) >> GB) // j; th = _cd(-((-th * xu) >> GB), j); sl += tl; sh += th
    tn = _cd(-((-th * xu) >> GB), EN)
    return Q(sl, ONE), Q(sh + 2 * tn + 2, ONE)
LOGS = {r: log(Q(m, r)) for r in set(profile) | {1}}
def moment(b, conservative):
    lo = hi = Q(0)
    terms = [(r, Q(n * r, m * W)) for r, n in profile.items()]
    if conservative: terms.append((1, BAD))
    for r, w in terms:
        l, h = LOGS[r]
        lo += w * exp(b * l)[0]; hi += w * exp(b * h)[1]
    return down(lo), up(hi)

def decimal_root():
    with localcontext() as c:
        c.prec = DIG + 60
        t = [(Decimal(n * r) / Decimal(m * W), (Decimal(m) / Decimal(r)).ln()) for r, n in profile.items()]
        t.append((Decimal(BAD.numerator) / Decimal(BAD.denominator), Decimal(m).ln()))
        b = Decimal('0.0016834')
        for _ in range(60):
            f = sum(w * (b * L).exp() for w, L in t) - 1
            d = sum(w * L * (b * L).exp() for w, L in t)
            b -= f / d
        return int(b.scaleb(DIG).to_integral_value(rounding='ROUND_FLOOR'))

if '--write' in sys.argv[1:]:
    C = Q(decimal_root(), 10 ** DIG)
else:
    C = Q(json.loads((HERE / 'ENDPOINT.json').read_text())['complex_lower'])
step = Q(1, 10 ** DIG)
assert (C * 10 ** DIG).denominator == 1
nat = moment(C, False); con = moment(C, True); rej = moment(C + step, True)
assert nat[1] < 1 and con[1] < 1, 'endpoint not accepted'
assert rej[0] > 1, 'next grid point not rejected (conservative)'
out = dict(schema='pr2260-complex-endpoint-v1', endpoint_digits=DIG, complex_lower=str(C),
           native_moment_upper_minus_one=str(nat[1] - 1), conservative_moment_upper_minus_one=str(con[1] - 1),
           conservative_moment_lower_minus_one_at_next_grid_point=str(rej[0] - 1),
           profile={str(k): v for k, v in sorted(profile.items())}, m=m, W=W, surcharge_weight=str(BAD))
if '--write' in sys.argv[1:]:
    (HERE / 'ENDPOINT.json').write_text(json.dumps(out, indent=1) + '\n')
else:
    assert json.loads((HERE / 'ENDPOINT.json').read_text()) == out, 'ENDPOINT.json differs from fresh certification'
with localcontext() as c:
    c.prec = 40
    print('PASS_ENDPOINT', 'C =', Decimal(C.numerator) / Decimal(C.denominator), 'DIG', DIG)
