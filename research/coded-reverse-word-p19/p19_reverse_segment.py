#!/usr/bin/env python3
"""Exact reverse/letter lowering using the inherited noncommutative algebra.

Algebra implementation: coded-native-caller/gauge.py, Apache-2.0,
with its retained PR4929 attribution. OpenAI-assisted construction.
"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def check():
    path = ROOT / 'research/coded-native-caller/gauge.py'
    spec = importlib.util.spec_from_file_location('reverse_segment_algebra', path)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    a = source.Algebra(2)
    q, c, d = a.gen(1), a.gen(2), a.D(0)
    shear = a.U(a.neg(a.mul(q, c)))
    native = a.mm(a.diag(d, d), shear)
    r = a.mul(d, q)
    wanted = a.mm(a.diag(r, r), shear)
    after = a.mm(a.diag(q, q), native)
    before = a.mm(native, a.diag(q, q))
    need(after == wanted, 'post-Q native backward equals reverse followed by R')
    need(native != wanted, 'omitting post-Q must change the operator')
    need(before != wanted, 'moving post-Q across the shear must fail')
    need(a.mul(c, q) != a.mul(q, c), 'noncommuting C/Q control')
    need(a.mul(c, r) == a.mul(r, c), 'source C/R relation')
    qi, ci, di = a.inv(q), a.inv(c), a.inv(d)
    forward = a.mm(a.diag(d, d), a.L(a.mul(c, qi)))
    target_forward = a.L(a.mul(ci, qi))
    pre = a.diag(a.one, a.mul(c, c))
    post = a.diag(a.one, a.mul(ci, ci))
    lowered_forward = a.mm(post, a.diag(di, di), forward, pre)
    need(lowered_forward == target_forward, 'exact forward shear lowering')
    need(a.mm(post, forward, pre) != target_forward,
         'forward native D removal cannot be omitted')
    need(a.mm(a.diag(di, di), post, forward, pre) != target_forward,
         'forward inverse D and code cannot exchange order')
    def query_segment(wrong_order=False, clear_work=True):
        rows = [[a.one, {}, {}], [{}, a.one, {}], [{}, {}, a.one]]
        rows[2] = [dict(x) for x in rows[0]]
        for op in ((ci, qi) if wrong_order else (qi, ci)):
            rows[2] = [a.mul(op, x) for x in rows[2]]
        rows[1] = [a.add(x, y) for x, y in zip(rows[1], rows[2])]
        if clear_work:
            rows[2] = [{}, {}, {}]
        return rows
    expected_query = [[a.one, {}, {}], [a.mul(ci, qi), a.one, {}], [{}, {}, {}]]
    need(query_segment() == expected_query, 'owned query on all three arbitrary input fields')
    need(query_segment(wrong_order=True) != expected_query, 'query order mutation')
    need(query_segment(clear_work=False) != expected_query, 'query work erasure mutation')
    import p19_word as W
    from collections import Counter
    gates = W.native_chain(19, 'I' * 9 + 'T' * 9)
    counts = Counter(g[0] for g in gates)
    thick = set(range(1, 38, 2))
    query_calls = counts['FORWARD'] * W.OWNERS
    need(query_calls == W.OWNERS * (39 - len(thick)) == 2240,
         'forward query ranks equal the invoice thin-query term')
    targets, paid = W.invoice(19, 'I' * 9 + 'T' * 9, thick, W.P_NEW)
    surplus = sum(r * n for r, n in targets.items()) - sum(r * n for r, n in paid.items())
    direct_corrections = 2 * W.OWNERS * counts['REVERSE']
    need(surplus == 2016 and direct_corrections == 4256,
         'direct lowering accounting control')
    bridge = a.L(a.one)
    equal_gauges = a.diag(q, q)
    mixed_gauges = a.diag(q, a.one)
    need(a.mm(bridge, equal_gauges) == a.mm(equal_gauges, bridge),
         'equal central gauges cross a scalar bridge')
    need(a.mm(bridge, mixed_gauges) != a.mm(mixed_gauges, bridge),
         'unequal central gauges cannot cross a scalar bridge unchanged')
    moved_bridge = a.mm(mixed_gauges, bridge, a.diag(qi, a.one))
    need(moved_bridge == a.L(qi), 'exact transported bridge coefficient')
    correction = a.L(a.add(qi, a.neg(a.one)))
    need(a.mm(correction, bridge) == moved_bridge,
         'one central query minus the original source repairs the bridge')
    need(a.mm(a.L(a.add(q, a.neg(a.one))), bridge) != moved_bridge,
         'wrong central inverse bridge repair rejected')
    central = [0] * 38
    first_mismatch = None
    for index, gate in enumerate(gates):
        if gate[0] == 'LETTER':
            for role in gate[1:3]:
                central[role] ^= 1
        elif gate[0] == 'IDLE':
            for role in gate[1:3]:
                central[role] ^= gate[3] % 2
        elif gate[0] == 'BRIDGE':
            dst, src = gate[1:3]
            if central[dst] != central[src]:
                first_mismatch = (index, dst, src, central[dst], central[src])
                break
    need(first_mismatch is not None, 'central-only propagation has a bridge checkpoint')
    print('PASS exact reverse/letter segment: diag(Q,Q) B(C) = diag(R,R) U(-QC)')
    print('PASS controls: omitted Q and pre-Q both rejected')
    print('PASS exact forward segment: diag(I,C^-2) diag(D^-1,D^-1) F(C) diag(I,C^2) = L(C^-1 Q^-1)')
    print('PASS controls: omitted inverse D and exchanged inverse D/code both rejected')
    print('PASS owned forward query: source unchanged, exact target shear, arbitrary work input removed, final work zero')
    print('PASS query controls: wrong order and omitted erasure rejected')
    print('PASS forward rank inventory: 20 x 112 = 2240, matching the existing thin-query term')
    print('PASS bridge controls: equal central gauges commute; unequal gauges do not')
    print('PASS bridge repair: diag(Q,I) L(I) diag(Q^-1,I) = L(Q^-1) = L(Q^-1-I) L(I)')
    print('PASS bridge repair control: Q substituted for Q^-1 is rejected')
    print('OPEN central-only propagation checkpoint (gate, dst, src, parities):', first_mismatch)
    print('OPEN reverse invoice: direct implementation adds %d rank-one calls before any proved cancellation'
          % direct_corrections)
    print('Direct lowering rank surplus: %d - %d = %d; reuse must save at least %d calls for positive surplus'
          % (surplus, direct_corrections, surplus - direct_corrections,
             direct_corrections - surplus + 1))
    print('Scope: local identities and one propagation checkpoint, not an exclusion of other lowerings')


if __name__ == '__main__':
    check()
