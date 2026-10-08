#!/usr/bin/env python3
"""Rebuild the attributed h32 producer and check every selected star circuit."""
from hashlib import sha256
from pathlib import Path
import argparse,importlib.util,json,struct,subprocess,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

def run(reuse=False):
    geometric=ROOT/'research/geometric-dimensions';build=ROOT/'build/geometric-dimensions';build.mkdir(parents=True,exist_ok=True)
    if not reuse:
        subprocess.run(['c++','-std=c++17','-O3',str(geometric/'supports.cpp'),'-o',str(build/'check')],check=True)
        subprocess.run([sys.executable,str(geometric/'explore.py'),'32'],check=True)
    screen=json.loads((build/'32/result.json').read_text())
    assert screen['h']==32 and screen['checked']['role_upper_bound']==25224960
    reference=ROOT/'research/prime-field-followup';sys.path[:0]=[str(reference),str(reference/'vendor'),str(ROOT/'scripts')]
    controls=module('h32_star_controls',reference/'verify.py');controls.provenance()
    data=(build/'32/templates.bin').read_bytes();words=iter(struct.unpack('<'+'I'*(len(data)//4),data));assert next(words)==32
    size=next(words);records=[]
    for _ in range(size):
        outputs,gates=next(words),next(words);targets=[next(words) for _ in range(outputs)];pairs=[(next(words),next(words)) for _ in range(gates)]
        controls.check(targets,pairs);records.append(controls.reversible_control(targets,pairs))
    assert next(words,None) is None
    assert size==screen['checked']['verified_templates']==561
    result=dict(status='FULL H32 PRODUCER AND ALL TEMPLATE CONTROLS PASS',producer=screen,
        template_controls=dict(templates=size,basis_directions_per_orientation=sum(x['basis_directions_per_orientation'] for x in records),
          every_dirty_scratch_and_role_support_check_passed=True,records=records,template_binary_sha256=sha256(data).hexdigest()),
        provenance=dict(PR7='6725c6a17b17871a35353fd29157f4ed851bc114',PR12='35d31e30f28bc5da0ae6a88e7b03d75ebc855534',
          attribution='Zhihao Chen ternary producer; Rohan Arun dimension checker and selected star refinements'),
        source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in [
          'research/geometric-dimensions/supports.cpp','research/geometric-dimensions/explore.py',
          'research/prime-field-followup/star_duality.py','research/prime-field-followup/verify.py']})
    (HERE/'producer-certificate.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS h32 producer,',size,'templates,',result['template_controls']['basis_directions_per_orientation'],'basis directions per orientation')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reuse-screen',action='store_true');args=p.parse_args();run(args.reuse_screen)
