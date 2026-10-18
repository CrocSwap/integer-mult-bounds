#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate dense-bin, sorted-prefix and Fraction-bisection cross-check."""
from collections import Counter
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def bound_root(r, degree):
    lo, hi = Q(0), Q(r)
    for _ in range(60):
        mid = (lo+hi)/2
        if mid**degree <= r:
            lo = mid
        else:
            hi = mid
    check(lo**degree <= r <= hi**degree, 'rational root bounds')
    return lo, hi


def run():
    receipt = read(HERE/'CERTIFICATE.json')
    arrays = {}
    for pr in (1022,1028,1031,1042):
        p = ROOT/f'research/community-batch1047-audit/variants/pr{pr}/research/gauge44-slots-t16/data'
        plan, roles = read(p/'PLAN.json'), read(p/'OWNERS.json.gz')
        bins = {(tuple(map(int,k.split(',')))+(port,)):[False]*v[0]
                for k,v in plan['windows'].items() for port in range(112)}
        for role in roles:
            row = bins[role['owner_replica'],role['child'],role['port']]
            a,b = role['offset'],role['offset']+role['width']
            check(0 <= a < b <= len(row), 'slice bounds')
            for i in range(a,b):
                check(not row[i], 'overlap')
                row[i] = True
        residuals = []
        for row in bins.values():
            check(row == sorted(row,reverse=True), 'occupied prefix')
            residuals.append(row.count(False))
        arrays[pr] = sorted(residuals,reverse=True)
        expected = receipt['maps'][str(pr)]['histogram']
        check({str(k):v for k,v in Counter(residuals).items()} == expected, 'independent dense histogram')
    tested = 0
    for key, record in receipt['comparisons'].items():
        a,b = map(int,key.split('->'))
        check(len(arrays[a]) == len(arrays[b]), 'equal sorted length')
        diff, margins = 0, []
        for x,y in zip(arrays[a],arrays[b]):
            diff += y-x
            margins.append(diff)
        check(diff == 0, 'equal mass')
        relation = 'new_majorizes_old' if min(margins)>=0 else 'old_majorizes_new' if max(margins)<=0 else 'incomparable'
        check(relation == record['relation'], 'sorted-prefix relation')
        old,new=Counter(arrays[a]),Counter(arrays[b])
        delta={r:new[r]-old[r] for r in set(old)|set(new) if new[r]!=old[r]}
        check(delta == {int(k):v for k,v in record['delta'].items()}, 'independent signed histogram difference')
        for degree, field in [(2,'power_cost_b_half'),(4,'power_cost_b_three_quarters')]:
            low=high=Q(0)
            for r,n in delta.items():
                if not r:
                    continue
                l,u=bound_root(r,degree)
                low += n*(l if n>0 else u)
                high += n*(u if n>0 else l)
            sign='negative' if high<0 else 'positive' if low>0 else 'unresolved'
            check(sign == record[field]['sign'], 'independent power sign')
            tested += 1
    check(len(receipt['comparisons']) == 6 and tested == 12, 'comparison inventory')
    print('PASS_INDEPENDENT_T16_CONCAVITY: 129024 dense residuals; 193536 sorted prefixes; 12 Fraction signs')


if __name__ == '__main__':
    run()
