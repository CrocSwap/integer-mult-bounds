#!/usr/bin/env python3
"""Real subprocess integrity failures in an isolated source mirror."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(condition,label):
    if not condition: raise ValueError(label)


def invoke(package,*,optimized=False,error=None):
    args=[sys.executable,'-B']+(['-O'] if optimized else [])+[str(package/'verify.py')]
    result=subprocess.run(args,cwd=package.parent.parent.parent,capture_output=True,text=True,timeout=120)
    text=result.stdout+result.stderr
    if error:
        need(result.returncode!=0 and error in text,'subprocess rejection: '+error+' '+text[-1000:])
    else:
        need(result.returncode==0 and text.startswith('PASS_FIXED_DIMENSION_COEFFICIENTS '),
             'isolated positive replay '+text[-1000:])
    return text.strip()


def main():
    with TemporaryDirectory(prefix='fixed-dimension-boundaries-') as temp:
        root=Path(temp); package=root/'research'/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        rows=json.loads((HERE/'SOURCES.json').read_text())['files']
        for row in rows:
            if row['usage']!='input': continue
            target=root/row['path']; target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/row['path'],target)
        invoke(package); invoke(package,optimized=True)
        receipt=package/'RESULT.json'; old=receipt.read_bytes()
        changed=json.loads(old); changed['schema']=True
        receipt.write_text(json.dumps(changed))
        invoke(package,optimized=True,error='typed complete RESULT equality')
        receipt.write_bytes(old)
        source=root/'research/delayed-cover-chronological-fields/numerical/records.py'
        old=source.read_bytes(); source.write_bytes(old+b'\n# intentional source drift\n')
        invoke(package,error='source drift:'); source.write_bytes(old)
        implementation=package/'consumer.py'; old=implementation.read_bytes()
        altered=old.replace(b'"residue_pending":16*n*n+128',b'"residue_pending":0*n*n+1')
        need(altered!=old,'capacity budget mutation applied')
        implementation.write_bytes(altered)
        invoke(package,optimized=True,error='pre-guard residue demand')
        implementation.write_bytes(old)
    print('PASS_FIXED_DIMENSION_BOUNDARIES 2 clean modes 3 real corruption controls')


if __name__=='__main__': main()
