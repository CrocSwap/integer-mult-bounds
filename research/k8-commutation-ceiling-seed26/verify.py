#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Scoped obstruction: commuting reorders plus free frames cannot lift the selected k8 word's ceiling by 5%.

Usage: python3 -I -B research/k8-commutation-ceiling-seed26/verify.py [--write]

PR1671 (research/selected-k8-frame-ceiling) frees every frame of the selected k8 complex word with its chronology
fixed; seed27 frees commuting-ADD order with frame slots fixed. This checks the joint class: every within-segment
reordering that keeps the order of non-commuting gates (the commutation trace class), with every legal nested frame
assignment under PR1671's rules. It certifies that no member has bill <= 1 at a* = (21/20) a_hi, i.e. the class cannot
lift the packing ceiling by 5% (and, with a second certificate, not by 0.7%).

  B  binding: PR1671's word, retained ceiling.py and frame code (digests pinned in SOURCES.json);
  M  model: the commutation rule agrees with exact rational products on every same-register pair; the DAG intervals
     (two implementations) reduce to PR1671's in chronological mode; the word's own frames lie in them;
  S  Stage 1: the exact order-free per-register bound (does not reject in the trace class);
  L  Stage 2: an exact Lagrangian bound with stored integer multipliers (LAMBDA.json, LAMBDA-1007.json) > 1;
  C  controls: two subspace enumerators agree, the bound stays below the given word's own bill, a toy exhaustive
     check (and its invalid-charging mutation) of the bound's soundness.

Expected last line: PASS_K8_COMMUTATION_CEILING
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import model as Mo  # noqa: E402
import toy  # noqa: E402


class Reject(Exception):
    """A check failed; the argument is the label of the check."""


