#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the pinned PR3133 recipe with the new exact T740 cap allocation.

New allocation and integration by Jeremy Diviney with substantial OpenAI Codex assistance.
Recipe, native/admission machinery and all mathematical checks are retained
unchanged from dcharb78, Marius-Paul Dumitrean, Jeremy Kothe, Mason Hale,
Nick Petalas and the credited predecessor chain. This follows PR3030's
three-argument composition mechanism; it does not replace source validators.
"""
import argparse
import hashlib
import gzip
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from fractions import Fraction as Q

SOURCE_MANIFEST='609209f577c9185b16825dd2e8bb30f0891205fddd2571a8f76c558e3cb1f70e'
EDIT_SOURCE='fa3e2d855ac5298ecc849e596d79dcef7a72668a276b6524585bc0cd616ce474'
PROFILE={1:16376940,2:4821840,3:1567431,4:679320,5:147075,8:53280,48:282569}
LOCAL={1:2433,2:724,3:228,4:102,5:20,8:8}
ALLOCATION={
 'COMPOSED-FILL.json.gz':'198765c74edb5494ef94c9aff958ab99d84eace5b77fafb7dd23d4e18d82aefa',
 'ORDER.json':'927226d702bf3cada076f4c459da9063c0df7e7154a62955cf75c40cf30215b9',
 'DISPATCH.json':'90edc935320dd6264e98dc735d868df3c95f5901c70d7d96171001fcb295cce0',
}
FILL_PAYLOAD='8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00'
STAGES=['export-pr2894','export-pr2833','four-kernel-stage','preload-stage',
        'parent-paired-stage','paired-extension-stage','rank7-overlay-stage',
        'declared-edit-stage','derive-closed-adapters','fresh-current-native','complete-admission']

def need(ok,why):
    if not ok:raise ValueError(why)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,value):p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def authenticate(source):
    need(sha(source/'MANIFEST.json')==SOURCE_MANIFEST,'exact PR3133 manifest')
    paths=list(source.rglob('*'))
    need(not any(p.is_symlink() for p in paths),'regular source files')
    # Only the package-root manifest is excluded; nested manifests are inputs.
    actual={p.relative_to(source).as_posix():sha(p) for p in paths if p.is_file() and p!=source/'MANIFEST.json'}
    need(actual==read(source/'MANIFEST.json'),'complete source inventory')

def allocation_binding(allocation):
    """Regenerated gzip containers may vary; the complete payload must not."""
    payload=hashlib.sha256()
    with gzip.open(allocation/'COMPOSED-FILL.json.gz','rb') as stream:
        while chunk:=stream.read(1024*1024):payload.update(chunk)
    need(payload.hexdigest()==FILL_PAYLOAD,'exact materialized fill payload')
    for name in ['ORDER.json','DISPATCH.json']:need(sha(allocation/name)==ALLOCATION[name],'pinned allocation '+name)
    return dict(fill_sha256=sha(allocation/'COMPOSED-FILL.json.gz'),fill_payload_sha256=payload.hexdigest(),
                order_sha256=sha(allocation/'ORDER.json'),dispatch_sha256=sha(allocation/'DISPATCH.json'))

def adapt(recipe,source,allocation):
    recipe=json.loads(json.dumps(recipe));names=[n for n,_ in recipe]
    need(names==STAGES or names==STAGES[:2]+['fresh-retained-bootstrap']+STAGES[2:],'complete source recipe')
    changes=[]
    for name,cmd in recipe:
        if name=='complete-admission':
            for flag,old,new in [('--fill','FILL.json.gz','COMPOSED-FILL.json.gz'),('--order','ORDER.json','ORDER.json'),('--dispatch','DISPATCH.json','DISPATCH.json')]:
                need(cmd.count(flag)==1,'unique allocation flag')
                i=cmd.index(flag)+1
                need(cmd[i]==str(source/'allocation'/old),'allocation preimage')
                changes.append(dict(stage=name,flag=flag,old=cmd[i],new=str(allocation/new)));cmd[i]=str(allocation/new)
    need(len(changes)==3,'exactly three argument changes')
    return recipe,changes

def validate(run,source,allocation):
    candidate=run/'candidate';a=read(candidate/'RESULT.json');r=read(candidate/'release/RELEASE-RECEIPT.json')
    need(a['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','complete admission')
    need(r['status']=='PASS_RELEASE','complete outer release')
    need({int(k):v for k,v in a['profile'].items()}==PROFILE,'exact composed paid profile')
    for key,name in [('fill_sha256','COMPOSED-FILL.json.gz'),('order_sha256','ORDER.json'),('dispatch_sha256','DISPATCH.json')]:
        need(a[key]==sha(allocation/name),'admitted allocation binding '+name)
    need(a['source_manifest_sha256']==EDIT_SOURCE,'unchanged coupled-carrier source')
    need(a['native_receipt_sha256']==sha(run/'native/NATIVE-RECEIPT.json'),'fresh native receipt')
    need(a['release_receipt_sha256']==sha(candidate/'release/RELEASE-RECEIPT.json'),'release receipt binding')
    need(a['package_manifest_sha256']==r['manifest_sha256'],'same admitted/released package')
    need(Q(a['kappa'])==Q(r['kappa_decimal']),'same released endpoint')
    baseline=Q(read(Path(__file__).resolve().parent/'BASELINE-PR3143.json')['kappa'])
    need(Q(a['kappa'])>baseline,'strict improvement over PR3143')
    need(sha(run/'source-edits/MANIFEST.json')==EDIT_SOURCE,'derived literal source binding')
    return dict(status='PASS_COUPLED_CARRIER_T740_COMPLETE_RELEASE',kappa=a['kappa'],kappa_decimal=a['kappa_decimal'],
                baseline_kappa=str(baseline),gain=str(Q(a['kappa'])-baseline),profile=PROFILE,
                source_manifest_sha256=EDIT_SOURCE,admission_sha256=sha(candidate/'RESULT.json'),
                release_receipt_sha256=sha(candidate/'release/RELEASE-RECEIPT.json'),
                native_receipt_sha256=sha(run/'native/NATIVE-RECEIPT.json'),
                scope='Conditional finite source/native/owner/outer release; inherited all-size, compiler, physical, precision and analytic obligations remain.')

def execute(run,source,allocation,output):
    need(__debug__,'inherited validators require assertions');need(not output.exists(),'fresh evidence directory')
    need(os.name=='posix','full replay process-group cleanup requires POSIX')
    authenticate(source)
    allocation_binding(allocation)
    recipe,changes=adapt(read(run/'PREFLIGHT.json')['commands'],source,allocation)
    output.mkdir(parents=True);save(output/'RECIPE.json',dict(commands=recipe,changes=changes))
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONINTMAXSTRDIGITS='0')
    for key in ['PYTHONPATH','PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER']:env.pop(key,None)
    stages=[]
    for name,cmd in recipe:
        path=output/(name+'.log');start=time.monotonic()
        with path.open('w') as log:
            proc=subprocess.Popen(cmd,cwd=run,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=proc.wait(timeout=3600)
            finally:
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
                try:os.killpg(proc.pid,signal.SIGKILL)
                except ProcessLookupError:pass
        stages.append(dict(stage=name,exit_code=code,seconds=time.monotonic()-start,log_sha256=sha(path)))
        save(output/'STAGES.json',stages);need(code==0,'failed '+name+'; see '+str(path));print('PASS',name,flush=True)
    result=validate(run,source,allocation);result['fresh_retained_bootstrap']=any(n=='fresh-retained-bootstrap' for n,_ in recipe)
    result['stages']=stages;save(output/'RESULT.json',result);print(result['status'],result['kappa_decimal'],flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['run','source','allocation','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();execute(a.run.resolve(),a.source.resolve(),a.allocation.resolve(),a.output.resolve())
