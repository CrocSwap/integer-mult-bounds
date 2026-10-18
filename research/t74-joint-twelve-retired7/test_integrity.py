#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Git-free read-only replay and fail-closed input/claim/optimization controls."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def hashes(root):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
def main():
 with tempfile.TemporaryDirectory(prefix='joint-twelve-retired7-controls-') as t:
  p=Path(t)/'package';shutil.copytree(HERE,p);before=hashes(p)
  def run(script='verify.py',flags=()):
   return subprocess.run([sys.executable,'-I','-B',*flags,str(p/script)],cwd=t,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),text=True,capture_output=True,timeout=300)
  r=run();need(r.returncode==0 and 'PASS_JOINT_TWELVE_RETIRED7_FINITE_REPLAY' in r.stdout,'relocated positive: '+r.stderr);need(hashes(p)==before,'read-only replay')
  r=run(flags=('-O',));need(r.returncode!=0 and 'run without -O' in r.stderr,'optimized verification refusal')
  r=run('generate.py',('-O',));need(r.returncode!=0 and 'assertions must be enabled' in r.stderr,'optimized generator refusal')
  f=p/'CLAIM.json';b=f.read_bytes();c=json.loads(b);c['kappa']='1';f.write_text(json.dumps(c));r=run();need(r.returncode!=0 and 'claim outer endpoint' in r.stderr,'claim corruption rejection');f.write_bytes(b)
  f=p/'inputs/WORD-base.json.gz';b=f.read_bytes();f.write_bytes(b+b'corruption');r=run();need(r.returncode!=0 and 'input digest' in r.stderr,'word authentication rejection');f.write_bytes(b)
  need(hashes(p)==before,'controls restore exact files')
 print('PASS_JOINT_TWELVE_RELOCATED_READ_ONLY_AND_INTEGRITY_CONTROLS')
if __name__=='__main__':main()
