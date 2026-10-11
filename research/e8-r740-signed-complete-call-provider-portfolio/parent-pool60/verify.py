"""Finite whole-owner pooled60 plus direct8 complex451, conditional interfaces explicit."""
from pathlib import Path
import json,gzip,hashlib,shutil,subprocess,sys,os
if not __debug__:raise SystemExit('Assertions required')
P=Path(__file__).resolve().parent;D=P/'derived';D.mkdir(exist_ok=True);rd=lambda p:json.loads(p.read_text());gz=lambda p:json.loads(gzip.decompress(p.read_bytes()));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda p:hashlib.sha256(gzip.decompress(p.read_bytes())).hexdigest()
E=rd(P/'EXPECTED.json');M=rd(P/'SOURCE-MANIFEST.json')
for n,h in M['files'].items():assert sha(P/n)==h,n
parent=P/'parent-prefix60';assert sha(parent/'SOURCE-MANIFEST.json')==E['parent_manifest_sha256']
for n,h in rd(parent/'SOURCE-MANIFEST.json')['files'].items():assert sha(parent/n)==h,n
calls=[];env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
def run(name,args):
 print('RUN',name,flush=True);calls.append(name)
 with (D/(name+'.log')).open('w')as out:subprocess.run([sys.executable,'-B',*map(str,args)],env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
 print('PASS',name,flush=True)
run('entire-immutable-published-signed60-default',[parent/'verify.py'])
W=D/'replay'
if W.exists():shutil.rmtree(W)
shutil.copytree(parent/'derived/replay',W);shutil.copytree(P/'sources',W,dirs_exist_ok=True)
A=W/'experiments/architecture/whole-owner-pooling-v4/bit60';C=W/'experiments/architecture/complex-direct8-eleven451';I=W/'experiments/architecture/independent-audit';B=W/'experiments/architecture/pr454-signed-extra-v4/with-prefix60'
# Parent source identity is numerical/native byte identity, never a substituted provider.
for n in ['word.json','word.json.gz','RESULT.json','decoder-and-dirt.json','signed-records.bin','SELECTION.json','PAIR-SELECTION.json','records/249-records.bin','records/249-states.json','records/frames.json']:
 assert (A/'local'/n).read_bytes()==(B/n).read_bytes(),n
run('fresh-local980-dirt-inverse-adjoint-controls',[A/'local/signed_source.py'])
assert (A/'local/signed-records.bin').read_bytes()==(B/'signed-records.bin').read_bytes()
run('fresh-local-literal-operator',[A/'verify_local.py'])
run('fresh-complex800-signed-dirt-inverse-adjoint',[I/'complex451_local.py'])
run('fresh-complex-local-global-phase',[I/'complex451_local_phase.py','complex-direct8-eleven451'])
run('fresh-complex-literal176048-176144-primitives',[C/'primitive_audit.py'])
run('independent-complex-literal-primitives',[I/'complex451_primitive.py','complex-direct8-eleven451'])
run('fresh-complex-data-idle-terminal-phase',[C/'geometry-audit/complex_phases.py',C/'split-centres/CANONICAL-WORD.json.gz',C/'hosted/DATA-PHASES.json'])
run('fresh-complex-eleven-hosted-template',[C/'complex_emit.py',C/'split-centres',C/'hosted'])
assert canon(C/'hosted/GLOBAL-TEMPLATE.json.gz')==E['complex_template_canonical_sha256'];assert rd(C/'hosted/GLOBAL.json')['profile']==E['complex_profile']
run('fresh-complex-source-digest-19controls',[C/'geometry-audit/complex_audit.py',C/'split-centres',C/'hosted'])
run('fresh-complex6160-full89-sigma',[C/'geometry-audit/selected_sigma.py'])
run('independent-complex49280-owners-phase-sigma',[I/'complex451_geometry.py'])
run('independent-complex8520-data-phase-identities',[I/'complex451_data_phases.py'])
run('independent-complex-tenrows24bridges',[I/'complex451_global_recipe.py'])
run('fresh-complex-rational-moment',[C/'moment.py'])
run('fresh-complex-full-primitive-invoice',[C/'invoice.py'])
run('independent-complex-invoice-secondengine',[I/'complex451_invoice.py'])
run('whole-owner-selection-replay',[A/'nominate.py','--replay'])
run('fresh-pooled-owner-template1713800instructions',[A/'emit.py','--word',A/'local/word.json.gz','--local-check',A/'local','--isometries',A/'ISOMETRIES.json','--out',A])
assert canon(A/'GLOBAL-TEMPLATE.json.gz')==E['bit_template_canonical_sha256'];g=rd(A/'GLOBAL.json');assert g['profile']==E['bit_profile'];assert (g['live'],g['physical'],g['hosted_residuals'],g['deficit'])==(9600,9609,65120,3264)
run('fresh-all65120-concrete78-sigma',[A/'hosted_sigma.py'])
run('fresh-target1320charts10560owners2520controls',[A/'target_address.py'])
op=rd(A/'TARGET-OPERATOR.json');assert op['source_template_sha256']==canon(A/'GLOBAL-TEMPLATE.json.gz') and len(op['checks'])==1320 and len(op['controls_rejected'])==2520 and op['actual_global_owner_gate_instances']==10560
for name in ['whole_pool60_word.py','whole_pool_bit_assignment60.py','whole_pool_bit_template60.py','whole_pool_sigma60.py','whole_pool_prefix_cut60.py','whole_pool60_operator_review.py']:
 run('independent-'+name[:-3],[I/name])
run('fresh-paid159prefix532cube-wholeowner-fees',[A/'local/bound.py']);assert rd(A/'local/GLOBAL-BOUND.json')['finite']==E['finite']
run('fresh-bit-rational-moment',[A/'moment.py'])
run('fresh-dualengines-eight47-bootstrap-grid-cap-row',[A/'refine_nomination.py']);r=rd(A/'REFINED-NOMINATION.json');assert r['kappa']==E['kappa']and len(r['bootstrap'])==8 and len(r['strict_constraints'])==47
run('independent-complete-invoice-eight47',[I/'whole_pool_arithmetic60.py'])
assert calls.count('entire-immutable-published-signed60-default')==1
res={'status':'PASS_SOURCE_CLOSED_CONDITIONAL_POOLED60_AND_COMPLEX451_FINITE_RELEASE','source_manifest_sha256':sha(P/'SOURCE-MANIFEST.json'),'kappa':E['kappa'],'whole_helper_owners':65120,'foreign_replica_owners':52484,'full_sigma_columns':78,'literal_instructions':1713800,'complex_sigma_maps':6160,'complex_owner_instances':49280,'target_charts':1320,'target_owner_gates':10560,'target_controls':2520,'prefix_bits':159,'three_level_bits':532,'charged_bits':1024,'row_coefficient':19431,'bootstrap':8,'strict_constraints':47,'scope':'Stage-cut prefix relies on complete physical helper endpoints being address permutations with restored work, full-cover data owner bijections, and every idle host pair differing from active pair on all replicas. Actual finite assignment/operator/invoice checked; universal stage-cut dirty-slot/full-call and current-label target-as-source weighted compiler, inherited all-size chart/commonprime/precision/tape/recovery/analytic/C_full remain conditions. No nativeF2 provider, splithelper, new GL/norm2 compiler, global optimum or unconditional theorem.'}
(D/'POOLED-RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
