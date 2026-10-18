#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Regenerate literal T530 owners, apply only the paid local-bill delta, and audit."""
from pathlib import Path
from collections import Counter
import argparse,gzip,hashlib,json,os,subprocess,sys,time

HERE=Path(__file__).resolve().parent

def need(ok,message):
 if not ok:raise ValueError(message)
def read(path):
 raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def snapshot():
 return {p.relative_to(HERE).as_posix():sha(p) for p in HERE.rglob('*') if p.is_file()}

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--out',type=Path,required=True,help='Fresh output directory outside this package')
 ap.add_argument('--repo',type=Path,default=HERE.parents[2],help='Checkout containing the 13 pinned main dependencies')
 args=ap.parse_args();out=args.out.resolve();repo=args.repo.resolve()
 need(__debug__ and not sys.flags.optimize,'Normal Python with enabled assertions is required')
 try:import numpy
 except ImportError:raise SystemExit('NumPy is required for the independent literal audit')
 need(out!=HERE and HERE not in out.parents,'Output must be outside the immutable package')
 need(not out.exists(),'Output directory must be fresh')
 before=snapshot();inputs=read(HERE/'PUBLIC-INPUTS.json');derivation=read(HERE/'DERIVATION.json')
 for rel,digest in inputs['repo_files'].items():need(sha(repo/rel)==digest,'Repository source hash: '+rel)
 for rel,key in [('independent_literal.py','derived_script_sha256'),('upstream/independent_literal.py','predecessor_script_sha256')]:
  need(sha(HERE/rel)==derivation[key],'Auditor source hash: '+rel)
 for rel,digest in read(HERE/'upstream/ARTIFACTS.json').items():need(sha(HERE/'upstream'/rel)==digest,'Upstream artifact: '+rel)
 out.mkdir(parents=True,exist_ok=False);env=os.environ.copy()
 env.update({'OWNER_SOURCE_REPO':str(repo),'PYTHONDONTWRITEBYTECODE':'1'})
 start=time.monotonic();literal=out/'literal'
 # The frozen producer retains its original local bill and source checks.
 subprocess.run([sys.executable,'-B',str(HERE/'upstream/portable_expand.py'),'--out',str(literal)],env=env,check=True)
 generated=read(literal/'PROFILE.json');expected=read(HERE/'upstream/EXPECTED.json')
 need(sha(literal/'PROFILE.json')==expected['literal_files']['PROFILE.json'],'Original generated profile binding')
 oldlocal={1:2439,2:726,3:224,4:102,5:20,8:8};newlocal=None
 for tag in ('base','extra'):
  path=HERE/'native'/f'checked-{tag}'/'CANONICAL-WORD.json.gz'
  need(sha(path)==derivation['native_pins'][tag],'Fresh canonical source pin')
  local={int(k):v for k,v in read(path)['local_profile'].items()}
  need(newlocal is None or newlocal==local,'Both actual providers have the same local bill');newlocal=local
 need(newlocal=={1:2437,2:724,3:226,4:102,5:20,8:8},'Expected retimed local bill')
 calls=len(read(literal/'ORDER.json'));need(calls==4770,'All T530 calls')
 total=Counter({int(k):v for k,v in generated.items()})
 for rank in oldlocal.keys()|newlocal.keys():total[rank]+=calls*(newlocal.get(rank,0)-oldlocal.get(rank,0))
 need(all(v>0 for v in total.values()),'Positive paid histogram')
 profile_text=json.dumps(dict(sorted(total.items())),indent=2)+'\n'
 (literal/'PROFILE.json').write_text(profile_text)
 need(total==Counter({int(k):v for k,v in read(HERE/'RESULT.json')['profile'].items()}),'New full invoice matches retained receipt')
 env.update({'OWNER_UPSTREAM_DIR':str(HERE/'upstream'),'OWNER_LITERAL_DIR':str(literal),'OWNER_NATIVE_DIR':str(HERE/'native'),'OWNER_AUDIT_OUTPUT':str(out/'RESULT.json')})
 subprocess.run([sys.executable,'-B',str(HERE/'semantic_gate_controls.py')],env=env,check=True)
 semantic=read(out/'SEMANTIC-GATES.json')
 need(semantic['status']=='PASS_FIVE_EXACT_PRODUCTION_GATE_MUTATIONS_AND_FIVE_DISABLE_SENSITIVITIES'
      and semantic['semantic_mutants_rejected']==semantic['gate_disable_sensitivities']==5
      and semantic['historical_reject_lambdas_counted'] is False,'Fresh semantic gate controls')
 need(semantic['source_sha256']==derivation['derived_script_sha256']
      and semantic['checker_sha256']==sha(HERE/'semantic_gate_controls.py')
      and semantic['positive_receipt_sha256']==sha(out/'RESULT.json'),'Semantic gate receipt binding')
 retained=read(HERE/'RESULT.json');actual=read(out/'RESULT.json')
 for key in ('status','replicas','calls','roles','physical','idle','profile','script_sha256','controls','scope'):
  need(actual[key]==retained[key],'Independent receipt mismatch: '+key)
 need(snapshot()==before,'Package changed during replay')
 receipt={'status':'PASS_LEAN_REGENERATED_OWNER_AUDIT','seconds':time.monotonic()-start,'python':sys.version,'numpy':numpy.__version__,'fresh_literal_reconstruction':True,'fresh_independent_owner_audit':True,'fresh_semantic_gate_mutations':5,'gate_disable_sensitivities':5,'historical_reject_lambdas_counted':False,'semantic_gate_receipt_sha256':sha(out/'SEMANTIC-GATES.json'),'package_files_unchanged':True,'source_files':len(inputs['repo_files']),'upstream_artifacts':len(read(HERE/'upstream/ARTIFACTS.json')),'derived_profile':dict(sorted(total.items())),'scope':'Fresh finite reconstruction and independent ownership/invoice checks; canonical native frame tables are authenticated inputs, not operator proofs rerun by this command.'}
 (out/'RUN.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
