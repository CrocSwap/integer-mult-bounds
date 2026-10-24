#!/usr/bin/env python3
"""Isolated cold replay and actual malformed-input/dual rejection. Apache-2.0."""
import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)

with tempfile.TemporaryDirectory(prefix='shared-port-controls-')as tmp:
    dst=Path(tmp)/'package';shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('__pycache__'))
    cmd=[sys.executable,'-I','-O','-B',str(dst/'verify.py')];env=dict(os.environ,PATH='/nonexistent')
    def run():return subprocess.run(cmd,cwd=tmp,env=env,capture_output=True,text=True,timeout=180)
    r=run();need(r.returncode==0,'cold optimized baseline failed '+r.stderr)
    p=dst/'inputs/pr4813-verify_schedule.py';raw=p.read_bytes();p.write_bytes(raw+b'\n');r=run();need(r.returncode!=0 and 'source hash' in r.stderr,'source corruption accepted');p.write_bytes(raw)
    p=dst/'verify.py';raw=p.read_bytes();changed=raw.replace(b"('add',g[2],g[1],-g[3])",b"('add',g[2],g[1],g[3])");need(changed!=raw,'dual mutation not applied');p.write_bytes(changed);r=run();need(r.returncode!=0 and 'serialized raw inverse transpose' in r.stderr,'wrong raw-dual ADD sign accepted');p.write_bytes(raw)
    p=dst/'RESULT.json';raw=p.read_bytes();data=json.loads(raw);data['new_kappa']=True;p.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n');r=run();need(r.returncode!=0 and 'receipt mismatch' in r.stderr,'false kappa receipt accepted');p.write_bytes(raw)
print('PASS_SHARED_PORT_MUTATIONS cold_optimized=PASS source=REJECT dual_sign=REJECT false_kappa_receipt=REJECT')
