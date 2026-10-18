#!/usr/bin/env python3
"""Reproduce both receipts and adversarial packaging controls, stdlib only.

Philipp / mightyOil with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def require(ok,message):
    if not ok:
        raise ValueError(message)


def run(script,*args,optimized=False,success=True):
    cmd=[sys.executable,'-I','-S','-B']+(['-O'] if optimized else [])+[str(script),*map(str,args)]
    p=subprocess.run(cmd,capture_output=True,text=True)
    require((p.returncode==0)==success,'unexpected subprocess result: '+str(cmd)+'\n'+p.stdout+p.stderr)
    return p


def main():
    before={p:sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}
    main_result=run(HERE/'verify.py','--with-predecessors')
    require('PASS_P112_COMPLEX_SINGLE_LIFT:' in main_result.stdout,'missing inherited replay')
    require('PASS_P112_SINGLE_LIFT_INDEPENDENT:' in main_result.stdout,'missing inherited independent replay')
    run(HERE/'verify.py',optimized=True)
    independent=run(HERE/'independent_check.py',optimized=True)
    require(json.loads(independent.stdout)==json.loads((HERE/'INDEPENDENT.json').read_text()),'independent receipt mismatch')
    checks=[]
    with tempfile.TemporaryDirectory(prefix='p112 two total ') as scratch:
        temp=Path(scratch)
        expected=json.loads((HERE/'CERTIFICATE.json').read_text())
        mutants=[]
        for key,value in [('examples',expected['examples'][:-1]),('assignment_seed',22),('no_new_kappa',False)]:
            m=dict(expected);m[key]=value;mutants.append((key,m))
        m=json.loads(json.dumps(expected));m['examples'][2]['quotient_rank']=0;mutants.append(('quotient_rank',m))
        for name,mutant in mutants:
            target=temp/(name+'.json');target.write_text(json.dumps(mutant))
            p=run(HERE/'verify.py','--check',target,success=False)
            require('certificate mismatch' in p.stderr,'wrong failure for '+name)
            checks.append('reject_receipt_'+name)
        output=temp/'existing.json';output.write_text('preserve me\n')
        run(HERE/'verify.py','--write',output,success=False)
        require(output.read_text()=='preserve me\n','output clobbered')
        checks.append('preserve_existing_output')
        regenerated=temp/'regenerated.json';run(HERE/'verify.py','--write',regenerated)
        require(regenerated.read_bytes()==(HERE/'CERTIFICATE.json').read_bytes(),'nondeterministic regeneration')
        checks.append('byte_identical_regeneration')
        relocated=temp/'isolated source tree'
        for directory in ('p112-single-lift','p112-complex-single-lift','p112-two-total-rank-one-seed21'):
            shutil.copytree(ROOT/'research'/directory,relocated/'research'/directory,
                            ignore=shutil.ignore_patterns('__pycache__'))
        copied=relocated/'research'/HERE.name
        run(copied/'verify.py',optimized=True)
        p=run(copied/'independent_check.py',optimized=True)
        require(json.loads(p.stdout)==json.loads((HERE/'INDEPENDENT.json').read_text()),'relocated independent result')
        checks.append('minimal_offline_relocation_with_spaces')
        source=relocated/'research/p112-single-lift/geometry.py'
        source.write_bytes(source.read_bytes()+b'\n# source mutation\n')
        p=run(copied/'verify.py',success=False)
        require('source hash:' in p.stderr,'source mutation not rejected at admission')
        checks.append('reject_source_drift_before_import')
    require(all(sha256(p.read_bytes()).hexdigest()==digest for p,digest in before.items()),'default checks modified package')
    print(main_result.stdout.strip())
    print('PASS_P112_TWO_TOTAL_PACKAGE controls='+str(len(checks))+' identities='+str(json.loads(independent.stdout)['full_matrix_identities']))
    print(json.dumps({'packaging_controls':checks},sort_keys=True))


if __name__=='__main__':
    main()
