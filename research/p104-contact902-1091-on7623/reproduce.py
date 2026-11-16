#!/usr/bin/env python3
"""Materialize frozen offline closure; --run explicitly starts fresh qualification."""
import argparse
import hashlib
import json
import runpy
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,obj):p.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n',encoding='utf-8')
def safe_rel(s):
    p=Path(s);need(not p.is_absolute() and '..' not in p.parts,'unsafe export mapping path');return p


def materialize(work):
    work=Path(work).resolve();need(not work.exists(),'work must not exist')
    integrity=HERE/'INTEGRITY.py'
    need(integrity.is_file() and not integrity.is_symlink(),'missing package integrity verifier')
    verifier=runpy.run_path(str(integrity));need(callable(verifier.get('verify')),'invalid integrity verifier')
    need(verifier['verify'](HERE) is not False,'package integrity verification failed')
    export=read(HERE/'EXPORT-MAP.json');need(export['schema']=='contact7623-offline-export/v1','export schema')
    need(sha((HERE/'reproduce.py').read_bytes())==export['reproducer_sha256'],'reproducer hash')
    freeze_bytes=(HERE/'evidence/ORIGINAL-FREEZE.json').read_bytes();plan_bytes=(HERE/'evidence/ORIGINAL-PLAN.json').read_bytes()
    need(sha(freeze_bytes)==export['freeze_sha256'] and sha(plan_bytes)==export['original_plan_sha256'],'original metadata hashes')
    freeze=json.loads(freeze_bytes);plan=json.loads(plan_bytes)
    entries=export['files'];need(len(freeze['files'])==export['frozen_file_count']==321,'frozen denominator')
    frozen=[r for r in entries if r['origin']=='frozen_input']
    need(len(frozen)==321 and len({r['original_path'] for r in frozen})==321,'frozen mapping denominator')
    source_map={r['original_path']:r for r in frozen}
    need(set(source_map)=={r['path'] for r in freeze['files']},'original freeze file identity')
    all_paths=set()
    for entry in entries:
        rel=safe_rel(entry['package_path']);need(str(rel) not in all_paths,'duplicate export path');all_paths.add(str(rel))
        p=HERE/rel;need(p.is_file() and not p.is_symlink(),'missing export file '+str(rel))
        b=p.read_bytes();need(sha(b)==entry['sha256'] and blob(b)==entry['git_blob'] and len(b)==entry['bytes'],'export hash mismatch '+str(rel))
    for item in freeze['files']:
        r=source_map[item['path']]
        need(r['sha256']==item['sha256'] and r['bytes']==item['bytes'],'source freeze mismatch')
        need(Path(r['package_path']).parts[0]=='replay','frozen input outside replay')
    work.mkdir(parents=True)
    old_to_new={}
    for r in frozen:
        rel=safe_rel(r['package_path']);dest=work/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes((HERE/rel).read_bytes());old_to_new[r['original_path']]=str(dest)
    old_package=Path(plan['package']);need(str(old_package/'PLAN.json') in old_to_new,'missing frozen original plan')
    new_package=Path(old_to_new[str(old_package/'PLAN.json')]).parent
    old_round=old_package.parent;new_round=new_package.parent
    prior_rounds=('kappa-research-20261115','kappa-research-20261115b')
    def rebase(value):
        for old,new in [(str(old_round),str(new_round))]+[(str(old_round.parent/x),str(new_round.parent/x)) for x in prior_rounds]:
            if value==old:return new
            if value.startswith(old+'/'):return new+value[len(old):]
        need(not value.startswith('/'),'unrecognized absolute stage path '+value)
        return value
    plan['package']=str(new_package)
    plan['required_frozen']=[old_to_new[p] for p in plan['required_frozen']]
    for stage in plan['stages']:stage['argv']=[rebase(x) for x in stage['argv']]
    plan_path=new_package/'PLAN.json';write(plan_path,plan)
    rebased=[]
    for item in freeze['files']:
        old=item['path'];dest=Path(old_to_new[old]);raw=dest.read_bytes()
        if dest!=plan_path:need(sha(raw)==item['sha256'],'non-plan input changed during rebase')
        rebased.append({**item,'path':str(dest),'sha256':sha(raw),'bytes':len(raw)})
    fresh_freeze={**freeze,'files':rebased};freeze_path=new_package/'FREEZE.json';write(freeze_path,fresh_freeze)
    receipt={'status':'MATERIALIZED_NOT_EXECUTED','candidate_canonical_sha256':export['candidate_canonical_sha256'],
             'original_freeze_sha256':export['freeze_sha256'],'original_plan_sha256':export['original_plan_sha256'],
             'rebased_plan_sha256':sha(plan_path.read_bytes()),'rebased_freeze_sha256':sha(freeze_path.read_bytes()),
             'package':str(new_package),'first_gate':'copied committed immutable evidence; not rerun',
             'scope':'Requires Linux systemd user services and cgroup controls. First-gate evidence is retained, not a cold rerun. Fresh qualification is conditional on common U; supplier implementation and same-premise dominance remain separate.'}
    write(work/'REBASE.json',receipt);return receipt


def main():
    p=argparse.ArgumentParser();p.add_argument('--work',required=True,type=Path);p.add_argument('--run',action='store_true');a=p.parse_args()
    receipt=materialize(a.work)
    if a.run:
        work=a.work.resolve();package=Path(receipt['package']);cmd=[sys.executable,'-I','-B',str(package/'launch.py'),
            '--control',str(work/'control'),'--out',str(work/'execution'),'--freeze-sha',receipt['rebased_freeze_sha256']]
        print(json.dumps({'status':'EXPLICIT_FRESH_QUALIFICATION_LAUNCH','argv':cmd},sort_keys=True),flush=True)
        result=subprocess.run(cmd,check=False)
        if result.returncode:raise SystemExit(result.returncode)
    else:print(json.dumps(receipt,sort_keys=True),flush=True)
if __name__=='__main__':main()
