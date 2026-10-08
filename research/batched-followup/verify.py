"""Rebuild h30 and verify every selected template plus exact assembly."""
from hashlib import sha256
from pathlib import Path
from fractions import Fraction as Q
import argparse
import importlib.util
import json
import struct
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from witness import certificate, bit, assembly
from prepare_layers import serializable


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reuse-screen',action='store_true',help='Use an already regenerated full h30 screen')
    args=parser.parse_args()
    geometric=ROOT/'research/geometric-dimensions'
    build=ROOT/'build/geometric-dimensions'
    build.mkdir(parents=True,exist_ok=True)
    if not args.reuse_screen:
        subprocess.run(['c++','-std=c++17','-O3',str(geometric/'supports.cpp'),'-o',str(build/'check')],check=True)
        subprocess.run([sys.executable,str(geometric/'explore.py'),'30'],check=True)
    screen=json.loads((build/'30/result.json').read_text())
    assert screen['h']==30
    roles=screen['checked']['role_upper_bound']
    matching=module('geometric_matching',geometric/'matching.py').matching(30)
    reference=ROOT/'research/prime-field-followup'
    sys.path[:0]=[str(reference),str(reference/'vendor')]
    controls=module('star_controls',reference/'verify.py')
    controls.provenance()
    data=(build/'30/templates.bin').read_bytes()
    words=iter(struct.unpack('<'+'I'*(len(data)//4),data))
    assert next(words)==30
    size=next(words)
    records=[]
    for _ in range(size):
        outputs,gates=next(words),next(words)
        targets=[next(words) for _ in range(outputs)]
        pairs=[(next(words),next(words)) for _ in range(gates)]
        controls.check(targets,pairs)
        records.append(controls.reversible_control(targets,pairs))
    assert next(words,None) is None
    assert size==screen['checked']['verified_templates']
    result=certificate(roles)
    # Negative controls address exponent overclaims and producer inflation.
    for action in (lambda:bit(roles,Q(254,10**9)),
                   lambda:bit(roles+1000000),
                   lambda:assembly(result['assembly']['minimum_margin'])):
        try:action()
        except AssertionError:pass
        else:raise AssertionError('Negative control unexpectedly accepted')
    result['producer']=screen
    result['matching']=matching
    result['template_controls']=dict(templates=size,
        basis_directions_per_orientation=sum(x['basis_directions_per_orientation'] for x in records),
        every_dirty_scratch_and_role_support_check_passed=True,
        records=records,template_binary_sha256=sha256(data).hexdigest())
    names=['research/geometric-dimensions/supports.cpp','research/geometric-dimensions/explore.py',
           'research/geometric-dimensions/matching.py','research/prime-field-followup/star_duality.py',
           'research/prime-field-followup/verify.py','scripts/controlled_bit_rank_moment.py',
           'scripts/batched_bit_rank_moment.py','scripts/bulk_complex_guard.py',
           'scripts/batched_network.py','scripts/fast_gaussian.py','scripts/certify.py',
           'scripts/compact_control_layer.py','research/batched-followup/witness.py',
           'research/batched-followup/verify.py','research/batched-followup/proof.tex']
    result['source_sha256']={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
    (HERE/'certificate.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS full h30 screen,',size,'template circuits and all matching images')
    print('PASS exact conditional kappa:',result['assembly']['parameters']['kappa'])
    print('PASS negative exponent, inflated-producer and absorption-boundary controls')


if __name__=='__main__':main()
