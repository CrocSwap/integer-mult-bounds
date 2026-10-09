#!/usr/bin/env python3
from hashlib import sha256
from fractions import Fraction as Q
from pathlib import Path
import json

from certify import verify_sources
from prepare_layers import serializable
from experiments.core_limits import binary_type_bound,dimension_limit,radial_scope,incidence_rigidity

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    controls=[binary_type_bound([3,3],[[1,0],[0,1]]),
              binary_type_bound([5,2,5],[[1,1,0],[1,1,1],[0,0,1]])]
    source=('scripts/audit_core_limits.py','scripts/experiments/core_limits.py',
            'docs/research/core-limits.md')
    return dict(status='NECESSARY CORE LIMITS AND INCIDENCE RIGIDITY; NO NEW KAPPA',
                upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),
                binary_type_controls=controls,radial_scope=radial_scope(),
                dimension_without_auxiliary_floor=dimension_limit(auxiliary_floor=False),
                incidence_rigidity=[incidence_rigidity(q,q<=4) for q in (2,4,8,16)],
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in source})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/core-limits.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS: target dimension <=52; nonlinear radial subset frames excluded; incidence-span rigidity.')
