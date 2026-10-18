"""Workspace-local relocation and package integrity checks."""
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
    with tempfile.TemporaryDirectory(prefix='.matching neighborhood13 ',dir=ROOT) as temp:
        root=Path(temp);package=root/'research/r439-matching-neighborhood13';shutil.copytree(P,package)
        pins=json.loads((P/'SOURCES.json').read_text())
        for source in pins['files']:
            target=root/source;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/source,target)
        def invoke(extra=()):return subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py'),*map(str,extra)],cwd=root,capture_output=True,text=True)
        need(invoke().returncode==0,'relocated replay');count=0
        def corrupt(path,data,message):
            nonlocal count
            old=path.read_bytes();path.write_bytes(data)
            try:
                result=invoke();need(result.returncode!=0 and message in result.stderr,'missed '+message);count+=1
            finally:path.write_bytes(old)
        changed=json.loads(json.dumps(pins));changed['files'].pop(next(iter(changed['files'])))
        corrupt(package/'SOURCES.json',json.dumps(changed).encode(),'source inventory')
        corrupt(root/'research/r439-helper-matching/build.py',b'# changed source','source hash')
        corrupt(package/'BASE-SELECTED.json',b'{}','selected snapshot')
        expected=json.loads((package/'EXPECTED.json').read_text())
        changed=dict(expected);changed['distinct_words']=857.0
        corrupt(package/'EXPECTED.json',json.dumps(changed).encode(),'certificate mismatch')
        changed=json.loads(json.dumps(expected));changed['records'].pop()
        corrupt(package/'EXPECTED.json',json.dumps(changed).encode(),'certificate mismatch')
        output=root/'existing.json';output.write_text('{}');result=invoke(('--write-certificate',output))
        need(result.returncode!=0 and 'FileExistsError' in result.stderr and output.read_text()=='{}','output overwrite');count+=1
        need(count==6,'control inventory')
    print('PASS_PACKAGE13 relocated=1 controls=6')


if __name__=='__main__':main()
