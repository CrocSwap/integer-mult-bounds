#!/usr/bin/env python3
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

from certify import require,verify_sources
from prepare_layers import serializable
from experiments.affine_vector_screens import leech_minor,polynomial_code_witness

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    data=json.loads((ROOT/'scripts/experiments/affine_vector_witnesses.json').read_text())
    lattice=[leech_minor(**f) for f in data['leech']]
    codes=[polynomial_code_witness(**f) for f in data['cubic_codes']]
    require(all(r['positive_deficit_excluded'] for r in lattice+codes),'A candidate survived')
    sources=('scripts/audit_affine_vectors.py','scripts/experiments/affine_vector_screens.py',
             'scripts/experiments/affine_vector_witnesses.json','scripts/experiments/cube_core_family.py',
             'scripts/experiments/single_intersection.py','docs/research/affine-vector-screens.md')
    return dict(status='NINE SPECIFIED CENTRAL MATRICES REJECTED; NO NEW KAPPA',
                upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),
                lattice_vector_screens=lattice,polynomial_code_screens=codes,
                scope='Only I plus each full stated zero relation. Other supported binary matrices and subfamilies remain untested.',
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/affine-vector-screens.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS nine exact affine/vector-code rank rejections; no full large matrix expanded.')
