#!/usr/bin/env python3
"""Fresh E8 supplier admission with a parity-correct full cover invoice.
OpenAI Codex assistance; upstream PR352 and Jacob Sussman sources remain unchanged.
No certificate-producer regeneration, Lean kernel build or combined kappa claim.
"""
import sys
if not __debug__:raise SystemExit('Assertions required; refusing -O')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from pathlib import Path
import argparse,gzip,hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
write=lambda p,x:p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def integrity():
 actual={}
 for p in ROOT.rglob('*'):
  assert not p.is_symlink(),'Symlink in package'
  if p.is_file() and p!=ROOT/'MANIFEST.json':actual[p.relative_to(ROOT).as_posix()]=sha(p)
 assert actual==read(ROOT/'MANIFEST.json')['files'],'Changed, missing or unpinned package source'
 pins=read(ROOT/'SOURCE.json');up=ROOT/'upstream/pr352';assert sha(up/'MANIFEST.sha256')==pins['upstream_manifest_sha256']
 entries={}
 for line in(up/'MANIFEST.sha256').read_text().splitlines():
  digest,rel=line.split(maxsplit=1);rel=rel.lstrip('*');assert sha(up/rel)==digest;entries[rel]=digest
 assert len(entries)==135
 assert sha(ROOT/pins['certificate_gzip_path'])==pins['certificate_gzip_sha256']
 assert hashlib.sha256(gzip.decompress((ROOT/pins['certificate_gzip_path']).read_bytes())).hexdigest()==pins['candidate_sha256']
 return sha(ROOT/'MANIFEST.json')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);args=ap.parse_args();assert sys.version_info>=(3,11)
 begun=time.monotonic();initial=integrity();pins=read(ROOT/'SOURCE.json');out=args.output.resolve();assert not out.exists() and not out.is_relative_to(ROOT);out.mkdir(parents=True);(out/'logs').mkdir();stages=[]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 for key in ['CX_PINS','CX_SOURCE_PINS','CX_RECORD']:env.pop(key,None)
 def run(stage,argv,isolated=False):
  print(stage,flush=True);start=time.monotonic();log=out/'logs'/(stage+'.log')
  with log.open('w')as f:r=subprocess.run([sys.executable]+(['-I']if isolated else [])+['-B']+list(map(str,argv)),cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT)
  assert r.returncode==0,stage+' failed with exit '+str(r.returncode)
  stages.append(dict(stage=stage,returncode=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)))
 try:
  up=ROOT/'upstream/pr352';e8=up/'code/complex/inputs/e8'
  run('complete-e8-scalar-splice-dirty-parity-guard',[ROOT/'admit.py','--source',up,'--output',out/'admission'])
  a=read(out/'admission/INDEPENDENT-AUDIT.json');g=read(out/'admission/UPSTREAM-GUARD.json')
  assert a['status']=='PASS_E8_INDEPENDENT_DIRTY_SCALARS_AND_CORRECTED_FINITE_GUARD' and a['certificate_sha256']==pins['candidate_sha256']
  assert a['guard_receipt_sha256']==sha(out/'admission/UPSTREAM-GUARD.json') and a['finite_guard']['all_retained_guards_pass']
  for orientation in ['forward','backward']:assert a['scalar_words'][orientation]['all_live_rows_correct'] and a['scalar_words'][orientation]['all_private_work_restored_zero'] and a['scalar_words'][orientation]['independent_live_columns']==1023
  assert len(g['splice']['controls'])==20 and all(z['rejected']for z in g['splice']['controls']) and len(g['program_check']['controls'])==2
  assert a['finite_guard']['physical_row_overcharge_coefficient']==11162 and a['finite_guard']['group_bits']==990 and all(a['finite_guard']['controls'].values())
  run('e8-lean-data-regeneration',[e8/'tools/gx/regen_check_e8.py','--keep',out/'lean-data'])
  last=(out/'logs/e8-lean-data-regeneration.log').read_text().strip().splitlines()[-1]
  assert last=='RESULT: REPRODUCED (25 repository files reproduced byte for byte, 0 different, 3 generated files not in the repository)'
  matched={};unmatched={};generator_logs={}
  for p in sorted((out/'lean-data').rglob('*')):
   if not p.is_file():continue
   rel=p.relative_to(out/'lean-data').as_posix()
   if rel.startswith('logs/'):generator_logs[rel]=sha(p);continue
   target='comparator/'+rel[4:]if rel.startswith('cmp/')else rel
   if(e8/target).is_file():assert p.read_bytes()==(e8/target).read_bytes();matched[target]=sha(p)
   else:unmatched[rel]=sha(p)
  assert len(matched)==25 and len(unmatched)==3
  write(out/'LEAN-DATA.json',dict(status='PASS_EXACT_E8_LEAN_DATA_REGENERATION',source_head=pins['e8_source_head'],certificate_sha256=pins['candidate_sha256'],matched_files=matched,unmatched_generated_files=unmatched,generator_log_hashes=generator_logs,upstream_lean_rebuilt=False,producer_regeneration_claim=False))
  run('e8-independent-replay',[e8/'tools/e8/replay.py',e8/'tools/certificate/gcert1-e8-r783.json.gz','e8'],isolated=True)
  last=(out/'logs/e8-independent-replay.log').read_text().strip().splitlines()[-1]
  assert last.startswith('REPLAY ACCEPTED: R=783 W=1263 D=120 cst=72 N=9039 figure=8762479') and 'E8 family: True' in last
  write(out/'INDEPENDENT-REPLAY.json',dict(status='PASS_UPSTREAM_STANDALONE_E8_REPLAY',certificate_sha256=pins['candidate_sha256'],script_sha256=sha(e8/'tools/e8/replay.py'),stdout_sha256=sha(out/'logs/e8-independent-replay.log'),summary=last))
  run('complete-e8-two-moment-pricing',[ROOT/'price.py','--guard',out/'admission/UPSTREAM-GUARD.json','--output',out/'SUPPLIER-CHECK.json'])
  c=read(out/'SUPPLIER-CHECK.json');assert c['status']=='PASS_E8_FULL_PAID_PROFILE_TWO_EXACT_MOMENTS' and c['candidate_sha256']==pins['candidate_sha256'] and c['kappa_claim']is False;assert c['roots']['with_fallback']['b']==pins['complex_coarse']
  (out/'candidate.json').write_bytes(gzip.decompress((ROOT/pins['certificate_gzip_path']).read_bytes()));assert sha(out/'candidate.json')==pins['candidate_sha256']
  assert integrity()==initial,'Package changed during replay'
  receipts=['candidate.json','admission/UPSTREAM-GUARD.json','admission/INDEPENDENT-AUDIT.json','LEAN-DATA.json','INDEPENDENT-REPLAY.json','SUPPLIER-CHECK.json']
  report=dict(status='PASS_PORTABLE_E8_CORRECTED_COMPLEX_SUPPLIER',manifest_sha256=initial,public_head=pins['public_head'],e8_source_head=pins['e8_source_head'],candidate_sha256=pins['candidate_sha256'],complex_coarse=pins['complex_coarse'],fresh_stages=stages,inputs_unchanged=True,receipt_hashes={r:sha(out/r)for r in receipts},seconds=time.monotonic()-begun,kappa_claim=False,producer_regeneration_claim=False,lean_data_regeneration_claim=True,upstream_lean_rebuilt=False,declarative_source=True,declarative_source_scope=pins['declarative_source_scope'],parity_corrected_complete_invoice=True,scope=pins['scope'])
  write(out/'VERIFICATION.json',report);print('PASS corrected E8 supplier; b = '+pins['complex_coarse']+'; no combined kappa claim',flush=True)
 except BaseException as e:write(out/'FAILURE.json',dict(status='FAIL',error=str(e),completed_stages=stages));raise
if __name__=='__main__':main()
