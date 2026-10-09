#!/usr/bin/env python3
"""Joint complex side kernel: exact scoped obstruction and expensive repair."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

from binary_phase_frames import contains
from certify import require,verify_sources
from experiments.parity_side import ParitySide
from experiments.parity_phase_repair import coarsen,five_point_obstruction
from prepare_layers import serializable

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    rows=[]
    for h in (8,10,26):
        c=ParitySide(h);raw=c.verify();repair=coarsen(c)
        require(raw['local_obstructions']>0,'The declared scalar topology lacks an obstruction')
        rows.append(dict(raw=raw,repair=repair,
            dag_sha256=sha256(json.dumps(dict(args=c.args,outputs=c.outputs),
                              sort_keys=True,separators=(',',':')).encode()).hexdigest()))
        print('Checked parity side:',h,raw['roles'],repair['repaired_roles'],flush=True)
    require(rows[-1]['raw']['roles']==82720 and rows[-1]['repair']['repaired_roles']==308336,
            'Specified construction counts changed')
    witness=rows[-1]['raw']['first_obstruction']
    a,b,c,d,e=(1<<i for i in range(21,26))
    source=(a|c|e,b|d|e);target=(a|b|e,c|d|e)
    require(all(contains(witness['S'],x) for x in source) and
            all(contains(witness['T'],x) for x in target),'Five-point witness not present')
    require(82720<89622<308336,'Scalar gain/repair loss comparison failed')
    sources=('scripts/audit_parity_side.py','scripts/experiments/parity_side.py',
             'scripts/experiments/parity_phase_repair.py','scripts/binary_phase_frames.py',
             'scripts/experiments/mixed_point_circuit.py','scripts/experiments/disjoint_tensor.py',
             'docs/research/parity-side.md')
    return dict(status='SPECIFIED SCALAR GAIN FAILS FRAME CONTRACT; SPECIFIED REPAIR TOO EXPENSIVE',
        upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),
        five_point_obstruction=five_point_obstruction(),experiments=rows,
        retained_complex_side_roles=89622,
        scope='Exact specified DAGs and their deterministic source-span coarsenings only. No lower bound on all parity circuits, all repairs, or arbitrary phase interfaces.',
        source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/parity-side.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS scoped parity-side obstruction and exact repair cost; no new kappa.')
