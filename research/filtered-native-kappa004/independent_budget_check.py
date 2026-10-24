#!/usr/bin/env python3
"""Independent algebraic-root enclosures for the raw kappa=1/250 budget.

Uses integer roots, without the retained logarithm/exponential engine.
This checks hypothetical invoices, never the existence of their words.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from pathlib import Path
import json

from acceptance_budget import invoice
from snapshot_probe import need

HERE = Path(__file__).resolve().parent
GRID = 2**80


def root_floor(n, k):
    x = 1 << ((n.bit_length()+k-1)//k)
    while True:
        y = ((k-1)*x+n//x**(k-1))//k
        if y >= x:
            break
        x = y
    need(x**k <= n < (x+1)**k, 'Certified integer root')
    return x


def power_bounds(rank):
    radicand = rank**249*GRID**250
    a = root_floor(radicand, 250)
    return Q(a, GRID), Q(a+1, GRID)


def margin(kind, replacements):
    target, paid = invoice(kind, replacements)
    lo = hi = Q(0)
    for rank in set(target) | set(paid):
        n = target[rank]-paid[rank]
        a, b = power_bounds(rank)
        lo += n*(a if n >= 0 else b)
        hi += n*(b if n >= 0 else a)
    return lo, hi


def main():
    retained = json.loads((HERE/'evidence/acceptance-budget.json').read_text())
    rows = {}
    for kind, minimum in [('complex', 3), ('bit', 2)]:
        rows[kind] = {}
        for count in range(5):
            a, b = margin(kind, count)
            old = retained['minimum_replacements_in_this_model'][kind]['raw_margins_at_kappa_004'][str(count)]
            old_a, old_b = Q(old['lower']), Q(old['upper'])
            need(max(a, old_a) <= min(b, old_b), 'Independent enclosures intersect')
            need((a > 0) == (count >= minimum), 'Exact conditional center threshold')
            rows[kind][str(count)] = [str(a), str(b)]
    # Deliberately altered inventories must lose their strict margin.
    need(margin('complex', 2)[1] < 0 and margin('bit', 1)[1] < 0,
         'One fewer replacement is rejected')
    out = {'status': 'PASS_INDEPENDENT_INTEGER_ROOT_RAW_BUDGET',
           'exponent': '249/250', 'denominator_grid': str(GRID),
           'margins': rows, 'new_kappa_claimed': False,
           'scope': 'Independent exact algebraic-root bounds for the raw hypothetical moment invoices. Compiler, outer ledger and physical words are separate obligations.'}
    (HERE/'evidence/independent-budget.json').write_text(json.dumps(out, indent=2)+'\n')
    print(out['status'])


if __name__ == '__main__':
    main()
