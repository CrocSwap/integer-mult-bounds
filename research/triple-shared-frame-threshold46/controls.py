#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v',HERE/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)


def reject(fn,message):
    try:
        fn()
    except ValueError as exc:
        v.need(message in str(exc),'wrong rejection: '+str(exc))
    else:
        raise ValueError('accepted negative control: '+message)


def run():
    s=(7,25)
    reject(lambda:v.admissible_pair(s,(11,21)),'common span')
    reject(lambda:v.admissible_pair(s,(11,38)),'scalar rank one')
    reject(lambda:v.admissible_pair(s,(11,49)),'cross orthogonality')
    reject(lambda:v.admissible_pair(s,(224,352)),'two degenerate pairs')
    reject(lambda:v.frame(10,s,(224,800),s),'degenerate frame')
    reject(lambda:v.frame(6,s,(11,19),(25,26,4)),'alternating residual')
    # The predecessor's general norm-one h8 control is legal and explicitly
    # outside the new triple-only theorem. No finite search creates it here.
    v.frame(8,(1,7),(16,112),(1,2,4,8))
    reject(lambda:v.admissible_pair((1,7),(16,112)),'triple labels')
    v.need(v.span(s)&v.span((11,21))=={0,30},'shared-radical witness')
    v.need(v.scalar(7,224)==v.scalar(25,800)==1 and v.scalar(7,11)==-1,'signed kernel controls')
    with tempfile.TemporaryDirectory(prefix='triple frame controls ',dir=v.ROOT) as folder:
        root=Path(folder);p=root/'research'/HERE.name
        shutil.copytree(HERE,p)
        for name in v.REQUIRED:
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(v.ROOT/name,target)
        command=[sys.executable,'-I','-O','-B',str(p/'verify.py')]
        def child(extra=()):
            return subprocess.run(command+list(extra),cwd=root,capture_output=True,text=True)
        result=child();v.need(result.returncode==0,'relocation: '+result.stderr)
        def alter(path,fn,message):
            old=path.read_bytes();path.write_bytes(fn(old));result=child();path.write_bytes(old)
            v.need(result.returncode!=0 and message in result.stderr,'failed package control '+message)
        def change(raw,fn):
            obj=json.loads(raw);fn(obj);return json.dumps(obj).encode()
        alter(p/'SOURCES.json',lambda x:change(x,lambda d:d['files'].pop(v.REQUIRED[0])),'exact source inventory')
        alter(root/v.REQUIRED[0],lambda x:x+b' ','source hash')
        alter(p/'BASE-SELECTED.json',lambda x:x+b' ','selected snapshot')
        alter(p/'CERTIFICATE.json',lambda x:change(x,lambda d:d.update(sharp_minimum_ambient=10.0)),'certificate mismatch')
        alter(p/'CERTIFICATE.json',lambda x:change(x,lambda d:d['census'].pop()),'certificate mismatch')
        result=child(['--write-certificate']);v.need(result.returncode!=0 and 'refusing certificate overwrite' in result.stderr,'overwrite control')
    print('PASS_TRIPLE_THRESHOLD_CONTROLS: ten semantic checks; six package rejections; spaced-path relocation')


if __name__=='__main__':
    run()
