#!/usr/bin/env python3
"""Fresh full-word verification followed by source-bound p10 fixed-prime assembly."""
import sys
if not __debug__:raise SystemExit('Assertions required; refusing -O')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 manifest=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
 actual={p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.rglob('*')if p.is_file()and p!=ROOT/'MANIFEST.json'}
 assert actual==manifest['files'],'Missing,changed or unpinned file'
 return sha(ROOT/'MANIFEST.json')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 digest=integrity();out=a.output.resolve();assert not out.exists()and not out.is_relative_to(ROOT),'Output must be new and outside package';out.mkdir(parents=True)
 t=time.monotonic();source=ROOT/'vendor/pr320-derived'
 # No old PASS receipt is an input: every mandatory supplier stage is freshly replayed.
 with(out/'supplier.log').open('w',encoding='utf-8')as log:
  subprocess.run([sys.executable,'-X','utf8','-B',str(source/'verify.py'),'--output',str(out/'supplier')],check=True,stdout=log,stderr=subprocess.STDOUT)
 import fixed_prime
 result=fixed_prime.run(out/'supplier',out/'certificate.json')
 assert integrity()==digest,'Package changed during replay'
 cert=dict(status=result['status'],kappa=str(result['kappa']),conditional=True,lean_certificate=False,manifest_sha256=digest,public_parent_head=result['source']['public_parent_head'],derived_supplier_manifest_sha256=result['source']['manifest_sha256'],source_manifest_sha256=result['source']['manifest_sha256'],inputs_unchanged=True,fresh_full_supplier_replay=True,fresh_adaptation_arithmetic=True,certificate_sha256=sha(out/'certificate.json'),seconds=time.monotonic()-t)
 (out/'verification.json').write_text(json.dumps(cert,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(cert),flush=True)
if __name__=='__main__':main()
