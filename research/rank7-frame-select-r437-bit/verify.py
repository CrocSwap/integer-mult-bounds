#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compose PR3955's complex endpoint (hosted frame selection, T740) with PR3647's R437 bit supplier.

Self-contained exact check (standard library only; does not import any other package's code):

* complex side: rank7-idle-frame-select/RESULT.json (bound by SHA-256 to that package's committed AUDIT.json
  status and its declared profile).  The profile's rank mass, halving guard and the 1e-25 root bracket are
  re-checked with this file's own directed-rounding interval arithmetic (m = 73, W = 896 * 740).
* bit side: R437-EXPECTED.json, PR3647's EXPECTED.json copied byte-for-byte (git blob pinned in SOURCES.json).
  Its paid profile is re-priced here (m = 64, W = 28416, with the inherited 10^-16 * 32 m^2 * N rank-1 fallback
  envelope): accepted at c and rejected at c + 10^-24; rank mass 1808352, maximum child 42 (2*42^2 < 64^2).
* kappa = min(floor24(complex_lower), c) - 10^-46 - 10^-70, with the bit side binding; gates over PR3955/PR3939.
Mutation controls must be rejected.
"""
import copy, hashlib, json
from fractions import Fraction as F
from pathlib import Path

PKG = Path(__file__).resolve().parent
CX = PKG.parent / 'rank7-idle-frame-select'
# PR3647's file is stored with CRLF line ends (blob bc2585e1, SHA-256 67d06bcb...2de0); this repository's
# text=auto/eol=lf attributes commit it LF-normalized.  Bind the line-end-normalized bytes.
EXPECTED_SHA = 'fa724e9a1e1588379dbcb0f3b6f8051c24c7cbdd4ef9c5e93167e846b294a9f9'
T = 740
GATES = dict(PR3955=F('0.0017349004315839471573409999999999999999999998999999999999999999999999'),
             PR3939=F('0.0017348651784727109982329999999999999999999998999999999999999999999999'))


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
def lnb(m, r):
    """Outward bounds on log(m / r)."""
    y, k = F(m, r), 0
    while y >= 2: y /= 2; k += 1
    a, e = atanh2((y - 1) / (y + 1), 90)
    return rd(a + k * L2[0]), ru(a + e + k * (L2[0] + L2[1]))
def exb(x0, x1):
    def tay(x):
        s, t = F(1), F(1)
        for j in range(1, 34): t = t * x / j; s += t
        return s, t * x / 34 * 3
    a, _ = tay(x0); b, t = tay(x1); return rd(a), ru(b + t)
def moment(prof, m, W, b, fallback):
    items = sorted(prof.items()) + ([(1, F(32 * m * m * sum(prof.values()), 10 ** 16))] if fallback else [])
    lo = hi = F(0)
    for r, n in items:
        l0, l1 = lnb(m, r); e0, e1 = exb(b * l0, b * l1); lo += n * r * e0; hi += n * r * e1
    return lo / (m * W), hi / (m * W)
def floor24(x): return F(x.numerator * 10 ** 24 // x.denominator, 10 ** 24)


def run(cx, bit, claim):
    prof = {int(k): v for k, v in cx['profile'].items()}
    req(sum(r * n for r, n in prof.items()) == 65088 * T and 73 * 73 > 2 * max(prof) ** 2, 'complex rank mass and halving')
    lo, hi = F(cx['complex_root'][0]), F(cx['complex_root'][1])
    req(hi - lo == F(1, 10 ** 25) and moment(prof, 73, 896 * T, lo, False)[1] < 1 < moment(prof, 73, 896 * T, hi, False)[0], 'complex root bracket')
    bp = {int(k): v for k, v in bit['profile'].items()}
    c = F(bit['BIT_c'])
    req(c == F(bit['BIT_c_decimal']) and F(bit['next_grid']) == c + F(1, 10 ** 24), 'R437 endpoint fields')
    req(bit['live'] == 28416 and sum(r * n for r, n in bp.items()) == bit['rank_mass'] == 1808352 and 2 * max(bp) ** 2 < 64 ** 2, 'R437 W, rank mass and halving')
    req(moment(bp, 64, 28416, c, True)[1] < 1 < moment(bp, 64, 28416, c + F(1, 10 ** 24), True)[0], 'R437 bit endpoint accepted at c, rejected at c + 1e-24')
    C = min(floor24(lo), c)
    req(c < floor24(lo) and C == c, 'bit binds: complex floor above the R437 endpoint')
    kappa = C - F(1, 10 ** 46) - F(1, 10 ** 70)
    req(kappa == F(claim['kappa']) == F(claim['kappa_decimal']), 'CLAIM kappa')
    for n, g in GATES.items(): req(kappa > g, 'kappa must exceed ' + n)
    return lo, c, kappa


def main():
    if not __debug__: raise SystemExit('assertions required')
    raw = (PKG / 'R437-EXPECTED.json').read_bytes()
    req(hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() == EXPECTED_SHA, 'R437 EXPECTED.json binding (PR3647 a24f9ff9)')
    bit = json.loads(raw)
    cx = json.loads((CX / 'RESULT.json').read_text())
    audit = json.loads((CX / 'AUDIT.json').read_text())
    req(audit['status'] == 'PASS_IDLE_FRAME_SELECT_AUDIT' and F(audit['complex_root_lower']) == F(cx['complex_root'][0]), 'PR3955 audit receipt binds the complex root')
    claim = json.loads((PKG / 'CLAIM.json').read_text())
    lo, c, kappa = run(cx, bit, claim)
    rej = {}
    def bad(name, f):
        a, b, cl = copy.deepcopy(cx), copy.deepcopy(bit), copy.deepcopy(claim); f(a, b, cl)
        try: run(a, b, cl)
        except Reject as e: rej[name] = str(e)
        else: raise SystemExit('mutation accepted: ' + name)
    nxt = str(c + F(1, 10 ** 24))
    bad('bit_next_grid', lambda a, b, cl: b.update(BIT_c=nxt, BIT_c_decimal=nxt, next_grid=str(c + F(2, 10 ** 24))))
    bad('bit_profile_tamper', lambda a, b, cl: b['profile'].update({'1': b['profile']['1'] + 2, '2': b['profile']['2'] - 1}))
    bad('bit_rank_mass', lambda a, b, cl: b['profile'].update({'1': b['profile']['1'] + 1}))
    bad('complex_next_grid', lambda a, b, cl: a.update(complex_root=[str(lo + F(1, 10 ** 25)), str(lo + F(2, 10 ** 25))]))
    bad('complex_profile_tamper', lambda a, b, cl: a['profile'].update({'1': a['profile']['1'] + 102, '51': a['profile']['51'] - 2}))
    bad('kappa_off_grid', lambda a, b, cl: cl.update(kappa=str(F(cl['kappa']) + F(1, 10 ** 24)), kappa_decimal=str(F(cl['kappa']) + F(1, 10 ** 24))))
    print('PASS_FRAME_SELECT_R437_BIT complex=%s bit=%s kappa=%s controls=%d' % (float(lo), float(c), float(kappa), len(rej)))
    print(json.dumps(rej, sort_keys=True))


if __name__ == '__main__':
    try: main()
    except Reject as e: raise SystemExit('FAIL: ' + str(e))
