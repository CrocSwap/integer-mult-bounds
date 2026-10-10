#!/usr/bin/env python3
"""Mandatory fresh public PR327 construction replay and full p10 operational transfer.
Prepared with substantial OpenAI Codex assistance; Apache-2.0. No kappa claim.
"""
import sys
if not __debug__:raise SystemExit('Assertions required; refusing -O')
sys.dont_write_bytecode=True
import argparse,gzip,hashlib,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def integrity():
 actual={}
 for p in ROOT.rglob('*'):
  assert not p.is_symlink(),'symlink in package'
  if p.is_file() and p!=ROOT/'MANIFEST.json':actual[p.relative_to(ROOT).as_posix()]=sha(p)
 assert actual==read(ROOT/'MANIFEST.json')['files'],'Changed, missing or unpinned package source'
 pins=read(ROOT/'SOURCE.json');assert sha(ROOT/'vendor/neutral/MANIFEST.json')==pins['neutral_reference_manifest_sha256']
 assert sha(ROOT/'vendor/pr327/SOURCE.json')==pins['public_source_json_sha256']
 assert sha(ROOT/'vendor/pr327/verify.py')==pins['public_verify_sha256']
 assert sha(ROOT/'vendor/pr327/certificate/expected.json')==pins['public_expected_sha256']
 public={p.relative_to(ROOT/'vendor/pr327').as_posix():sha(p) for p in (ROOT/'vendor/pr327').rglob('*') if p.is_file()}
 assert public==pins['public_files'],'public PR327 subtree changed'
 return sha(ROOT/'MANIFEST.json')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
 assert sys.version_info>=(3,11);begun=time.monotonic();initial=integrity();pins=read(ROOT/'SOURCE.json')
 out=args.output.resolve();assert not out.exists() and not out.is_relative_to(ROOT),'Use a fresh external output'
 out.mkdir(parents=True);(out/'logs').mkdir();(out/'upstream-work').mkdir();stages=[]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 def run(stage,argv):
  print(stage,flush=True);start=time.monotonic();log=out/'logs'/(stage+'.log')
  with log.open('w') as f:subprocess.run([sys.executable,'-B']+list(map(str,argv)),cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
  stages.append(dict(stage=stage,seconds=time.monotonic()-start,log_sha256=sha(log)))
 try:
  run('complete-public-pr327-replay',[ROOT/'vendor/pr327/verify.py','--temp-root',out/'upstream-work'])
  transcript=(out/'logs/complete-public-pr327-replay.log').read_text()
  assert 'PASS expected.json reproduced: at p = 10' in transcript and 'committed certificates reproduced byte for byte' in transcript
  compressed=(ROOT/pins['candidate_path']).read_bytes();assert hashlib.sha256(compressed).hexdigest()==pins['candidate_compressed_sha256']
  raw=gzip.decompress(compressed);assert hashlib.sha256(raw).hexdigest()==pins['candidate_sha256'];(out/'candidate.json').write_bytes(raw)
  run('complete-p10-operational-transfer',[ROOT/'verify_supplier.py','--input',out/'candidate.json','--expected-sha256',pins['candidate_sha256'],'--output',out/'SUPPLIER-CHECK.json'])
  receipt=read(out/'SUPPLIER-CHECK.json')
  assert receipt['status']=='PASS_RESEARCH_P10_COMPLEX_SUPPLIER_FULL_SCALAR_SPLICE_GUARD_TWO_MOMENTS'
  assert receipt['candidate_sha256']==pins['candidate_sha256'] and receipt['roots']['with_fallback']['b']==pins['complex_coarse'] and receipt['kappa_claim'] is False
  assert receipt['ledger']['calls']==247575 and receipt['ledger']['rank_mass']==1027460 and receipt['ledger']['deficit']==2040
  assert len(receipt['mutation_controls'])==20 and len(receipt['gx_check']['controls'])==2
  assert receipt['finite_guard']['status']=='PASS_FRESH_EXACT_P10_COMPLEX_GUARD' and receipt['finite_guard']['retained_row_coefficient']==20161
  assert integrity()==initial,'Package source changed during replay'
  report=dict(status='PASS_PORTABLE_PUBLIC_PR327_P10_COMPLEX_SUPPLIER_TRANSFER',manifest_sha256=initial,public_head=pins['public_head'],public_source_json_sha256=pins['public_source_json_sha256'],candidate_sha256=pins['candidate_sha256'],complex_coarse=pins['complex_coarse'],fresh_stages=stages,inputs_unchanged=True,receipt_hashes={name:sha(out/name) for name in ('candidate.json','SUPPLIER-CHECK.json')},seconds=time.monotonic()-begun,kappa_claim=False,scope=receipt['scope'])
  (out/'VERIFICATION.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print('PASS public PR327 complex supplier transfer; b = '+pins['complex_coarse']+'; no kappa claim',flush=True)
 except BaseException as error:
  (out/'FAILURE.json').write_text(json.dumps(dict(status='FAIL',error=str(error),completed_stages=stages),indent=2)+'\n');raise
if __name__=='__main__':main()
