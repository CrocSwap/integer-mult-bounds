"""Portable finite local/global admission runner; standard-library Python only."""
import argparse,os,sys,subprocess,json,hashlib,gzip,time,shutil
from pathlib import Path
sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--base',required=True);p.add_argument('--candidate',required=True);p.add_argument('--output',required=True);p.add_argument('--phase-receipts');a=p.parse_args()
here=Path(__file__).resolve().parent;source=Path(a.source).resolve();base=Path(a.base).resolve();candidate=Path(a.candidate).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest();read=lambda x:json.loads(Path(x).read_text(encoding='utf-8-sig'))
geometry=source/'geometry' if (source/'geometry').is_dir() else source/'work/odd-stages'
env=dict(os.environ,COMPLEX_SOURCE=str(source),COMPLEX_BASE_CERT=str(base),COMPLEX_CERT=str(candidate),COMPLEX_OUTPUT=str(out),PYTHONDONTWRITEBYTECODE='1')
pins={str(q):sha(q) for q in list(here.glob('*.py'))+[base,candidate]};stages=[]
def stage(name):
 start=time.monotonic();log=out/(name+'.log')
 with log.open('w',encoding='utf-8') as f:r=subprocess.run([sys.executable,'-B',str(here/(name+'.py'))],env=env,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(name+' failed; inspect '+str(log))
 stages.append(dict(stage=name,seconds=time.monotonic()-start,log_sha256=sha(log)));print('PASS',name,flush=True)
stage('complex-compose')
if a.phase_receipts:
 old=Path(a.phase_receipts).resolve();review=read(old/'CLIFFORD-REVIEW.json')
 assert review['status']=='PASS_EXACT_GAUSSIAN_CLIFFORD_LOCAL_FRAMES_AND_CHILDREN'
 assert review['certificate_sha256']==sha(candidate) and review['engine_sha256']==sha(geometry/'clifford_exact.py')
 assert review['recipe_sha256']==sha(old/'CLIFFORD-RECIPES.json') and review['all_child_equalities_include_global_phase']
 for name in ('CLIFFORD-REVIEW.json','CLIFFORD-RECIPES.json'):shutil.copyfile(old/name,out/name)
 (out/'PHASE-REUSE.json').write_text(json.dumps(dict(status='PASS_BYTE_BOUND_SAME_CANDIDATE_AND_ENGINE_PHASE_REUSE',review_sha256=sha(old/'CLIFFORD-REVIEW.json'),recipes_sha256=sha(old/'CLIFFORD-RECIPES.json'),candidate_sha256=sha(candidate),engine_sha256=sha(geometry/'clifford_exact.py')),indent=2))
 print('PASS byte-bound canonical phase receipt reuse',flush=True)
else:stage('complex-clifford')
for name in ('data_phases','global-template','audit-global-template','join-admission'):stage(name) if name!='join-admission' else None
# join-admission takes the output directory as a positional argument.
log=out/'join-admission.log'
with log.open('w',encoding='utf-8') as f:r=subprocess.run([sys.executable,'-B',str(here/'join-admission.py'),str(out)],env=env,stdout=f,stderr=subprocess.STDOUT)
assert r.returncode==0,'join-admission failed'
local=read(out/'JOINED-ADMISSION.json');glob=read(out/'GLOBAL-REVIEW.json');audit=read(out/'INDEPENDENT-TEMPLATE-AUDIT.json')
assert glob['template_sha256']==audit['template_sha256'] and glob['profile']==audit['paid_profile']==read(out/'RESULT.json')['profile']
assert glob['whole_residual_assignments']==9*8*read(out/'RESULT.json')['R'] and glob['invocations']==72
assert audit['coarse_complex']==local['complex_coarse'] and audit['bridge_omission_controls']==9
assert len(audit['structural_controls_rejected'])==5 and glob['owner_injections'] and glob['work_lifetimes_freshly_revalidated']
assert all(sha(q)==h for q,h in pins.items())
final=dict(status='PASS_FINITE_CHANGED_LOCAL_AND_GLOBAL_TEMPLATE_ADMISSION',complex_coarse=local['complex_coarse'],profile=local['profile'],m=73,stock=glob['live'],physical=glob['physical'],bridge=local['bridge'],local_admission_sha256=sha(out/'JOINED-ADMISSION.json'),global_review_sha256=sha(out/'GLOBAL-REVIEW.json'),independent_global_audit_sha256=sha(out/'INDEPENDENT-TEMPLATE-AUDIT.json'),global_template_sha256=glob['template_sha256'],stages=stages,runner_source_sha256=pins[str(here/'run-admission.py')],source_hashes=pins,scope='Finite E8 changed-source local and global template checks. Retains inherited compressed-window, arbitrary-bank correlated-dirt, local/compiler, precision, analytic, restored-row and completed ordinary-wrapper theorem assumptions. No Lean build or unconditional multiplication exponent proof.')
(out/'FINAL-ADMISSION.json').write_text(json.dumps(final,indent=2)+'\n');print(final['status'],final['complex_coarse'])
