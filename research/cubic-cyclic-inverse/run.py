"""Run the complete scoped package and bind its deterministic evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

P = Path(__file__).resolve().parent


def need(ok, message):
    if not ok: raise ValueError(message)


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def source_check():
    manifest = json.loads((P/'MANIFEST.json').read_text())
    required = {'PROOF.md','COMPOSITION-PROOF.md','README.md','NOTICE.md','SOURCE.json',
                'EXPECTED.json','budget.py','source_scan.py','dense.py','verify.py',
                'composition.py','check_composition.py','run.py'}
    required.update(json.loads((P/'SOURCE.json').read_text())['files'])
    need(set(manifest) == required, 'required source inventory')
    for path, digest in manifest.items():
        need((P/path).is_file() and sha(P/path) == digest, 'source hash: '+path)
    return sha(P/'MANIFEST.json')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    out=args.out.resolve()
    need(not out.is_relative_to(P),'output must be outside source package')
    manifest=source_check()
    out.mkdir(parents=True,exist_ok=False)
    stages=[]
    optimize=['-O'] if sys.flags.optimize else []
    for name,script in (('kernel','verify.py'),('composition','check_composition.py')):
        argv=[sys.executable,'-I','-B',*optimize,str(P/script),'--out',str(out/name)]
        start=time.perf_counter_ns()
        with (out/(name+'.log')).open('w') as log:
            result=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,check=False)
        record=dict(name=name,script=script,exit_code=result.returncode,
                    elapsed_ms=(time.perf_counter_ns()-start)//1000000,
                    log_sha256=sha(out/(name+'.log')))
        stages.append(record)
        (out/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n')
        need(result.returncode == 0,'stage failed: '+name)
        print('PASS',name,flush=True)
    expected=json.loads((P/'EXPECTED.json').read_text())
    artifacts={path:sha(out/path) for path in expected['artifacts']}
    need(artifacts == expected['artifacts'],'mathematical artifact mismatch')
    need(source_check() == manifest,'source changed during execution')
    receipt=dict(status='passed',scope='cubic cyclic inverse and coarse-grid composition; no new kappa',
                 manifest_sha256=manifest,expected_sha256=sha(P/'EXPECTED.json'),
                 python=sys.version,platform=platform.platform(),optimized=bool(sys.flags.optimize),
                 stages=stages,artifacts=artifacts)
    (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS_CUBIC_CYCLIC_INVERSE budgets=5220 kernels=120 prefix_dense=60 composition=20 composition_dense=12 controls=10')


if __name__=='__main__': main()
