"""Relocated replay and fail-closed package controls."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parents[1]


def need(ok, message):
    if not ok:raise ValueError(message)


def main():
    # Keep temporary writes within the explicit checkout workspace on Windows.
    with tempfile.TemporaryDirectory(prefix='.word precision53 ', dir=ROOT) as temp:
        root=Path(temp); package=root/'research/word-precision53'
        shutil.copytree(P,package)
        pins=json.loads((P/'SOURCES.json').read_text())
        for source in pins['files']:
            dest=root/source;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/source,dest)
        def invoke(extra=()):
            return subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py'),*map(str,extra)],
                                  cwd=root,capture_output=True,text=True)
        need(invoke().returncode==0,'relocated positive replay')
        count=0
        def corrupt(path,content,message):
            nonlocal count
            old=path.read_bytes();path.write_text(content,encoding='utf-8')
            try:
                result=invoke();need(result.returncode!=0 and message in result.stderr,'missed corruption '+message)
                count+=1
            finally:path.write_bytes(old)
        changed=dict(pins);changed['files']=dict(pins['files']);changed['files'].pop(next(iter(changed['files'])))
        corrupt(package/'SOURCES.json',json.dumps(changed),'source inventory')
        corrupt(root/'research/cubic-cyclic-inverse/composition.py','# altered\n','source hash')
        corrupt(package/'BASE-SELECTED.json','{}','selected snapshot')
        expected=json.loads((package/'EXPECTED.json').read_text())
        for value in (20.0,True):
            changed=dict(expected);changed['source_cases']=value
            corrupt(package/'EXPECTED.json',json.dumps(changed),'certificate mismatch')
        output=root/'already exists.json';output.write_text('{}')
        result=invoke(('--write-certificate',output))
        need(result.returncode!=0 and 'FileExistsError' in result.stderr,'overwrite accepted')
        need(output.read_text()=='{}','overwrite changed bytes');count+=1
        need(count==6,'control inventory')
    print('PASS_PACKAGE53 relocated=1 controls=6')


if __name__=='__main__':main()
