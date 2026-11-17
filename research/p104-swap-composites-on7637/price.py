#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify the price with the repository's own invoice tools.

Runs scripts/compare_recursive_invoices.py (#7637 invoice against the new
one, concave order) and scripts/evaluate_recursive_power.py (new invoice
against the empty invoice at r^t, t = 1 - C) and requires:
  - the new invoice is uniformly better than #7637's for every increasing
    concave tariff, strictly for r^(1-C), 0 < C < 1;
  - at C = 0.0037136318149 the new paid cost is strictly below the new
    targets (F(C) > 0), so the crossing is above the claim;
  - at C = 0.0037136318150 it is strictly above (F(C) < 0);
  - at #7637's C = 0.00370007700378 the new invoice is strictly favourable.
The invoices themselves are recomputed from the words by check.py.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = HERE / 'data'
CLAIM, ABOVE, PR7637 = '0.0037136318149', '0.0037136318150', '0.00370007700378'


def tool(name, *args):
    out = subprocess.run([sys.executable, '-I', '-B', str(ROOT / 'scripts' / name), *map(str, args)],
                         capture_output=True, text=True, check=True, timeout=120)
    return json.loads(out.stdout)


def one_minus(c):
    from decimal import Decimal
    return str(1 - Decimal(c))


def main():
    old, new, zero = DATA / 'invoice-7637.json', DATA / 'invoice-new.json', DATA / 'invoice-zero.json'
    rep = tool('compare_recursive_invoices.py', old, new)
    assert rep['classification'] == 'uniformly_better', rep['classification']
    assert rep['power_moment']['new_minus_old_sign'] == 'strictly_negative'
    assert rep['delta_paid'] == {'2': -272, '3': -85, '4': -272, '6': 238, '9': 51}, rep['delta_paid']
    assert rep['delta_targets'] == {}, rep['delta_targets']
    print('PASS compare_recursive_invoices #7637 -> new: uniformly_better, paid delta', rep['delta_paid'], 'target delta', rep['delta_targets'])
    for c, want in ((CLAIM, 'new_cost_lower'), (ABOVE, 'new_cost_higher'), (PR7637, 'new_cost_lower')):
        r = tool('evaluate_recursive_power.py', zero, new, '--exponent', one_minus(c), '--bits', 256)
        assert r['classification'] == want, (c, r['classification'])
        print('PASS evaluate_recursive_power at C = %s (t = %s): %s' % (c, r['exponent'], want))
    print('PASS_PRICE kappa in (%s, %s)' % (CLAIM, ABOVE))


if __name__ == '__main__':
    sys.exit(main())
