#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded local/native/owner/moment replay with stored full-release binding."""
import hashlib,json,os,subprocess,sys,tempfile
from fractions import Fraction as Q
from pathlib import Path
P=Path(__file__).resolve().parent

def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert __debug__;pins=read(P/'MANIFEST.json')
 actual={f.relative_to(P).as_posix():sha(f) for f in P.rglob('*') if f.is_file() and f!=P/'MANIFEST.json'}
 assert not any(f.is_symlink() for f in P.rglob('*')) and actual==pins
 with tempfile.TemporaryDirectory(prefix='helper408-replay-') as temp:
  out=Path(temp);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');env.pop('PYTHONOPTIMIZE',None)
  for script,args in [('verify.py',['--native','--work',str(out/'local')]),('check_allocation.py',['--work',str(out/'owners')])]:
   log=out/(script+'.log')
   with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(P/script),*args],stdout=f,stderr=subprocess.STDOUT,env=env)
   if r.returncode:print(log.read_text()[-4000:]);raise SystemExit(r.returncode)
  local=read(out/'local/RESULT.json');owner=read(out/'owners/RESULT.json');claim=read(P/'CLAIM.json');admit=read(P/'evidence/ADMISSION-RESULT.json');release=read(P/'evidence/RELEASE-RECEIPT.json');native=read(P/'evidence/FULL-NATIVE-RESULT.json')
  assert local['native_replayed'] and set(local['native'])=={'base','extra'}
  assert admit['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and release['status']=='PASS_RELEASE'
  assert Q(owner['moment']['target'])==Q(claim['kappa'])==Q(admit['kappa'])==Q(release['kappa_decimal'])
  assert claim['release_receipt_sha256']==admit['release_receipt_sha256']==sha(P/'evidence/RELEASE-RECEIPT.json')
  assert claim['native_receipt_sha256']==admit['native_receipt_sha256']==native['native_receipt_sha256']==sha(P/'evidence/FULL-NATIVE-RECEIPT.json')
  assert {f.relative_to(P).as_posix():sha(f) for f in P.rglob('*') if f.is_file() and f!=P/'MANIFEST.json'}==pins
  print('PASS_TWO_SIDED_HELPER408_REGISTERED_LOCAL_NATIVE_OWNER_MOMENT',claim['kappa'])
  print('Full integrated admission is authenticated stored evidence here; reproduce.py reruns it. Inherited all-size assumptions remain.')
if __name__=='__main__':main()
