#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certified decoder copy budgets for the plane-port coverage law (both suppliers).

Model: the coverage-law relaxation of research/complex-local-word-ceiling (complex) and
research/bit-revision3-levers-seed03 (bit), with ctoth's plane-port contract (discussion 1587):
  * two unpaid coordinates per live family (unpaid = 2);
  * every data incidence climbs one coordinate less (complex 8 -> 7, bit 7 -> 6), so the local
    data mass drops by one unit per incidence (complex 224 = 2 * 112 per call, bit 222 = 2 * 111);
  * today's copies (complex 8 rank-8, bit 9 rank-7) are removed and replaced by k decoder copies of
    one rank r, so the per-call copy charge is C = r * k;
  * everything else in the shipped local word is kept; remaining mass goes to idle children at the
    cap R (complex 51; bit 45 as admitted by the record's PR510 row bound, and 53 as the most
    permissive elementary-cover cap).
The data shrink is bracketed. 'unchanged' leaves the word as shipped (pessimistic: valid because a
one-unit shortening at child rank <= 8 removes at least the cost of one idle unit at rank R >= 45,
see README). 'shrink' removes the drop as rank-1 children (favorable: the largest possible cost
removal per unit of mass). A budget is the largest integer k with the relaxed moment certified < 1
at the target saving a*, with k + 1 certified > 1. Moments are monotone in k.

