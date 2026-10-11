"""Full source-closed hosted finite extension replay. Assertions required."""
from pathlib import Path
import json,hashlib,subprocess,sys,os,shutil,gzip,copy
P=Path(__file__).resolve().parent;D=P/'derived';D.mkdir(exist_ok=True)
if not __debug__:raise SystemExit('Assertions required')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rd=lambda p:json.loads(p.read_text());E=rd(P/'EXPECTED.json');M=rd(P/'SOURCE-MANIFEST.json')
for n,h in M['files'].items():assert sha(P/n)==h,n
# Every immutable parent publication input is retained, including its prior manifest.
parent=rd(P/'parent-inputs/SOURCE-MANIFEST.json')
for n,h in parent['files'].items():
 f=P/n if n.startswith('evidence/')else P/'parent-inputs'/n
 assert sha(f)==h,n
pr442=rd(P/'PR442-SOURCE.json')
for z in pr442['files']:assert sha(P/'evidence/experiments/verification/proposal-scout/pr442'/z['local_path'])==z['sha256']
review=P/'evidence/experiments/verification/pr441-hosting-independent'
for n,h in rd(review/'PROJECTED-SCIENCE-GATE.json')['inputs'].items():assert sha(review/n)==h
runenv={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
def run(name,args,cwd=P):
 print('RUN',name,flush=True)
 with(D/(name+'.log')).open('w')as out:subprocess.run([sys.executable,'-B',*map(str,args)],cwd=cwd,env=runenv,stdout=out,stderr=subprocess.STDOUT,check=True)
 print('PASS',name,flush=True)
run('parent-full-native-signed-geometry',[P/'parent_verify.py'])
W=D/'replay';A=W/'experiments/stage-search/pr441-signed75-hosting';J=W/'experiments/architecture/joint-design';I=W/'experiments/architecture/independent-audit';F=W/'experiments/stage-search/pr441-signed-retime/full';B=F/'bit426-source-centres';C=W/'experiments/stage-search/pr433-split/full/split-centres'
for n,script,args in [('bit','bit_hosted.py',[B/'global',B]),('complex','complex_hosted.py',[C])]:
 out=D/('reemitted-'+n)
 if out.exists():shutil.rmtree(out)
 run('emit-'+n,[A/script,*args,out])
 expected=E[n+'_template_canonical_sha256'];assert hashlib.sha256(gzip.decompress((out/'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()==expected
 dest=A/('hosted'if n=='bit'else'complex-hosted')
 for file in out.iterdir():shutil.copyfile(file,dest/file.name)
run('bit-assignment',[J/'audit_hosted_template.py',B/'global',A/'hosted','--out',A/'hosted/INDEPENDENT-ASSIGNMENT.json'])
run('bit-concrete-sigma',[J/'hosted_sigma.py'])
run('complex-concrete-sigma-and-all-character-phase',[J/'complex_sigma.py'])
run('independent-bit-assignment',[I/'signed75_assignment.py'])
run('independent-bit-sigma',[I/'signed75_sigma.py'])
run('independent-complex-assignment-phase',[I/'complex_assignment.py'])
# Rebind generated proof receipt hashes only; actual route bound is fixed in EXPECTED science.
geo=rd(A/'hosted/GEOMETRY.json');geo['sigma_certificate_sha256']=sha(A/'hosted/HOSTED-SIGMA.json');geo['assignment_certificate_sha256']=sha(A/'hosted/INDEPENDENT-ASSIGNMENT.json');(A/'hosted/GEOMETRY.json').write_text(json.dumps(geo,indent=2)+'\n')
run('fresh-local-signed-nine-controls',[A/'signed/signed_source.py'])
r=rd(A/'signed/RESULT.json');assert sha(A/'signed/signed-records.bin')==E['signed_record_sha256'];assert len(r['controls'])==9 and all(c['rejected']for c in r['controls']);assert r['arbitrary_helper_dirt_restored_exactly']and r['forward_then_signed_inverse_identity']
run('both-profile-moments',[A/'price.py'])
run('complex-conservative-extra-selectors-invoice',[A/'complex_invoice.py'])
run('signed-complete-prefix-hosted-invoice',[A/'signed/bound.py']);assert rd(A/'signed/GLOBAL-BOUND.json')['finite']==E['finite']
# Independent rejecting assignment controls; recompute template hash to test semantics.
controls=[];original=json.loads(gzip.decompress((A/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()));g=rd(A/'hosted/GLOBAL.json')
for name in ('outside_window','overlap','missing_host','understated_stock','wrong_profile'):
 t=copy.deepcopy(original);gg=copy.deepcopy(g)
 if name=='outside_window':t['hosting']['slots'][0][4]=99
 elif name=='overlap':t['hosting']['slots'][1][0:3]=t['hosting']['slots'][0][0:3]
 elif name=='missing_host':t['hosting']['slots'].pop()
 elif name=='understated_stock':t['live']-=1
 else:gg['profile']['1']-=1
 raw=json.dumps(t,sort_keys=True,separators=(',',':')).encode();gg['template_sha256']=hashlib.sha256(raw).hexdigest();out=D/('mutation-'+name);out.mkdir(exist_ok=True);(out/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(raw,mtime=0));(out/'GLOBAL.json').write_text(json.dumps(gg))
 with(D/(name+'.log')).open('w')as log:ret=subprocess.run([sys.executable,'-B',str(J/'audit_hosted_template.py'),str(B/'global'),str(out),'--out',str(out/'RESULT.json')],env=runenv,stdout=log,stderr=subprocess.STDOUT)
 assert ret.returncode!=0,name;controls.append(name)
run('both-exact-moments-eight-47-and-grid-cap',[A/'compose.py','--complex',A/'complex/full','--bit',A/'signed','--native-bit',F,'--engines',W/'experiments/bit-search/pr433/source/research/split-centres-global/vendor/engines'])
c=rd(A/'REFINED-ASSEMBLY.json');assert c['kappa']==E['kappa']and c['bit_c']==E['bit_c']and c['complex_b']==E['complex_b'];assert len(c['bootstrap_chain'])-1==8 and len(c['assembly']['strict_constraints'])==47
run('independent-invoices-moments-closed-bootstrap',[I/'hosted_arithmetic.py'])
bs=rd(A/'hosted/HOSTED-SIGMA.json');cs=rd(A/'complex-hosted/HOSTED-SIGMA.json');assert bs['slots_per_replica']==4760 and cs['slots_per_replica']==4320 and cs['source_idle_phase_polynomials_checked']==2400
result=dict(status='PASS_SOURCE_CLOSED_OWN_SIGNED75_AND_FULLPHASE_COMPLEX_HOSTED_FINITE_EXTENSION',kappa=E['kappa'],source_manifest_sha256=sha(P/'SOURCE-MANIFEST.json'),bit_sigma_maps=4760,complex_sigma_maps=4320,all_character_phase_checks=2400,assignment_mutations_rejected=controls,parent_native_bank_controls=8,parent_bridge_controls=18,signed_controls=9,continuations=8,strict_constraints=47,scope='Finite conditional hosted interface extension; all-size compiler, rational chart/common-prime/precision/tape/recovery, correlated-bank/compressed-window, hosted sigma/selector address compiler, analytic and C_full hypotheses remain explicit. Not unconditional fully expanded primitive admission.')
(D/'HOSTED-RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(result,indent=2))
