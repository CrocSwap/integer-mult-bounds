"""Reconstruct both complete joint-prefix providers and admit all 72 calls.
Prepared with OpenAI Codex assistance; Apache-2.0. See NOTICE.md for sources.
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,time,shutil,platform,zlib
from pathlib import Path
from fractions import Fraction as Q
if not __debug__:raise RuntimeError('Assertions required; refusing optimized verification')
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
O=a.work.resolve();assert not O.exists()and not O.is_relative_to(P)
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8',newline='\n')
def inventory():return{f.relative_to(P).as_posix():sha(f)for f in P.rglob('*')if f.is_file()and f!=P/'MANIFEST.json'and'__pycache__'not in f.parts}
actual=inventory();assert actual==read(P/'MANIFEST.json');manifest_sha256=sha(P/'MANIFEST.json')
source_pins=read(P/'SOURCE-PINS.json')['files']
for rel,pin in source_pins.items():assert sha(P/rel)==pin['sha256'],'Immutable source pin mismatch: '+rel
claim=read(P/'proof/CLAIM.json')
O.mkdir(parents=True);steps=[];start=time.monotonic()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
def begin(name,script,*args):
 log=O/(name+'.log');f=log.open('w',encoding='utf-8');t=time.monotonic();print('RUN',name,flush=True)
 proc=subprocess.Popen([sys.executable,'-B',str(P/'code/run_portable.py'),str(script),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=env)
 return name,log,f,t,proc
def finish(job):
 name,log,f,t,proc=job;code=proc.wait();f.close()
 steps.append(dict(name=name,exit_code=code,seconds=time.monotonic()-t,log_sha256=sha(log)));dump(O/'STAGES.json',steps)
 if code:raise RuntimeError(name+' failed\n'+log.read_text(encoding='utf-8')[-6000:])
 print('PASS',name,flush=True)
def run(name,script,*args):finish(begin(name,script,*args))
B=P/'vendor/pr558';F=B/'vendor/pr552';V=F/'complex-global/vendor531'
baseline=O/'baseline558';first=O/'first-cold-word';plainword=O/'eightcold-word';promoted=O/'width7-word'
plain=O/'eightcold-local';width7=O/'width7-local';G=O/'mixed-global'
plainjoint=O/'eightcold-joint-word';width7joint=O/'width7-joint-word'
run('standard-library-packing-rebuild',P/'code/replay_packing.py','--recipe',P/'data/PACKING-CONSTRUCTION.json','--source-plan',P/'data/packing-source/PLAN.json','--source-owners',P/'data/packing-source/OWNERS.json.gz','--plan',P/'data/PLAN.json','--owners',P/'data/OWNERS.json.gz','--receipt',O/'PACKING-REPLAY.json')
run('frozen558-full-replay',P/'code/replay558_portable.py','--work',baseline)
run('portable-promotion-identity-controls',P/'code/promotion_identity_controls.py','--source',baseline/'reconstruction/weighted/FULL-WORD.json.gz','--out',O/'PROMOTION-IDENTITY-CONTROLS.json')
raw=baseline/'reconstruction/promoted/FULL-WORD.json.gz'
recipe=P/'data/EIGHT-COLD.json';multi=P/'data/EIGHT-MULTICOLD.json'
run('first-cold-construction',P/'code/build_cold_kernel.py','--input',raw,'--recipe',recipe,'--gk-dir',F/'complex-local/static44/gk','--out',first)
run('first-cold-kernel-omissions',P/'code/audit_kernel_controls.py','--word',first/'FULL-WORD.json.gz','--recipe',recipe,'--out',first/'KERNEL-OMISSION-CONTROLS.json')
run('eightcold-construction',P/'code/build_multicut_kernels.py','--input',first/'FULL-WORD.json.gz','--recipe',multi,'--gk-dir',F/'complex-local/static44/gk','--out',plainword)
# All eight source kernels are checked again on the complete scalar word.
run('eightcold-all-kernel-omissions',P/'code/audit_multicold_controls.py','--word',plainword/'FULL-WORD.json.gz','--recipe',P/'data/EIGHT-ALL-KERNELS.json','--out',plainword/'ALL-COLD-CONTROLS.json')
run('eightcold-inherited44-omissions',F/'complex-local/static44/audit_scalar.py',plainword/'FULL-WORD.json.gz',baseline/'reconstruction/static44/SELECTION.json',plainword/'STATIC44-SCALAR-AUDIT.json')
shutil.copyfile(raw.parent/'PROMOTION.json',plainword/'PROMOTION.json')
run('eightcold-rank5-omissions',B/'code/audit_promoted_scalar.py',plainword/'FULL-WORD.json.gz',baseline/'reconstruction/static44/SELECTION.json',plainword/'PROMOTED-SCALAR-AUDIT.json')
run('width7-construction',P/'code/build_entrance_promotions.py','--word',plainword/'FULL-WORD.json.gz','--recipes',P/'data/width7/eight/RECIPES.json','--gk-dir',F/'complex-local/static44/gk','--out',promoted)
run('width7-all-kernel-omissions',P/'code/audit_multicold_controls.py','--word',promoted/'FULL-WORD.json.gz','--recipe',P/'data/EIGHT-ALL-KERNELS.json','--out',promoted/'ALL-COLD-CONTROLS.json')
run('width7-independent-scalar-identity-and-omission-transfer',P/'code/audit_eightcold_frame_promotions.py','--source',plainword/'FULL-WORD.json.gz','--word',promoted/'FULL-WORD.json.gz','--recipes',P/'data/width7/eight/RECIPES.json','--kernel-recipes',P/'data/EIGHT-ALL-KERNELS.json','--source-controls',plainword,'--final-controls',promoted,'--selection',baseline/'reconstruction/static44/SELECTION.json','--promotion',plainword/'PROMOTION.json','--promotions',8,'--out',promoted/'FRAME-PROMOTION-AUDIT.json')
for name,source,word,local,kernels in [('eightcold',plainword,plainjoint,plain,'EIGHTCOLD-JOINT-KERNELS.json'),('width7',promoted,width7joint,width7,'WIDTH7-JOINT-KERNELS.json')]:
 run(name+'-joint-prefix-construction',P/'code/build_joint_prefix.py','--input',source/'FULL-WORD.json.gz','--recipe',P/'data/JOINT-PREFIX.json','--variant',name,'--gk-dir',F/'complex-local/static44/gk','--out',word)
 shutil.copyfile(plainword/'PROMOTION.json',word/'PROMOTION.json')
 run(name+'-joint-prefix-all-kernel-omissions',P/'code/audit_multicold_controls.py','--word',word/'FULL-WORD.json.gz','--recipe',P/'data'/kernels,'--out',word/'ALL-KERNEL-CONTROLS.json')
 run(name+'-joint-prefix-rank5-omissions',B/'code/audit_promoted_scalar.py',word/'FULL-WORD.json.gz',baseline/'reconstruction/static44/SELECTION.json',word/'RANK5-CONTROLS.json')
 run(name+'-independent-joint-prefix-and-coverage',P/'code/audit_joint_prefix.py','--source',source/'FULL-WORD.json.gz','--word',word/'FULL-WORD.json.gz','--recipe',P/'data/JOINT-PREFIX.json','--variant',name,'--kernel-recipes',P/'data'/kernels,'--controls',word/'ALL-KERNEL-CONTROLS.json','--rank5-controls',word/'RANK5-CONTROLS.json','--promotion',word/'PROMOTION.json','--selection',baseline/'reconstruction/static44/SELECTION.json','--out',word/'JOINT-PREFIX-AUDIT.json')
 run(name+'-all-columns-native-frames',V/'code/audit_and_transport.py','--raw',word/'FULL-WORD.json.gz','--routing',F/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz','--out',local)
 run(name+'-both-reflected-ledgers',V/'code/emit_local.py',local)
 run(name+'-independent-local-controls',V/'code/audit_local.py',local)
 run(name+'-normalized-wrappers',V/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
jobs=[begin(name+'-all-phase-edges',B/'code/phases_full.py',local,V/'vendor/clifford')for name,local in [('eightcold',plain),('width7',width7)]]
for job in jobs:finish(job)
run('bind-two-providers',P/'code/bind_providers_portable.py','--baseline',baseline,'--plain',plain,'--width7',width7,'--plan',P/'data/PLAN.json','--out',G)
run('emit-two-provider-controller',P/'code/emit_allcold.py','--base',G/'base','--owners',P/'data/OWNERS.json.gz','--plan',G/'PLAN.json','--out',G/'hosted')
run('independent-literal-owner-geometry',P/'code/review_owners.py','--base',G/'base','--plan',G/'PLAN.json','--owners',P/'data/OWNERS.json.gz','--plain',G/'base/providers/eightcold_eight','--width7',G/'base/providers/width7_eight','--nomination-receipt',P/'proof/OWNER-NOMINATION.json','--out',O/'INDEPENDENT-OWNER-REVIEW.json')
(G/'audit').mkdir()
run('independent-controller-and-controls',P/'code/audit_allcold.py',G/'base',G/'hosted',G/'audit/ASYNC-AUDIT.json','--mutation-controls')
run('fresh-two-provider-invoice',P/'code/invoice_allcold.py','--base',G/'base','--hosted',G/'hosted','--audit',G/'audit','--out',G/'audit','--retained-invoice',V/'evidence/audit/PREFIX-AND-INVOICE.json')
run('conservative-and-native-exact-assembly',P/'code/assemble.py',P,G,O/'ASSEMBLY.json')
run('admission-mutation-controls',P/'code/assembly_controls.py','--owner',G/'audit/OWNERS-AND-PROFILE.json','--invoice',G/'audit/PREFIX-AND-INVOICE.json','--out',O/'ASSEMBLY-CONTROLS.json')
run('phase-timing-portability-controls',P/'code/phase_timing_controls.py',G/'base',G/'audit',O/'PHASE-TIMING-CONTROLS.json')
run('generated-artifact-content-and-recompression-controls',P/'code/generated_identity_controls.py','--base',G/'base','--audit',G/'audit','--out',O/'GENERATED-IDENTITY-CONTROLS.json')
for local,edges in [(plain,2928),(width7,3004)]:
 r=read(local/'INDEPENDENT-LOCAL-REPLAY.json');ph=read(local/'CLIFFORD-REVIEW.json')
 assert len(r['negative_controls_rejected'])==11 and r['paid_profiles']['forward']==r['paid_profiles']['backward']
 assert ph['status']=='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES'and ph['all_child_equalities_include_global_phase']is True and ph['directed_edges']==edges and ph['endpoint_adapters']==224
for word in (plainword,promoted):assert len(read(word/'ALL-COLD-CONTROLS.json')['controls'])==38
transfer=read(promoted/'FRAME-PROMOTION-AUDIT.json')
assert transfer['status']=='PASS_EIGHT_COLD_FRAME_PROMOTION_SCALAR_TRANSFER'and transfer['all_scalar_operations_identical']is True
assert transfer['changed_frames']==96 and transfer['promotions']==32 and transfer['rank_five_promotions']==8
assert len(transfer['negative_controls_rejected'])==9
for word in (plainjoint,width7joint):
 assert sha(word/'PROMOTION.json')==sha(plainword/'PROMOTION.json')
 c=read(word/'ALL-KERNEL-CONTROLS.json');r5=read(word/'RANK5-CONTROLS.json');j=read(word/'JOINT-PREFIX-AUDIT.json')
 assert len(c['controls'])==135 and all(x['forward_rejected'] and x['reflected_rejected'] for x in c['controls'])
 assert len(r5['controls'])==8
 assert j['status']=='PASS_INDEPENDENT_LITERAL_PREFIX_AND_FINAL_KERNEL_COVERAGE'
 assert (j['old_prefix'],j['new_prefix'],j['prefix_kernels'],j['cold_kernels'],j['omission_cases'],j['distinct_omitted_position_sets'],j['rank5_omission_cases'])==(69,57,40,8,135,103,8)
 assert len(set(j['negative_controls_rejected']))==len(j['negative_controls_rejected'])==15
 assert j['unchanged_retained_event_frames'] and j['unchanged_A_tail_and_B'] and j['exact_regenerated_cleanup']
assert len(read(G/'audit/ASYNC-AUDIT.json')['mutations_rejected'])==claim['controller_mutations']
assert len(read(O/'ASSEMBLY-CONTROLS.json')['rejected_controls'])==claim['assembly_mutations']
assert read(O/'GENERATED-IDENTITY-CONTROLS.json')['counts']==dict(recompression_accepted=2,semantic_rejected=18,reference_or_metadata_rejected=18)
assert read(O/'PROMOTION-IDENTITY-CONTROLS.json')['counts']==dict(recompression_accepted=4,mutations_rejected=8)
assert inventory()==actual and sha(P/'MANIFEST.json')==manifest_sha256,'Package changed during full replay'
z=read(O/'ASSEMBLY.json')
assert Q(z['kappa_decimal'])==Q(claim['kappa_decimal'])>Q('0.001600682403612293')
assert Q(z['conservative_kappa_decimal'])==Q(claim['conservative_kappa_decimal'])
assert z['complex_profile']==claim['profile'] and z['provider_counts']==claim['provider_counts']
r=dict(status='PASS_ALL72_JOINT_PREFIX_NATIVE_COMPLEX_AND_CITED_BIT',kappa=z['kappa'],kappa_decimal=z['kappa_decimal'],complex_lower=z['complex_lower'],bit_lower=z['bit_lower'],conservative_kappa_decimal=z['conservative_kappa_decimal'],conservative_complex_lower=z['conservative_complex_lower'],global_profile=z['complex_profile'],provider_counts=z['provider_counts'],surcharge_model=z['surcharge_model'],seconds=time.monotonic()-start,scope=z['scope'])
dump(O/'RESULT.json',r)
paths=['PACKING-REPLAY.json','INDEPENDENT-OWNER-REVIEW.json','PROMOTION-IDENTITY-CONTROLS.json','GENERATED-IDENTITY-CONTROLS.json','PHASE-TIMING-CONTROLS.json','mixed-global/audit/IDLE-REMAINDER-FRAMES.json','RESULT.json','ASSEMBLY.json','ASSEMBLY-CONTROLS.json','mixed-global/BINDING.json','mixed-global/audit/ASYNC-AUDIT.json','mixed-global/audit/OWNERS-AND-PROFILE.json','mixed-global/audit/PREFIX-AND-INVOICE.json','first-cold-word/KERNEL-CONSTRUCTION.json','first-cold-word/KERNEL-OMISSION-CONTROLS.json','eightcold-word/KERNEL-CONSTRUCTION.json','eightcold-word/ALL-COLD-CONTROLS.json','eightcold-word/STATIC44-SCALAR-AUDIT.json','eightcold-word/PROMOTED-SCALAR-AUDIT.json','width7-word/CONSTRUCTION.json','width7-word/ALL-COLD-CONTROLS.json','width7-word/FRAME-PROMOTION-AUDIT.json']
for name in ('eightcold','width7'):
 for fn in ('CONSTRUCTION.json','ALL-KERNEL-CONTROLS.json','RANK5-CONTROLS.json','JOINT-PREFIX-AUDIT.json'):paths.append(name+'-joint-word/'+fn)
 for fn in ('INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json','WRAPPER-CHECKS.json'):paths.append(name+'-local/'+fn)
dump(O/'RECEIPT.json',dict(status=r['status'],steps=steps,artifacts={name:sha(O/name)for name in paths},manifest_sha256=manifest_sha256,immutable_source_pins_checked=len(source_pins),inputs_unchanged=True,runtime=dict(python=sys.version,platform=platform.platform(),zlib_version=zlib.ZLIB_VERSION,zlib_runtime_version=zlib.ZLIB_RUNTIME_VERSION)))
print(json.dumps(r,indent=2))
