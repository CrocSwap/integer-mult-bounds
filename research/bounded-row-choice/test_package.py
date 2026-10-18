"""Effective source/receipt controls on a Git-free relocation."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def invoke(p,ok,phrase):
    r=subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py')],capture_output=True,text=True,timeout=120)
    if (r.returncode==0)!=ok or phrase not in r.stdout+r.stderr:raise ValueError(r.stdout+r.stderr)


def main():
    with tempfile.TemporaryDirectory(prefix='row-choice-') as temp:
        root=Path(temp);p=root/'research/bounded-row-choice'
        shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__'))
        source=json.loads((HERE/'SOURCES.json').read_text())
        for row in source['files']:
            if row['usage']=='input':
                dest=root/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['path'],dest)
        invoke(p,True,'PASS_BOUNDED_ROW_CHOICE')
        first=next(r for r in source['files'] if r['usage']=='input')
        for path,msg in [(root/first['path'],'source drift'),(p/'snapshots/pr2097-verify.py','snapshot drift')]:
            raw=path.read_bytes();path.write_bytes(raw+b'\nCORRUPTED\n');invoke(p,False,msg);path.write_bytes(raw)
        path=p/'RESULT.json';raw=path.read_bytes();v=json.loads(raw);v['schema_version']=True
        path.write_text(json.dumps(v),encoding='utf-8');invoke(p,False,'typed receipt mismatch');path.write_bytes(raw)
    print('PASS_ROW_CHOICE_PACKAGE Git-free optimized replay;3 real integrity failures')


if __name__=='__main__':main()
