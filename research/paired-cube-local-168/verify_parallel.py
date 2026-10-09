#!/usr/bin/env python3
"""Run every native verify group in isolated copies of one frozen source tree.

Technique: PR154 by eumemic, pinned at
d67773363075cc787b6f6ffa07191475c7c3fbec (Apache-2.0).
Adaptation: Chafik Boukhalfa with OpenAI Codex assistance.

The strict recipe parser rejects unaccounted commands, and source manifests
are compared before/after snapshot creation and after all groups finish.
The new finite package is an additional group. No producer/check is omitted.
Unrelated PR154 source-pin and workflow policy changes are not adopted.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
GIT=['git','-c','core.autocrlf=false','-c','commit.gpgsign=false',
     '-c','user.name=isolated-verification','-c','user.email=verify@localhost']


def need(ok,message):
    if not ok:raise ValueError(message)


def git(*args,cwd=ROOT):
    return subprocess.check_output([*GIT,*args],cwd=cwd)


def dump(path,value):
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');temp.replace(path)


def native_groups():
    text=(ROOT/'Makefile').read_text();lines=text.splitlines();found=[];in_rule=False
    need(lines.count('verify:')==1,'exactly one native verify recipe is required')
    for line in lines:
        if line=='verify:':
            need(not in_rule and not found,'duplicate verify recipe');in_rule=True;continue
        if not in_rule:continue
        if line.startswith('\t'):
            match=re.fullmatch(r'\t\$\(MAKE\) (verify-[a-z0-9-]+)',line)
            need(match is not None,'unaccounted direct command in verify: '+line)
            found.append(match.group(1));continue
        if line.strip() and not line.startswith('#'):break
    need(found and len(set(found))==len(found),'nonempty unique native verify groups')
    need(len(found)==14,'review coverage before changing the native group count')
    return found


def source_names():
    names=git('ls-files','-z','--cached','--others','--exclude-standard').split(b'\0')
    return sorted({n.decode() for n in names if n and (ROOT/n.decode()).is_file()})


def manifest(root,names):
    result={}
    for name in names:
        path=root/name;need(path.is_file() and not path.is_symlink(),'regular source file required: '+name)
        data=path.read_bytes();result[name]=dict(bytes=len(data),sha256=sha256(data).hexdigest())
    return result


def main():
    pipeline_begin=time.monotonic()
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--jobs',type=int,default=8)
    ap.add_argument('--group-timeout',type=int,default=2400)
    args=ap.parse_args();need(1<=args.jobs<=8,'group workers must be in [1,8]')
    output=args.output.resolve();need(not output.exists(),'output directory must be new')
    output.mkdir(parents=True);(output/'logs').mkdir();(output/'trees').mkdir()
    groups=native_groups();names=source_names();before=manifest(ROOT,names)
    need(len(names)>1500,'incomplete source tree')
    template=output/'template';template.mkdir()
    for name in names:
        target=template/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    need(manifest(template,names)==before==manifest(ROOT,names),'source drift during snapshot')
    git('init','-q',cwd=template);git('add','-A',cwd=template)
    git('commit','-q','--no-verify','-m','Frozen complete verification input',cwd=template)
    commit=git('rev-parse','HEAD',cwd=template).decode().strip()
    need(not git('status','--porcelain',cwd=template),'snapshot must be clean')
    package=str(HERE.relative_to(ROOT)/'verify.py')
    commands={g:['make',g] for g in groups};commands['selected-finite-package']=[sys.executable,'-B',package]
    # Start historical finite searches and complete tests early; their slower
    # tail otherwise dominates the run. The coverage record keeps native order.
    priority=['verify-research','verify-tests','verify-joint','verify-producers',
        'verify-community','verify-clones','verify-strips','verify-pair']
    schedule=priority+[g for g in commands if g not in priority]
    need(len(schedule)==len(commands) and set(schedule)==set(commands),'schedule coverage')
    coverage=dict(technique_pr=154,technique_commit='d67773363075cc787b6f6ffa07191475c7c3fbec',
        makefile_sha256=before['Makefile']['sha256'],native_recipe=groups,native_group_count=len(groups),
        scheduled_commands=commands,execution_order=schedule,all_native_commands_covered=True,unaccounted_recipe_commands=0,
        snapshot_commit=commit,source_files=before,group_workers=args.jobs,nested_jobs=1)
    dump(output/'coverage.json',coverage)
    env={k:v for k,v in os.environ.items() if k not in ('MAKEFLAGS','MFLAGS','MAKELEVEL')}
    env.update(JOBS='1',MAKEFLAGS='-j1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
    setup_seconds=time.monotonic()-pipeline_begin;started=time.time();results={}
    def run(label,command):
        group_begin=time.monotonic()
        tree=output/'trees'/label;git('clone','-q',str(template),str(tree),cwd=output)
        need(git('rev-parse','HEAD',cwd=tree).decode().strip()==commit,'snapshot commit mismatch')
        need(manifest(tree,names)==before,'group input manifest mismatch')
        preparation_seconds=time.monotonic()-group_begin;begin=time.time();error=None;code=None
        log=output/'logs'/(label+'.log')
        with log.open('w') as stream:
            try:
                child=subprocess.Popen(command,cwd=tree,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
                code=child.wait(timeout=args.group_timeout)
            except subprocess.TimeoutExpired:
                error='group timeout';os.killpg(child.pid,signal.SIGTERM)
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
        changed=git('status','--porcelain','--untracked-files=no',cwd=tree).decode()
        try:unchanged=manifest(tree,names)==before
        except (OSError,ValueError):unchanged=False
        return label,dict(status='PASS' if code==0 and unchanged and not changed and not error else 'FAIL',
            command=command,exit_code=code,error=error,elapsed_seconds=round(time.time()-begin,3),
            clone_and_input_check_seconds=round(preparation_seconds,3),total_group_seconds=round(time.monotonic()-group_begin,3),
            input_snapshot=commit,all_input_bytes_unchanged=unchanged,tracked_changes=changed,
            log=str(log.relative_to(output)))
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        pending={pool.submit(run,label,commands[label]):label for label in schedule}
        for future in as_completed(pending):
            label=pending[future]
            try:label,result=future.result()
            except Exception as exc:result=dict(status='FAIL',error=repr(exc),input_snapshot=commit)
            results[label]=result;dump(output/'progress.json',dict(results=results,total=len(commands),snapshot_commit=commit))
            print('[%d/%d] %s %s'%(len(results),len(commands),result['status'],label),flush=True)
    after=manifest(ROOT,names)
    stable=after==before and source_names()==names
    complete=set(results)==set(commands)
    ok=stable and complete and all(r['status']=='PASS' for r in results.values())
    report=dict(status='PASS' if ok else 'FAIL',snapshot_commit=commit,
        source_stable_before_and_after=stable,all_scheduled_groups_completed=complete,
        coverage_sha256=sha256((output/'coverage.json').read_bytes()).hexdigest(),
        setup_seconds=round(setup_seconds,3),elapsed_seconds=round(time.time()-started,3),
        total_wall_seconds=round(time.monotonic()-pipeline_begin,3),results=results)
    dump(output/'result.json',report)
    print(report['status']+' complete isolated verification: '+str(len(results))+' groups',flush=True)
    if not ok:raise SystemExit(1)


if __name__=='__main__':main()
