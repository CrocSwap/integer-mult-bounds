#!/usr/bin/env python3
"""Exact rejection of a specified n-role Gauss--Jordan side family."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from math import comb
import json

from certify import require,verify_sources
from prepare_layers import serializable
from experiments.inplace_side import central_type,compile_side,verify_prefix
from experiments.core_limits import dimension_limit

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    witnesses=json.loads((ROOT/'scripts/experiments/inplace_side_witnesses.json').read_text())
    checks=[verify_prefix(w['h'],w['pivots'],w['swaps']) for w in witnesses]
    require([x['h'] for x in checks]==[42,46,50],'Missing target-range witness')
    require(all(x['no_positive_deficit'] for x in checks),'Rank rejection failed')
    controls=[]
    for h in (6,10):
        c=compile_side(h)
        controls.append(dict(h=h,n=c['roles'],scalar_gates=len(c['gates']),
                             exact_side_map=True,physical_identity_paths=verify_prefix(h,c['pivots'],[])))
    require(all(comb(h,3)<=6*h*h for h in range(6,40,2)),'Low-h rejection failed')
    types=[central_type(h) for h in range(40,53,2)]
    limit=dimension_limit(Q(1,2**25),auxiliary_floor=True)
    sources=('scripts/audit_inplace_side.py','scripts/experiments/inplace_side.py',
             'scripts/experiments/inplace_side_witnesses.json','scripts/experiments/core_limits.py',
             'docs/research/inplace-side.md')
    return dict(status='SPECIFIED IN-PLACE FAMILY EXCLUDED; NO STRONGER KAPPA',
                upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),
                target_kappa=Q(1,2**25),prefix_checks=checks,small_scalar_controls=controls,
                target_range_side_types=types,dimension_screen=limit,
                scope='Identical triple factors, even h, exactly n side roles, lexicographic smallest-row Gauss--Jordan, retained central and data boundaries. All internal rational frames allowed.',
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/inplace-side.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS: exact path excess rejects the specified in-place family for kappa >= 2^-25.')
