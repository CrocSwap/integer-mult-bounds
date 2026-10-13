"""Fresh deterministic complex replay. Default requires literalnewownerplan.
Prepared with OpenAI Codex assistance. Apache-2.0.
The --local-only diagnostic does not certify global hosting or a kappa record.
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
if not __debug__:raise SystemExit('Assertions must remain enabled')
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--local-only',action='store_true');a=ap.parse_args();O=a.work.resolve();assert not O.exists()and not O.is_relative_to(P)
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
# Final package manifest is supplied after the literalownerplan and assembly
# have been integrated; source pins are mandatory even for localdiagnostics.
if(P/'MANIFEST.json').exists():
 actual={q.relative_to(P).as_posix():sha(q)for q in P.rglob('*')if q.is_file()and q!=P/'MANIFEST.json'and'__pycache__'not in q.parts};assert actual==read(P/'MANIFEST.json'),'package manifest'
else:assert a.local_only,'full replay requires final manifest'
for rel,pin in read(P/'SOURCE-PINS.json')['files'].items():assert sha(P/rel)==pin['sha256'],rel
if not a.local_only:assert(P/'data/OWNERS.json.gz').is_file()and(P/'data/PLAN.json').is_file(),'literal new owners and plan required'
O.mkdir(parents=True);steps=[];start=time.monotonic();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONUTF8='1');env.pop('PYTHONOPTIMIZE',None)
def run(name,script,*args):
 t=time.monotonic();log=O/(name+'.log');print('RUN',name,flush=True)
 with log.open('w')as f:r=subprocess.run([sys.executable,'-B',str(P/'code/run_portable.py'),str(script),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=env)
 steps.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));dump(O/'STAGES.json',steps)
 if r.returncode:raise RuntimeError(name+' failed\n'+log.read_text()[-6000:])
 print('PASS',name,flush=True)
v=P/'vendor/pr552';V=v/'complex-global/vendor531';local=O/'complex-local'
run('reconstruct552-and-promote8',P/'code/reconstruct.py','--out',O/'reconstruction')
run('all-columns-native-frames',V/'code/audit_and_transport.py','--raw',O/'reconstruction/promoted/FULL-WORD.json.gz','--routing',v/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz','--out',local)
run('emit-both-reflected-ledgers',V/'code/emit_local.py',local)
run('independent-local-and-controls',V/'code/audit_local.py',local)
run('normalized-wrappers',V/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
if a.local_only:
 dump(O/'RESULT.json',dict(status='PASS_LOCAL_DIAGNOSTIC_ONLY',word_sha256=sha(O/'reconstruction/promoted/FULL-WORD.json.gz'),local=read(local/'INDEPENDENT-LOCAL-REPLAY.json'),scope='No phase/global/invoice/assembly admission claimed.'));sys.exit(0)
run('all-phase-recipes',P/'code/phases_full.py',local,V/'vendor/clifford')
run('literal-owners-full-invoice',v/'complex-global/run_complex44.py',V,v/'complex-global/vendor535',local,P/'data/OWNERS.json.gz',P/'data/PLAN.json',P/'code/run_portable.py',O/'complex-global')
run('two-engine-exact-assembly',P/'code/assemble.py',P,O/'complex-global',O/'ASSEMBLY.json')
run('assembly-admission-controls',P/'code/assembly_controls.py','--owner',O/'complex-global/audit/OWNERS-AND-PROFILE.json','--invoice',O/'complex-global/audit/PREFIX-AND-INVOICE.json','--out',O/'ASSEMBLY-CONTROLS.json')
assembly=read(O/'ASSEMBLY.json');phase=read(local/'CLIFFORD-REVIEW.json');native=read(local/'INDEPENDENT-LOCAL-REPLAY.json');owners=read(O/'complex-global/audit/OWNERS-AND-PROFILE.json');invoice=read(O/'complex-global/audit/PREFIX-AND-INVOICE.json')
assert phase['all_child_equalities_include_global_phase']and phase['endpoint_adapters']==224 and phase['directed_edges']==2929
assert len(read(O/'complex-global/audit/ASYNC-AUDIT.json')['mutations_rejected'])==7
assert native['paid_profiles']['forward']==native['paid_profiles']['backward']and len(native['negative_controls_rejected'])==11
assert all(invoice['strict_checks'].values())and owners['template_sha256']==invoice['template_sha256']
result=dict(status='PASS_COMPLEX_EIGHT_RANK5_PIVOTS_AND_CITED_BIT',kappa=assembly['kappa'],kappa_decimal=assembly['kappa_decimal'],complex_lower=assembly['complex_lower'],bit_lower=assembly['bit_lower'],word_sha256=sha(O/'reconstruction/promoted/FULL-WORD.json.gz'),local_profile=native['paid_profiles']['forward'],global_profile=owners['paid_profile'],seconds=time.monotonic()-start,scope=assembly['scope']);assert result['kappa_decimal']=='0.001592517889315014'
dump(O/'RESULT.json',result)
dump(O/'RECEIPT.json',dict(status=result['status'],steps=steps,artifacts={name:sha(O/name)for name in ['RESULT.json','ASSEMBLY.json','ASSEMBLY-CONTROLS.json','reconstruction/promoted/PROMOTION.json','complex-local/INDEPENDENT-LOCAL-REPLAY.json','complex-local/CLIFFORD-REVIEW.json','complex-global/audit/ASYNC-AUDIT.json','complex-global/audit/OWNERS-AND-PROFILE.json','complex-global/audit/PREFIX-AND-INVOICE.json']},manifest_sha256=sha(P/'MANIFEST.json')))
print(json.dumps(result,indent=2))
