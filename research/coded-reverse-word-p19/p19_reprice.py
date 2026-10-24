#!/usr/bin/env python3
"""Reprice the complex side from the operator's own target census.

The invoice models 4 intermediate target roles per stage and 2 full-stack roles; the p=19
operator has 3 and 11.  Both cover 38 roles and 4256 calls.  This receipt keeps the invoice
untouched, prices the operator's own census instead, and reports the raw root with a solver
that cannot return an artificial bracket bound:

    f(c) = sum_T n r^(1-c) - sum_D n r^(1-c)
    require f(0) > 0, then expand hi until f(hi) <= 0, then bisect.

The paid D histogram is the inherited profile and is labelled as such, not derived.  The
helper target mass is the inherited Option A block.  A control re-derives the invoiced root
from the invoiced histogram, so the solver is shown to reproduce a known value before its
new number is quoted.
"""
import json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p19_word as W

PUBLISHED = 0.007578535189897761

def need(ok, why):
    if not ok: raise ValueError(why)

def solve(T, D, tag):
    f = lambda c: sum(n*(r**(1-c)) for r, n in T.items()) - sum(n*(r**(1-c)) for r, n in D.items())
    need(f(0.0) > 0, 'f(0) > 0 at ' + tag)
    lo, hi = 0.0, 0.05
    steps = 0
    while f(hi) > 0:
        hi *= 2
        steps += 1
        need(hi < 1.0, 'no root below c = 1 at ' + tag)
    need(f(hi) <= 0, 'bracket closes at ' + tag)
    for _ in range(300):
        mid = (lo+hi)/2
        if f(mid) > 0: lo = mid
        else: hi = mid
    return lo, hi, steps

def main():
    p, pat = 19, 'I'*9+'T'*9
    P_NEW = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}
    thick = frozenset(range(1, 2*p, 2))
    T_inv_raw, D_raw = W.invoice(p, pat, thick, P_NEW)
    T_inv = Counter(); D = Counter()
    for k, v in T_inv_raw.items(): T_inv[int(k)] += v
    for k, v in D_raw.items(): D[int(k)] += v
    helper = {r: p*n for r, n in W.H.items()}

    row = json.loads((HERE/'P19_ROWFRAME.json').read_text())
    main_phys = {int(k): v for k, v in row['derived_row_T'].items()}
    T_phys = Counter(main_phys)
    for r, n in helper.items(): T_phys[r] += n

    print('invoiced T total :', dict(sorted(T_inv.items())))
    print('physical T total :', dict(sorted(T_phys.items())))
    print('paid D (inherited):', dict(sorted(D.items())))
    print()

    # control: the solver must reproduce the published invoiced root
    lo_i, hi_i, st_i = solve(T_inv, D, 'invoiced')
    print('control  invoiced histogram -> root in [%.15f, %.15f] (%d bracket expansions)' % (lo_i, hi_i, st_i))
    need(abs(lo_i - PUBLISHED) < 1e-12, 'the solver reproduces the published invoiced root')
    print('PASS control: the solver reproduces %.15f from the invoiced histogram' % PUBLISHED)

    lo_p, hi_p, st_p = solve(T_phys, D, 'physical')
    print()
    print('physical histogram -> root in [%.15f, %.15f] (%d bracket expansions)' % (lo_p, hi_p, st_p))
    print('raw moment sign at the physical root: f(root) > 0 on the lower side')
    ratio = lo_p/lo_i
    print('physical root / invoiced root = %.4f' % ratio)
    print('physical root vs BIT cap 0.0034        : %+.1f%%' % (100*(lo_p/0.0034-1)))
    print('physical root vs frontier 0.00302728823: %+.1f%%' % (100*(lo_p/0.00302728823-1)))
    print('physical root vs selected record 0.00302015: %+.1f%%' % (100*(lo_p/0.00302015-1)))

    receipt = {
        'status': 'REPRICE_PHYSICAL_CENSUS',
        'solver': {'f0_positive': True, 'expanding_bracket': True,
                   'invoiced_bracket_expansions': st_i, 'physical_bracket_expansions': st_p},
        'control': {'invoiced_root': lo_i, 'published': PUBLISHED, 'reproduces': abs(lo_i-PUBLISHED) < 1e-12},
        'invoiced_T': dict(sorted(T_inv.items())),
        'physical_T': dict(sorted(T_phys.items())),
        'paid_D_inherited': dict(sorted(D.items())),
        'paid_D_status': 'inherited profile, not derived',
        'helper_mass': 'inherited Option A block ' + str(helper),
        'physical_root': lo_p, 'physical_root_bracket': [lo_p, hi_p],
        'invoiced_root': lo_i,
        'note': ('the repriced number is a different claim from the invoiced one; the invoice, the published root '
                 'and the kappa are left unchanged here')}
    (HERE/'P19_REPRICE.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print()
    print('NEW ROOT (physical census, inherited D): %.15f' % lo_p)

if __name__ == '__main__':
    main()
