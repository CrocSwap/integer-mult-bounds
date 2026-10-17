#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compose the PR3190 idle-remainder complex endpoint with the R438 bit supplier.

PR3190 (research/rank7-idle-remainder-donors-t740) raised the complex root of PR3133's words on
PR3148's T740 fill to 0.0017347705571115131604951, past the PR589 bit saving, so its kappa was
bit-capped at 0.001733427039589844234749.  The R438 bit supplier (PR1043 word, PR2423 transport and
re-hosting, natively replayed in research/r438-native-rehost on main) has bit endpoint
0.001734846264120199151475, above that complex root.  With it the complex side binds again.

This verifier (standard library only):
  1. re-derives the complex root bracket of PR3190's declared profile with its own interval arithmetic;
  2. re-derives the R438 bit endpoint from the certificate's own bit profile (m = 64, live = 28,416,
     with the 10^-16 * 32 m^2 fallback envelope): accepted at c, rejected at c + 1e-24;
  3. computes kappa = min(floor24(complex_lower), floor24(bit_lower)) - 1e-46 - 1e-70 and gates it.
The moves and profile of PR3190 are checked by that package's own registered verifier.
"""
import argparse, hashlib, json
from fractions import Fraction as F
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
COMPLEX = ROOT / 'research/rank7-idle-remainder-donors-t740/RESULT.json'
BITCERT = ROOT / 'research/r438-native-rehost/CERTIFICATE.json'
GATES = dict(PR3148=F('0.0017297774946785970118859999999999999999999998999999999999999999999999'),
             PR3184=F('0.0017301890612338507600949999999999999999999998999999999999999999999999'),
             PR3190=F('0.0017334270395898442347489999999999999999999998999999999999999999999999'))


class Reject(Exception): pass
def req(ok, why):
    if not ok: raise Reject(why)

Q72 = 10 ** 72
def rd(x): return F(x.numerator * Q72 // x.denominator, Q72)
def ru(x): return F(-((-x.numerator * Q72) // x.denominator), Q72)
def atanh2(z, n):
    s, p = F(0), z
    for j in range(n): s += p / (2 * j + 1); p *= z * z
    return 2 * s, 2 * p / ((2 * n + 1) * (1 - z * z))
L2 = atanh2(F(1, 3), 130)
def ln_box(y):
    k = 0
    while y >= 2: y /= 2; k += 1
    a, e = atanh2((y - 1) / (y + 1), 90)
    return rd(a + k * L2[0]), ru(a + e + k * (L2[0] + L2[1]))
def exp_box(x0, x1):
    def tay(x):
        s, t = F(1), F(1)
        for j in range(1, 34): t = t * x / j; s += t
        return s, t * x / 34 * 3
    a, _ = tay(x0); b, t = tay(x1)
    return rd(a), ru(b + t)
def moment(prof, m, W, b, bad=False):
    lo = hi = F(0)
    items = sorted(prof.items())
    if bad:  # bad-edge Gaussian fallback envelope, 10^-16 * 32 m^2 rank-1 children per child (bit pricing)
        items = items + [(1, F(32 * m * m * sum(prof.values()), 10 ** 16))]
    for r, n in items:
        l0, l1 = ln_box(F(m, r)); e0, e1 = exp_box(b * l0, b * l1)
        lo += n * r * e0; hi += n * r * e1
    return lo / (m * W), hi / (m * W)


def compose(cx, bit):
    prof = {int(k): v for k, v in cx['profile'].items()}
    req(sum(r * n for r, n in prof.items()) == 65088 * 740 and max(prof) <= 51, 'PR3190 profile mass/halving')
    lo, hi = F(cx['complex_root'][0]), F(cx['complex_root'][1])
    req(hi - lo == F(1, 10 ** 25) and moment(prof, 73, 896 * 740, lo)[1] < 1 < moment(prof, 73, 896 * 740, hi)[0], 'complex root bracket')
    inv = bit['pipeline']['candidate']['hosted']['invoice']
    bprof = {int(k): v for k, v in json.loads(inv['bit_profile'].replace("'", '"')).items()} if isinstance(inv['bit_profile'], str) else {int(k): v for k, v in inv['bit_profile'].items()}
    c = F(inv['bit_lower']); c_next = F(inv['next_grid_point_rejected'])
    req(c == F(inv['bit_lower_decimal']) and c_next - c == F(1, 10 ** 24), 'bit certificate fields')
    W = 28416
    req(64 * W - sum(r * n for r, n in bprof.items()) > 0 and 2 * max(bprof) ** 2 < 64 ** 2, 'bit profile deficit/halving')
    req(moment(bprof, 64, W, c, True)[1] < 1 and moment(bprof, 64, W, c_next, True)[0] > 1, 'bit endpoint accepted at c, rejected at c+1e-24')
    floor24 = lambda x: F(x.numerator * 10 ** 24 // x.denominator, 10 ** 24)
    C = min(floor24(lo), floor24(c))
    req(C == floor24(lo) and floor24(lo) < c, 'complex binds below the R438 bit endpoint')
    kappa = C - F(1, 10 ** 46) - F(1, 10 ** 70)
    for n, g in GATES.items(): req(kappa > g, 'kappa must exceed ' + n)
    return kappa, lo, c


def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.parse_args()
    if not __debug__: raise SystemExit('assertions required')
    cx = json.loads(COMPLEX.read_text()); bit = json.loads(BITCERT.read_text())
    claim = json.loads((PKG / 'CLAIM.json').read_text())
    kappa, lo, c = compose(cx, bit)
    req(F(claim['kappa']) == kappa == F(claim['kappa_decimal']), 'CLAIM kappa')
    rej = {}
    import copy
    for name, mut in [('complex_next_grid', lambda x, b: x.__setitem__('complex_root', [str(lo + F(1, 10**25)), str(lo + F(2, 10**25))])),
                      ('bit_next_grid', lambda x, b: b['pipeline']['candidate']['hosted']['invoice'].update(
                          bit_lower=str(F(b['pipeline']['candidate']['hosted']['invoice']['next_grid_point_rejected'])),
                          bit_lower_decimal=str(F(b['pipeline']['candidate']['hosted']['invoice']['next_grid_point_rejected'])),
                          next_grid_point_rejected=str(F(b['pipeline']['candidate']['hosted']['invoice']['next_grid_point_rejected']) + F(1, 10**24)))),
                      ('pr589_bit', lambda x, b: b['pipeline']['candidate']['hosted']['invoice'].update(
                          bit_lower='1733427039589844234749/1000000000000000000000000', bit_lower_decimal='1733427039589844234749/1000000000000000000000000',
                          next_grid_point_rejected='1733427039589844234750/1000000000000000000000000'))]:
        x, b = copy.deepcopy(cx), copy.deepcopy(bit); mut(x, b)
        try: compose(x, b)
        except Reject as e: rej[name] = str(e)
        else: raise SystemExit('mutation accepted: ' + name)
    print('PASS_R438_COMPOSITION kappa=%s complex=%s bit=%s controls=%d' % (float(kappa), float(lo), float(c), len(rej)))
    print(json.dumps(rej, sort_keys=True))


if __name__ == '__main__':
    try: main()
    except Reject as e: raise SystemExit('FAIL: ' + str(e))
