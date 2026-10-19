#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent verifier for the pooled R437 owner map and its composition with the PR3955 complex endpoint.

Does not import build.py.  Rebuilds all 125,856 R437 hosted roles (32 replicas x 9 stages x 437 helpers) from
PR3647's template-bound per-replica placement (hosting.slots), applies POOL-MOVES.json, and checks every role
against the slot rules: host child window contains the stage, the host pair is inactive at that stage, width 8
inside capacity, disjoint cells, compact prefixes, every (stage, replica, helper) hosted exactly once.  It prices
the baseline (must equal PR3647's EXPECTED profile and endpoint) and the pooled profile with its own interval
arithmetic (10^-16 * 32 m^2 fallback envelope), then composes with PR3955's complex root.
"""
import copy, gzip, hashlib, json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
V, T, COPIES, STAGES, R = 111, 32, 222, 9, 437
LOCAL_B = {1: 1320, 2: 1344, 3: 77, 4: 43, 5: 102, 6: 11, 7: 18}   # R437 local profile (PR3647 EXPECTED minus slot remainders)
ACTIVE = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3}     # pair swept at each stage
GATES = dict(PR3958=F('0.0017366460420384465785509999999999999999999998999999999999999999999999'),
             PR3955=F('0.0017349004315839471573409999999999999999999998999999999999999999999999'))
EXPECTED = ROOT / 'research/rank7-frame-select-r437-bit/R437-EXPECTED.json'
EXPECTED_LF_SHA = 'fa724e9a1e1588379dbcb0f3b6f8051c24c7cbdd4ef9c5e93167e846b294a9f9'


class Reject(Exception): pass
def req(ok, why):
    if not ok: raise Reject(why)


TEMPLATE = None
def windows():
    return {int(i): (v[0], v[1], tuple(v[2])) for i, v in TEMPLATE['hosting']['windows'].items()}


def roles(alloc, hosting, moves):
    out = {}
    for rep in range(T):
        for child, cp, off, w, s, h in alloc:
            pair = hosting[child][0]
            out[s, rep, h] = (rep * 8 * V + (2 * pair + cp // V) * V + cp % V, child, off, w)
    for m in moves:
        k = (m['stage'], m['call_replica'], m['helper'])
        req(k in out and out[k][:3] == (m['old']['family'], m['old']['child'], m['old']['offset']), 'move source matches baseline')
        out[k] = (m['new']['family'], m['new']['child'], m['new']['offset'], 8)
    return out


def audit(rl, hosting):
    req(set(rl) == {(s, r, h) for s in range(STAGES) for r in range(T) for h in range(R)}, 'every role hosted once')
    cells = defaultdict(set)
    for (s, rep, h), (fam, child, off, w) in rl.items():
        pair, cap, stages = hosting[child]
        frep, rest = divmod(fam, 8 * V); pair2, port = divmod(rest, V)
        req(0 <= frep < T and pair2 // 2 == pair, 'family encodes the host child pair')
        req(s in stages, 'stage inside host window'); req(pair != ACTIVE[s], 'host pair inactive at stage')
        req(w == 8 and 0 <= off and off + w <= cap, 'residual extent')
        key = (frep, child, (pair2 % 2) * V + port); new = set(range(off, off + w))
        req(not cells[key] & new, 'cell collision'); cells[key] |= new
    idle = Counter()
    for frep in range(T):
        for child, (pair, cap, st) in hosting.items():
            for cp in range(COPIES):
                c = cells.get((frep, child, cp), set())
                req(c == set(range(len(c))), 'compact prefix')
                if cap - len(c): idle[cap - len(c)] += 1
    return idle


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
def moment(p, m, W, b, bad):
    items = sorted(p.items()) + ([(1, F(32 * m * m * sum(p.values()), 10 ** 16))] if bad else [])
    lo = hi = F(0)
    for r, n in items:
        l0, l1 = lnb(m, r); e0, e1 = ex(b * l0, b * l1); lo += n * r * e0; hi += n * r * e1
    return lo / (m * W), hi / (m * W)


def bitprof(idle):
    H = Counter({r: n * STAGES * T for r, n in LOCAL_B.items()}); H.update(idle); return dict(sorted(H.items()))


def run(alloc, moves, claim, cx):
    hosting = windows()
    req(all(hosting[i][0] != ACTIVE[s] for i in hosting for s in hosting[i][2]), 'template windows avoid active pairs')
    i0 = audit(roles(alloc, hosting, []), hosting); i1 = audit(roles(alloc, hosting, moves), hosting)
    exp = json.loads(EXPECTED.read_text())
    req(bitprof(i0) == {int(k): v for k, v in exp['profile'].items()}, 'baseline equals the PR3647 EXPECTED profile')
    c0 = F(exp['BIT_c'])
    req(moment(bitprof(i0), 64, 28416, c0, True)[1] < 1 < moment(bitprof(i0), 64, 28416, c0 + F(1, 10 ** 24), True)[0], 'R437 endpoint')
    p1 = bitprof(i1); c1 = F(claim['bit_pooled'])
    req(sum(r * n for r, n in p1.items()) == sum(r * n for r, n in bitprof(i0).items()) and 2 * max(p1) ** 2 < 64 ** 2, 'mass and halving')
    req(moment(p1, 64, 28416, c1, True)[1] < 1 < moment(p1, 64, 28416, c1 + F(1, 10 ** 24), True)[0], 'pooled bit endpoint')
    prof = {int(k): v for k, v in cx['profile'].items()}
    lo, hi = F(cx['complex_root'][0]), F(cx['complex_root'][1])
    req(hi - lo == F(1, 10 ** 25) and moment(prof, 73, 896 * 740, lo, False)[1] < 1 < moment(prof, 73, 896 * 740, hi, False)[0], 'PR3955 complex root')
    fl = lambda x: F(x.numerator * 10 ** 24 // x.denominator, 10 ** 24)
    req(c0 < c1 < fl(lo), 'complex floor above the pooled R437 bit endpoint')
    kappa = min(fl(lo), fl(c1)) - F(1, 10 ** 46) - F(1, 10 ** 70)
    req(kappa == F(claim['kappa']) == F(claim['kappa_decimal']), 'CLAIM kappa')
    for n, g in GATES.items(): req(kappa > g, 'kappa must exceed ' + n)
    return i0, i1, c1, kappa, lo


def main():
    if not __debug__: raise SystemExit('assertions required')
    global TEMPLATE
    eraw = EXPECTED.read_bytes()
    req(hashlib.sha256(eraw.replace(b'\r\n', b'\n')).hexdigest() == EXPECTED_LF_SHA, 'PR3647 EXPECTED binding')
    raw = gzip.decompress((PKG / 'R437-GLOBAL-TEMPLATE.json.gz').read_bytes())
    req(hashlib.sha256(raw).hexdigest() == json.loads(eraw)['template_content_sha256'], 'R437 template binding (PR3647 template_content_sha256)')
    TEMPLATE = json.loads(raw)
    alloc = [tuple(t) for t in TEMPLATE['hosting']['slots']]
    moves = json.loads((PKG / 'POOL-MOVES.json').read_text())['moves']
    claim = json.loads((PKG / 'CLAIM.json').read_text())
    cx = json.loads((ROOT / 'research/rank7-idle-frame-select/RESULT.json').read_text())
    i0, i1, c1, kappa, lo = run(alloc, moves, claim, cx)
    rej = {}
    def bad(name, f, c=claim):
        mv = copy.deepcopy(moves); cl = copy.deepcopy(c); f(mv, cl)
        try: run(alloc, mv, cl, cx)
        except Reject as e: rej[name] = str(e)
        else: raise SystemExit('mutation accepted: ' + name)
    bad('outside_window', lambda mv, cl: mv[0]['new'].update(child=2, family=mv[0]['new']['family'] - 4 * V + 4 * V))
    bad('cell_collision', lambda mv, cl: mv[1]['new'].update(offset=mv[0]['new']['offset']) if mv[0]['new']['family'] == mv[1]['new']['family'] else None)
    bad('wrong_source', lambda mv, cl: mv[0]['old'].update(offset=mv[0]['old']['offset'] + 8))
    bad('dropped_move', lambda mv, cl: mv.pop())
    bad('pooled_next_grid', lambda mv, cl: cl.update(bit_pooled=str(F(cl['bit_pooled']) + F(1, 10 ** 24))))
    bad('kappa_off_grid', lambda mv, cl: cl.update(kappa=str(F(cl['kappa']) + F(1, 10 ** 24)), kappa_decimal=str(F(cl['kappa']) + F(1, 10 ** 24))))
    print('PASS_POOLED_R437_BIT idle_delta=%s bit=%s complex=%s kappa=%s controls=%d' % (
        {k: v for k, v in sorted((Counter(i1) - Counter(i0) + Counter()).items())}, float(c1), float(lo), float(kappa), len(rej)))
    print(json.dumps(rej, sort_keys=True))


if __name__ == '__main__':
    try: main()
    except Reject as e: raise SystemExit('FAIL: ' + str(e))
