#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pool R437's width-8 slack across the 32 bit replicas with an explicit cross-replica owner map (PR3939's idea on R437).

R437 (PR3647, ai-nanachi) hosts all 125,856 helper residuals in PR1023-model slots.  Per replica, window 6
(capacity 42, pair 0, stages 3..8) keeps 209 five-residual families, one two-residual family (idle 26) and 12 empty
families; window 8 (capacity 14, pair 2, stages 7..8) keeps one residual per copy (idle 6).  Pooled over 32 replicas
the window-6 slack is 32*63 = 2016 = 403*5 + 1 places.  The pooled32 slot optimum (bit-partial-width7-optimum,
residue t = 1) is 403 empty 42-families and one empty capacity-14 copy.  This builder realizes it literally:

* the 62 residuals of the two-residual families of replicas 1..31 and one window-8 residual of replica 0
  (stage 8, inside window 6) are moved;
* replica 0's two-residual family receives three of them (offsets 16, 24, 32) and replica 0's 12 empty window-6
  families receive five each.

Idle bill change: {2:+13, 6:-1, 14:+1, 26:-32, 42:+19}; rank mass and maxchild 42 unchanged.
Input: R437-GLOBAL-TEMPLATE.json.gz (PR3647 generated/GLOBAL-TEMPLATE.json.gz, content SHA-256 equal to EXPECTED's
template_content_sha256).  Output: POOL-MOVES.json, CLAIM.json.
"""
import gzip, hashlib, json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V, T, COPIES, STAGES = 111, 32, 222, 9
LOCAL_B = {1: 1320, 2: 1344, 3: 77, 4: 43, 5: 102, 6: 11, 7: 18}


def need(ok, why):
    if not ok: raise SystemExit('FAIL: ' + why)


Q72 = 10 ** 72
def rd(x): return F(x.numerator * Q72 // x.denominator, Q72)
def ru(x): return F(-((-x.numerator * Q72) // x.denominator), Q72)
def at(z, n):
    s, p = F(0), z
    for j in range(n): s += p / (2 * j + 1); p *= z * z
    return 2 * s, 2 * p / ((2 * n + 1) * (1 - z * z))
L2 = at(F(1, 3), 130)
def lnb(m, r):
    y, k = F(m, r), 0
    while y >= 2: y /= 2; k += 1
    a, e = at((y - 1) / (y + 1), 90)
    return rd(a + k * L2[0]), ru(a + e + k * (L2[0] + L2[1]))
def ex(x0, x1):
    def tay(x):
        s, t = F(1), F(1)
        for j in range(1, 34): t = t * x / j; s += t
        return s, t * x / 34 * 3
    a, _ = tay(x0); b, t = tay(x1); return rd(a), ru(b + t)
def moment(p, b):
    m, W = 64, 28416
    items = sorted(p.items()) + [(1, F(32 * m * m * sum(p.values()), 10 ** 16))]
    lo = hi = F(0)
    for r, n in items:
        l0, l1 = lnb(m, r); e0, e1 = ex(b * l0, b * l1); lo += n * r * e0; hi += n * r * e1
    return lo / (m * W), hi / (m * W)


def endpoint(p, start):
    k0, k1 = int(start * 10 ** 24), int(start * 10 ** 24) + 10 ** 18
    need(moment(p, F(k0, 10 ** 24))[1] < 1 and moment(p, F(k1, 10 ** 24))[0] > 1, 'bracket')
    while k1 - k0 > 1:
        k = (k0 + k1) // 2; lo, hi = moment(p, F(k, 10 ** 24))
        if hi < 1: k0 = k
        elif lo > 1: k1 = k
        else: raise SystemExit('wide interval')
    return F(k0, 10 ** 24)


def main():
    raw = gzip.decompress((HERE / 'R437-GLOBAL-TEMPLATE.json.gz').read_bytes())
    exp = json.loads((ROOT / 'research/rank7-frame-select-r437-bit/R437-EXPECTED.json').read_text())
    need(hashlib.sha256(raw).hexdigest() == exp['template_content_sha256'], 'R437 template binding')
    tpl = json.loads(raw)
    slots = tpl['hosting']['slots']
    pair = {int(i): w[0] for i, w in tpl['hosting']['windows'].items()}
    occ = defaultdict(list)
    for child, cp, off, w, s, h in slots: occ[child, cp].append((off, s, h))
    two = [cp for cp in range(COPIES) if len(occ.get((6, cp), [])) == 2]
    empty = [cp for cp in range(COPIES) if not occ.get((6, cp))]
    need(len(two) == 1 and len(empty) == 12, 'R437 window-6 shape: one two-residual family and 12 empty families')
    fam = lambda rep, child, cp: rep * 8 * V + (2 * pair[child] + cp // V) * V + cp % V
    src8 = (0, 8, 0, *occ[8, 0][0])                     # replica 0, child 8, copy 0, its single residual
    need(src8[4] in (7, 8) and src8[3] == 0, 'window-8 residual at stage 7 or 8')
    movers = [(rep, 6, two[0], off, s, h) for rep in range(1, T) for off, s, h in sorted(occ[6, two[0]])]
    movers.append(src8)
    need(len(movers) == 63, '63 residuals')
    dests = [(two[0], 16), (two[0], 24), (two[0], 32)] + [(cp, 8 * k) for cp in empty for k in range(5)]
    moves = []
    for (rep, child, cp, off, s, h), (cpd, offd) in zip(movers, dests):
        moves.append(dict(stage=s, call_replica=rep, helper=h, old=dict(family=fam(rep, child, cp), child=child, offset=off),
                          new=dict(family=fam(0, 6, cpd), child=6, offset=offd)))
    # price: idle bill change {2:+13, 6:-1, 14:+1, 26:-32, 42:+19}
    base = Counter({r: n * STAGES * T for r, n in LOCAL_B.items()})
    for i, rem in tpl['hosting']['remainders'].items():
        for r, n in rem.items(): base[int(r)] += n * T
    need({str(k): v for k, v in sorted(base.items())} == exp['profile'], 'baseline profile equals PR3647 EXPECTED')
    pooled = Counter(base); pooled.update({2: 13, 6: -1, 14: 1, 26: -32, 42: 19}); pooled = {r: n for r, n in sorted(pooled.items()) if n}
    need(sum(r * n for r, n in pooled.items()) == exp['rank_mass'], 'rank mass')
    c0 = F(exp['BIT_c']); c1 = endpoint(pooled, c0)
    cx = json.loads((ROOT / 'research/rank7-idle-frame-select/RESULT.json').read_text())
    lo = F(cx['complex_root'][0]); fl = F(lo.numerator * 10 ** 24 // lo.denominator, 10 ** 24)
    need(c1 < fl, 'complex floor above the pooled bit endpoint')
    kappa = min(fl, c1) - F(1, 10 ** 46) - F(1, 10 ** 70)
    g = F('0.0017366460420384465785509999999999999999999998999999999999999999999999')
    (HERE / 'POOL-MOVES.json').write_text(json.dumps(dict(template_content_sha256=exp['template_content_sha256'], moves=moves), indent=1) + '\n')
    claim = dict(kappa=str(kappa), kappa_decimal='0.' + str(kappa.numerator * 10 ** 70 // kappa.denominator).rjust(70, '0'),
                 binding='bit (pooled R437)', bit_r437=str(c0), bit_pooled=str(c1), bit_pooled_decimal='0.' + str(c1.numerator * 10 ** 24 // c1.denominator).rjust(24, '0'),
                 pooled_profile={str(k): v for k, v in pooled.items()}, complex_root=cx['complex_root'],
                 gain_over_pr3958=str(kappa - g), gain_over_pr3958_percent=str(float((kappa - g) / g * 100)),
                 status='author-checked conditional candidate')
    (HERE / 'CLAIM.json').write_text(json.dumps(claim, indent=1) + '\n')
    print('PASS pooled R437 moves', len(moves), 'bit', claim['bit_pooled_decimal'], 'gain%', claim['gain_over_pr3958_percent'])


if __name__ == '__main__':
    main()
