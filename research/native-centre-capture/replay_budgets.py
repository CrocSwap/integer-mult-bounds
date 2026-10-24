#!/usr/bin/env python3
"""Replay the three historical conditional budget reviews."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent

def need(test, reason):
    if not test:
        raise ValueError(reason)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--optimized',action='store_true')
    args=parser.parse_args()
    out=args.out.resolve()
    need(not out.exists(),'The output directory must be absent.')
    manifest=json.loads((ROOT/'SOURCE-MANIFEST.json').read_text())
    for row in manifest['files']:
        need(digest((ROOT/row['path']).read_bytes())==row['sha256'],'Source pin: '+row['path'])
    need(shutil.disk_usage(ROOT).free>=3*1024**3,'Keep at least 3 GiB free.')
    out.mkdir(parents=True)
    shutil.copytree(ROOT/'frozen',out/'campaign')
    shutil.copytree(ROOT/'historical',out/'historical')
    lane=out/'campaign/lanes/bridge-review-20261017'
    adaptations=json.loads((ROOT/'adapters/ADAPTATIONS.json').read_text())
    for row in adaptations['files']:
        need(digest((ROOT/row['original']).read_bytes())==row['original_sha256'],'Original checker pin')
        need(digest((ROOT/row['adapter']).read_bytes())==row['adapter_sha256'],'Adapter pin')
        name=Path(row['original']).parent.name
        shutil.copyfile(ROOT/row['adapter'],lane/name/'portable_check_review.py')
    jobs=[
        ('low-displacement','low-displacement-budget-review-20261020','portable_check_review.py',[str(out/'low-displacement.json')],'REVIEW.json',out/'low-displacement.json','PASS 176 exact profile intervals; 24 literal words; 16 unchanged scalar sequences'),
        ('clean-exchange','clean-exchange-budget-review-20261020','portable_check_review.py',['--output',str(out/'clean-exchange')],'normal/REVIEW-CHECKS.json',out/'clean-exchange/REVIEW-CHECKS.json','PASS_INDEPENDENT_CLEAN_EXCHANGE_BUDGET'),
        ('coalesced','coalesced-budget-review-20261020','check_budget.py',[str(out/'coalesced.json')],'normal.json',out/'coalesced.json','PASS_THIRD_ENGINE_COALESCED_BUDGET')]
    results=[]
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    for name,directory,script,arguments,expected,receipt,status in jobs:
        command=[sys.executable,'-I','-B']+(['-O'] if args.optimized else [])+[str(lane/directory/script)]+arguments
        start=time.monotonic()
        run=subprocess.run(command,cwd=out,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/(name+'.log')).write_text(run.stdout)
        need(run.returncode==0,name+' failed; see '+str(out/(name+'.log')))
        need(status in run.stdout,name+' status differs')
        actual=json.loads(receipt.read_text())
        original=json.loads((ROOT/'frozen/lanes/bridge-review-20261017'/directory/expected).read_text())
        if script=='portable_check_review.py':
            need(actual['checker_sha256']==digest((lane/directory/script).read_bytes()),'Actual adapter checksum')
            actual['checker_sha256']=original['checker_sha256']
        need(actual==original,name+' mathematical receipt differs')
        results.append(dict(stage=name,status=status,receipt_sha256=digest(receipt.read_bytes()),seconds=round(time.monotonic()-start,3),comparison='All fields match; only the two adapter self-hashes differ.'))
        print(name+': PASS; historical mathematical receipt matches',flush=True)
    report=dict(status='PASS_NATIVE_CAPTURE_HISTORICAL_BUDGETS',optimized=args.optimized,source_manifest_sha256=digest((ROOT/'SOURCE-MANIFEST.json').read_bytes()),stages=results)
    (out/'REPLAY.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(report['status'])

if __name__=='__main__':
    main()
