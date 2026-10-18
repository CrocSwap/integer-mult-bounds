#!/usr/bin/env python3
"""Portable replay and actual source corruption controls; Apache-2.0."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

def run(p):
    return subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py')],cwd=p,
                          capture_output=True,text=True,timeout=30)
def require(ok,msg):
    if not ok:raise ValueError(msg)
def main():
    package=Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix='signed port space ') as d:
        p=Path(d)/'relocated package';shutil.copytree(package,p)
        for f in p.iterdir():
            if f.is_file():f.chmod(0o444)
        p.chmod(0o555)
        try:
            result=run(p);require(result.returncode==0,result.stderr)
            require(json.loads(result.stdout)['status']=='PASS_NONUNIT_SIGNED_CONNECTOR_RIGIDITY','relocation status')
        finally:
            p.chmod(0o755)
            for f in p.iterdir():
                if f.is_file():f.chmod(0o644)
        original=(p/'verify.py').read_text()
        mutations=[("('w','x0',-1,'B0')","('w','x1',-1,'B0')"),
                   ('for bits in product((0,1),repeat=4):','for bits in product((0,2),repeat=4):')]
        for before,after in mutations:
            require(original.count(before)==1,'unique mutation site')
            (p/'verify.py').write_text(original.replace(before,after))
            result=run(p);require(result.returncode!=0 and 'ValueError' in result.stderr,'corruption not rejected')
        (p/'verify.py').write_text(original)
    print('PASS_NONUNIT_PORT_PACKAGE relocation=1 semantic_disk_corruptions=2')
if __name__=='__main__':main()
