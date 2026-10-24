#!/usr/bin/env python3
"""Regenerate the finite profile and independently audit its literal word."""
import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from math import comb
from pathlib import Path

if sys.flags.optimize:
    raise ValueError('optimized Python is forbidden')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def validate(p):
    h, v, m, R, N, W, L = (p[k] for k in ('h','v','m','R','N','W','L'))
    assert v == comb(h, 3) and m == h*h and N == v*v, 'dimensions'
    assert W == 2*N+2*v*R and L == 2*v*h*(h-1), 'physical ledger'
    z = {int(t):c for t,c in p['child_multiplicities'].items()}
    assert all(0<t<m and type(c) is int and c>0 for t,c in z.items()), 'child range'
    assert sum(t*c for t,c in z.items()) == p['total_rank'] == W*m-N+L, 'rank mass'
    assert p['maxchild'] == max(z) and p['deficit'] == N-L
    if 'links' in p:
        assert R == p['additions']+p['roots']-p['links'], 'role ledger'
        assert sum(p['deferred_dims'].values()) == p['deferred_roles']

def sources():
    manifest = json.loads((HERE/'SOURCE.json').read_text())
    for name, expected in manifest['sha256'].items():
        path = ROOT/name
        assert path.is_relative_to(ROOT) and '..' not in Path(name).parts
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'source drift: '+name

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--write-receipt', action='store_true')
    args=parser.parse_args()
    if (HERE/'SOURCE.json').exists(): sources()
    bit=json.loads((HERE/'bit-profile.json').read_text())
    phase=json.loads((HERE/'complex-profile.json').read_text())
    validate(bit);validate(phase)
    import bit_round7
    with tempfile.TemporaryDirectory() as directory:
        bit_round7.HERE=Path(directory)
        bit_round7.main(HERE/'inputs')
        assert json.loads((Path(directory)/'bit-profile.json').read_text()) == bit
    import certificate
    assert certificate.js(certificate.exact()) == json.loads((HERE/'certificate.json').read_text())
    print('PASS exact moments, next-grid rejections, 47 constraints and 7 margins', flush=True)
    from reflection_audit import capture, audit
    state=capture(HERE/'complex_deferred.py')
    assert json.loads(json.dumps(state['out'])) == phase, 'regenerated profile differs'
    print('PASS full compiler, arbitrary-scratch replay and exact binary frame chains', flush=True)
    result=audit(state)
    result['source_sha256']=hashlib.sha256((HERE/'complex_deferred.py').read_bytes()).hexdigest()
    receipt=HERE/'reflection-audit.json'
    if args.write_receipt:
        receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        assert json.loads(json.dumps(result)) == json.loads(receipt.read_text()), 'reflection receipt differs'
    if (HERE/'SOURCE.json').exists(): sources()
    print('PASS exact scalar map, dirty transpose, reflected incidences and complete child histogram', flush=True)

if __name__=='__main__': main()
