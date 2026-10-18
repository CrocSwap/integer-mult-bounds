#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Supplementary scan, not part of the registered replay.

For every in-repo research/*/ASSEMBLY.json branch that records bootstrap
cutoffs, check stages 3 onward against the carried-constant rule with the
minimal carry ceil(L_(i-1)*(a_(i-1)-a_(i-2))). Recorded exponents only; no
chain start or allowance is assumed. Exact rationals, standard library only.
"""
import glob
import json
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def ceil(x):
    return -(-x.numerator // x.denominator)


branches = stages = failing = 0
for path in sorted(glob.glob(str(ROOT / 'research/*/ASSEMBLY.json'))):
    try:
        record = json.loads(Path(path).read_text())
    except ValueError:
        continue
    for name in ('bootstrap', 'conservative_bootstrap'):
        rows = record.get(name)
        if not (isinstance(rows, list) and rows and isinstance(rows[0], dict) and 'cutoff_log2' in rows[0]):
            continue
        branches += 1
        a = [Q(r['exponent']) for r in rows]
        gap = [Q(r['gap']) for r in rows]
        cut = [int(r['cutoff_log2']) for r in rows]
        for i in range(2, len(rows)):
            stages += 1
            carry = ceil(cut[i - 1] * (a[i - 1] - a[i - 2]))
            if cut[i] * gap[i] < 2 * (4 + carry):
                failing += 1
            else:
                print('PAYS', Path(path).relative_to(ROOT), name, i + 1)
print(f'SCAN receipt_branches={branches} stages_from_3={stages} failing_carry={failing}')
