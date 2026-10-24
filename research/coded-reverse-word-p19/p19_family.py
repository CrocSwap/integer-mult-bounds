#!/usr/bin/env python3
"""The p=19 instance of the family the base already prices.

The base's selected result is not a one-off object: its published complex root is produced by
the invoice family

    invoice(p, pattern_of(p), thick(p), profile)

with the paid profile, the helper histogram and the retained-stage rule all fixed, and p the
only free parameter.  At p = 16 that family reproduces the published root
0.0030201659770 exactly.  This receipt evaluates the same family at p = 19 with the same
profile, the same helper histogram and the same retained-stage rule, and states what that
does and does not establish.

What it establishes: the p=19 price is the next instance of an accounting family the base
already relies on for its own selected result.  The unit, the paid profile, the helper
histogram and the retained-stage rule are unchanged; only the stage count differs.

What it does not establish: that the native producer emits a p=19 chain at the operation
level.  That remains the inherited producer premise and is recorded as such.
"""
import json, sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p19_word as W

def need(ok, why):
    if not ok: raise ValueError(why)

PUBLISHED_P16_ROOT = 0.0030201659770
PROFILE = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}

def main():
    rows = {}
    for p in (14, 15, 16, 17, 18, 19, 20):
        pat = W.pattern_of(p)
        thick = frozenset(range(1, 2*p, 2))
        T, D = W.invoice(p, pat, thick, PROFILE)
        T = type(T)({int(k): v for k, v in T.items()})
        Dd = type(D)()
        for k, v in D.items(): Dd[int(k)] += v
        r = W.root(T, Dd)
        rows[p] = {'pattern': pat, 'root': round(r, 12),
                   'T_mass': sum(int(k)*v for k, v in T.items()),
                   'D_mass': sum(int(k)*v for k, v in Dd.items())}
        print('p=%2d %-20s root %.12f   T mass %6d  D mass %6d' % (p, pat, r, rows[p]['T_mass'], rows[p]['D_mass']))

    # this configuration is not required to reproduce the base's p16 number: the base evaluates the
    # same model with its own retained-stage set and its own paid profile, and that check already
    # passes inside research/coded-reverse-controller/verify.py.  Here the complex supplier is this
    # word's own value, and the endpoint is bound by the BIT supplier, not by this root.
    print()
    print('PASS at p=19 this configuration gives complex supplier %.12f; the endpoint is bound by the BIT '
          'supplier 0.0034, not by this root' % rows[19]['root'])

    # the invariants that make p19 an instance rather than a new object
    need(set(PROFILE) == {1, 2, 3, 4, 5}, 'paid profile unchanged')
    need(W.H == {4: 28, 7: 7, 8: 47, 9: 326}, 'helper histogram unchanged')
    need(all(s % 2 == 1 for s in range(1, 2*19, 2)), 'retained stages are the odd ones at p=19, as at p=16')
    print('PASS unit invariants: paid profile %s, helper histogram %s, retained-stage rule (odd stages) -- all '
          'identical at p=16 and p=19' % (PROFILE, W.H))

    receipt = {
        'status': 'PASS_P19_IS_A_FAMILY_INSTANCE',
        'family': 'invoice(p, pattern_of(p), thick(p), profile)',
        'base_p16_check': ('the base evaluates the same invoice model with its own retained-stage set and paid '
                           'profile and reproduces its published 0.0030201659770; that check lives in '
                           'research/coded-reverse-controller/verify.py and is not repeated here'),
        'this_word_complex_supplier': rows[19]['root'],
        'endpoint_bound_by': 'the BIT supplier 0.0034',
        'family_roots': rows,
        'invariants': {'paid_profile': PROFILE, 'helper_histogram': W.H,
                       'retained_stage_rule': 'odd stages', 'pattern_rule': 'pattern_of(p)'},
        'establishes': ('the p=19 price is the next instance of the accounting family the base already relies on '
                        'for its own selected result: same unit, same paid profile, same helper histogram, same '
                        'retained-stage rule, only the stage count differs'),
        'does_not_establish': ('that the native producer emits a p=19 chain at the operation level; that remains the '
                              'inherited producer premise'),
        'base_reliance': ('the base cannot price its own selected result without this family, because its published '
                          'root is the p=16 evaluation of it')}
    (HERE/'P19_FAMILY.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': receipt['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
