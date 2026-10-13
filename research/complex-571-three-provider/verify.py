"""Admit the three-provider literal witness: #571's width-seven prefix word (P571), the same word with twelve PR568 multi-cut cold kernels (P571K), and PR568's eight-cold eight-pivot provider (E8).
Prepared with Claude Code assistance. Apache-2.0; see NOTICE.md.
The unchanged PR568 package (research/complex-multicold) and #571 package (research/structural-gain) are pinned external sources.
P571K is built by PR568's unchanged build_multicut_kernels.py from #571's pinned word and data/P571K-MULTICOLD.json.
Global stages are spec-driven: every pinned witness value is in data/WITNESS-SPEC.json (read by code/witness.py).
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,time,shutil
from pathlib import Path
from fractions import Fraction as Q
assert __debug__, 'Assertions required'
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True)
ap.add_argument('--multicold',type=Path,default=P.parent/'complex-multicold',help='unchanged PR568 package')
ap.add_argument('--structural-gain',type=Path,default=P.parent/'structural-gain',help='unchanged #571 package')
a=ap.parse_args();O=a.work.resolve();S=a.multicold.resolve();L=a.structural_gain.resolve()
assert not O.exists() and not any(O.is_relative_to(x)for x in (P,S,L))
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def tree(root,skip):return{f.relative_to(root).as_posix():sha(f)for f in root.rglob('*')if f.is_file()and f!=root/skip and'__pycache__'not in f.parts}
assert tree(P,'MANIFEST.json')==read(P/'MANIFEST.json')
pins=read(P/'data/PINS.json');spec=read(P/'data/WITNESS-SPEC.json');X=spec['expected']
assert spec['data']['plan_sha256']==sha(P/'data/PLAN.json') and spec['data']['owners_sha256']==sha(P/'data/OWNERS.json.gz')
assert sha(S/'MANIFEST.json')==pins['multicold_source']['manifest_sha256'] and tree(S,'MANIFEST.json')==read(S/'MANIFEST.json')
assert sha(L/'MANIFEST.json')==pins['structural_gain_source']['manifest_sha256']
for name,value in pins['structural_gain_source']['files'].items():assert sha(L/name)==value==read(L/'MANIFEST.json')['files'][name]
O.mkdir(parents=True);steps=[];start=time.monotonic()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',MULTICOLD_SOURCE=str(S),GAIN_PR564_SOURCE=str(S),WITNESS_SPEC=str(P/'data/WITNESS-SPEC.json'));env.pop('WITNESS_DISCOVER',None);env.pop('PYTHONOPTIMIZE',None)
def begin(name,script,*args):
 log=O/(name+'.log');f=log.open('w');t=time.monotonic();print('RUN',name,flush=True)
 proc=subprocess.Popen([sys.executable,'-B',str(S/'code/run_portable.py'),str(script),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=env)
 return name,log,f,t,proc
def finish(job):
 name,log,f,t,proc=job;code=proc.wait();f.close();steps.append(dict(name=name,exit_code=code,seconds=time.monotonic()-t,log_sha256=sha(log)));dump(O/'STAGES.json',steps)
 if code:raise RuntimeError(name+' failed\n'+log.read_text()[-6000:])
 print('PASS',name,flush=True)
def run(name,script,*args):finish(begin(name,script,*args))
B=S/'vendor/pr558';F=B/'vendor/pr552';V=F/'complex-global/vendor531';GK=F/'complex-local/static44/gk';baseline=O/'baseline558';SEL=baseline/'reconstruction/static44/SELECTION.json';G=O/'mixed-global'
run('frozen558-full-replay',B/'verify.py','--work',baseline)
# PR568's eight-pivot provider, rebuilt exactly as research/complex-multicold/verify.py does.
raw=baseline/'reconstruction/promoted/FULL-WORD.json.gz';cold=O/'eight-cold-word';word=O/'eight-multicold-word';recipe=S/'data/EIGHT-COLD.json';multi=S/'data/EIGHT-MULTICOLD.json'
run('eight-cold-construction',S/'code/build_cold_kernel.py','--input',raw,'--recipe',recipe,'--gk-dir',GK,'--out',cold)
run('eight-cold-kernel-omissions',S/'code/audit_kernel_controls.py','--word',cold/'FULL-WORD.json.gz','--recipe',recipe,'--out',cold/'KERNEL-OMISSION-CONTROLS.json')
run('eight-multicold-construction',S/'code/build_multicut_kernels.py','--input',cold/'FULL-WORD.json.gz','--recipe',multi,'--gk-dir',GK,'--out',word)
run('eight-multicold-kernel-omissions',S/'code/audit_multicold_controls.py','--word',word/'FULL-WORD.json.gz','--recipe',multi,'--out',word/'MULTICOLD-OMISSION-CONTROLS.json')
run('eight-inherited-44-omissions',F/'complex-local/static44/audit_scalar.py',word/'FULL-WORD.json.gz',SEL,word/'STATIC44-SCALAR-AUDIT.json')
shutil.copyfile(raw.parent/'PROMOTION.json',word/'PROMOTION.json')
run('eight-promoted-omissions',B/'code/audit_promoted_scalar.py',word/'FULL-WORD.json.gz',SEL,word/'PROMOTED-SCALAR-AUDIT.json')
assert hashlib.sha256(gzip.decompress((word/'FULL-WORD.json.gz').read_bytes())).hexdigest()==pins['eight_multicold_word_content_sha256']
# #571's admitted combined-prefix word (pinned by its manifest), localized by the same unchanged vendor pipeline #571 uses.
w7src=L/'frontier-composition/combined-prefix-word';w7retained=L/'frontier-composition/combined-prefix-local'
assert hashlib.sha256(gzip.decompress((w7src/'FULL-WORD.json.gz').read_bytes())).hexdigest()==pins['width7_word_content_sha256']
# P571K: PR568's unchanged multi-cut kernel constructor applied to #571's pinned word, then its omission controls.
kword=O/'prefixk-word'
run('prefixk-multicold-construction',S/'code/build_multicut_kernels.py','--input',w7src/'FULL-WORD.json.gz','--recipe',P/'data/P571K-MULTICOLD.json','--gk-dir',GK,'--out',kword)
assert hashlib.sha256(gzip.decompress((kword/'FULL-WORD.json.gz').read_bytes())).hexdigest()==pins['prefixk_word_content_sha256']
run('prefixk-multicold-kernel-omissions',S/'code/audit_multicold_controls.py','--word',kword/'FULL-WORD.json.gz','--recipe',P/'data/P571K-MULTICOLD.json','--out',kword/'MULTICOLD-OMISSION-CONTROLS.json')
providers={'eight':(word,O/'eight-cold-local'),'width7':(w7src,O/'width7-local'),'prefixk':(kword,O/'prefixk-local')}
for name,(src,local) in providers.items():
 run(name+'-all-columns-native-frames',V/'code/audit_and_transport.py','--raw',src/'FULL-WORD.json.gz','--routing',F/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz','--out',local)
 run(name+'-both-reflected-ledgers',V/'code/emit_local.py',local)
 run(name+'-independent-local-controls',V/'code/audit_local.py',local)
 run(name+'-normalized-wrappers',V/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
phase_jobs=[begin(name+'-all-phase-edges',B/'code/phases_full.py',local,V/'vendor/clifford')for name,(src,local) in providers.items()]
for job in phase_jobs:finish(job)
eight,width7,prefixk=(providers[n][1] for n in ('eight','width7','prefixk'))
# The fresh width-seven local is byte-identical to #571's retained, manifest-pinned local (phase review up to timing).
for name in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','INDEPENDENT-LOCAL-REPLAY.json','RESIDUAL-ADAPTERS.json','WRAPPER-CHECKS.json','CLIFFORD-RECIPES.json'):
 assert sha(width7/name)==sha(w7retained/name),name
fresh,kept=read(width7/'CLIFFORD-REVIEW.json'),read(w7retained/'CLIFFORD-REVIEW.json')
assert {k:v for k,v in fresh.items()if k!='seconds'}=={k:v for k,v in kept.items()if k!='seconds'}
locals_={'fourcold_eight':eight,'width7_eight':width7,'prefixk_eight':prefixk}
assert set(locals_)==set(spec['providers'])
run('bind-three-providers',P/'code/bind_providers_portable.py','--baseline',baseline,*[x for pid,d in sorted(locals_.items()) for x in ('--provider','%s=%s'%(pid,d))],'--plan',P/'data/PLAN.json','--out',G)
run('emit-three-provider-controller',P/'code/emit_allcold.py','--base',G/'base','--owners',P/'data/OWNERS.json.gz','--plan',G/'PLAN.json','--out',G/'hosted')
(G/'audit').mkdir()
run('independent-controller-and-controls',P/'code/audit_allcold.py',G/'base',G/'hosted',G/'audit/ASYNC-AUDIT.json','--mutation-controls')
run('fresh-three-provider-invoice',P/'code/invoice_allcold.py','--base',G/'base','--hosted',G/'hosted','--audit',G/'audit','--out',G/'audit','--retained-invoice',V/'evidence/audit/PREFIX-AND-INVOICE.json')
run('conservative-and-native-exact-assembly',P/'code/assemble.py',S,G,O/'ASSEMBLY.json')
run('admission-controls',P/'code/assembly_controls.py','--source-package',S,'--owner',G/'audit/OWNERS-AND-PROFILE.json','--invoice',G/'audit/PREFIX-AND-INVOICE.json','--out',O/'ASSEMBLY-CONTROLS.json')
run('phase-timing-portability-controls',P/'code/phase_timing_controls.py',S,G/'base',G/'audit',O/'PHASE-TIMING-CONTROLS.json')
for pid,local in locals_.items():
 r=read(local/'INDEPENDENT-LOCAL-REPLAY.json');ph=read(local/'CLIFFORD-REVIEW.json');sp=spec['providers'][pid]
 assert len(r['negative_controls_rejected'])==sp['native_negative_controls']==11 and r['paid_profiles']['forward']==r['paid_profiles']['backward']
 assert ph['status']=='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES' and ph['all_child_equalities_include_global_phase']is True and ph['directed_edges']==sp['phase_edges'] and ph['endpoint_adapters']==224
assert len(read(kword/'MULTICOLD-OMISSION-CONTROLS.json')['controls'])==pins['prefixk_multicold_omission_controls']
assert len(read(cold/'KERNEL-OMISSION-CONTROLS.json')['controls'])==6
assert len(read(word/'MULTICOLD-OMISSION-CONTROLS.json')['controls'])==32
assert len(read(G/'audit/ASYNC-AUDIT.json')['mutations_rejected'])==X['mutations_rejected']
assert len(read(O/'ASSEMBLY-CONTROLS.json')['rejected_controls'])==X['assembly_controls_rejected']
z=read(O/'ASSEMBLY.json');assert Q(z['kappa_decimal'])==Q(X['kappa_decimal']) and Q(z['conservative_kappa_decimal'])==Q(X['conservative_kappa_decimal'])
assert {str(k):v for k,v in z['complex_profile'].items()}==X['global_profile'] and z['provider_counts']==X['provider_counts']
r=dict(status='PASS_PR571_PREFIX_WORD_PREFIXK_AND_PR568_EIGHT_COLD_THREE_PROVIDER_NATIVE_COMPLEX_AND_CITED_BIT',kappa=z['kappa'],kappa_decimal=z['kappa_decimal'],complex_lower=z['complex_lower'],bit_lower=z['bit_lower'],conservative_kappa_decimal=z['conservative_kappa_decimal'],conservative_complex_lower=z['conservative_complex_lower'],global_profile=z['complex_profile'],provider_counts=z['provider_counts'],surcharge_model=z['surcharge_model'],seconds=time.monotonic()-start,scope=z['scope']);dump(O/'RESULT.json',r)
paths=['PHASE-TIMING-CONTROLS.json','mixed-global/audit/IDLE-REMAINDER-FRAMES.json','RESULT.json','ASSEMBLY.json','ASSEMBLY-CONTROLS.json','mixed-global/BINDING.json','mixed-global/audit/ASYNC-AUDIT.json','mixed-global/audit/OWNERS-AND-PROFILE.json','mixed-global/audit/PREFIX-AND-INVOICE.json',
 'eight-cold-word/KERNEL-CONSTRUCTION.json','eight-cold-word/KERNEL-OMISSION-CONTROLS.json','eight-multicold-word/KERNEL-CONSTRUCTION.json','eight-multicold-word/MULTICOLD-OMISSION-CONTROLS.json','eight-multicold-word/STATIC44-SCALAR-AUDIT.json','eight-multicold-word/PROMOTED-SCALAR-AUDIT.json','prefixk-word/KERNEL-CONSTRUCTION.json','prefixk-word/MULTICOLD-OMISSION-CONTROLS.json']
for name in ('eight-cold-local','width7-local','prefixk-local'):
 for fn in ('INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json','WRAPPER-CHECKS.json'):paths.append(name+'/'+fn)
dump(O/'RECEIPT.json',dict(status=r['status'],steps=steps,artifacts={name:sha(O/name)for name in paths},manifest_sha256=sha(P/'MANIFEST.json'),multicold_manifest_sha256=sha(S/'MANIFEST.json'),structural_gain_manifest_sha256=sha(L/'MANIFEST.json'),witness_spec_sha256=sha(P/'data/WITNESS-SPEC.json')))
print(json.dumps(r,indent=2))
