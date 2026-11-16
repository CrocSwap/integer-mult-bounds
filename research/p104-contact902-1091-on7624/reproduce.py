#!/usr/bin/env python3
"""Materialize frozen offline closure with a path-adapted runtime copy."""
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

def adapt_runtime(application, old_to_new, nested_freeze, retained, work):
    """Patch only two counted metadata path constructions in a disposable clone."""
    work=Path(work).resolve();application=Path(application)
    need(len(old_to_new)==502 and all(Path(k).is_absolute() for k in old_to_new),'closed 502-path source mapping')
    need(len(set(old_to_new.values()))==502,'duplicate runtime mapping target')
    for old,new in old_to_new.items():
        target=Path(new);need(target.is_absolute() and target.is_relative_to(work) and target.is_file() and not target.is_symlink(),'unsafe or missing runtime target '+old)
    nested=read(nested_freeze); retained_obj=read(retained)
    groups=[('completion_freeze',nested['files'],104),('retained_evidence',retained_obj['evidence'],14)]
    counts={}
    for label,rows,count in groups:
        need(len(rows)==count and len({r['path'] for r in rows})==count,'nested source denominator '+label)
        for row in rows:
            need(row['path'] in old_to_new,'nested mapping missing '+row['path'])
            target=Path(old_to_new[row['path']]);need(sha(target.read_bytes())==row['sha256'],'nested target bytes '+row['path'])
        counts[label]=count
    original=application.read_bytes();text=original.decode('utf-8')
    anchor='HERE = Path(__file__).resolve().parent\n'
    substitutions=[("p=Path(row['path']); need(p.is_file()", "p=_relocated_path(row['path']); need(p.is_file()"),
                   ("original=Path(item['path']); need(original.is_file()", "original=_relocated_path(item['path']); need(original.is_file()"),
                   ("    shim=root/'inputs/pr7624/research/p104-w2-primal-dual-bypass/windows_path_shim.py'", "    shim_source=root/'inputs/pr7624/research/p104-w2-primal-dual-bypass/windows_path_shim.py'\n    need(shim_source.is_file() and not shim_source.is_symlink() and sha(shim_source)=='918d245bd2a398dde8b3ef923aa17dc160bbe7cf645e0ec28d876d0a341ab620','pinned shim bytes')\n    shim=work/'isolated/windows_path_shim.py'\n    need(shim.parent.is_dir() and not shim.parent.is_symlink(),'isolated shim directory')\n    if shim.exists() or shim.is_symlink():\n        need(shim.is_file() and not shim.is_symlink() and sha(shim)==sha(shim_source),'existing isolated shim differs')\n    else:\n        with shim.open('xb') as stream: stream.write(shim_source.read_bytes())\n        need(sha(shim)==sha(shim_source),'copied isolated shim differs')")]
    need(text.count(anchor)==1,'runtime insertion anchor count')
    for old,new in substitutions:
        need(text.count(old)==1,'runtime source path anchor count '+old);text=text.replace(old,new,1)
    mapping=dict(sorted(old_to_new.items()))
    inline="\n# Materialization-only closed relocation of pinned evidence paths.\n_RELOCATION_MAP = "+repr(mapping)+"\ndef _relocated_path(value):\n    if type(value) is not str or value not in _RELOCATION_MAP:\n        raise ValueError('unmapped frozen evidence path')\n    return Path(_RELOCATION_MAP[value])\n"
    text=text.replace(anchor,anchor+inline,1);patched=text.encode('utf-8');compile(patched,str(application),'exec')
    application.write_bytes(patched)
    return {'kind':'counted_runtime_path_relocation_and_isolated_shim','source_sha256':sha(original),'runtime_sha256':sha(patched),'mapping_sha256':sha(json.dumps(mapping,sort_keys=True,separators=(',',':')).encode()),'mapping_count':len(mapping),'nested_targets_checked':counts,'edits':[{'site':'gate_control Path(row[path])','count':1},{'site':'gate_values Path(item[path])','count':1},{'site':'closed resolver insertion','count':1},{'site':'byte-pinned shim selection copied into isolated work','count':1}], 'shim_sha256':'918d245bd2a398dde8b3ef923aa17dc160bbe7cf645e0ec28d876d0a341ab620','immutable_nested_json_unchanged':True}


