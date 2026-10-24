#!/usr/bin/env python3
"""Actual isolated exported-byte rejection controls, Apache-2.0."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent

def require(ok,why):
    if not ok: raise ValueError(why)

with tempfile.TemporaryDirectory(prefix='cascade-audit-controls-') as temp:
    dst=Path(temp)/'package'
    shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('__pycache__'))
    cmd=[sys.executable,'-I','-O','-B',str(dst/'verify.py')]
    env=dict(os.environ,PATH='/nonexistent')
    def run(): return subprocess.run(cmd,cwd=temp,env=env,capture_output=True,text=True,timeout=120)
    baseline=run()
    require(baseline.returncode==0,'Git-free optimized baseline failed: '+baseline.stderr)
    source=dst/'inputs/pr4826-verify_ports.py';original=source.read_bytes()
    source.write_bytes(original+b'\n')
    changed=run()
    require(changed.returncode!=0 and 'source bytes differ' in changed.stderr,'source-byte mutation accepted')
    source.write_bytes(original)
    receipt=dst/'RESULT.json';original_receipt=receipt.read_bytes()
    data=json.loads(original_receipt);data['new_kappa']=True
    receipt.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    changed=run()
    require(changed.returncode!=0 and 'receipt mismatch' in changed.stderr,'scientific receipt mutation accepted')
    receipt.write_bytes(original_receipt)
    require(source.read_bytes()==original and receipt.read_bytes()==original_receipt,'failed restoration')
print('PASS_CASCADE_AUDIT_EXPORT_MUTATIONS source_corruption=REJECT receipt_corruption=REJECT git_free_optimized=PASS')
