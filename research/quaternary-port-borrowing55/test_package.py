"""Workspace-local standalone source/receipt rejection tests."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
scratch=ROOT/'.firecrawl';scratch.mkdir(exist_ok=True)
def need(ok,msg):
    if not ok:raise ValueError(msg)
with tempfile.TemporaryDirectory(prefix='borrow55-',dir=scratch) as name:
    dst=Path(name)/'research'/HERE.name
    shutil.copytree(HERE,dst,ignore=shutil.ignore_patterns('__pycache__'))
    def run():return subprocess.run([sys.executable,'-I','-O','-B',str(dst/'verify.py')],capture_output=True,text=True)
    def edit(path,fn):
        p=dst/path;before=p.read_bytes();p.write_bytes(fn(before));r=run();p.write_bytes(before)
        need(r.returncode!=0 and 'ValueError' in r.stderr,'mutation accepted or wrong failure')
    need(run().returncode==0,'standalone baseline')
    edit('vendor/pr1057/borrow.py',lambda b:b+b'\n# changed source\n')
    def missing(b):
        o=json.loads(b);o['package_files'].pop('vendor/pr1057/checks.py');return json.dumps(o).encode()
    edit('SOURCES.json',missing)
    def receipt(b):
        o=json.loads(b);o['calls_saved']=481;return json.dumps(o).encode()
    edit('EXPECTED.json',receipt)
    def typed(b):
        o=json.loads(b);o['calls_saved']=480.0;return json.dumps(o).encode()
    edit('EXPECTED.json',typed)
    need(run().returncode==0,'restored receipt')
print('PASS_QUATERNARY_PACKAGE relocation=1 mutations=4 restored=PASS')
