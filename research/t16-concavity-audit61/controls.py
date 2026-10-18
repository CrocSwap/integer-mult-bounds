#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Semantic mutation controls and relocated package fail-closed checks."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('audit', HERE/'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def reject(action, fragment):
    try:
        action()
    except (ValueError, KeyError) as exc:
        v.require(fragment in str(exc), 'unexpected rejection: '+str(exc))
    else:
        raise ValueError('accepted control: '+fragment)


def run():
    folder=v.ROOT/f'{v.PREFIX}/pr1042/research/gauge44-slots-t16/data'
    plan,roles=v.read(folder/'PLAN.json'),v.read(folder/'OWNERS.json.gz')
    reject(lambda:v.reconstruct(plan,roles[1:]),'role count')
    for label, edit in [('helper inventory',lambda rs:rs[1].update(helper=rs[0]['helper'])),
                        ('whole width binding',lambda rs:rs[0].update(width=rs[0]['width']+1)),
                        ('slice coordinates',lambda rs:rs[0].update(offset=-1))]:
        changed=copy.deepcopy(roles)
        edit(changed)
        reject(lambda:v.reconstruct(plan,changed),label)
    changed=copy.deepcopy(roles)
    first=changed[0]
    allowed=plan['windows'][f"{first['owner_replica']},{first['child']}"][1]
    time=next(t for t in range(144) if t not in allowed)
    first.update(time=time,stage=plan['order'][time][0],replica=plan['order'][time][1])
    reject(lambda:v.reconstruct(plan,changed),'window/capacity')
    cert=v.read(HERE/'CERTIFICATE.json')
    a={int(k):n for k,n in cert['maps']['1031']['histogram'].items()}
    b={int(k):n for k,n in cert['maps']['1042']['histogram'].items()}
    reject(lambda:v.compare({r:n for r,n in a.items() if r},{r:n for r,n in b.items() if r}),'equal residual count')
    reverse=v.compare(b,a)
    v.require(reverse['power_cost_b_half']['sign']=='positive' and reverse['power_cost_b_three_quarters']['sign']=='negative','orientation control')
    v.require(sum(min(r,3)*n for r,n in b.items())-sum(min(r,3)*n for r,n in a.items())==9,'concave counterexample')
    checks=8
    with tempfile.TemporaryDirectory(prefix='t16 audit controls ',dir=v.ROOT) as name:
        root=Path(name)
        package=root/'research'/HERE.name
        shutil.copytree(HERE,package)
        for rel in v.REQUIRED:
            dest=root/rel
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(v.ROOT/rel,dest)
        command=[sys.executable,'-I','-O','-B',str(package/'verify.py')]
        def run_child(extra=()):
            return subprocess.run(command+list(extra),cwd=root,capture_output=True,text=True)
        honest=run_child()
        v.require(honest.returncode==0,'relocated honest replay: '+honest.stderr)
        def tamper(path,fn,fragment):
            old=path.read_bytes()
            path.write_bytes(fn(old))
            outcome=run_child()
            path.write_bytes(old)
            v.require(outcome.returncode!=0 and fragment in outcome.stderr,'package rejection '+fragment)
        def json_edit(raw,fn):
            data=json.loads(raw); fn(data)
            return json.dumps(data).encode()
        tamper(package/'SOURCES.json',lambda x:json_edit(x,lambda d:d['files'].pop(v.REQUIRED[0])),'exact source inventory')
        tamper(root/v.REQUIRED[0],lambda x:x+b' ','source hash')
        tamper(package/'BASE-SELECTED.json',lambda x:x+b' ','selected snapshot hash')
        tamper(package/'CERTIFICATE.json',lambda x:json_edit(x,lambda d:d['maps']['1042'].update(roles=69120.0)),'certificate mismatch')
        tamper(package/'CERTIFICATE.json',lambda x:json_edit(x,lambda d:d['comparisons'].pop('1031->1042')),'certificate mismatch')
        duplicate=run_child(['--write-certificate'])
        v.require(duplicate.returncode!=0 and 'refusing certificate overwrite' in duplicate.stderr,'overwrite control')
    print(f'PASS_T16_CONCAVITY_CONTROLS: {checks} mathematical checks; six package rejections; spaced-path relocation')


if __name__=='__main__':
    run()