def need(ok, label):
    if not ok:
        raise Reject(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bind():
    pins = {f['path']: f['sha256'] for f in json.loads((HERE / 'SOURCES.json').read_text())['files']}
    base = 'research/selected-k8-frame-ceiling/'
    for rel in ('independent.py', 'common.py', 'EXPECTED.json', 'references/WORD.json.gz', 'references/SLOT-PINS.json',
                'references/frame_model.py', 'references/ceiling.py'):
        need(sha((ROOT / (base + rel)).read_bytes()) == pins[base + rel], 'B PR1671 file pinned: ' + rel)
    return {base + rel: pins[base + rel] for rel in ('independent.py', 'references/WORD.json.gz', 'references/ceiling.py')}


def load_lambda(name, W, lo, hi):
    d = json.loads((HERE / name).read_text())
    need(d['word_sha256'] == 'c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8' and d['denominator_bits'] == Mo.LAMBDA_BITS,
         'L certificate header: ' + name)
    lam = {}
    for g, k in d['lam'].items():
        g = int(g)
        need(type(k) is int and W.ops[g][0] == 'add' and lo[('G', g)] != hi[('G', g)], 'L multipliers only on free ADD gates: ' + name)
        lam[g] = k
    return lam, Q(d['a_factor_of_base_hi'])


def commute_exact(W):
    """every same-register gate pair: the rule's verdict equals exact composition in both orders on the rows involved."""
    distinct = {(g, h) for gs in W.on.values() for x, h in enumerate(gs) for g in gs[:x]}
    pairs = agree = 0
    for g, h in sorted(distinct):
        e, f = W.ops[g], W.ops[h]
        regs = set(Mo.regs(e)) | set(Mo.regs(f))
        rows1 = {r: {r: Q(1)} for r in regs}
        rows2 = {r: {r: Q(1)} for r in regs}
        for gate, rows in ((e, rows1), (f, rows1), (f, rows2), (e, rows2)):
            _apply_rows(gate, rows)
        pairs += 1
        agree += (rows1 == rows2) == Mo.commute(e, f)
    return pairs, agree


def _apply_rows(e, rows):
    if e[0] == 'add':
        t, s = e[1], e[2]
        c = Q(e[3], e[4])
        new = dict(rows[t])
        for k, v in rows[s].items():
            new[k] = new.get(k, Q(0)) + c * v
        rows[t] = {k: v for k, v in new.items() if v}
    else:
        c = Q(e[2], e[3])
        rows[e[1]] = {k: v * c for k, v in rows[e[1]].items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    binding = bind()
    I = Mo.load_1671()
    W = Mo.Word(I)
    C = W.U.retained('ceiling.py')
    need(C.ceiling(Mo.PROFILE, 73, 896, 9, 64) == (Mo.BASE_LO, Mo.BASE_HI), 'B ceiling bracket of the selected profile')
    profile = Mo.given_word_profile(W)
    need(profile == Mo.PROFILE, 'M the word\'s own frames give the selected profile')
    cost, SC = Mo.costs(C, Mo.A_STAR)
    given_bill = (sum(Q(cost[r], SC) * n for r, n in profile.items()) + Q(1646, 51) * C.child_cost(51, 73, Mo.A_STAR)[0]) / Q(896, 9)
    # model checks
    pairs, agree = commute_exact(W)
    need(pairs == agree, 'M commutation rule = exact composition on every same-register pair')
    adj = [(W.on[q][k], W.on[q][k + 1]) for q in W.on for k in range(len(W.on[q]) - 1)
           if W.seg[W.on[q][k]] == W.seg[W.on[q][k + 1]]]
    adj_comm = sum(Mo.commute(W.ops[g], W.ops[h]) for g, h in adj)
    lo1, hi1 = W.intervals('chrono')
    G = [('G', i) for i in range(len(W.ops))]
    need(all(lo1[g] == W.chrono['lo'][g] and hi1[g] == W.chrono['hi'][g] for g in G), 'M chronological intervals = PR1671\'s')
    lo2, hi2 = W.intervals('trace')
    c_lo, c_hi = W.intervals_closed('trace')
    need(all(c_lo[g] == lo2[g] and c_hi[g] == hi2[g] for g in G), 'M two interval implementations agree')
    need(all(lo2[g] & ~lo1[g] == 0 and hi1[g] & ~hi2[g] == 0 for g in G), 'M trace intervals contain chronological ones')
    need(all(lo2[('G', i)] & ~I.frame(W.ops[i][-1]) == 0 and I.frame(W.ops[i][-1]) & ~hi2[('G', i)] == 0 for i in range(len(W.ops))),
         'M the word\'s own frames lie in the trace intervals')
    qd = Counter(I.dimension(hi2[g]) - I.dimension(lo2[g]) for g in G)
    # enumerators
    distinct = sorted({(lo2[g], hi2[g]) for g in G}, key=lambda lh: (lh[1].bit_count(), lh))
    need(all(set(Mo.subspaces_closure(I, l, h)) == Mo.subspaces_rref(I, l, h) for l, h in distinct), 'C subspace enumerators agree')
    counts = {k: len(Mo.subspaces_rref(I, 1, _span(I, k))) for k in range(7)}
    need(counts == {0: 1, 1: 2, 2: 5, 3: 16, 4: 67, 5: 374, 6: 2825}, 'C subspace counts of F2^k')
    # bounds
    s1_trace, _ = Mo.bound(W, lo2, hi2, Mo.A_STAR)
    s1_chrono, _ = Mo.bound(W, lo1, hi1, Mo.A_STAR)
    need(s1_chrono > 1 and s1_trace <= 1, 'S Stage 1 rejects in chronological mode only')
    certs = {}
    for name in ('LAMBDA.json', 'LAMBDA-1007.json'):
        lam, fac = load_lambda(name, W, lo2, hi2)
        at = fac * Mo.BASE_HI
        b, _ = Mo.bound(W, lo2, hi2, at, lam)
        need(b > 1, 'L certificate %s: bill lower bound > 1' % name)
        certs[name] = dict(a='%s x a_hi' % fac, nonzero_multipliers=len(lam), bill_lower_minus_one='%.15e' % float(b - 1),
                           bill_lower_exact_sign='> 1')
        if fac == Q(21, 20):
            need(b <= given_bill, 'C the bound does not exceed the given word\'s own bill')
    # toy soundness control
    done, multi = toy.run(1, 150)
    caught = False
    try:
        toy.run(1, 150, mutated=True)
    except AssertionError:
        caught = True
    need(caught, 'C toy check catches the invalid charging rule')
    result = dict(
        status='PASS_K8_COMMUTATION_CEILING',
        binding=binding,
        model=dict(registers=W.n, gates=len(W.ops), same_register_pairs=pairs, commutation_rule_exact=True,
                   adjacent_within_segment=len(adj), adjacent_commuting=adj_comm,
                   forced_chronological=sum(lo1[g] == hi1[g] for g in G), forced_trace=sum(lo2[g] == hi2[g] for g in G),
                   changed_intervals=sum((lo1[g], hi1[g]) != (lo2[g], hi2[g]) for g in G),
                   quotient_dims_trace={str(k): v for k, v in sorted(qd.items())}, cone_registers=len(W.caps)),
        given_word=dict(profile={str(k): v for k, v in profile.items()}, bill_lower_at_a_star='%.15f' % float(given_bill)),
        stage1=dict(trace='%.15f' % float(s1_trace), chronological='%.15f' % float(s1_chrono),
                    verdict='decoupled bound rejects only with the chronology fixed'),
        stage2=certs,
        toy=dict(trials=done, with_several_linear_extensions=multi, invalid_charging_caught=True),
        a_star='%s = (21/20) x %s' % (Mo.A_STAR, Mo.BASE_HI),
        scope='Within-segment commuting reorders of A, B and the tail with every legal PR1671 frame assignment; no cross-segment '
              'moves, rescaling rewrites, changed cut/compensation/pins/endpoints, new child interfaces or other words; no kappa')
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    target = HERE / 'RESULT.json'
    if a.write:
        target.write_text(text)
    else:
        need(target.read_text() == text, 'RESULT.json reproduced byte for byte')
    print('stage1 trace %s chrono %s; stage2 %s' % (result['stage1']['trace'], result['stage1']['chronological'],
                                                  {k: v['bill_lower_minus_one'] for k, v in certs.items()}))
    print('PASS_K8_COMMUTATION_CEILING')


def _span(I, k):
    f = 1
    for j in range(k):
        f = I.extend(f, 1 << j)
    return f


if __name__ == '__main__':
    try:
        main()
    except Reject as exc:
        raise SystemExit('FAIL ' + str(exc))