Both engines are imported unchanged from the base commit; their sha256 is checked first.
usage: verify.py [--write]   (--write regenerates RESULT.json; default compares with it)
Claude Code (Claude Opus 5.5) for JosieElliston. Apache-2.0.
"""
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


class Fail(Exception):
    pass


def need(ok, why):
    if not ok:
        raise Fail(why)


def load(rel, name):
    path = ROOT / rel
    pins = {f['path']: f['sha256'] for f in json.loads((HERE / 'SOURCES.json').read_text())['files']}
    need(hashlib.sha256(path.read_bytes()).hexdigest() == pins[rel], 'source pin mismatch: ' + rel)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CX = load('research/complex-local-word-ceiling/ceiling.py', 'cx_ceiling')
BT = load('research/bit-revision3-levers-seed03/levers.py', 'bit_levers')

# complex: selected #1094 local word per call (complex-local-word-ceiling); 8 rank-8 = the centre copies
CM, CFAM, CST = 73, 896, 9
CWORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
CW = Q(CFAM, CST)
CR = CX.max_idle_rank(CM)
CDATA_DROP = 224                         # 2 * 112 data incidences per call, one unit each

# bit: PR589 word per call, replayed in bit-revision3-levers-seed03/RESULT.json
BM, BW = 64, Q(888, 9)
BDATA_DROP = 222                         # 2 * 111 data registers per call, one unit each
COPY_RANKS = (1, 2, 7, 8)


def bit_word():
    rep = json.loads((ROOT / 'research/bit-revision3-levers-seed03/RESULT.json').read_text())['replay']
    local = {}
    for cls in ('sources', 'targets', 'helpers', 'totals'):
        for r, n in rep['class_split'][cls].items():
            local[int(r)] = local.get(int(r), 0) + int(n)
    copies = {int(r): int(n) for r, n in rep['copies'].items()}
    need(copies == {7: 9} and rep['copy_charge_per_call'] == 63, 'bit copies are nine rank-7')
    data_rank1 = int(rep['class_split']['sources']['1']) + int(rep['class_split']['targets']['1'])
    for r, n in copies.items():
        local[r] += n
    return local, copies, data_rank1


def cx_moment(local, centre, a, unpaid):
    return CX.relax(local, CM, CFAM, CST, centre, a, unpaid=unpaid)


def cx_verdict(local, centre, a, unpaid):
    try:
        lo, hi = cx_moment(local, centre, a, unpaid)
    except ValueError:
        return 'fail'                    # local mass exceeds the coverage law
    return 'pass' if hi < 1 else 'fail' if lo > 1 else 'undecided'


def bt_verdict(local, cst, a, R, unpaid):
    try:
        H = BT.relaxed(local, BM, BW, cst, R, unpaid)
    except BT.Reject:
        return 'fail'
    return BT.verdict(H, BM, BW, a)


def budget(verdict_of_k, limit=4000):
    """Largest k in [0, limit] whose verdict is 'pass', with k+1 certified 'fail'; None if k = 0 fails."""
    v0 = verdict_of_k(0)
    need(v0 != 'undecided', 'undecided at k = 0')
    if v0 == 'fail':
        return None
    lo, hi = 0, limit
    need(verdict_of_k(limit) == 'fail', 'search limit too small')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        v = verdict_of_k(mid)
        need(v != 'undecided', 'undecided boundary')
        lo, hi = (mid, hi) if v == 'pass' else (lo, mid)
    need(verdict_of_k(lo) == 'pass' and verdict_of_k(lo + 1) == 'fail', 'sharpness')
    return lo


def sub(word, r, n):
    w = dict(word)
    w[r] = w.get(r, 0) - n
    need(w[r] >= 0, 'not enough children to remove')
    return w


def main(write):
    sel = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    kappa = Q(sel['kappa'])
    need(kappa == Q(836330098538459, 500000000000000000), 'selected kappa')
    a_sel = kappa / (1 - kappa)
    k10 = kappa * Q(11, 10)
    a10 = k10 / (1 - k10)
    a99 = Q(1, 99)

    # --- positive controls: the predecessors' incumbent ceilings
    cx_base = CX.ceiling(CWORD, CM, CFAM, CST, 64, grid=Q(1, 10 ** 12))
    need(abs(float(cx_base[1]) - 0.001690054) < 1e-9, 'complex incumbent ceiling reproduces complex-local-word-ceiling')
    need(cx_verdict(CWORD, 64, cx_base[0], 1) == 'pass' and cx_verdict(CWORD, 64, cx_base[1], 1) == 'fail', 'complex bracket')
    blocal, bcopies, bdata1 = bit_word()
    need(sum(r * n for r, n in blocal.items()) == 5129, 'bit local rank mass per call')
    bt_base = {R: BT.root(BT.relaxed(blocal, BM, BW, 63, R), BM, BW) for R in (45, 53)}
    need(BT.dec(bt_base[45][0]) == '0.001955918756', 'bit incumbent ceiling (cap 45) reproduces bit-revision3-levers-seed03')

    # --- coverage-law bookkeeping (per call)
    cx_mass_line = sum(r * n for r, n in CWORD.items())
    need(cx_mass_line == 5586 and (CM - 1) * CW + 64 - cx_mass_line == Q(1646), 'complex idle mass 1646 per call')
    need((CM - 2) * CW - (cx_mass_line - 64 - CDATA_DROP) == Q(15934, 9), "complex plane-port idle (before copies) 1770.4")

    cx_scen = {
        'unchanged': sub(CWORD, 8, 8),
        'shrink': sub(sub(CWORD, 8, 8), 1, CDATA_DROP),
    }
    need(bdata1 >= BDATA_DROP, 'bit data has enough rank-1 climbs to shrink')
    bt_scen = {
        'unchanged': sub(blocal, 7, 9),
        'shrink': sub(sub(blocal, 7, 9), 1, BDATA_DROP),
    }
    targets_cx = {'incumbent_ceiling': cx_base[1], 'selected_endpoint': a_sel, 'kappa_plus_10pct': a10, 'a_1_over_99': a99}
    targets_bt = {'incumbent_ceiling_cap45': bt_base[45][1], 'kappa_plus_10pct': a10, 'a_1_over_99': a99}

    out = dict(
        status='PASS_PLANE_PORT_COPY_BUDGETS',
        targets=dict(selected_kappa=str(kappa), a_selected=str(a_sel), a_plus_10pct=str(a10), a_1_over_99=str(a99),
                     complex_incumbent_ceiling=[str(x) for x in cx_base],
                     bit_incumbent_ceiling={str(R): [str(x) for x in v] for R, v in bt_base.items()}),
        first_order=dict(complex_break_even=str(Q(1472, 9)),
                         note='ctoth (1587): deficit 2w - C > w - 64 with the word unchanged'),
        complex={}, bit={},
    )
    for name, base in cx_scen.items():
        rows = {}
        for r in COPY_RANKS:
            for tname, a in targets_cx.items():
                k = budget(lambda k: cx_verdict({**base, r: base.get(r, 0) + k}, r * k, a, 2))
                rows['rank%d/%s' % (r, tname)] = None if k is None else dict(copies=k, charge=r * k)
        # ceiling of the plane-port relaxation at today's charge (64 as 8 rank-8 copies) and at ctoth's naive 224
        rows['ceiling_at_charge_64'] = str(CX.ceiling({**base, 8: base.get(8, 0) + 8}, CM, CFAM, CST, 64,
                                                      grid=Q(1, 10 ** 12), unpaid=2)[1])
        rows['ceiling_at_charge_0'] = str(CX.ceiling(base, CM, CFAM, CST, 0, grid=Q(1, 10 ** 12), unpaid=2)[1])
        rows['naive_224_rank2_passes_any_target'] = any(
            cx_verdict({**base, 2: base.get(2, 0) + 112}, 224, a, 2) == 'pass' for a in targets_cx.values())
        out['complex'][name] = rows
    for name, base in bt_scen.items():
        rows = {}
        for R in (45, 53):
            for r in COPY_RANKS:
                for tname, a in targets_bt.items():
                    k = budget(lambda k: bt_verdict({**base, r: base.get(r, 0) + k}, r * k, a, R, 2))
                    rows['cap%d/rank%d/%s' % (R, r, tname)] = None if k is None else dict(copies=k, charge=r * k)
        rows['ceiling_cap45_at_charge_63'] = str(BT.root(BT.relaxed({**base, 7: base.get(7, 0) + 9}, BM, BW, 63, 45, 2),
                                                         BM, BW)[1])
        rows['ceiling_cap45_at_charge_0'] = str(BT.root(BT.relaxed(base, BM, BW, 0, 45, 2), BM, BW)[1])
        out['bit'][name] = rows

    # --- controls on the line-port law (unpaid = 1)
    need(cx_verdict(cx_scen['unchanged'], 0, a10, 1) == 'pass', 'control: complex centre-free line law passes +10% (lever table x2.80)')
    need(cx_verdict(CWORD, 64, a_sel, 1) == 'pass' and cx_verdict(CWORD, 64, a10, 1) == 'fail', 'control: incumbent passes selected, fails +10%')
    need(bt_verdict(blocal, 63, a10, 45, 1) == 'pass' and bt_verdict(blocal, 63, a99, 53, 1) == 'fail',
         'control: bit incumbent relaxation passes +10% (ceiling 0.001956, not tight) and fails 1/99')

    path = HERE / 'RESULT.json'
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if write:
        path.write_text(text)
    else:
        need(path.read_text() == text, 'RESULT.json differs from the recomputed receipt')
    print(out['status'])
    for side in ('complex', 'bit'):
        for name, rows in out[side].items():
            for key, v in rows.items():
                print(side, name, key, v)


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('run without -O: checks use need(), but refuse -O for parity with the engines')
    try:
        main('--write' in sys.argv[1:])
    except Fail as e:
        raise SystemExit('FAIL: ' + str(e))
