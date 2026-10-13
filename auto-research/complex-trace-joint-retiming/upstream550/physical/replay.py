"""Fresh complex-only scalar, frame, phase, owner and finite-invoice admission.

All mathematical verifier sources and data are pinned in UPSTREAM-SOURCES.json.
This orchestration harness was prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
if not __debug__:raise SystemExit('Assertions must remain enabled')
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--word',type=Path,required=True)
ap.add_argument('--word-sha256',required=True)
ap.add_argument('--out',type=Path,required=True)
ap.add_argument('--expected-price',type=Path)
ap.add_argument('--plan',type=Path,help='Optional new plan; only its complete profile may differ from pinned548.')
a=ap.parse_args();O=a.out.resolve();assert not O.exists() and not O.is_relative_to(ROOT)
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
for rel,pin in read(ROOT/'UPSTREAM-SOURCES.json')['files'].items():
 b=(ROOT/rel).read_bytes();assert blob(b)==pin['git_blob_sha1'] and sha(ROOT/rel)==pin['sha256'] and len(b)==pin['bytes'],rel
assert sha(a.word)==a.word_sha256,'constructor word hash mismatch'
O.mkdir(parents=True);inp=O/'inputs';inp.mkdir();shutil.copyfile(a.word,inp/'FULL-WORD.json.gz')
if a.expected_price:shutil.copyfile(a.expected_price,inp/'EXPECTED-PRICE.json')
baseline=read(ROOT/'data/SAT534-PLAN.json')
plan=read(a.plan)if a.plan else baseline
assert {k:v for k,v in plan.items()if k!='profile'}=={k:v for k,v in baseline.items()if k!='profile'},'changed controller/window geometry'
if a.expected_price:assert plan['profile']==read(inp/'EXPECTED-PRICE.json')['global_profile']
if a.plan:shutil.copyfile(a.plan,inp/'PLAN.json')
else:shutil.copyfile(ROOT/'data/SAT534-PLAN.json',inp/'PLAN.json')
dump(inp/'PLAN-CHECK.json',dict(pinned_plan_sha256=sha(ROOT/'data/SAT534-PLAN.json'),actual_plan_sha256=sha(inp/'PLAN.json'),changed_fields=['profile']if plan['profile']!=baseline['profile']else[],all_non_profile_fields_equal=True))
P=ROOT/'vendor/pr531';D=ROOT/'data';stages=[];began=time.monotonic()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONUTF8='1');env.pop('PYTHONOPTIMIZE',None)
def run(name,script,*args):
 t=time.monotonic();log=O/(name+'.log');print('RUN',name,flush=True)
 cmd=[sys.executable,'-B',str(ROOT/'code/run_portable.py'),str(script),*map(str,args)]
 with log.open('w',encoding='utf-8',newline='\n')as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-t,script=script.relative_to(ROOT).as_posix(),script_sha256=sha(script),log_sha256=sha(log)))
 dump(O/'STAGES.json',stages)
 if r.returncode:raise RuntimeError(name+' failed\n'+log.read_text()[-6000:])
 print('PASS',name,flush=True)
try:
 local=O/'complex-local';base=O/'complex-base';host=O/'complex-hosted';audit=O/'complex-audit';audit.mkdir()
 run('complex-scalar-frame-transport',P/'code/audit_and_transport.py','--raw',inp/'FULL-WORD.json.gz','--routing',D/'ROUTING-CANONICAL-WORD.json.gz','--out',local)
 run('complex-emit-local',P/'code/emit_local.py',local)
 run('complex-independent-local',P/'code/audit_local.py',local)
 run('complex-normalized-wrappers',P/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
 run('complex-every-local-phase',ROOT/'code/phases_full.py',local,P/'vendor/clifford')
 run('complex-bind-retained-data',P/'code/prepare_supplier_base.py','--data-base',D/'controller-input','--local',local,'--out',base)
 run('complex-emit-whole-owners',P/'code/emit_supplier_hosted.py','--base',base,'--owners',D/'SAT-OWNERS.json.gz','--plan',inp/'PLAN.json','--out',host)
 run('complex-independent-owners-and-controls',P/'code/audit_supplier_hosted.py',base,host,audit/'ASYNC-AUDIT.json','--mutation-controls')
 run('complex-finite-invoice',P/'code/invoice_final.py','--base',base,'--hosted',host,'--audit',audit,'--out',audit,'--retained-invoice',D/'RETAINED-INVOICE.json')
 owner=read(audit/'OWNERS-AND-PROFILE.json');invoice=read(audit/'PREFIX-AND-INVOICE.json');phase=read(local/'CLIFFORD-REVIEW.json');controls=read(audit/'ASYNC-AUDIT.json');native=read(local/'INDEPENDENT-LOCAL-REPLAY.json')
 assert phase['all_child_equalities_include_global_phase'] and phase['endpoint_adapters']==224
 assert controls['mutation_controls_run'] and len(controls['mutations_rejected'])==7
 assert all(invoice['strict_checks'].values()) and owner['template_sha256']==invoice['template_sha256']
 for orientation in ('forward','backward'):
  j=invoice['local'][orientation]
  assert j['all_exact_columns']==728 and j['dirty_helper_columns']==504 and j['all_dirty_helper_columns_restored'] and j['private_centres_and_coefficient_work_cleared']
 assert native['paid_profiles']['forward']==native['paid_profiles']['backward']
 if a.expected_price:assert owner['paid_profile']==read(inp/'EXPECTED-PRICE.json')['global_profile']
 result=dict(status='PASS_FRESH_COMPLEX_ONLY_FULL_PHYSICAL_ADMISSION',input_word_sha256=a.word_sha256,canonical_word_sha256=sha(local/'CANONICAL-WORD.json.gz'),local_program_sha256=sha(local/'LOCAL-PROGRAMS.json.gz'),phase_recipe_sha256=sha(local/'CLIFFORD-RECIPES.json'),template_sha256=owner['template_sha256'],local_profile=native['paid_profiles']['forward'],global_profile=owner['paid_profile'],live=owner['live'],physical=owner['physical'],deficit=owner['deficit'],hosted_residuals=owner['hosted_residuals'],actual_charts=owner['actual_73column_sigmas'],phase_edges=phase['directed_edges'],endpoint_adapters=phase['endpoint_adapters'],prefix_bits=invoice['global_prefix_bits'],charged_prefix_bits=invoice['charged_prefix_bits'],seconds=time.monotonic()-began,python=sys.version,scope='Finite complex-only admission. No bit replay or outer assembly is claimed here; retained all-size, common-label, hosting and analytic contracts remain conditional.')
 dump(O/'RESULT.json',result)
 paths=['inputs/FULL-WORD.json.gz','inputs/PLAN.json','inputs/PLAN-CHECK.json','complex-local/INDEPENDENT-LOCAL-REPLAY.json','complex-local/CLIFFORD-REVIEW.json','complex-local/WRAPPER-CHECKS.json','complex-audit/ASYNC-AUDIT.json','complex-audit/OWNERS-AND-PROFILE.json','complex-audit/PREFIX-AND-INVOICE.json','RESULT.json']
 dump(O/'RECEIPT.json',dict(status=result['status'],source_pins_sha256=sha(ROOT/'UPSTREAM-SOURCES.json'),harness_sha256=sha(Path(__file__)),stages=stages,artifacts={p:sha(O/p)for p in paths}))
 print(result['status'],result['seconds'],flush=True)
except BaseException as e:
 dump(O/'FAILURE.json',dict(error=repr(e),stages=stages));raise