def materialize(work):
    work=Path(work).resolve();need(not work.exists(),'work must not exist')
    integrity=HERE/'INTEGRITY.py'
    need(integrity.is_file() and not integrity.is_symlink(),'missing package integrity verifier')
    verifier=runpy.run_path(str(integrity));need(callable(verifier.get('verify')),'invalid integrity verifier')
    need(verifier['verify'](HERE) is not False,'package integrity verification failed')
    export=read(HERE/'EXPORT-MAP.json');need(export['schema']=='contact7624-offline-export/v1','export schema')
    need(sha((HERE/'reproduce.py').read_bytes())==export['reproducer_sha256'],'reproducer hash')
    freeze_bytes=(HERE/'evidence/ORIGINAL-FULL-FREEZE.json').read_bytes();plan_bytes=(HERE/'evidence/ORIGINAL-FULL-PLAN.json').read_bytes()
    need(sha(freeze_bytes)==export['original_full_freeze_sha256'] and sha(plan_bytes)==export['original_full_plan_sha256'],'original metadata hashes')
    freeze=json.loads(freeze_bytes);plan=json.loads(plan_bytes)
    entries=export['files'];need(len(freeze['files'])==300 and export['frozen_file_count']==502,'frozen denominator')
    frozen=[r for r in entries if r['origin']=='frozen_input']
    need(len(frozen)==502 and len({r['original_path'] for r in frozen})==502,'frozen mapping denominator')
    source_map={r['original_path']:r for r in frozen}
    need({r['path'] for r in freeze['files']} <= set(source_map),'original freeze file identity')
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
    app_old=str(old_package/'application.py');need(app_old in old_to_new and app_old in plan['required_frozen'],'runtime application closure')
    app=Path(old_to_new[app_old]);need(sha(app.read_bytes())==source_map[app_old]['sha256'],'original application bytes')
    nested_old=str(old_round/'compose7624_completion/FREEZE.json');retained_old=str(old_round/'compose7624_completion/run/case/RETAINED-PASSED.json')
    need(nested_old in old_to_new and retained_old in old_to_new,'nested receipt closure')
    patch=adapt_runtime(app,old_to_new,Path(old_to_new[nested_old]),Path(old_to_new[retained_old]),work)
    prior_rounds=('kappa-research-20261115','kappa-research-20261115b','kappa-research-20261116')
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
        if dest not in (plan_path,app):need(sha(raw)==item['sha256'],'non-plan/non-runtime-app input changed during rebase')
        rebased.append({**item,'path':str(dest),'sha256':sha(raw),'bytes':len(raw)})
    fresh_freeze={**freeze,'files':rebased};freeze_path=new_package/'FREEZE.json';write(freeze_path,fresh_freeze)
    receipt={'status':'MATERIALIZED_NOT_EXECUTED','candidate_canonical_sha256':export['candidate_canonical_sha256'],
             'original_freeze_sha256':export['original_full_freeze_sha256'],'original_plan_sha256':export['original_full_plan_sha256'],
             'rebased_plan_sha256':sha(plan_path.read_bytes()),'rebased_freeze_sha256':sha(freeze_path.read_bytes()),
             'package':str(new_package),'application_portability_patch':patch,'first_gate':'copied committed immutable evidence; not rerun',
             'scope':'Requires Linux systemd user services and cgroup controls. Optional future fresh six-stage qualification uses a counted path-adapted operational copy and isolated byte-pinned shim, not unchanged original 300 source bytes; first-gate evidence is retained and not cold-rerun. Conditional common U remains unimplemented.'}
    write(work/'MATERIALIZED.json',receipt);return receipt


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
