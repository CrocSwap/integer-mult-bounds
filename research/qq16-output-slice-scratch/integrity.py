#!/usr/bin/env python3
"""Source, candidate and typed receipt controls in a Git-free export."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


with tempfile.TemporaryDirectory(prefix='qq16-slices-') as temporary:
    root=Path(temporary);p=root/'research'/HERE.name
    shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__'))
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            destination=root/row['path'];destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/row['path'],destination)
    def run(*args):
        return subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py'),*args],
                              capture_output=True,text=True,timeout=90,cwd=root)
    good=run();need(good.returncode==0,'Git-free replay: '+good.stderr)
    need(run('--write').returncode!=0,'refuse overwrite')
    for name,marker in [('vendor/verify.py','source authentication'),('vendor/README.md','source authentication')]:
        target=p/name;raw=target.read_bytes();target.write_bytes(raw+b'\nBROKEN\n')
        bad=run();need(bad.returncode!=0 and marker in bad.stderr,'pre-import corrupt source rejection')
        target.write_bytes(raw)
    target=p/'WORD.json';raw=target.read_bytes();word=json.loads(raw)
    word[634]['field']='W1';target.write_text(json.dumps(word))
    bad=run();need(bad.returncode!=0 and 'literal word mismatch' in bad.stderr,'candidate corruption')
    target.write_bytes(raw)
    target=p/'RESULT.json';raw=target.read_bytes();receipt=json.loads(raw)
    receipt['schema_version']=True;target.write_text(json.dumps(receipt))
    bad=run();need(bad.returncode!=0 and 'typed receipt mismatch' in bad.stderr,'bool/int receipt control')
print('PASS_QQ16_SLICE_INTEGRITY git_free=1 source_corruptions=2 candidate=1 typed_receipt=1 overwrite=1')
