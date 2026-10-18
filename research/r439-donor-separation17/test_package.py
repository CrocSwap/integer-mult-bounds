"""Relocated exact replay and immutable-input controls."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]


def need(ok,msg):
    if not ok:raise ValueError(msg)


def main():
    with tempfile.TemporaryDirectory(prefix='.donor separation17 ',dir=ROOT) as temp:
        root=Path(temp);package=root/'research/r439-donor-separation17'
        shutil.copytree(P,package);pins=json.loads((P/'SOURCES.json').read_text())
        for source in pins['files']:
            target=root/source;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/source,target)
        def invoke(extra=()):
            return subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py'),*map(str,extra)],cwd=root,capture_output=True,text=True)
        need(invoke().returncode==0,'relocated replay');count=0
        def corrupt(path,data,message):
            nonlocal count
            original=path.read_bytes();path.write_bytes(data)
            try:
                result=invoke();need(result.returncode!=0 and message in result.stderr,'missed '+message);count+=1
            finally:path.write_bytes(original)
        bad=json.loads(json.dumps(pins));bad['files'].pop(next(iter(bad['files'])))
        corrupt(package/'SOURCES.json',json.dumps(bad).encode(),'source inventory')
        source=root/'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
        corrupt(source,b'changed immutable archive','source hash')
        corrupt(package/'BASE-SELECTED.json',b'{}','selected snapshot')
        expected=json.loads((package/'EXPECTED.json').read_text())
        for value in (23.0,True):
            bad=dict(expected);bad['rows_checked']=value
            corrupt(package/'EXPECTED.json',json.dumps(bad).encode(),'certificate mismatch')
        existing=root/'existing.json';existing.write_text('{}')
        result=invoke(('--write-certificate',existing))
        need(result.returncode!=0 and 'FileExistsError' in result.stderr and existing.read_text()=='{}','output overwrite');count+=1
        need(count==6,'control inventory')
    print('PASS_PACKAGE17 relocated=1 controls=6')


if __name__=='__main__':main()
