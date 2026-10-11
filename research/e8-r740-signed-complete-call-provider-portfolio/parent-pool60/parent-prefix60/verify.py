"""Source-closed conditional routed target-prefix finite composition."""
from pathlib import Path
import hashlib,json,gzip,shutil,subprocess,os,sys
P=Path(__file__).resolve().parent;D=P/'derived';D.mkdir(exist_ok=True)
if not __debug__:raise SystemExit('Assertions required')
rd=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
E=rd(P/'EXPECTED.json');manifest=rd(P/'SOURCE-MANIFEST.json')
for f,h in manifest['files'].items():assert sha(P/f)==h,f
parent=P/'parent-prefix56';assert sha(parent/'SOURCE-MANIFEST.json')==E['parent_manifest_sha256']
for f,h in rd(parent/'SOURCE-MANIFEST.json')['files'].items():assert sha(parent/f)==h,f
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
def run(name,args):
 print('RUN',name,flush=True)
 with(D/(name+'.log')).open('w')as out:subprocess.run([sys.executable,'-B',*map(str,args)],env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
 print('PASS',name,flush=True)
run('entire-immutable-published-prefix56-default',[parent/'verify.py'])
W=D/'replay'
if W.exists():shutil.rmtree(W)
shutil.copytree(parent/'derived/replay',W);shutil.copytree(P/'sources',W,dirs_exist_ok=True)
A=W/'experiments/architecture/pr454-signed-extra-v4/with-prefix60';G=A/'global';S=G/'signed';I=W/'experiments/architecture/signed60-independent';V=W/'experiments/verification/target-prefix60-independent'
run('fresh-target-prefix-source980-dirt-inverse-adjoint-controls',[A/'construct.py'])
run('actual-address-pullback1320-owner10560-wrongroute2520',[A/'target_address.py']);assert sha(A/'OPERATOR.json')==E['operator_sha256']
shutil.copyfile(A/'OPERATOR.json',G/'TARGET-OPERATOR.json')
run('fresh-global-local980-signed-source',[S/'signed_source.py']);assert sha(S/'signed-records.bin')==E['signed_record_sha256']
Q=V/'signed-rerun';shutil.copytree(S,Q,dirs_exist_ok=True)
# This output location has two fewer path components than the producer source.
source=(Q/'signed_source.py').read_text();assert 'R=P.parents[5]'in source
(Q/'signed_source.py').write_text(source.replace('R=P.parents[5]','R=P.parents[3]'))
run('independent-fresh-endpoint-reconstruction',[Q/'signed_source.py'])
run('independent-actual980-word',[I/'audit_word.py'])
run('independent-last-prefix-cuts',[I/'prefix.py'])
run('independent-relative-addresses',[I/'addresses.py'])
run('independent-local-paid-units',[I/'units_prefix.py'])
run('independent-own88-call-binding',[I/'owners.py'])
run('actual-widths-selection-reemit',[G/'nominate.py','--replay'])
run('actual-eleven-hosted-template-reemit',[G/'emit.py','--word',G/'word.json.gz','--local-check',S,'--isometries',G/'ISOMETRIES.json','--out',G/'hosted'])
g=rd(G/'hosted/GLOBAL.json');assert g['profile']==E['profile'];assert(g['live'],g['physical'],g['hosted_residuals'],g['deficit'])==(9600,9609,65120,3264)
assert hashlib.sha256(gzip.decompress((G/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()==E['template_canonical_sha256']
old=W/'experiments/architecture/target-prefix-multipair-complete/global/hosted'
assert (G/'hosted/GEOMETRY.json').read_bytes()==(old/'GEOMETRY.json').read_bytes()
newt=rd_template=json.loads(gzip.decompress((G/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()))
oldt=json.loads(gzip.decompress((old/'GLOBAL-TEMPLATE.json.gz').read_bytes()))
assert len(newt['calls'])==len(oldt['calls'])==88
assert [c['owners']for c in newt['calls']]==[c['owners']for c in oldt['calls']]
run('all9340-columns-24bridges-22schedule-controls',[G/'audit.py',S,G/'hosted'])
run('actual-owner-window-paid-profile',[G/'audit_assignment.py'])
run('all8140-complete78-column-sigma',[G/'hosted_sigma.py'])
run('fresh-paid159prefix532cube-253693440selectors',[S/'bound.py']);assert rd(S/'GLOBAL-BOUND.json')['finite']==E['finite']
run('two-engines-eight47-strict-grid-cap-row',[G/'refine_nomination.py']);r=rd(G/'REFINED-NOMINATION.json');assert all(r[k]==E[k]for k in ['kappa','bit_lower','complex_lower']);assert len(r['bootstrap'])==8 and len(r['strict_constraints'])==47
run('independent-full-prefix',[V/'review_prefix.py'])
run('independent-dual-engine-full47',[V/'review_arithmetic.py'])
result=dict(status='PASS_SOURCE_CLOSED_CONDITIONAL_ROUTED_TARGET_PREFIX60_FINITE_EXTENSION',kappa=E['kappa'],source_manifest_sha256=sha(P/'SOURCE-MANIFEST.json'),address_columns=156,relative_chart_instances=1320,actual_owner_instances=10560,address_controls=2520,extra_selectors=253693440,scope='Explicit currently-labelled target-as-source pointwise routed weighted compiler extension. Finite arbitrary-array address algebra with donor read f_w(Rx), R=CwCu^-1 (value pushforward R^-1), literal signed inverse. Inherited hosting/correlated-bank/reflected-chart/general all-size compiler interfaces remain conditional. No unconditional fully expanded physical primitive admission.')
(D/'TARGET-RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
