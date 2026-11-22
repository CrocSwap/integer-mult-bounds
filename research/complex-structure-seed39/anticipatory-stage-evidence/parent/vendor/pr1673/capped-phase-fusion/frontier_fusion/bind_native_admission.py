"""Bind the completed unmodified PR1661 verifier run to the new outer corollary."""
from pathlib import Path
from fractions import Fraction as Q
import gzip,hashlib,json,sys
# The pinned 400-digit ledger expands exact rational slacks to 145k digits.
sys.set_int_max_str_digits(500000)
P=Path(__file__).resolve().parent;W=P.parent
RUN=W/'target002_upstream/full-1661-verification'
SRC=W/'target002_upstream/pr1661/research/gmx-t74-p566-ep400'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(RUN/'RESULT.json');claim=read(SRC/'CLAIM.json');spec=read(SRC/'new/SPEC.json')
assert r['status']=='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION'
assert Q(r['kappa'])==Q(claim['kappa'])==Q(spec['expected']['kappa'])
assert r['manifest_sha256']==sha(SRC/'MANIFEST.json')
steps=read(RUN/'STAGES.json')
required={'fine-engine-oracle','retained-provider-and-parent-admission','native-new-base','native-new-extra','reconstruct-owners','lift-parent','rebuild-words-566','audit-local-566-base','audit-local-566-extra','rebind-566','strict-t74','geometry-controls'}
assert {s['name'] for s in steps}==required and all(s['exit_code']==0 for s in steps)
assert steps==r['stages']
for z in steps:
 assert z['log_sha256']==sha(RUN/(z['name']+'.log'))
strict=read(RUN/'strict/RESULT.json')
assert strict['status']=='PASS_STRICT_MIXED_T74_EXACT_FILL' and Q(strict['kappa'])==Q(r['kappa'])
assembly=read(RUN/'strict/ASSEMBLY.json')
assert assembly['status']=='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY'
assert Q(assembly['complex_lower'])==Q(spec['expected']['complex_lower'])
assert assembly['complex_profile']=={str(k):v for k,v in spec['expected']['global_profile'].items()}
assert len(assembly['outer'])==47 and all(Q(x)>0 for x in assembly['outer'].values())
checks=[]
for key,word in [('base','gauge44-word-566.json.gz'),('extra','extra-word-566.json.gz')]:
 d=RUN/('native-new-'+key)
 st=read(d/'STEPS.json')
 assert [z['step'] for z in st]==['native','ledgers','local-replay','wrappers','phases']
 assert all(z['exit_code']==0 for z in st)
 assert gzip.decompress((d/'local/FULL-WORD.json.gz').read_bytes())==gzip.decompress((SRC/'new'/word).read_bytes())
 checks.append({'provider':key,'word_sha256':sha(SRC/'new'/word),'native_steps':st})
paths={RUN/'RESULT.json',RUN/'STAGES.json',RUN/'parent/RESULT.json',RUN/'strict/RESULT.json',RUN/'strict/STAGES.json',RUN/'strict/ASSEMBLY.json',SRC/'MANIFEST.json',SRC/'CLAIM.json',SRC/'new/SPEC.json',SRC/'new/PROFILE.json'}
for base in [RUN/'native-new-base',RUN/'native-new-extra',RUN/'strict']:
 for f in base.rglob('*.json'):
  if any(tag in f.name.upper() for tag in ['CONTROL','CHECK','REVIEW','AUDIT','REPLAY','INVOICE','STAGES']):paths.add(f)
for z in steps:paths.add(RUN/(z['name']+'.log'))
report={'status':'PASS_FRESH_NATIVE_ADMISSION_BOUND_TO_CONDITIONAL_SUBSTITUTION',
 'scope':'Unmodified PR1661 complete fresh finite/native/global verifier passed; the independently reviewed phase-fusion recomposition retains all inherited all-size, hosting, precision/tape, exact-recovery and analytic hypotheses. The matrix corollary additionally assumes omega_C<=9/4.',
 'source_pr':1661,'source_head':'f852af5e178ce035cd46181a29d9330bcbcaa206','source_manifest_sha256':r['manifest_sha256'],
 'complex_lower_pinned':assembly['complex_lower'],'complex_lower_used':'0.00167971337478','native_profile':assembly['complex_profile'],
 'full_status':r['status'],'control_counts':r['controls'],'new_native_provider_checks':checks,
 'claimed_upstream_kappa':r['kappa'],'recomposed_final_kappa':{'strassen':'0.001677160151714381','matrix_9_4':'0.001677600129305161'},
 'receipt_sha256':{str(f.relative_to(W)):sha(f) for f in sorted(paths)}}
(P/'NATIVE-ADMISSION-BINDING.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['status'],len(paths),'bound receipt files')
