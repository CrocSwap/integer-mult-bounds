"""Source-closed signed79 eleven-stage finite conditional extension default."""
from pathlib import Path
import hashlib,json,gzip,shutil,subprocess,os,sys
P=Path(__file__).resolve().parent;D=P/'derived';D.mkdir(exist_ok=True)
if not __debug__:raise SystemExit('Assertions required')
rd=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
E=rd(P/'EXPECTED.json');manifest=rd(P/'SOURCE-MANIFEST.json')
for f,h in manifest['files'].items():assert sha(P/f)==h,f
parent=P/'parent-hosted';pm=rd(parent/'SOURCE-MANIFEST.json')
for f,h in pm['files'].items():assert sha(parent/f)==h,f
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
def run(name,args,cwd=P):
 print('RUN',name,flush=True)
 with(D/(name+'.log')).open('w')as out:subprocess.run([sys.executable,'-B',*map(str,args)],cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
 print('PASS',name,flush=True)
run('immutable-parent-entire-default',[parent/'verify.py'])
W=D/'replay'
if W.exists():shutil.rmtree(W)
shutil.copytree(parent/'derived/replay',W)
shutil.copytree(P/'sources',W,dirs_exist_ok=True)
A=W/'experiments/stage-search/pr445-signed79-eleven';S=A/'signed';J=W/'experiments/architecture/joint-design';I=W/'experiments/architecture/independent-audit'
run('fresh-all980-signed-dirt-inverse-nine-controls',[S/'signed_source.py'])
r=rd(S/'RESULT.json');assert r['integer_kernel']['pivots']==79 and r['integer_kernel']['all_positive_start_responses_zero_over_Z']
assert r['arbitrary_helper_dirt_restored_exactly']and r['forward_then_signed_inverse_identity'];assert len(r['controls'])==9 and all(x['rejected']for x in r['controls']);assert sha(S/'signed-records.bin')==E['signed_record_sha256']
run('independent-79-word-and-common-frame',[I/'signed79_word.py'])
run('own-widths-reemit-selection',[A/'nominate.py','--replay'])
run('eleven-template-reemit',[A/'emit.py','--word',A/'word.json.gz','--local-check',S,'--isometries',A/'ISOMETRIES.json','--out',A/'hosted'])
g=rd(A/'hosted/GLOBAL.json');assert hashlib.sha256(gzip.decompress((A/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()==E['template_canonical_sha256'];assert g['profile']==E['profile'];assert(g['live'],g['physical'],g['hosted_residuals'],g['deficit'])==(9600,9609,65120,3264)
run('actual-eleven-schedule-owner-route-22-semantic-controls',[A/'audit.py',S,A/'hosted'])
run('independent-eleven-assignment',[I/'signed79_eleven_assignment.py'])
run('all8140-actual78-axis-isometries',[J/'hosted_sigma_eleven79.py'])
run('independent-all-selected-sigma',[I/'signed79_eleven_sigma.py'])
run('complete-signed-eleven-prefix-conservative-invoice',[S/'bound.py']);assert rd(S/'GLOBAL-BOUND.json')['finite']==E['finite']
run('two-moments-eight-47-grid-cap-and-rowproof',[A/'refine_nomination.py']);z=rd(A/'REFINED-NOMINATION.json');assert z['kappa']==E['kappa']and z['bit_lower']==E['bit_lower']and z['complex_lower']==E['complex_lower'];assert len(z['bootstrap'])==8 and len(z['strict_constraints'])==47
run('independent-invoice-second-engine-closed-bootstrap',[I/'signed79_eleven_arithmetic.py'])
run('independent-complete-prefix',[W/'experiments/verification/review_pr445_eleven79_prefix.py'])
run('independent-full47-twoengines-eight-thirddepth',[W/'experiments/verification/review_pr445_eleven79_arithmetic.py'])
result=dict(status='PASS_SOURCE_CLOSED_SIGNED79_ELEVEN_STAGE_HOSTED_FINITE_EXTENSION',kappa=E['kappa'],source_manifest_sha256=sha(P/'SOURCE-MANIFEST.json'),pivots=79,entrance_rank=103,live=9600,physical=9609,hosted_residuals=65120,bit_sigma_maps=8140,local_controls=9,assignment_semantic_controls=22,bridge_controls=24,continuations=8,strict_constraints=47,scope='Finite conditional eleven-stage/third-depth hosted extension. Inherited all-size weighted compiler, common-prime/chart/precision/tape/recovery, correlated-bank/compressed-window, selected sigma/selector address compiler, analytic/C_full and restored-row constants remain explicit. No unconditional fully-expanded primitive admission.')
(D/'ELEVEN-RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(result,indent=2))
