"""Minimal relocated source closure and actual subprocess rejection controls."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
scratch=ROOT/'.firecrawl';scratch.mkdir(exist_ok=True)
def need(x,msg):
    if not x:raise ValueError(msg)
with tempfile.TemporaryDirectory(prefix='factor47-',dir=scratch) as name:
    dest=Path(name);p=dest/'research'/HERE.name
    shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__'))
    for rel in json.loads((HERE/'SOURCES.json').read_text())['files']:
        q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,q)
    def run():return subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py')],capture_output=True,text=True)
    def edit(q,fn):
        old=q.read_bytes();q.write_bytes(fn(old));r=run();q.write_bytes(old)
        need(r.returncode!=0 and 'ValueError' in r.stderr,'missed mutation or wrong rejection')
    need(run().returncode==0,'relocated baseline')
    q=dest/'research/complex-decoder-field-extension-seed44/PROOF.md'
    edit(q,lambda b:b+b'\nchanged premise\n')
    def missing(b):
        x=json.loads(b);x['files'].pop(next(iter(x['files'])));return json.dumps(x).encode()
    edit(p/'SOURCES.json',missing)
    def typed(b):
        x=json.loads(b);x['root_pair_checks']=1024.0;return json.dumps(x).encode()
    edit(p/'EXPECTED.json',typed)
    def wrong(b):
        x=json.loads(b);x['outside_code_countercontrol']['augmented_rank']=8;return json.dumps(x).encode()
    edit(p/'EXPECTED.json',wrong)
    edit(p/'EXPECTED.json',lambda b:b.replace(b'"seed": 47',b'"seed": 47, "seed": 47'))
    edit(p/'SOURCES.json',lambda b:b.replace(b'"base":',b'"unused": NaN, "base":',1))
    need(run().returncode==0,'restored receipt')
print('PASS_FACTOR_LINEAR_PACKAGE relocation=1 mutations=6')
